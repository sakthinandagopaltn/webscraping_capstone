import os

import pandas as pd

RAW_CSV = 'data/raw_weather.csv'
CLEAN_CSV = 'data/clean_weather.csv'


def extract_number(series):
    """Pull the first number out of text like '52 °F' or '65%'. Bad values become missing."""
    text = series.astype('string')  # keeps missing values missing
    numbers = text.str.extract(r'(-?\d+(?:\.\d+)?)')[0]
    return pd.to_numeric(numbers, errors='coerce').astype(float)


# 1. Load the raw data
df = pd.read_csv(RAW_CSV)
print('BEFORE CLEANING')
print(f'Shape: {df.shape}')
print(df.head())
print('\nMissing values per column:')
print(df.isna().sum())
print('\nData types:')
print(df.dtypes)

# 2. Clean missing, duplicate and malformed entries
df = df.replace(r'^\s*$', pd.NA, regex=True)  # blank strings become real missing values

# Use the string type so missing values stay missing (astype(str) would turn them into 'nan')
for col in ['query', 'conditions']:
    df[col] = df[col].astype('string').str.strip()
df['conditions'] = df['conditions'].str.split('\n').str[0]  # keep the first line only
print('\nUnique conditions after cleanup:', df['conditions'].unique())

# Remove repeats: exact duplicates and the same city scraped twice in the same second
df = df.drop_duplicates()
df = df.drop_duplicates(subset=['query', 'scraped_at'])

df = df.dropna(subset=['query', 'url'])  # a row with no source is unusable
df = df.dropna(subset=['temperature'])   # no temperature means the scrape failed

# 3. Transform: split the query into city and state
parts = df['query'].str.split(',', n=1, expand=True)
df['city'] = parts[0].str.strip()
df['state'] = parts[1].str.strip() if parts.shape[1] > 1 else pd.NA

# Temperature: number and unit
df['temp_value'] = extract_number(df['temperature'])
df['temp_unit'] = df['temperature'].astype('string').str.extract(r'°\s*([FC])')[0]

# Drop malformed rows: missing number, or a unit that is not F or C.
# Without this, a missing unit would silently be treated as Celsius.
before = len(df)
df = df.dropna(subset=['temp_value'])
df = df[df['temp_unit'].isin(['F', 'C'])]
print(f'\nDropped {before - len(df)} rows with a missing or invalid temperature')

# Both Celsius and Fahrenheit
is_f = df['temp_unit'] == 'F'
df['temp_f'] = df['temp_value'].where(is_f, df['temp_value'] * 9 / 5 + 32).round(1)
df['temp_c'] = df['temp_value'].where(~is_f, (df['temp_value'] - 32) * 5 / 9).round(1)

# Other numeric columns
df['humidity_pct'] = extract_number(df['humidity'])
df['visibility'] = extract_number(df['visibility'])
df['pressure'] = extract_number(df['pressure'])
df['dew_point'] = extract_number(df['dew_point'])

df['scraped_at'] = pd.to_datetime(df['scraped_at'], errors='coerce')

# 4. Keep the useful columns in a sensible order
columns = ['city', 'state', 'temp_f', 'temp_c', 'conditions', 'humidity_pct',
           'visibility', 'pressure', 'dew_point', 'scraped_at', 'url']
df = df[[c for c in columns if c in df.columns]]

# 5. AFTER CLEANING: the comparison with the BEFORE block above
print('\nAFTER CLEANING')
print(f'Shape: {df.shape}')
print(df.head())
print('\nMissing values per column:')
print(df.isna().sum())
print('\nData types:')
print(df.dtypes)

# 6. Save the clean data (rebuilt from the raw file on every run)
os.makedirs('data', exist_ok=True)
df.to_csv(CLEAN_CSV, index=False)
print(f'\nSaved {CLEAN_CSV}')