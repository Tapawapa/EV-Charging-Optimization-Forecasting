import os
import geopandas as gpd

#This script extracts the top 100 optimal locations for charging stations from the ranked list

# This script reads the file with all the ranked locations...
INPUT_FILENAME = "ranked_optimal_locations.geojson"
# ...and creates a new, clean file containing only the very best spots.
OUTPUT_FILENAME = "top_charging_locations.geojson"

# Define the paths. We assume this script is run from the project's root directory.
PROCESSED_DATA_PATH = "data/processed/"
INPUT_FILE_PATH = os.path.join(PROCESSED_DATA_PATH, INPUT_FILENAME)
OUTPUT_FILE_PATH = os.path.join(PROCESSED_DATA_PATH, OUTPUT_FILENAME)

NUMBER_OF_TOP_SPOTS = 200

def main():
    #this function filters the top locations and saves them to a new file
    print("--- Extracting Top Optimal Locations for EV Charging Stations ---")

    print(f"Loading ranked locations from '{INPUT_FILE_PATH}'...")
    try:
        ranked_gdf = gpd.read_file(INPUT_FILE_PATH)
        print(f"Successfully loaded {len(ranked_gdf)} ranked locations.")
    except Exception as e:
        print(f"Could not locate or read the file '{INPUT_FILE_PATH}'. Please ensure the file exists and is accessible.")
        return
    
    print(f"Extracting the top {NUMBER_OF_TOP_SPOTS} locations...")
    top_spots_gdf = ranked_gdf.head(NUMBER_OF_TOP_SPOTS)
    print(f"Extracted {len(top_spots_gdf)} top locations.")
    top_spots_gdf['rank'] = range(1, len(top_spots_gdf) + 1)

    print(f"Here are the top 5 locations")
    print(top_spots_gdf[['rank', 'suitability_score']].head().to_string())

      # making it much faster and more efficient than loading the entire grid every time.
    print(f"\nSaving the top {NUMBER_OF_TOP_SPOTS} locations to '{OUTPUT_FILENAME}'...")
    try:
        top_spots_gdf.to_file(OUTPUT_FILE_PATH, driver='GeoJSON')
        print("--- Analysis complete! Your final data file is ready for the dashboard. ---")
    except Exception as e:
        print(f"Error saving the final output file: {e}")

    
if __name__ == "__main__":
    main()
    
