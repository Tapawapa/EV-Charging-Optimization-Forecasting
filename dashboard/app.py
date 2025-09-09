import dash
from dash import dcc, html
import plotly.express as px
import geopandas as gpd
import pandas as pd
from dotenv import load_dotenv
import os
load_dotenv()
# Loading the data
# Make sure to use the correct path to your GeoJSON file
file_path = r"C:\EV Project\EV-Charging-Optimization-Forecasting\data\processed\top_charging_locations.geojson"
try:
    gdf = gpd.read_file(file_path)
except Exception as e:
    print(f"Error loading file: {e}")
    # Create a dummy GeoDataFrame to prevent the app from crashing if the file is not found
    gdf = gpd.GeoDataFrame(
        {'rank': [], 'suitability_score': [], 'geometry': []},
        crs="EPSG:4326"
    )


# --- FIX STARTS HERE ---

# Ensure the initial CRS is geographic (latitude/longitude)
if gdf.crs != "EPSG:4326":
    gdf = gdf.to_crs("EPSG:4326")

# To accurately calculate centroids, we must first re-project the geometries.
# 1. Project to a suitable projected CRS for Washington state (EPSG:32148), which uses meters.
# 2. Calculate the centroid on this projected data, which gives an accurate geometric center.
# 3. Convert the calculated centroid's CRS back to the geographic CRS (EPSG:4326) for plotting.
projected_gdf = gdf.to_crs("EPSG:32148")
gdf['centroid_geom'] = projected_gdf['geometry'].centroid.to_crs("EPSG:4326")

# Now, we extract latitude and longitude from our new, accurate centroid column.
gdf['lat'] = gdf['centroid_geom'].y
gdf['lon'] = gdf['centroid_geom'].x




# Using a public token for MapLibre styles
# You can get your own free token from Mapbox
mapbox_token = os.getenv("MAPBOX_TOKEN")
px.set_mapbox_access_token(mapbox_token)

# Creating the map using the corrected latitude and longitude columns
fig = px.scatter_map(
    gdf,
    lat="lat",
    lon="lon",
    hover_name="rank",
    hover_data={"suitability_score": True, "lat": False, "lon": False}, # Hide lat/lon from hover data if desired
    color_discrete_sequence=["#FF0000"], # A bright cyan for visibility on a dark map
    zoom=6,
    height=800,
    center={"lat": 47.75, "lon": -120.74} # Center of Washington State
)

fig.update_layout(
    map_style="dark",
    title_text="Recommended EV Charging Station Locations in Washington Based on XGBoost Model. Hover for details. The big number indicates rank of a station.",
    title_x=0.5,
    margin={"r":0,"t":40,"l":0,"b":0}
)

# Creating the dash app
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(
        children='EV Charging Station Dashboard',
        style={'textAlign': 'center'}
    ),
    dcc.Graph(
        id='ev-map',
        figure=fig
    )
])

# Running the app
if __name__ == '__main__':
    app.run(debug=True) # Use run_server for Dash
