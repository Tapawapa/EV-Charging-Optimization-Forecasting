import os
import pandas as pd
import geopandas as gpd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error
import joblib

# --- CONFIGURATION ---
PROCESSED_DATA_PATH = "data/processed/"
MODELS_PATH = "models/"

def main():
    """
    Loads processed data, trains an XGBoost model to predict the opening year of a station,
    evaluates its performance, and saves the trained model.
    """
    print("--- Starting Model Training: EV Station Opening Year Prediction ---")

    # LOAD DATA
    print("Loading feature-engineered dataset...")
    try:
        input_file = os.path.join(PROCESSED_DATA_PATH, "afdc_unique_stations_with_features.geojson")
        gdf_master = gpd.read_file(input_file)
        print(f"Successfully loaded master GeoDataFrame with {len(gdf_master)} records.")
    except FileNotFoundError:
        print(f"ERROR: The file '{input_file}' was not found. Please run the feature engineering notebook first.")
        return

    #Preparing data
    print("Preparing data for training...")
    # Convert 'Open Date' to datetime objects and drop rows where the date is invalid
    gdf_master['Open Date'] = pd.to_datetime(gdf_master['Open Date'], errors='coerce')
    gdf_master.dropna(subset=['Open Date'], inplace=True)
    
    # Create the target variable: the year the station opened
    gdf_master['open_year'] = gdf_master['Open Date'].dt.year
    print(f"After cleaning, {len(gdf_master)} records remain with a valid 'Open Date'.")

    # DEFINE FEATURES AND TARGET 
    # These are the features the model will use to make predictions.
    # It must match the features used in your predict_demand.py script.
    features = ['dist_to_major_road_m', 'poi_density_1.5m', 'dist_to_nearest_station_m']
    target = 'open_year'
    
    X = gdf_master[features]
    y = gdf_master[target]

    # creating train and test splits
    print("Splitting data into training (before 2024) and testing (2024) sets...")
    train_indices = gdf_master[gdf_master['open_year'] < 2024].index
    test_indices = gdf_master[gdf_master['open_year'] >= 2024].index

    X_train, X_test = X.loc[train_indices], X.loc[test_indices]
    y_train, y_test = y.loc[train_indices], y.loc[test_indices]
    print(f"Training data shape: {X_train.shape}")
    print(f"Test data shape: {X_test.shape}")

    # -Training xgboost model
    print("Training XGBoost Regressor model...")
    # These parameters (n_estimators, random_state) are from your notebook.
    xgb_reg = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=500, random_state=42)
    
    # Fit the model to the training data
    xgb_reg.fit(X_train, y_train)
    print("Model training complete.")

    # evaluating performance
    print("Evaluating model performance on the test set...")
    predictions = xgb_reg.predict(X_test)
    predictions_rounded = predictions.round().astype(int) # Round predictions to the nearest year
    
    mae = mean_absolute_error(y_test, predictions_rounded)
    print(f"-> Mean Absolute Error (MAE) on 2024 data: {mae:.4f} years")

    # saving the trained model
    # Ensure the directory for saving models exists
    os.makedirs(MODELS_PATH, exist_ok=True)
    model_filename = os.path.join(MODELS_PATH, 'xgb_year_prediction_model.pkl')
    
    print(f"Saving trained model to '{model_filename}'...")
    joblib.dump(xgb_reg, model_filename)
    
    print("--- Model training and saving process complete! ---")

if __name__ == "__main__":
    main()
