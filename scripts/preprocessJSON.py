import pandas as pd
import geopandas as gpd
import os


def clean_charging_stations(raw_data_path, processed_data_path):
    columns_to_keep = [
        'access', 'amenity', 'brand', 'operator',
        'capacity', 'fee', 'opening_hours', 'geometry'
    ]

    input_file = os.path.join(raw_data_path, "chargingStationWashington.geojson")
    output_file = os.path.join(processed_data_path, "chargingStationWashington_cleaned.geojson")

    try:
        gdf = gpd.read_file(input_file)
        print(f"Loaded '{os.path.basename(input_file)}': Found {len(gdf)} features.")

        existing_columns = [col for col in gdf.columns if col in columns_to_keep or col.startswith('socket:')]
        gdf_cleaned = gdf[existing_columns]

        print(f"-> Kept {len(gdf_cleaned.columns)} relevant columns.")
        gdf_cleaned.to_file(output_file, driver='GeoJSON')
        print(f"-> Successfully saved cleaned file to '{output_file}'")
    except FileNotFoundError:
        print(f"Error: The file was not found at {input_file}")
    except Exception as e:
        print(f"An error occurred: {e}")


def clean_amenities(raw_data_path, processed_data_path):
    columns_to_keep = [
        'amenity', 'access', 'fee', 'capacity',
        'building', 'shop', 'leisure', 'geometry'
    ]

    input_file = os.path.join(raw_data_path, "amenitiesWashington.geojson")
    output_file = os.path.join(processed_data_path, "amenitiesWashington_cleaned.geojson")

    try:
        gdf = gpd.read_file(input_file)
        print(f"Loaded '{os.path.basename(input_file)}': Found {len(gdf)} total amenities.")

        existing_columns = [col for col in gdf.columns if col in columns_to_keep]
        gdf_cleaned = gdf[existing_columns]

        print(f"-> Kept {len(gdf_cleaned.columns)} relevant columns.")
        gdf_cleaned.to_file(output_file, driver='GeoJSON')
        print(f"-> Successfully saved cleaned amenities file to '{output_file}'")
    except FileNotFoundError:
        print(f"Error: The file was not found at {input_file}")
    except Exception as e:
        print(f"An error occurred: {e}")


def clean_major_roads(raw_data_path, processed_data_path):
    columns_to_keep = ['highway', 'geometry']
    input_file = os.path.join(raw_data_path, "majorRoadsWashington.geojson")
    output_file = os.path.join(processed_data_path, "majorRoadsWashington_cleaned.geojson")

    try:
        gdf = gpd.read_file(input_file)
        print(f"Loaded '{os.path.basename(input_file)}': Found {len(gdf)} road segments.")

        existing_columns = [col for col in gdf.columns if col in columns_to_keep]
        gdf_cleaned = gdf[existing_columns]

        print(f"-> Kept {len(gdf_cleaned.columns)} essential columns.")
        gdf_cleaned.to_file(output_file, driver='GeoJSON')
        print(f"-> Successfully saved cleaned roads file to '{output_file}'")
    except FileNotFoundError:
        print(f"Error: The file was not found at {input_file}")
    except Exception as e:
        print(f"An error occurred: {e}")


def clean_leisure(raw_data_path, processed_data_path):
    columns_to_keep = ['leisure', 'name', 'geometry']
    input_file = os.path.join(raw_data_path, "leisureWashington.geojson")
    output_file = os.path.join(processed_data_path, "leisureWashington_cleaned.geojson")

    try:
        gdf = gpd.read_file(input_file)
        print(f"Loaded '{os.path.basename(input_file)}': Found {len(gdf)} leisure features.")

        existing_columns = [col for col in gdf.columns if col in columns_to_keep]
        gdf_cleaned = gdf[existing_columns]

        print(f"-> Kept {len(gdf_cleaned.columns)} essential columns.")
        gdf_cleaned.to_file(output_file, driver='GeoJSON')
        print(f"-> Successfully saved cleaned leisure file to '{output_file}'")
    except FileNotFoundError:
        print(f"Error: The file was not found at {input_file}")
    except Exception as e:
        print(f"An error occurred: {e}")


def clean_shops(raw_data_path, processed_data_path):
    columns_to_keep = ['shop', 'name', 'geometry']
    input_file = os.path.join(raw_data_path, "shopsWashington.geojson")
    output_file = os.path.join(processed_data_path, "shopsWashington_cleaned.geojson")

    try:
        gdf = gpd.read_file(input_file)
        print(f"Loaded '{os.path.basename(input_file)}': Found {len(gdf)} shop features.")

        existing_columns = [col for col in gdf.columns if col in columns_to_keep]
        gdf_cleaned = gdf[existing_columns]

        print(f"-> Kept {len(gdf_cleaned.columns)} essential columns.")
        gdf_cleaned.to_file(output_file, driver='GeoJSON')
        print(f"-> Successfully saved cleaned shops file to '{output_file}'")
    except FileNotFoundError:
        print(f"Error: The file was not found at {input_file}")
    except Exception as e:
        print(f"An error occurred: {e}")


def clean_residential(raw_data_path, processed_data_path):
    columns_to_keep = ['building', 'name', 'geometry']
    input_file = os.path.join(raw_data_path, "residentialWashington.geojson")  # fixed typo
    output_file = os.path.join(processed_data_path, "residentialWashington_cleaned.geojson")

    try:
        gdf = gpd.read_file(input_file)
        print(f"Loaded '{os.path.basename(input_file)}': Found {len(gdf)} building features.")

        existing_columns = [col for col in gdf.columns if col in columns_to_keep]
        gdf_cleaned = gdf[existing_columns]

        print(f"-> Kept {len(gdf_cleaned.columns)} essential columns.")
        gdf_cleaned.to_file(output_file, driver='GeoJSON')
        print(f"-> Successfully saved cleaned residential buildings file to '{output_file}'")
    except FileNotFoundError:
        print(f"Error: The file was not found at {input_file}. Please check the filename.")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    raw_data_path = "EV-Charging-Optimization-Forecasting/data/raw/"
    processed_data_path = "EV-Charging-Optimization-Forecasting/data/processed/"

    clean_charging_stations(raw_data_path, processed_data_path)
    clean_amenities(raw_data_path, processed_data_path)
    clean_major_roads(raw_data_path, processed_data_path)
    clean_leisure(raw_data_path, processed_data_path)
    clean_shops(raw_data_path, processed_data_path)
    clean_residential(raw_data_path, processed_data_path)


if __name__ == "__main__":
    main()
