from dash import dcc, html

# This is the central layout for your Dash application.
# It defines all the visual components that the user will see.

layout = html.Div(children=[
    # A main container for styling and alignment.
    html.Div(
        className="container",
        children=[
            # The main title of the dashboard.
            html.H1(children='EV Charging Station Demand Forecast'),

            # A brief description of the project and how to use the dashboard.
            html.P(
                children="This dashboard visualizes the optimal locations for new EV charging stations "
                         "across Washington, based on a predictive model. Higher-ranked spots represent areas "
                         "with high predicted demand and low existing charger density ('charging deserts'). "
                         "Use the slider below to adjust the number of top locations displayed on the map.",
                className="description"
            ),

            # The interactive map component.
            # 'id' is a unique identifier that allows our callback to target this specific map.
            # The 'figure' will be generated and updated by our callback function.
            dcc.Graph(
                id='demand-map',
                config={'displayModeBar': False} # Hides the plotly toolbar for a cleaner look.
            ),

            # A container for the slider control.
            html.Div(
                className="slider-container",
                children=[
                    html.Label("Number of Top Locations to Display:"),
                    # The slider allows users to interactively choose how many points to show.
                    dcc.Slider(
                        id='top-n-slider',
                        min=10,
                        max=100,
                        step=10,
                        value=50,  # The initial value when the page loads.
                        marks={i: str(i) for i in range(10, 101, 10)}, # Creates labels on the slider.
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ]
            )
        ]
    )
])
