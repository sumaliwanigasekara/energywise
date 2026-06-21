import pandas as pd
import requests
import time
import os

# --- Coordinates ---
COLOMBO_LAT  = 6.9271
COLOMBO_LON  = 79.8612

AREA_TO_DISTRICT = {
    'MORATUWA NORTH': 'Colombo', 'MORATUWA SOUTH': 'Colombo',
    'MAHARAGAMA':     'Colombo', 'BORALASGAMUWA':  'Colombo',
    'PITA-KOTTE':     'Colombo', 'KOLONNAWA':      'Colombo',
    'KOTIKAWATTA':    'Colombo', 'NUGEGODA':       'Colombo',
    'NEGOMBO':        'Gampaha', 'MAHARA':         'Gampaha',
    'JA-ELA':         'Gampaha', 'KANDANA':        'Gampaha',
    'DALUGAMA':       'Gampaha', 'SEEDUWA':        'Gampaha',
    'WATTALA':        'Gampaha',
    'PANADURA':       'Kalutara', 'PAYAGALA':      'Kalutara',
    'KALUTARA':       'Kalutara', 'ALUTHGAMA':     'Kalutara',
    'KESELWATTA':     'Kalutara',
    'GALLE':          'Galle',   'HIKKADUWA':      'Galle',
    'AMBALANGODA':    'Galle',
}

DISTRICT_COORDS = {
    'Colombo':  {'lat': 6.9271, 'lon': 79.8612},
    'Gampaha':  {'lat': 7.0917, 'lon': 80.0000},
    'Kalutara': {'lat': 6.5854, 'lon': 79.9607},
    'Galle':    {'lat': 6.0535, 'lon': 80.2210},
}

DISTRICT_MAP = {'Colombo': 1, 'Gampaha': 2, 'Kalutara': 3, 'Galle': 4}

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
household  = pd.read_csv('data/raw/survey_data/wave_1/w1_household_information_and_history.csv')

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

# --- Step 5: Aggregate appliances data per household ---
appliances['no_of_hours_used_during_last_week'] = pd.to_numeric(
    appliances['no_of_hours_used_during_last_week'], errors='coerce'
).fillna(0)
appliances['monthly_hours'] = appliances['no_of_hours_used_during_last_week'] * 4.33

fridge = appliances[appliances['appliance_ID'].str.startswith('O1')]
fridge_agg = fridge.groupby('household_ID').agg(
    fridge_count=('appliance_ID', 'count')
).reset_index()

washer = appliances[appliances['appliance_type'].str.contains('Washing', na=False)]
washer_agg = washer.groupby('household_ID').agg(
    washer_hours_per_month=('monthly_hours', 'sum')
).reset_index()

heater = appliances[appliances['appliance_type'].str.contains('heater|water heat', case=False, na=False)]
heater_agg = heater.groupby('household_ID').agg(
    heater_hours_per_month=('monthly_hours', 'sum')
).reset_index()

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

# --- Step 6: Aggregate household info ---
household_agg = household[[
    'household_ID',
    'no_of_household_members',
    'total_monthly_expenditure_of_last_month',
    'electricity_provider_csc_area'
]].copy()

household_agg['no_of_household_members'] = household_agg['no_of_household_members'].fillna(
    household_agg['no_of_household_members'].median()
)
household_agg['total_monthly_expenditure_of_last_month'] = household_agg['total_monthly_expenditure_of_last_month'].fillna(
    household_agg['total_monthly_expenditure_of_last_month'].mean()
)

# --- Step 6b: Map CEB area to district ---
household_agg['district'] = household_agg['electricity_provider_csc_area'].map(AREA_TO_DISTRICT)
household_agg['district'] = household_agg['district'].fillna('Colombo')

# --- Merge all survey tables ---
survey = household_agg.copy()
for df_part in [ac_agg, fan_agg, fridge_agg, washer_agg, heater_agg, other_agg]:
    survey = survey.merge(df_part, on='household_ID', how='left')

zero_cols = [
    'ac_count', 'ac_hours_per_month', 'ac_tons',
    'fan_count', 'fan_hours_per_month',
    'fridge_count', 'washer_hours_per_month',
    'heater_hours_per_month', 'other_hours_per_month'
]
survey[zero_cols] = survey[zero_cols].fillna(0)

print("\nSurvey merged shape:", survey.shape)

# --- Step 7: Join consumption + survey ---
consumption['month'] = pd.to_datetime(consumption['month']).dt.to_period('M').astype(str)
consumption['month_num'] = pd.to_datetime(consumption['month']).dt.month

df = consumption.merge(survey, on='household_ID', how='inner')
df = df.sort_values(['household_ID', 'month']).reset_index(drop=True)

grp = df.groupby('household_ID')['consumption']

# 3-month rolling average of previous months (no fillna — NaN rows dropped below)
df['avg_prev_bill'] = grp.transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())

# Previous month's actual consumption (t-1)
df['prev_month_consumption'] = grp.transform(lambda x: x.shift(1))

# Variability in the last 3 months (fill 0 when fewer than 2 prior readings)
df['std_prev_3months'] = grp.transform(
    lambda x: x.shift(1).rolling(3, min_periods=2).std()
).fillna(0)

# Direction of change: last month minus the month before (fill 0 when unknown)
df['consumption_trend'] = grp.transform(
    lambda x: x.shift(1) - x.shift(2)
).fillna(0)

print("\nJoined dataset shape:", df.shape)

# --- Step 8: Build feature set ---
final_df = pd.DataFrame({
    'household_ID':           df['household_ID'],
    'members':                df['no_of_household_members'],
    'avg_prev_bill':          df['avg_prev_bill'],
    'prev_month_consumption': df['prev_month_consumption'],
    'std_prev_3months':       df['std_prev_3months'],
    'consumption_trend':      df['consumption_trend'],
    'fan_count':              df['fan_count'],
    'fan_hours_per_month':    df['fan_hours_per_month'],
    'ac_count':               df['ac_count'],
    'ac_hours_per_month':     df['ac_hours_per_month'],
    'ac_tons':                df['ac_tons'],
    'fridge_count':           df['fridge_count'],
    'washer_hours_per_month': df['washer_hours_per_month'],
    'heater_hours_per_month': df['heater_hours_per_month'],
    'other_hours_per_month':  df['other_hours_per_month'],
    'avg_temp':               None,
    'avg_humidity':           None,
    'total_precip':           None,
    'avg_wind':               None,
    'month':                  df['month_num'],
    'district':               df['district'],
    'consumption_kwh':        df['consumption'],
})

# Drop first month per household — prev_month_consumption is NaN there (no prior data)
before = len(final_df)
final_df = final_df.dropna(subset=['prev_month_consumption', 'avg_prev_bill'])
after = len(final_df)
print(f"\nRows dropped (first month per household): {before - after}")
print(f"Intermediate dataset shape: {final_df.shape}")

os.makedirs('data/processed', exist_ok=True)
final_df.to_csv('data/processed/training_dataset_no_weather.csv', index=False)
print("Saved intermediate file.")

# --- Step 9: Fetch monthly weather per district ---
def fetch_monthly_weather(year, month, lat=COLOMBO_LAT, lon=COLOMBO_LON):
    import calendar
    last_day = calendar.monthrange(year, month)[1]
    start = f"{year}-{month:02d}-01"
    end   = f"{year}-{month:02d}-{last_day}"

    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
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

        temps_max  = [x for x in daily.get("temperature_2m_max", [])  if x is not None]
        temps_min  = [x for x in daily.get("temperature_2m_min", [])  if x is not None]
        humidities = [x for x in daily.get("relative_humidity_2m_mean", []) if x is not None]
        precips    = [x for x in daily.get("precipitation_sum", [])   if x is not None]
        winds      = [x for x in daily.get("windspeed_10m_max", [])   if x is not None]

        daily_means = [(h + l) / 2 for h, l in zip(temps_max, temps_min)]

        return {
            "avg_temp":     round(sum(daily_means) / len(daily_means), 2) if daily_means else 29.0,
            "avg_humidity": round(sum(humidities)  / len(humidities),  2) if humidities  else 78.0,
            "total_precip": round(sum(precips), 1),
            "avg_wind":     round(sum(winds)    / len(winds),    2) if winds      else 12.0,
        }
    except Exception as e:
        print(f"    WARNING: {year}-{month:02d} {lat},{lon} failed — {e}")
        return {"avg_temp": 29.0, "avg_humidity": 78.0, "total_precip": 15.0, "avg_wind": 12.0}

unique_month_strs = sorted(df['month'].unique())
districts = list(DISTRICT_COORDS.keys())

WEATHER_CACHE = 'data/processed/weather_cache.csv'

if os.path.exists(WEATHER_CACHE):
    print(f"\nLoading weather from cache: {WEATHER_CACHE}")
    weather_df = pd.read_csv(WEATHER_CACHE)
else:
    print(f"\nFetching weather for {len(unique_month_strs)} months x {len(districts)} districts...")
    weather_records = []
    for district in districts:
        coords = DISTRICT_COORDS[district]
        for m in unique_month_strs:
            year, mon = int(m[:4]), int(m[5:])
            print(f"  {district} {m}...", end=" ", flush=True)
            w = fetch_monthly_weather(year, mon, coords['lat'], coords['lon'])
            w['month'] = m
            w['district'] = district
            weather_records.append(w)
            print(f"temp={w['avg_temp']}°C")
            time.sleep(0.3)
    weather_df = pd.DataFrame(weather_records)
    weather_df.to_csv(WEATHER_CACHE, index=False)
    print(f"Weather cached to {WEATHER_CACHE}")

# --- Step 10: Join weather by month and district, save ---
final_df['month_str'] = df['month']
final_df['district_name'] = df['district']

final_df = final_df.merge(
    weather_df,
    left_on=['month_str', 'district_name'],
    right_on=['month', 'district'],
    how='left'
)

final_df['avg_temp']     = final_df['avg_temp_y']
final_df['avg_humidity'] = final_df['avg_humidity_y']
final_df['total_precip'] = final_df['total_precip_y']
final_df['avg_wind']     = final_df['avg_wind_y']

final_df['district'] = final_df['district_name'].map(DISTRICT_MAP)

final_df = final_df.drop(columns=[
    'month_str', 'district_name', 'month_y', 'district_x', 'district_y',
    'avg_temp_x', 'avg_humidity_x', 'total_precip_x', 'avg_wind_x',
    'avg_temp_y', 'avg_humidity_y', 'total_precip_y', 'avg_wind_y',
], errors='ignore')

final_df = final_df.rename(columns={'month_x': 'month'})
final_df = final_df.dropna()

print(f"\nFinal dataset shape: {final_df.shape}")
print(f"Columns: {final_df.columns.tolist()}")
print(final_df.head())

final_df.to_csv('data/processed/training_dataset.csv', index=False)
print("\nSaved to data/processed/training_dataset.csv")