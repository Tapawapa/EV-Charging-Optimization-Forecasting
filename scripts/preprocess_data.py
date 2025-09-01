import pandas as pd
import geopandas as gpd
import os
import glob


#Delete all values where state != 'WA' in AFDC data
# --- 1. Define the correct, cross-platform paths ---
# We use forward slashes, which work on all operating systems.
base_path = "EV-Charging-Optimization-Forecasting/data/raw"

# --- 2. Process all AFDC historical files in a loop ---

print("--- Processing AFDC Historical Data ---")
search_pattern = os.path.join(base_path, "alt_fuel_stations_historical_day*.csv")
all_afdc_files = glob.glob(search_pattern)

for file_path in all_afdc_files:
    try:
        df = pd.read_csv(file_path, low_memory=False)
        if 'State' in df.columns:
            original_rows = len(df)
            df_filtered = df[df['State'] == 'WA'].copy() #Copies only rows where State is WA
            # Overwrite the original file with the filtered data
            df_filtered.to_csv(file_path, index=False)
            print(f"-> Overwrote {os.path.basename(file_path)}: {original_rows} rows -> {len(df_filtered)} rows.")
        else:
            print(f"Warning: 'State' column not found in {os.path.basename(file_path)}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        

# --- 1. Define the columns you want to KEEP for your model ---
# It's easier and safer to specify what you need, rather than what you don't.
columns_to_keep = [
    'ID',
    'Latitude',
    'Longitude',
    'State', # We'll use this to filter, then it can be dropped if desired
    'EV Level1 EVSE Num',
    'EV Level2 EVSE Num',
    'EV DC Fast Count',
    'EV Connector Types',
    'Groups With Access Code', # Often used for Public/Private status
    'Access Days Time',
    'Facility Type',
    'EV Workplace Charging',
    'Open Date',
    'EV Network',
    'EV Pricing'
]

# --- 2. Define your input and output directories ---
raw_data_path = "EV-Charging-Optimization-Forecasting/data/raw/"
processed_data_path = "EV-Charging-Optimization-Forecasting/data/processed/"

# Create the output directory if it doesn't already exist
os.makedirs(processed_data_path, exist_ok=True)

# --- 3. Find all the AFDC historical CSV files ---
search_pattern = os.path.join(raw_data_path, "alt_fuel_stations_historical_day*.csv")
all_files = glob.glob(search_pattern)

print(f"Found {len(all_files)} files to process.")

# --- 4. Loop through each file, clean it, and save to the processed folder ---
for file_path in all_files:
    try:
        base_name = os.path.basename(file_path)
        
        # Read the raw CSV file
        df = pd.read_csv(file_path, low_memory=False)
        print(f"\nProcessing '{base_name}' with {len(df)} rows and {len(df.columns)} columns.")

        # --- Step B: Filter by relevant columns ---
        # Find which of our desired columns actually exist in this specific file
        existing_columns_to_keep = [col for col in columns_to_keep if col in df.columns]
        
        # Keep only those columns
        df_cleaned = df[existing_columns_to_keep]
        
        print(f"-> Kept {len(df_cleaned.columns)} relevant columns.")

        # --- Step C: Save the cleaned file to the processed directory ---
        output_path = os.path.join(processed_data_path, base_name)
        df_cleaned.to_csv(output_path, index=False)
        
        print(f"-> Successfully saved cleaned file to '{output_path}'")

    except Exception as e:
        print(f"An error occurred while processing {file_path}: {e}")

print("\n\nAll files have been processed.")
