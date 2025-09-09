#File that will rank and look for optimal locations based on the open year XGboost model
import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
import numpy as np
from tqdm import tqdm
import joblib

#This section sets up the key variables for our script
#By defining file paths and parameters at the top, we make it easy to adjust settings without digging through the code.
PROCESSED_DATA_PATH = "data/processed/"
MODELS_PATH = "models/"
OUTPUT_PATH = "data/processed/"

#defining a grid size we use for our analysis
#1000 meters (1 km) is a reasonable choice for urban planning
GRID_SIZE = 1000  # in meters

#firstly we define the CRS we will use for our geospatial data
TARGET_CRS = "EPSG:32148" #Washington/North

def create_prediction_grid(gdf):
    """
    This is a helper function that creates a square grid of polygons.
    It takes a gdf and uses its boundaries to determine the extennt of the grid
    ensuring our areas of interest are fully covered.
    
    """
    #find the bounds of our data
    xmin, ymin, xmax, ymax = gdf.total_bounds

    #Create a series of points along the x and y axes at intervals defined by GRID_SIZE
    cols = list(np.arange(xmin, xmax + GRID_SIZE, GRID_SIZE))
    rows = list(np.arange(ymin, ymax + GRID_SIZE, GRID_SIZE))

    #Now we create a square polygon for each cell in the grid
    polygons = []
    for x in cols[:-1]:
        for y in rows[:-1]:
            # A polygon is defined by the coordinates of its four corners.
            polygons.append(Polygon([(x, y), (x + GRID_SIZE, y), (x + GRID_SIZE, y + GRID_SIZE), (x, y + GRID_SIZE)]))
    #Finally we return a GeoDataFrame containing all the grid cells
    return gpd.GeoDataFrame({'geometry': polygons}, crs=TARGET_CRS)

def main():
    """
    this is the main function that orchestrates the prediction process
    """
    print("Starting demand prediction...")
    #Load the processed data
    print("Loading processed data...")
    try:
        #We need ecisting stations to calc distances to the nearest rival
        gdf_stations = gpd.read_file(os.path.join(PROCESSED_DATA_PATH, "afdc_unique_stations_with_features.geojson"))
        #We need roads and POIs to calc features for our grid cells
        gdf_roads = gpd.read_file(os.path.join(PROCESSED_DATA_PATH, "majorRoadsWashington_cleaned.geojson"))
        #Concacenated POI data
        gdf_pois = gpd.read_file(os.path.join(PROCESSED_DATA_PATH, "all_pois_Washington.geojson"))

        #Use joblib to load the model saved from forecast_demand.py
        model = joblib.load(os.path.join(MODELS_PATH, "xgb_year_prediction_model.pkl"))

        print("Successfully loaded all datasets9.")
    except FileNotFoundError as e:
        print(f"ERROR: {e}. Please ensure all required files are present.")
        return


    #Ensure all data is in the same CRS for accurate spatial calculations
    print("Reprojecting datasets to target CRS...")
    gdf_stations = gdf_stations.to_crs(TARGET_CRS)
    gdf_roads = gdf_roads.to_crs(TARGET_CRS)
    gdf_pois = gdf_pois.to_crs(TARGET_CRS)
    print("Reprojection complete.")
    #Filter roads to only include major roads as we did in feature engineering
    major_road_types = ['motorway', 'trunk', 'primary', 'secondary']
    gdf_major_roads = gdf_roads[gdf_roads['highway'].isin(major_road_types)]

    #Grid of potential locations to analyze the entire state.
    print("Creating prediction grid...")
    grid_gdf = create_prediction_grid(gdf_roads)
    #We will use the center point of each grid cell for our calculations
    grid_gdf['centroid']= grid_gdf.geometry.centroid
    print(f"Created grid with {len(grid_gdf)} potential locations.")

    #for every cell in our grid we also need to calculate the same features our model was trained on
    print("Calculating features for each grid cell...")

    tqdm.pandas()  # Enable tqdm progress bar for pandas operations

    # Calculate the distance from the center of each grid cell to the nearest major road.
    print("  - Calculating distance to nearest major road...")
    grid_gdf['dist_to_major_road_m'] = grid_gdf['centroid'].progress_apply(
        lambda point: gdf_major_roads.distance(point).min()
    )

    # Calculate the distance from the center of each grid cell to the nearest EXISTING station.
    print("  - Calculating distance to nearest existing station...")
    grid_gdf['dist_to_nearest_station_m'] = grid_gdf['centroid'].progress_apply(
        lambda point: gdf_stations.distance(point).min()
    )

    # Calculate how many points of interest (shops, etc.) are within a 1.5-mile radius.
    print("  - Calculating POI density...")
    buffer_radius = 2414  # Approximately 1.5 miles in meters
    buffers = grid_gdf.geometry.buffer(buffer_radius)
    # A spatial join is a special operation that finds which points fall inside which polygons.
    joined_pois = gpd.sjoin(gdf_pois, gpd.GeoDataFrame(geometry=buffers), how="inner", predicate="within")
    # We group by each grid cell and count how many POIs were found inside.
    poi_counts = joined_pois.groupby(joined_pois.index_right).size()
    grid_gdf['poi_density_1.5m'] = poi_counts
    # If a grid cell had no POIs nearby, we fill its value with 0.
    grid_gdf['poi_density_1.5m'] = grid_gdf['poi_density_1.5m'].fillna(0)

    print("Feature engineering complete.")

    #Now we use our trained model to predict the open year for each grid cell which is a proxy for demand

    print("running model to predict demand for each grid cell...")
    features = ['dist_to_major_road_m', 'poi_density_1.5m', 'dist_to_nearest_station_m'] #must be in same order as training
    X_grid = grid_gdf[features]
    #predicting open year
    grid_gdf['predicted_open_year'] = model.predict(X_grid)
    print("Prediction complete.")

    print("Ranking potential locations by identifying charging deserts")
    # First, we filter out any grid cells that are already close to an existing station.
    #If a cell is more than 2 miles (3218 meters) from the nearest station, we consider it a "charging desert"
    charging_deserts_gdf = grid_gdf[grid_gdf['dist_to_nearest_station_m'] > 3218].copy()

    #Now we createa final 'sustainability score' that ranks remaining locations
    #A great spot is one that is far from other stations and has high demand (low predicted open year)
    #We will add a bonus for having more pois
    charging_deserts_gdf['suitability_score'] = \
        (charging_deserts_gdf['dist_to_nearest_station_m'] / charging_deserts_gdf['predicted_open_year']) * \
        (1 + np.log1p(charging_deserts_gdf['poi_density_1.5m']))
    
    #Sort locations by their suitability score in descending order
    ranked_locations_gdf = charging_deserts_gdf.sort_values(by='suitability_score', ascending=False)
    print(f"Identified {len(ranked_locations_gdf)} potential locations in charging deserts.")

    #Finally, we save our complete and ranked list to a new file
    output_file = os.path.join(OUTPUT_PATH, "ranked_optimal_locations.geojson")
    print(f"Saving ranked locations to {output_file}...")
    try:
        # We only need to save the columns that will be useful for the next script and the dashboard.
        columns_to_save = ['geometry', 'predicted_open_year', 'suitability_score', 'dist_to_nearest_station_m', 'poi_density_1.5m']
        ranked_locations_gdf[columns_to_save].to_file(output_file, driver='GeoJSON')
        print("Prediction and ranking process complete!")
    except Exception as e:
        print(f"An error occurred while saving the output file: {e}")


if __name__ == "__main__":
    main()

