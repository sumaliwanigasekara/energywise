import pandas as pd

# --- Step 1: Load consumption data ---
consumption = pd.read_csv(
    'data/raw/consumption_data/non_smart_meter/monthly_consumption.csv',
    thousands=','
)
print(consumption.shape)
print(consumption.head())

# --- Step 2: Load wave 1 survey files ---
ac        = pd.read_csv('data/raw/survey_data/wave_1/w1_ac_roster.csv')
fan       = pd.read_csv('data/raw/survey_data/wave_1/w1_fan_roster.csv')
appliances = pd.read_csv('data/raw/survey_data/wave_1/w1_appliances.csv')
household = pd.read_csv('data/raw/survey_data/wave_1/w1_household_information_and_history.csv')

print("\nAC columns:", ac.columns.tolist())
print("Fan columns:", fan.columns.tolist())
print("Appliances columns:", appliances.columns.tolist())
print("Household columns:", household.columns.tolist())

# --- Step 3: Aggregate AC data per household ---
ac['total_ac_hours_last_week'] = (
    ac['no_of_hours_ac_was_on_during_daytime_last_week'].fillna(0) +
    ac['no_of_hours_ac_was_on_during_night_last_week'].fillna(0)
)
ac['ac_hours_per_month'] = ac['total_ac_hours_last_week'] * 4.33
ac['ac_tons'] = ac['btu_of_the_ac'].fillna(18000) / 12000

ac_agg = ac.groupby('household_ID').agg(
    ac_count=('ac_ID', 'count'),
    ac_hours_per_month=('ac_hours_per_month', 'sum'),
    ac_tons=('ac_tons', 'mean')
).reset_index()

print("\nAC aggregated shape:", ac_agg.shape)
print(ac_agg.head())

# --- Step 4: Aggregate fan data per household ---
fan['total_fan_hours_last_week'] = (
    fan['no_of_hours_fan_was_on_during_daytime_last_week'].fillna(0) +
    fan['no_of_hours_fan_was_on_during_night_last_week'].fillna(0)
)
fan['fan_hours_per_month'] = fan['total_fan_hours_last_week'] * 4.33

fan_agg = fan.groupby('household_ID').agg(
    fan_count=('fan_ID', 'count'),
    fan_hours_per_month=('fan_hours_per_month', 'sum')
).reset_index()

print("\nFan aggregated shape:", fan_agg.shape)
print(fan_agg.head())

# --- Step 5: Aggregate appliances data per household ---
appliances['no_of_hours_used_during_last_week'] = pd.to_numeric(
    appliances['no_of_hours_used_during_last_week'], errors='coerce'
).fillna(0)
appliances['monthly_hours'] = appliances['no_of_hours_used_during_last_week'] * 4.33

# Fridge count — appliance_ID starts with 'O1'
fridge = appliances[appliances['appliance_ID'].str.startswith('O1')]
fridge_agg = fridge.groupby('household_ID').agg(
    fridge_count=('appliance_ID', 'count')
).reset_index()

# Washer hours
washer = appliances[appliances['appliance_type'].str.contains('Washing', na=False)]
washer_agg = washer.groupby('household_ID').agg(
    washer_hours_per_month=('monthly_hours', 'sum')
).reset_index()

# Heater hours
heater = appliances[appliances['appliance_type'].str.contains('heater|water heat', case=False, na=False)]
heater_agg = heater.groupby('household_ID').agg(
    heater_hours_per_month=('monthly_hours', 'sum')
).reset_index()

# Other hours — everything except fridge, washer, heater
other = appliances[~appliances['appliance_type'].str.contains(
    'Refrigerator|Washing|heater|water heat', case=False, na=False
)]
other_agg = other.groupby('household_ID').agg(
    other_hours_per_month=('monthly_hours', 'sum')
).reset_index()

print("\nFridge shape:", fridge_agg.shape)
print("Washer shape:", washer_agg.shape)
print("Heater shape:", heater_agg.shape)
print("Other shape:", other_agg.shape)
print(fridge_agg.head())

# --- Step 6: Aggregate household info and merge all survey data ---
household_agg = household[['household_ID', 'no_of_household_members',
                            'total_monthly_expenditure_of_last_month']].copy()

# Fill missing values
household_agg['no_of_household_members'] = household_agg['no_of_household_members'].fillna(
    household_agg['no_of_household_members'].median()
)
household_agg['total_monthly_expenditure_of_last_month'] = household_agg['total_monthly_expenditure_of_last_month'].fillna(
    household_agg['total_monthly_expenditure_of_last_month'].mean()
)

# Merge all survey tables on household_ID
survey = household_agg.copy()
for df in [ac_agg, fan_agg, fridge_agg, washer_agg, heater_agg, other_agg]:
    survey = survey.merge(df, on='household_ID', how='left')

# Fill missing appliance values with 0 (household doesn't own that appliance)
zero_cols = ['ac_count', 'ac_hours_per_month', 'ac_tons',
             'fan_count', 'fan_hours_per_month',
             'fridge_count', 'washer_hours_per_month',
             'heater_hours_per_month', 'other_hours_per_month']
survey[zero_cols] = survey[zero_cols].fillna(0)

print("\nSurvey merged shape:", survey.shape)
print(survey.head())

# --- Step 7: Join consumption + survey, fix month, calculate avg_prev_bill ---

# Convert month from '2022-10-31' to '2022-10'
consumption['month'] = pd.to_datetime(consumption['month']).dt.to_period('M').astype(str)

# Extract numeric month (1-12) for seasonal feature
consumption['month_num'] = pd.to_datetime(consumption['month']).dt.month

# Join consumption with survey on household_ID
df = consumption.merge(survey, on='household_ID', how='inner')

# Sort by household and month for rolling calculation
df = df.sort_values(['household_ID', 'month']).reset_index(drop=True)

# avg_prev_bill — mean of previous 3 months consumption per household
df['avg_prev_bill'] = (
    df.groupby('household_ID')['consumption']
    .transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
)

# For first month of each household, use their own consumption value
df['avg_prev_bill'] = df['avg_prev_bill'].fillna(df['consumption'])

print("\nJoined dataset shape:", df.shape)
print(df[['household_ID', 'month', 'consumption', 'avg_prev_bill', 
          'no_of_household_members', 'ac_count', 'fan_count']].head(10))

# --- Step 8: Build final feature set and save ---
final_df = pd.DataFrame({
    'members':                df['no_of_household_members'],
    'avg_prev_bill':          df['avg_prev_bill'],
    'fan_count':              df['fan_count'],
    'ac_count':               df['ac_count'],
    'ac_hours_per_month':     df['ac_hours_per_month'],
    'ac_tons':                df['ac_tons'],
    'fridge_count':           df['fridge_count'],
    'washer_hours_per_month': df['washer_hours_per_month'],
    'heater_hours_per_month': df['heater_hours_per_month'],
    'other_hours_per_month':  df['other_hours_per_month'],
    'avg_temp':               None,   # placeholder — weather coming next
    'avg_humidity':           None,
    'total_precip':           None,
    'avg_wind':               None,
    'month':                  df['month_num'],
    'consumption_kwh':        df['consumption'],
})

before = len(final_df)
final_df = final_df.dropna(subset=[c for c in final_df.columns if c not in 
                                    ['avg_temp','avg_humidity','total_precip','avg_wind']])
after = len(final_df)

print("\nFinal dataset shape:", final_df.shape)
print(f"Rows dropped: {before - after}")
print(final_df.head())

# Save intermediate version before weather
import os
os.makedirs('data/processed', exist_ok=True)
final_df.to_csv('data/processed/training_dataset_no_weather.csv', index=False)
print("\nSaved to data/processed/training_dataset_no_weather.csv")

# --- Step 9: Fetch monthly weather from Open-Meteo ---
import requests
import time

COLOMBO_LAT = 6.9271
COLOMBO_LON = 79.8612

def fetch_monthly_weather(year, month):
    import calendar
    last_day = calendar.monthrange(year, month)[1]
    start = f"{year}-{month:02d}-01"
    end   = f"{year}-{month:02d}-{last_day}"

    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={COLOMBO_LAT}&longitude={COLOMBO_LON}"
        f"&start_date={start}&end_date={end}"
        f"&daily=temperature_2m_max,temperature_2m_min,"
        f"relative_humidity_2m_mean,precipitation_sum,"
        f"windspeed_10m_max"
        f"&timezone=Asia%2FColombo"
    )

    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        daily = resp.json().get("daily", {})

        temps_max  = [x for x in daily.get("temperature_2m_max", []) if x is not None]
        temps_min  = [x for x in daily.get("temperature_2m_min", []) if x is not None]
        humidities = [x for x in daily.get("relative_humidity_2m_mean", []) if x is not None]
        precips    = [x for x in daily.get("precipitation_sum", []) if x is not None]
        winds      = [x for x in daily.get("windspeed_10m_max", []) if x is not None]

        daily_means = [(h + l) / 2 for h, l in zip(temps_max, temps_min)]

        return {
            "avg_temp":     round(sum(daily_means) / len(daily_means), 2) if daily_means else 29.0,
            "avg_humidity": round(sum(humidities) / len(humidities), 2) if humidities else 78.0,
            "total_precip": round(sum(precips), 1),
            "avg_wind":     round(sum(winds) / len(winds), 2) if winds else 12.0,
        }
    except Exception as e:
        print(f"    WARNING: {year}-{month:02d} failed — {e}")
        return {"avg_temp": 29.0, "avg_humidity": 78.0, "total_precip": 15.0, "avg_wind": 12.0}

# Get unique months from dataset
unique_months = sorted(final_df['month'].unique())
print(f"\nFetching weather for {len(unique_months)} months...")

weather_records = []
for m in unique_months:
    # month column is numeric (1-12) — we need year too
    # get year from the df month column
    pass

# Use the original df which still has the YYYY-MM month string
unique_month_strs = sorted(df['month'].unique())
print("Months to fetch:", unique_month_strs)

weather_records = []
for m in unique_month_strs:
    year, mon = int(m[:4]), int(m[5:])
    print(f"  Fetching {m}...", end=" ", flush=True)
    w = fetch_monthly_weather(year, mon)
    w['month'] = m
    weather_records.append(w)
    print(f"temp={w['avg_temp']}°C")
    time.sleep(0.5)

weather_df = pd.DataFrame(weather_records)
print("\nWeather fetched:")
print(weather_df)

# --- Step 10: Join weather and save final training dataset ---
final_df['month_str'] = df['month']

final_df = final_df.merge(weather_df, left_on='month_str', right_on='month', how='left')

# Use the real weather values from _y columns
final_df['avg_temp']     = final_df['avg_temp_y']
final_df['avg_humidity'] = final_df['avg_humidity_y']
final_df['total_precip'] = final_df['total_precip_y']
final_df['avg_wind']     = final_df['avg_wind_y']

# Drop all helper and duplicate columns
final_df = final_df.drop(columns=[
    'month_str', 'month_y',
    'avg_temp_x', 'avg_humidity_x', 'total_precip_x', 'avg_wind_x',
    'avg_temp_y', 'avg_humidity_y', 'total_precip_y', 'avg_wind_y',
])

# Drop any remaining nulls
before = len(final_df)
final_df = final_df.dropna()
after = len(final_df)
print(f"\nRows dropped: {before - after}")
print(f"Final dataset shape: {final_df.shape}")
print(f"Columns: {final_df.columns.tolist()}")
print(final_df.head())

final_df = final_df.rename(columns={'month_x': 'month'})

# Save
final_df.to_csv('data/processed/training_dataset.csv', index=False)
print("\nSaved to data/processed/training_dataset.csv")
