from dash import dcc, html, dash_table
import requests # Keep import for potential data fetching in callbacks
import pandas as pd # Keep import

# Define layouts for each page

def layout_home():
    return html.Div([
        html.H1("Welcome to rambo-the-algo"),
        html.P("Select a section from the navigation bar to view data."),
    ])

def layout_market():
    return html.Div([
        html.H1("Market Data"),
        html.P("Content for Market data goes here."),
        # Add specific components for the market page here
    ])

def layout_watchlist():
    return html.Div([
        html.H1("Watchlist"),
        html.P("This is the base Watchlist page. Select a specific watchlist from the menu."),
        # Add general watchlist content here
    ])

def layout_watchlist_1():
    return html.Div([
        html.H1("Watchlist 1"),
        html.P("Content for Watchlist 1 goes here."),
        # Add components for Watchlist 1
    ])

def layout_watchlist_2():
    return html.Div([
        html.H1("Watchlist 2"),
        html.P("Content for Watchlist 2 goes here."),
        # Add components for Watchlist 2
    ])

def layout_holdings():
     return html.Div([
        html.H1("Holdings"),
        html.P("Content for Holdings goes here."),
        # Add components for Holdings
    ])

def layout_positions():
     return html.Div([
        html.H1("Positions"),
        html.P("Content for Positions goes here."),
        # Add components for Positions
    ])

def layout_trades():
    return html.Div([
        html.H1("Trades"),
        html.P("Content for Trades goes here."),
        # Add components for Trades
    ])

def layout_orders():
    return html.Div([
        html.H1("Orders"),
        html.P("Content for Orders goes here."),
        # Add components for Orders
    ])


# --- Ticker Page Layout and Callback ---
def layout_ticker():
    return html.Div([
        html.H3("Live Ticker Data"),
        dash_table.DataTable(
            id='ticks-table',
            columns=[
                {"name": "Instrument Token", "id": "instrument_token"},
                {"name": "Last Price", "id": "last_price"},
                {"name": "Timestamp", "id": "timestamp"}
            ],
            data=[], # Initial empty data
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'},
            style_header={
                'backgroundColor': '#1e1e2f',
                'color': 'white',
                'fontWeight': 'bold'
            }
        ),
        # Interval component placed within the ticker layout
        dcc.Interval(id='interval-component', interval=5000, n_intervals=0)
    ])

# Add the callback for the ticker table update here (or in index.py if preferred, but keeping it with the layout is often cleaner)
# Make sure app is accessible if defining callback here, or move to index.py
# Example if in layouts.py, assuming 'app' is passed or imported:
# @app.callback(Output('ticks-table', 'data'), Input('interval-component', 'n_intervals'))
# def update_ticks_callback(n):
#      try:
#         response = requests.get('http://127.0.0.1:5000/get_ticks')
#         response.raise_for_status()
#         data = response.json()
#         return data if data else []
#      except requests.exceptions.RequestException as e:
#         print(f"Error fetching ticks: {e}")
#         return []


def layout_settings():
    return html.Div([
        html.H1("Settings"),
        html.P("Content for Settings goes here."),
        # Add components for Settings
    ])

def layout_auth(pathname):

    # Common background styling
    background_style = {
        'backgroundImage': 'url("/assets/loading.gif")',  # assuming background.gif is in your assets folder
        'backgroundSize': '100% 100%',
        'backgroundPosition': 'center',
        'backgroundRepeat': 'no-repeat',
        'height': '100vh',
        'width': '100vw',
        'overflow': 'hidden',
        'display': 'flex',
        'justifyContent': 'center',
        'alignItems': 'center',
        'flexDirection': 'column',
        'textAlign': 'center',
        'margin': '0',  # remove margin
        'padding': '0',  # also remove padding
        'position': 'fixed',  # better than absolute
        'top': '0',
        'left': '0',
    }
    # This layout can dynamically show signin/signup/signout forms
    # based on the pathname passed from the main callback.
    if pathname == '/signin':
        content = html.Div([
             html.H1("Sign In"),
             html.P("Sign In form goes here."),
             # Add Sign In form components
        ])
    elif pathname == '/signup':
         content = html.Div([
             html.H1("Sign Up"),
             html.P("Sign Up form goes here."),
             # Add Sign Up form components
        ])
    elif pathname == '/signout':
         content = html.Div([
             html.H1("Sign Out"),
             html.P("Content for Sign Out confirmation/message goes here."),
             # Add Sign Out components
        ])
    else: # Should not happen with correct routing
        content = html.Div([
             html.H1("Authentication"),
             html.P("Select an authentication option."),
        ])

    # Wrap authentication content in the background div
    return html.Div(id='auth-page-background',   style=background_style, children=[
        html.Div(id='auth-page-content-container', children=content)
    ])

# --- Example of System Logs Layout and Callback (Similar to Ticker) ---
# def layout_system_logs():
#     return html.Div([
#         html.H3("System Logs"),
#         html.Pre(id='logs-content', style={'whiteSpace': 'pre-wrap', 'background-color': '#f9f9f9', 'padding': '10px'}),
#         dcc.Interval(id='logs-interval-component', interval=5000, n_intervals=0) # Interval for logs
#     ])

# # Add the callback for system logs update
# # @app.callback(Output('logs-content', 'children'), Input('logs-interval-component', 'n_intervals'))
# # def update_logs_callback(n):
# #     try:
# #         response = requests.get('http://127.0.0.1:5000/get_logs')
# #         response.raise_for_status()
# #         text = response.text
# #         return text
# #     except requests.exceptions.RequestException as e:
# #         print(f"Error fetching logs: {e}")
# #         return "Error loading logs."