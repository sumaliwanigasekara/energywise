"""
train_model.py
Generates synthetic Sri Lankan household electricity data and trains a
RandomForestRegressor as a placeholder model.

When Sumali has the real dataset:
  1. Load real data into X, y below
  2. Run:  python ml/train_model.py
  3. The new model.pkl replaces this one - no other changes needed.
"""

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

SAVE_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
np.random.seed(42)
N = 6000


def generate_synthetic_data():
    members = np.random.randint(1, 9, N)
    avg_prev_bill = np.random.uniform(500, 25000, N)

    fan_count = np.random.randint(0, 8, N)
    ac_count = np.random.randint(0, 4, N)
    ac_hours_per_day = np.where(ac_count > 0, np.random.uniform(1, 14, N), 0.0)
    ac_tons = np.random.choice([1.0, 1.5, 2.0], N)
    fridge_count = np.random.randint(0, 3, N)
    washer_hours_week = np.random.uniform(0, 14, N)
    heater_hours_week = np.random.uniform(0, 10, N)
    other_hours_per_day = np.random.uniform(1, 8, N)

    # Weather features
    avg_temp = np.random.uniform(24, 36, N)
    avg_humidity = np.random.uniform(60, 95, N)
    total_precip = np.random.uniform(0, 300, N)
    avg_wind = np.random.uniform(5, 30, N)
    month = np.random.randint(1, 13, N)

    # Physics-based formula (appliance consumption)
    daily_kwh = (
        ac_count * ac_hours_per_day * ac_tons * 0.7
        + fan_count * 0.06 * np.random.uniform(6, 14, N)
        + fridge_count * 0.15 * 24
        + washer_hours_week / 7 * 2.0
        + heater_hours_week / 7 * 1.5
        + other_hours_per_day * 0.3
    )

    base_load = members * 0.25
    temp_factor = 1.0 + np.maximum(0, avg_temp - 28) * 0.025

    # Months 3,4,5,9,10,11 are hotter/wetter in Sri Lanka — higher consumption
    seasonal_factor = np.where(np.isin(month, [3, 4, 5, 9, 10, 11]), 1.08, 1.0)

    # Previous bill influence (captures household behaviour patterns)
    bill_factor = 0.6 + 0.4 * (avg_prev_bill / avg_prev_bill.max())

    monthly_units = (daily_kwh + base_load) * 30 * temp_factor * seasonal_factor * bill_factor
    noise = np.random.uniform(0.88, 1.12, N)
    monthly_units = np.clip(monthly_units * noise, 5, 1500)

    # Feature order must match ml_service.py exactly (15 features)
    X = pd.DataFrame({
        "members":                members,          # 1
        "avg_prev_bill":          avg_prev_bill,    # 2
        "fan_count":              fan_count,        # 3
        "ac_count":               ac_count,         # 4
        "ac_hours_per_day":       ac_hours_per_day, # 5
        "ac_tons":                ac_tons,          # 6
        "fridge_count":           fridge_count,     # 7
        "washer_hours_per_week":  washer_hours_week,# 8
        "heater_hours_per_week":  heater_hours_week,# 9
        "other_hours_per_day":    other_hours_per_day, # 10
        "avg_temp":               avg_temp,         # 11
        "avg_humidity":           avg_humidity,     # 12
        "total_precip":           total_precip,     # 13
        "avg_wind":               avg_wind,         # 14
        "month":                  month,            # 15
    })

    return X, monthly_units


def train():
    print("Generating synthetic training data...")
    X, y = generate_synthetic_data()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Training RandomForestRegressor...")
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=12,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"MAE: {mae:.2f} kWh | R²: {r2:.4f}")
    print(f"Saving model to {SAVE_PATH}")

    joblib.dump(model, SAVE_PATH)
    print("Done.")


if __name__ == "__main__":
    train()
