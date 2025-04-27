import dash
from dash import dcc, html
from dash.dependencies import Input, Output

import requests
import pandas as pd # Keep import for potential future use in callbacks

# Import page layouts (assuming you create these files/functions)
from layouts import layout_home, layout_market, layout_watchlist, layout_watchlist_1, layout_watchlist_2, layout_holdings, layout_positions, layout_trades, layout_orders, layout_ticker, layout_settings, layout_auth # Assuming layout_auth handles signin/signup/signout forms

# Minimal index_string for basic HTML structure and loader
index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>rambo-the-algo</title>
        {%favicon%}
        {%css%}
       
    </head>
    <body>
        <div id="loader-wrapper">
            <img src="/assets/loading.gif" alt="Loading...">
            <div id="loader-text">Loading...</div>
        </div>

        {%app_entry%}

        {%config%}
        {%scripts%}
        {%renderer%}

         <script>
            window.addEventListener('load', function () {
                setTimeout(function () {
                    const loader = document.getElementById('loader-wrapper');
                    if (loader) loader.style.display = 'none';
                     // No need to set active class or showPage via JS anymore, Dash handles routing
                }, 2000);
                 // Remove JS event listeners for nav links as Dash handles routing
            });
            // Remove showPage, updateTicks, updateLogs functions as Dash handles content and data
        </script>

    </body>
</html>
'''


app = dash.Dash(__name__, title="rambo-the-algo", assets_folder='./assets', suppress_callback_exceptions=True)
app._favicon = "favicon.ico"
app.index_string = index_string

# Define the main app layout with persistent header and footer
def serve_layout():
    # Extract header and footer HTML structure and convert to Dash components
    header = html.Div(className='navbar', children=[
        html.Img(src="assets/logo.png", alt="Rambo Logo"),
        html.Div(className='nav-links', children=[
            dcc.Link(html.Div([html.Img(src="https://cdn-icons-png.freepik.com/256/8784/8784978.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid", alt="Home", width="20", height="20"), " Home"]), href="/", className="nav-link"),
            dcc.Link(html.Div([html.Img(src="https://cdn-icons-png.freepik.com/256/2254/2254981.png?ga=GA1.1.1753840782.1745663557&semt=ais_hybrid", alt="Market", width="20", height="20"), " Market"]), href="/market", className="nav-link"),
            html.Div(className="nav-item", children=[ # Watchlist with submenu
                html.Div([html.Img(src="https://cdn-icons-png.freepik.com/256/15597/15597823.png?ga=GA1.1.1753840782.1745663557&semt=ais_hybrid", alt="Watchlist", width="20", height="20"), " Watchlist"], className="nav-link-btn"),
                html.Ul(className="nav-submenu", children=[
                    html.Li(dcc.Link("Watchlist 1", href="/watchlist/1", className="nav-link")),
                    html.Li(dcc.Link("Watchlist 2", href="/watchlist/2", className="nav-link")),
                ])
            ]),
            dcc.Link(html.Div([html.Img(src="https://cdn-icons-png.freepik.com/256/17063/17063555.png?ga=GA1.1.1753840782.1745663557&semt=ais_hybrid", alt="Holdings", width="20", height="20"), " Holdings"]), href="/holdings", className="nav-link"),
            dcc.Link(html.Div([html.Img(src="https://cdn-icons-png.freepik.com/256/7169/7169336.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid", alt="Positions", width="20", height="20"), " Positions"]), href="/positions", className="nav-link"),
            dcc.Link(html.Div([html.Img(src="https://cdn-icons-png.freepik.com/256/8155/8155692.png?ga=GA1.1.1753840782.1745663557&semt=ais_hybrid", alt="Trades", width="20", height="20"), " Trades"]), href="/trades", className="nav-link"),
            dcc.Link(html.Div([html.Img(src="https://cdn-icons-png.freepik.com/256/4240/4240419.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid", alt="Orders", width="20", height="20"), " Orders"]), href="/orders", className="nav-link"),
            dcc.Link(html.Div([html.Img(src="https://cdn-icons-png.freepik.com/256/14872/14872554.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid", alt="Console", width="20", height="20"), " Console"]), href="/ticker", className="nav-link"), # Renamed from console to ticker based on usage
            dcc.Link(html.Div([html.Img(src="https://cdn-icons-png.freepik.com/256/14668/14668098.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid", alt="Settings", width="20", height="20"), " Settings"]), href="/settings", className="nav-link"),
        ]),
        html.Div(className='nav-links auth-links', children=[
            dcc.Link(html.Div([html.Img(src="https://cdn-icons-png.freepik.com/256/10908/10908421.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid", alt="Sign In", width="20", height="20"), " Sign In"]), href="/signin", className="nav-link"),
            dcc.Link(html.Div([html.Img(src="https://cdn-icons-png.freepik.com/256/17026/17026380.png?ga=GA1.1.707069739.1745663557&semt=ais_hybrid", alt="Sign Up", width="20", height="20"), " Sign Up"]), href="/signup", className="nav-link"),
            dcc.Link(html.Div([html.Img(src="https://cdn-icons-png.freepik.com/256/4476/4476505.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid", alt="Sign Out", width="20", height="20"), " Sign Out"]), href="/signout", className="nav-link"),
        ])
    ])

    footer = html.Footer(children=[
        html.Div(style={"display": "flex", "align-items": "center", "gap": "8px"}, children=[
            html.Span("© 2025 Ramana Ambore, FRM, CFA Level 3 Candidate"),
            html.Img(src="/assets/ramana.jpg", alt="Ramana Ambore")
        ])
    ])

    return html.Div([
        dcc.Location(id='url', refresh=False), # Component to track URL
        header, # Persistent Header
        html.Div(id='page-content', className='page-content'), # Content area updated by callback
        footer # Persistent Footer
    ])

app.layout = serve_layout

# Callback to update page content based on URL
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/market':
        return layout_market()
    elif pathname == '/watchlist':
        return layout_watchlist() # Base watchlist page
    elif pathname == '/watchlist/1':
        return layout_watchlist_1()
    elif pathname == '/watchlist/2':
        return layout_watchlist_2()
    elif pathname == '/holdings':
        return layout_holdings()
    elif pathname == '/positions':
        return layout_positions()
    elif pathname == '/trades':
        return layout_trades()
    elif pathname == '/orders':
        return layout_orders()
    elif pathname == '/ticker':
        # Ticker page needs its own layout and callbacks
        return layout_ticker()
    elif pathname == '/settings':
        return layout_settings()
    elif pathname in ['/signin', '/signup', '/signout']:
         # Authentication pages might share a layout structure or have specific forms
         return layout_auth(pathname) # Pass pathname to auth layout for specific forms
    elif pathname == '/':
        return layout_home() # Home page
    else:
        return html.Div([
            html.H1("404 - Not Found"),
            html.P(f"The page {pathname} does not exist.")
        ])

# Add callbacks for page-specific interactions within their respective layout files
# For the ticker page, the interval and data update callback will be defined in layouts.py (or ticker_layout.py)
# Example:
# @app.callback(Output('ticks-table', 'data'), Input('interval-component', 'n_intervals'))
# def update_ticks_callback(n):
#     # Fetch data from your backend
#     try:
#         response = requests.get('http://127.0.0.1:5000/get_ticks')
#         response.raise_for_status() # Raise an exception for bad status codes
#         data = response.json()
#         return data if data else [] # Return empty list if data is None or empty
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching ticks: {e}")
#         return []


if __name__ == '__main__':
    app.run_server(debug=True)
