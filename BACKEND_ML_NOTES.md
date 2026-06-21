# EnergyWise — Backend & ML Training Notes

## Project Overview

EnergyWise is an AI-based web application that predicts monthly electricity consumption (kWh) and estimated bill (LKR) for domestic households in the **Colombo District, Sri Lanka**. It uses a trained ML model served through a Flask REST API with a React frontend. No smart meters or IoT devices are required — all inputs are user-reported.

---

## Dataset

- **Source**: LIRNEasia household survey (Wave 1) + CEB non-smart-meter monthly consumption data
- **Scope**: Colombo District only (8 areas: Moratuwa North/South, Maharagama, Boralasgamuwa, Pita-Kotte, Kolonnawa, Kotikawatta, Nugegoda)
- **Households**: 1,676 unique households
- **Time period**: October 2022 – October 2024 (25 months)
- **Raw consumption rows**: 101,575
- **After preprocessing**: ~39,812 rows (Colombo filter + outlier removal + lag feature drop)

---

## Preprocessing Pipeline

**File**: `data/preprocess.py`  
**Output**: `data/processed/training_dataset.csv`

### Steps

1. **Load raw data** — monthly consumption CSV + wave 1 survey files (AC, fan, appliances, household info)
2. **Fill missing consumption** — per-household mean imputation (590 NaN values)
3. **Remove outliers** — drop rows where `consumption > 1000 kWh` (removes ~101 extreme rows)
4. **Colombo filter** — keep only households in the 8 Colombo CEB areas
5. **Aggregate appliances per household**:
   - AC: count, monthly hours, average tons (BTU/12000); missing BTU filled with 18,000 (1.5 ton default)
   - Fan: count, monthly hours
   - Fridge: count
   - Washing machine: monthly hours
   - Water heater: monthly hours
   - Other appliances: monthly hours
6. **Compute lag features** (after sorting by household + month):
   - `avg_prev_bill` — rolling 3-month average of previous consumption
   - `prev_month_consumption` — actual consumption in month t-1
   - `std_prev_3months` — std dev of last 3 months (0 if fewer than 2 readings)
   - `consumption_trend` — (t-1) minus (t-2), i.e. direction of change (0 if unknown)
7. **Drop first month per household** — rows where `prev_month_consumption` is NaN (no prior data; these are also the leakage rows)
8. **Fetch weather** — Open-Meteo archive API, per area per month: avg_temp, avg_humidity, total_precip, avg_wind. Results cached at `data/processed/weather_cache_areas.csv` to avoid re-fetching.
9. **Join weather** — merge final_df with weather on (area, month_str)
10. **Save** — `data/processed/training_dataset.csv`

---

## Features (21 total)

| Feature | Description |
|---|---|
| `members` | Number of household members |
| `avg_prev_bill` | 3-month rolling average of past consumption (kWh) |
| `prev_month_consumption` | Last month's actual consumption (kWh) |
| `std_prev_3months` | Std dev of last 3 months' consumption |
| `consumption_trend` | Change from month before last to last month |
| `fan_count` | Number of fans |
| `fan_hours_per_month` | Total fan usage hours/month |
| `ac_count` | Number of AC units |
| `ac_hours_per_month` | Total AC usage hours/month |
| `ac_tons` | Average AC capacity (tons of refrigeration) |
| `fridge_count` | Number of refrigerators |
| `washer_hours_per_month` | Washing machine usage hours/month |
| `heater_hours_per_month` | Water heater usage hours/month |
| `other_hours_per_month` | Other appliances usage hours/month |
| `avg_temp` | Monthly average temperature (°C) |
| `avg_humidity` | Monthly average relative humidity (%) |
| `total_precip` | Monthly total precipitation (mm) |
| `avg_wind` | Monthly average wind speed (km/h) |
| `month` | Month number (1–12) |
| `ac_kwh_est` | Physics estimate: `ac_count × ac_hours × ac_tons × 0.7` |
| `total_load_est` | Physics estimate of total appliance load (kWh) |

**Target**: `consumption_kwh` — actual monthly meter reading

---

## ML Training

**File**: `backend/ml/train_model.py`

### Train/Test Split
- 80% train / 20% test, `random_state=42`
- ~31,850 training rows, ~7,962 test rows

### Models Trained

#### 1. Linear Regression (baseline)
- No hyperparameters
- R² ≈ 0.870

#### 2. Random Forest (winner for Colombo-only)
```python
RandomForestRegressor(
    n_estimators=300,
    max_depth=15,
    min_samples_leaf=3,
    max_features=5,
    random_state=42,
    n_jobs=-1,
)
```
- **R² = 0.886**, MAE ≈ 19.9 kWh

#### 3. XGBoost
```python
XGBRegressor(
    n_estimators=500,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.7,
    min_child_weight=5,
    reg_alpha=0.1,
    reg_lambda=1.0,
    random_state=42,
    n_jobs=-1,
)
```
- R² = 0.884, MAE ≈ 19.8 kWh

### Hyperparameter Tuning
GridSearchCV with 5-fold cross-validation was run over 81 combinations for each model. Best params are encoded directly in the training script.

### Model Selection
Best model saved to `backend/ml/model.pkl` using `joblib.dump()`.

---

## Key Feature Importances (Random Forest)

| Feature | Importance |
|---|---|
| `avg_prev_bill` | ~38% |
| `prev_month_consumption` | ~25% |
| `ac_hours_per_month` | ~8% |
| `ac_kwh_est` | ~5% |
| `total_load_est` | ~4% |
| Weather + other features | ~20% |

`avg_prev_bill` and `prev_month_consumption` together dominate because the dataset is a time series — a household's past usage is the strongest predictor of its next month's usage.

---

## Backend Architecture

**Framework**: Flask (Python)  
**Entry point**: `backend/app/` (routes, services, models)

### Key Files

| File | Purpose |
|---|---|
| `backend/ml/train_model.py` | Trains and saves the model |
| `backend/ml/model.pkl` | Serialized Random Forest model |
| `backend/app/services/ml_service.py` | Loads model, computes features at inference, returns prediction |
| `backend/app/services/tariff_service.py` | PUCSL 2026 tariff calculation (LKR from kWh) |
| `backend/app/routes/predict.py` | `/predict` API endpoint |
| `backend/app/routes/appliances.py` | Appliance-related routes |

### Inference Flow (`ml_service.py`)

1. Receives payload: `members`, `prev_bill_1/2/3`, `fan_count`, `fan_hours_per_month`, `ac_count`, `ac_hours_per_month`, `ac_tons`, `fridge_count`, `washer_hours_per_month`, `heater_hours_per_month`, `other_hours_per_month`, `weather` (auto-fetched)
2. Computes lag features from prev bills:
   - `avg_prev_bill` = mean of non-zero prev bills
   - `prev_month_consumption` = `prev_bill_1`
   - `std_prev_3months` = std of non-zero prev bills
   - `consumption_trend` = `prev_bill_1 - prev_bill_2`
3. Computes engineered features (`ac_kwh_est`, `total_load_est`)
4. Runs `model.predict()` → `predicted_units` (kWh)
5. Calls `calculate_bill(predicted_units)` → `predicted_bill` (LKR)
6. Calls recommendation engine → personalized tips with LKR savings
7. Returns JSON with `predicted_units`, `predicted_bill`, `risk_level`, `recommendations`, `appliance_breakdown`

---

## Tariff Structure (PUCSL 2026)

Three-schedule structure. The recommendation engine detects proximity to tariff boundaries (60 kWh and 180 kWh) and calculates exact LKR savings if the user crosses into a lower schedule.

---

## Notebooks

**File**: `EnergyWise_Pipeline.ipynb`

Runs the full pipeline end-to-end and is used for presenting results. Steps:
1. Load raw data
2. Process AC / fan / appliance data
3. Colombo filter + outlier removal (>1000 kWh)
4. Merge survey tables
5. Join consumption + compute lag features
6. Build feature set (drop first month per household)
7. Fetch weather (cached at `data/processed/weather_cache_areas.csv`)
8. Join weather + save training CSV
9. EDA (distribution, correlation heatmap)
10. Train/test split + feature engineering
11. Train Linear Regression, Random Forest, XGBoost
12. Compare results + save best model
13. Feature importance plot

---

## Model Performance Summary

| Model | R² | MAE (kWh) |
|---|---|---|
| Linear Regression | 0.870 | 20.7 |
| Random Forest | **0.886** | 19.9 |
| XGBoost | 0.884 | 19.8 |

Target R² set by lecturer: >0.85, ideally close to 0.90. **Current best: 0.886.**

---

## To Retrain

```bash
cd energywise_git
python data/preprocess.py       # regenerates training_dataset.csv (uses weather cache)
python backend/ml/train_model.py  # trains all models, saves best to model.pkl
```

Or run the notebook top-to-bottom: **Kernel → Restart & Run All**
