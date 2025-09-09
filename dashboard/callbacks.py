import os
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import geopandas as gpd
from app import app  # Import the app instance from app.py
from dotenv import load_dotenv # Import the function to load .env files

# Load environment variables from the .env file in the project's root directory.
load_dotenv()

# FILE PATH CONFIGURATION
# This is the final, cleaned data file produced by your geospatial_analysis.py script.
DATA_FILE = "top_charging_locations.geojson"
PROCESSED_DATA_PATH = "data/processed/" # Note the path goes UP one level from /dashboard
DATA_FILE_PATH = os.path.join(PROCESSED_DATA_PATH, DATA_FILE)

print(f"found file with {len(gpd.read_file(DATA_FILE_PATH))} rows")

# --- MAPBOX CONFIGURATION ---
# Now, we securely access the Mapbox token from the environment variables.
# os.getenv() reads the value of the key you defined in your .env file.
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")

# Check if the token was loaded correctly.
if not MAPBOX_TOKEN:
    print("WARNING: Mapbox token not found. Please ensure it is set in your .env file.")
    # You could provide a default public (but limited) token here if you wanted.

print("Mapbox token loaded successfully.")
# --- LOAD DATA ---
# We load the data once when the server starts to make the dashboard more efficient.
try:
    gdf = gpd.read_file(DATA_FILE_PATH)
    # The GeoJSON is in our target CRS (EPSG:32148), but Plotly needs standard lat/lon (EPSG:4326).
    # We re-project the data here for display purposes.
    gdf_display = gdf.to_crs("EPSG:4326")
except FileNotFoundError:
    print(f"ERROR: Data file not found at {DATA_FILE_PATH}. Please run the analysis scripts first.")
    # Create an empty GeoDataFrame with the necessary columns to prevent callback errors.
    gdf_display = gpd.GeoDataFrame(columns=['rank', 'suitability_score', 'geometry'])
    gdf_display.set_crs("EPSG:4326", inplace=True)

# --- DASH CALLBACK ---
# This is the core of the dashboard's interactivity.
# The @app.callback decorator links the inputs and outputs.
@app.callback(
    # The Output is the 'figure' property of the map component with the id 'demand-map'.
    Output('demand-map', 'figure'),
    # The Input is the 'value' property of the slider with the id 'top-n-slider'.
    Input('top-n-slider', 'value')
)
def update_map(top_n_value):
    """
    This function is automatically called by Dash whenever the slider's value changes.
    It receives the new slider value (top_n_value) and returns an updated map figure.
    """
    # First, check if our GeoDataFrame is empty (which happens if the data file was not found).
    # This prevents the app from crashing and provides a better user experience.
    if gdf_display.empty:
        fig = go.Figure()
        fig.update_layout(
            title_text="Data file not found. Please run the analysis scripts.",
            mapbox_style="dark",
            mapbox_accesstoken=MAPBOX_TOKEN,
            mapbox_center={"lat": 47.75, "lon": -120.74}, # Centered on Washington State.
            mapbox_zoom=5.5,
            margin={"r":0,"t":40,"l":0,"b":0}
        )
        return fig

    # Filter the main dataframe to show only the top N locations selected by the slider.
    # The 'rank' column was created in the geospatial_analysis.py script.
    filtered_gdf = gdf_display[gdf_display['rank'] <= top_n_value]

    # Create the map figure using Plotly's graph_objects.
    fig = go.Figure()

    # Add the data points (the optimal locations) to the map.
    fig.add_trace(go.Scattermapbox(
        # The lat and lon are derived from the 'geometry' column.
        lat=filtered_gdf.geometry.y,
        lon=filtered_gdf.geometry.x,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=12,
            # We color the points based on their suitability score for a nice visual effect.
            color=filtered_gdf['suitability_score'],
            colorscale='Viridis', # A vibrant and accessible color scale.
            showscale=True, # Shows the color bar legend.
            colorbar=dict(title='Suitability Score')
        ),
        # This is the text that appears when you hover over a point on the map.
        hoverinfo='text',
        text=[
            f"Rank: {rank}<br>Suitability Score: {score:.2f}"
            for rank, score in zip(filtered_gdf['rank'], filtered_gdf['suitability_score'])
        ]
    ))

    # Update the layout of the map to center it on Washington and set the style.
    fig.update_layout(
        title=f'Top {top_n_value} Recommended EV Charger Locations',
        mapbox_style="dark", # Using a dark theme for the map background.
        mapbox_accesstoken=MAPBOX_TOKEN,
        mapbox_center={"lat": 47.75, "lon": -120.74}, # Centered on Washington State.
        mapbox_zoom=5.5,
        margin={"r":0,"t":40,"l":0,"b":0}
    )

    return fig

