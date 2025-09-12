import dash
from dash import dcc, html
import plotly.express as px
import geopandas as gpd
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

# --- DATA LOADING (UPDATED) ---
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, '..', 'data', 'processed', 'top_charging_locations.geojson')

try:
    gdf = gpd.read_file(file_path)
except Exception as e:
    print(f"Error loading file: {e}")
    gdf = gpd.GeoDataFrame(
        {'rank': [], 'suitability_score': [], 'geometry': []},
        crs="EPSG:4326"
    )

# --- (The rest of your data processing code remains the same) ---
if gdf.crs != "EPSG:4326":
    gdf = gdf.to_crs("EPSG:4326")

projected_gdf = gdf.to_crs("EPSG:32148")
gdf['centroid_geom'] = projected_gdf['geometry'].centroid.to_crs("EPSG:4326")
gdf['lat'] = gdf['centroid_geom'].y
gdf['lon'] = gdf['centroid_geom'].x


mapbox_token = os.getenv("MAPBOX_TOKEN")
px.set_mapbox_access_token(mapbox_token)

fig = px.scatter_map(
    gdf,
    lat="lat",
    lon="lon",
    hover_name="rank",
    hover_data={"suitability_score": True, "lat": False, "lon": False},
    color_discrete_sequence=["#FF0000"],
    zoom=6,
    height=800,
    center={"lat": 47.75, "lon": -120.74}
)

fig.update_layout(
    map_style="dark",
    title_text="Recommended EV Charging Station Locations in Washington Based on XGBoost Model. Hover for details. The big number indicates rank of a station.",
    title_x=0.5,
    margin={"r":0,"t":40,"l":0,"b":0}
)

# 
app = dash.Dash(__name__)
server = app.server  # Add this line

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


if __name__ == '__main__':
    app.run(debug=True)
