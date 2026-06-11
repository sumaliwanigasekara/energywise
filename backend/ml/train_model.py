"""
train_model.py
Trains RandomForestRegressor and XGBoostRegressor on real Sri Lankan
household electricity consumption data. Compares both models and saves
the better performing one as model.pkl.

Dataset: data/processed/training_dataset.csv (produced by data/preprocess.py)
Fallback: synthetic data if dataset file is not found.

To retrain:
    python backend/ml/train_model.py
"""

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor
import joblib

SAVE_PATH    = os.path.join(os.path.dirname(__file__), "model.pkl")
DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "training_dataset.csv")
np.random.seed(42)
N = 6000

FEATURE_COLS = [
    "members", "avg_prev_bill", "fan_count", "ac_count",
    "ac_hours_per_month", "ac_tons", "fridge_count",
    "washer_hours_per_month", "heater_hours_per_month",
    "other_hours_per_month", "avg_temp", "avg_humidity",
    "total_precip", "avg_wind", "month"
]


# ---------------------------------------------------------------------------
# SYNTHETIC FALLBACK
# ---------------------------------------------------------------------------
def generate_synthetic_data():
    members = np.random.randint(1, 9, N)
    avg_prev_bill = np.random.uniform(500, 25000, N)
    fan_count = np.random.randint(0, 8, N)
    ac_count = np.random.randint(0, 4, N)
    ac_hours_per_month = np.where(ac_count > 0, np.random.uniform(0, 300, N), 0.0)
    ac_tons = np.random.choice([1.0, 1.5, 2.0], N)
    fridge_count = np.random.randint(0, 3, N)
    washer_hours_per_month = np.random.uniform(0, 60, N)
    heater_hours_per_month = np.random.uniform(0, 43, N)
    other_hours_per_month = np.random.uniform(4, 120, N)
    avg_temp = np.random.uniform(24, 36, N)
    avg_humidity = np.random.uniform(60, 95, N)
    total_precip = np.random.uniform(0, 300, N)
    avg_wind = np.random.uniform(5, 30, N)
    month = np.random.randint(1, 13, N)

    daily_kwh = (
        ac_count * (ac_hours_per_month / 30) * ac_tons * 0.7
        + fan_count * 0.06 * np.random.uniform(6, 14, N)
        + fridge_count * 0.15 * 24
        + washer_hours_per_month / 30 * 2.0
        + heater_hours_per_month / 30 * 1.5
        + (other_hours_per_month / 30) * 0.3
    )
    base_load = members * 0.25
    temp_factor = 1.0 + np.maximum(0, avg_temp - 28) * 0.025
    seasonal_factor = np.where(np.isin(month, [3, 4, 5, 9, 10, 11]), 1.08, 1.0)
    bill_factor = 0.6 + 0.4 * (avg_prev_bill / avg_prev_bill.max())
    monthly_units = (daily_kwh + base_load) * 30 * temp_factor * seasonal_factor * bill_factor
    noise = np.random.uniform(0.88, 1.12, N)
    monthly_units = np.clip(monthly_units * noise, 5, 1500)

    X = pd.DataFrame({
        "members": members, "avg_prev_bill": avg_prev_bill,
        "fan_count": fan_count, "ac_count": ac_count,
        "ac_hours_per_month": ac_hours_per_month, "ac_tons": ac_tons,
        "fridge_count": fridge_count,
        "washer_hours_per_month": washer_hours_per_month,
        "heater_hours_per_month": heater_hours_per_month,
        "other_hours_per_month": other_hours_per_month,
        "avg_temp": avg_temp, "avg_humidity": avg_humidity,
        "total_precip": total_precip, "avg_wind": avg_wind,
        "month": month,
    })
    return X, monthly_units


# ---------------------------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------------------------
def load_data():
    dataset_path = os.path.abspath(DATASET_PATH)
    if os.path.exists(dataset_path):
        print(f"Loading real dataset from: {dataset_path}")
        df = pd.read_csv(dataset_path)
        X = df[FEATURE_COLS]
        y = df["consumption_kwh"]
        print(f"Real dataset loaded: {len(df)} rows")
        return X, y, "real"
    else:
        print("WARNING: Real dataset not found — using synthetic fallback.")
        print(f"Expected path: {dataset_path}")
        X, y = generate_synthetic_data()
        return X, y, "synthetic"


# ---------------------------------------------------------------------------
# EVALUATE
# ---------------------------------------------------------------------------
def evaluate(model, X_test, y_test, name):
    y_pred = model.predict(X_test)
    mae  = mean_absolute_error(y_test, y_pred)
    mse  = mean_squared_error(y_test, y_pred)
    r2   = r2_score(y_test, y_pred)
    print(f"\n{name} Results:")
    print(f"  MAE : {mae:.2f} kWh")
    print(f"  MSE : {mse:.2f}")
    print(f"  R²  : {r2:.4f}")
    return mae, mse, r2


# ---------------------------------------------------------------------------
# TRAIN
# ---------------------------------------------------------------------------
def train():
    X, y, source = load_data()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"\nTraining on {len(X_train)} rows | Testing on {len(X_test)} rows")

    # --- Random Forest ---
    print("\nTraining RandomForestRegressor...")
    rf_model = RandomForestRegressor(
        n_estimators=200,
        max_depth=12,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
    )
    rf_model.fit(X_train, y_train)
    rf_mae, rf_mse, rf_r2 = evaluate(rf_model, X_test, y_test, "Random Forest")

    # --- XGBoost ---
    print("\nTraining XGBoostRegressor...")
    xgb_model = XGBRegressor(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        verbosity=0,
    )
    xgb_model.fit(X_train, y_train)
    xgb_mae, xgb_mse, xgb_r2 = evaluate(xgb_model, X_test, y_test, "XGBoost")

    # --- Compare and save winner ---
    print("\n--- Model Comparison ---")
    print(f"{'Metric':<10} {'Random Forest':>15} {'XGBoost':>15}")
    print(f"{'MAE':<10} {rf_mae:>15.2f} {xgb_mae:>15.2f}")
    print(f"{'MSE':<10} {rf_mse:>15.2f} {xgb_mse:>15.2f}")
    print(f"{'R²':<10} {rf_r2:>15.4f} {xgb_r2:>15.4f}")

    if rf_r2 >= xgb_r2:
        winner = rf_model
        winner_name = "Random Forest"
    else:
        winner = xgb_model
        winner_name = "XGBoost"

    print(f"\nWinner: {winner_name} (R²: {max(rf_r2, xgb_r2):.4f})")
    print(f"Saving to {SAVE_PATH}")
    joblib.dump(winner, SAVE_PATH)
    print(f"Done. Data source: {source}")


if __name__ == "__main__":
    train()