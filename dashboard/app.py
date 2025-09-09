import dash
from dash import dcc, html

# This is the main application file. Its primary jobs are to:
# 1. Initialize the Dash application instance.
# 2. Import and set the application's layout from layouts.py.
# 3. Import the callbacks from callbacks.py to make the app interactive.
# 4. Run the web server.

# Initialize the Dash app.
# The __name__ variable is a standard Python convention.
# We also include an external stylesheet for some basic, clean styling.
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
server = app.server

# Import the layout from our layouts.py file.
# The app.layout defines the entire visual structure of your web application.
from layouts import layout
app.layout = layout

# Import the callbacks from our callbacks.py file.
# This line is crucial! It registers the callback functions with the app,
# making the dashboard interactive. Without this, the slider would do nothing.
import callbacks

# This is the standard entry point for running a Dash application.
# The 'if __name__ == "__main__":' block ensures that the server is only run
# when this script is executed directly (not when it's imported by another script).
if __name__ == '__main__':
    # app.run_server(debug=True) starts the development server.
    # 'debug=True' is very helpful during development as it automatically reloads
    # the server when you make changes to your code.
    app.run(debug=True)

