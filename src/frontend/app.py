import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Import page layouts (assuming you create these files/functions)
from layouts import layout_home, layout_market, layout_watchlist, layout_watchlist_1, layout_watchlist_2, \
    layout_holdings, layout_positions, layout_trades, layout_orders, layout_ticker, layout_settings, \
    layout_auth  # Assuming layout_auth handles signin/signup/signout forms

# Define CDN links as a dictionary
CDN_LINKS = {
    "home": "https://cdn-icons-png.freepik.com/256/8784/8784978.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid",
    "market": "https://cdn-icons-png.freepik.com/256/2254/2254981.png?ga=GA1.1.1753840782.1745663557&semt=ais_hybrid",
    "watchlist": "https://cdn-icons-png.freepik.com/256/15597/15597823.png?ga=GA1.1.1753840782.1745663557&semt=ais_hybrid",
    "holdings": "https://cdn-icons-png.freepik.com/256/17063/17063555.png?ga=GA1.1.1753840782.1745663557&semt=ais_hybrid",
    "positions": "https://cdn-icons-png.freepik.com/256/7169/7169336.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid",
    "orders": "https://cdn-icons-png.freepik.com/256/10319/10319450.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid",
    "trades": "https://cdn-icons-png.freepik.com/256/8155/8155692.png?ga=GA1.1.1753840782.1745663557&semt=ais_hybrid",
    "ticker": "https://cdn-icons-png.freepik.com/256/14872/14872554.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid",
    "settings": "https://cdn-icons-png.freepik.com/256/14668/14668098.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid",
    "signin": "https://cdn-icons-png.freepik.com/256/10908/10908421.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid",
    "signup": "https://cdn-icons-png.freepik.com/256/17026/17026380.png?ga=GA1.1.707069739.1745663557&semt=ais_hybrid",
    "signout": "https://cdn-icons-png.freepik.com/256/4476/4476505.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid",
}

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
                }, 100);
            });
        </script>
    </body>
</html>
'''

app = dash.Dash(__name__, title="rambo-the-algo", assets_folder='./assets', suppress_callback_exceptions=True,
                pages_folder="")
app._favicon = "favicon.ico"
app.index_string = index_string


# Function to generate a navigation link
def generate_nav_link(href, label, icon_key):
    return dcc.Link(
        html.Div([html.Img(src=CDN_LINKS[icon_key], alt=label, width="20", height="20"), label]),
        href=href,
        className="nav-link"
    )


# Function to generate a submenu
def generate_submenu(label, submenu_items):
    return html.Div(className="nav-item", children=[
        html.Div([html.Img(src=CDN_LINKS[label], alt=label, width="20", height="20"), label], className="nav-link-btn"),
        html.Ul(className="nav-submenu", children=[
            html.Li(dcc.Link(item, href=f"/watchlist/{i + 1}", className="nav-link")) for i, item in
            enumerate(submenu_items)
        ])
    ])


# Define the main app layout with persistent header and footer
def serve_layout():
    # Extract header and footer HTML structure and convert to Dash components
    header = html.Div(className='navbar', children=[
        html.Img(src="assets/logo.png", alt="Rambo Logo"),
        html.Div(className='nav-links', children=[
            generate_nav_link("/", "Home", "home"),
            generate_nav_link("/market", "Market", "market"),
            generate_submenu("watchlist", ["Watchlist 1", "Watchlist 2"]),
            generate_nav_link("/holdings", "Holdings", "holdings"),
            generate_nav_link("/positions", "Positions", "positions"),
            generate_nav_link("/orders", "Orders", "orders"),
            generate_nav_link("/trades", "Trades", "trades"),
            generate_nav_link("/ticker", "Console", "ticker"),
            generate_nav_link("/settings", "Settings", "settings"),
        ]),
        html.Div(className='nav-links auth-links', children=[
            generate_nav_link("/signin", "Sign In", "signin"),
            generate_nav_link("/signup", "Sign Up", "signup"),
            generate_nav_link("/signout", "Sign Out", "signout"),
        ])
    ])

    footer = html.Footer(children=[
        html.Div(style={"display": "flex", "align-items": "center", "gap": "8px"}, children=[
            html.Span("© 2025 Ramana Ambore, FRM, CFA Level 3 Candidate"),
            html.Img(src="/assets/ramana.jpg", alt="Ramana Ambore")
        ])
    ])

    return html.Div([
        dcc.Location(id='url', refresh=False),  # Component to track URL
        header,  # Persistent Header
        html.Div(id='page-content', className='page-content'),  # Content area updated by callback
        footer  # Persistent Footer
    ])


app.layout = serve_layout


# Callback to update page content based on URL
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/market':
        return layout_market()
    elif pathname == '/watchlist':
        return layout_watchlist()  # Base watchlist page
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
        return layout_auth(pathname)  # Pass pathname to auth layout for specific forms
    elif pathname == '/':
        return layout_home()  # Home page
    else:
        return html.Div([
            html.H1("404 - Not Found"),
            html.P(f"The page {pathname} does not exist.")
        ])


if __name__ == '__main__':
    app.run_server(debug=True)
