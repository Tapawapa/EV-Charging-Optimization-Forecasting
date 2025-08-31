import pandas as pd
import glob
import os

base_path = "EV-Charging-Optimization-Forecasting/data/raw"
search_pattern = os.path.join(base_path, "alt_fuel_stations_historical_day*.csv")
all_afdc_files = glob.glob(search_pattern)

count = 0
for file_path in all_afdc_files:
    count += len(pd.read_csv(file_path, low_memory=False))

print(f"Total rows across all AFDC historical files: {count}")