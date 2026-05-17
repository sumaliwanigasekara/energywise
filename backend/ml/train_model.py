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
    ac_hours = np.where(ac_count > 0, np.random.uniform(1, 14, N), 0.0)
    ac_tons = np.random.choice([1.0, 1.5, 2.0], N)
    fridge_count = np.random.randint(0, 3, N)
    washer_hours_week = np.random.uniform(0, 14, N)
    heater_hours_week = np.random.uniform(0, 10, N)
    other_hours_day = np.random.uniform(1, 8, N)
    temperature = np.random.uniform(24, 36, N)

    # Physics-based formula (appliance consumption)
    daily_kwh = (
        ac_count * ac_hours * ac_tons * 0.7
        + fan_count * 0.06 * np.random.uniform(6, 14, N)
        + fridge_count * 0.15 * 24
        + washer_hours_week / 7 * 2.0
        + heater_hours_week / 7 * 1.5
        + other_hours_day * 0.3
    )

    base_load = members * 0.25
    temp_factor = 1.0 + np.maximum(0, temperature - 28) * 0.025

    # Previous bill influence (captures household behaviour patterns)
    bill_factor = 0.6 + 0.4 * (avg_prev_bill / avg_prev_bill.max())

    monthly_units = (daily_kwh + base_load) * 30 * temp_factor * bill_factor
    noise = np.random.uniform(0.88, 1.12, N)
    monthly_units = np.clip(monthly_units * noise, 5, 1500)

    X = pd.DataFrame({
        "members": members,
        "avg_prev_bill": avg_prev_bill,
        "fan_count": fan_count,
        "ac_count": ac_count,
        "ac_hours_per_day": ac_hours,
        "ac_tons": ac_tons,
        "fridge_count": fridge_count,
        "washer_hours_per_week": washer_hours_week,
        "heater_hours_per_week": heater_hours_week,
        "other_hours_per_day": other_hours_day,
        "temperature": temperature,
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
