import dash
from dash import dcc, html
import requests
from dash.dependencies import Input, Output

# from src.frontend.constants import CDN_LINKS  # Assuming these are in the global scope or defined here
# from src.frontend.extract_string import index_string #Assuming these are in the global scope or defined here

CDN_LINKS = {
    "home": "https://cdn-icons-png.freepik.com/256/8784/8784978.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid",
    "market": "https://cdn-icons-png.freepik.com/256/2254/2254981.png?ga=GA1.1.1753840782.1745663557&semt=ais_hybrid",
    "watchlist": "https://cdn-icons-png.freepik.com/256/15597/15597823.png?ga=GA1.1.1753840782.1745663557&semt=ais_hybrid",
    "holdings": "https://cdn-icons-png.freepik.com/256/17063/17063555.png?ga=GA1.1.1753840782.1745663557&semt=ais_hybrid",
    "positions": "https://cdn-icons-png.freepik.com/256/7169/7169336.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid",
    "orders": "https://cdn-icons-png.freepik.com/256/10319/10319450.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid",
    "trades": "https://cdn-icons-png.freepik.com/256/8155/8155692.png?ga=GA1.1.1753840782.1745663557&semt=ais_hybrid",
    "logs": "https://cdn-icons-png.freepik.com/256/14872/14872554.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid",
    "settings": "https://cdn-icons-png.freepik.com/256/14668/14668098.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid",
    "signin": "https://cdn-icons-png.freepik.com/256/10908/10908421.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid",
    "signout": "https://cdn-icons-png.freepik.com/256/4476/4476505.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid",
}

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

# Initialize Dash app
app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    assets_folder='./assets',
    title="rambo-the-algo",
)
app.index_string = index_string
app._favicon = "favicon.ico"

# --- Navigation Helpers ---
def generate_nav_link(href, label, icon_key):
    return dcc.Link(
        html.Div([html.Img(src=CDN_LINKS[icon_key], alt=label, width="20", height="20"), label]),
        href=href,
        className="nav-link"
    )

def generate_submenu(label, submenu_items):
    return html.Div(className="nav-item", children=[
        html.Div([html.Img(src=CDN_LINKS[label], alt=label, width="20", height="20"), label], className="nav-link-btn"),
        html.Ul(className="nav-submenu", children=[
            html.Li(dcc.Link(item, href=f"/watchlist/{i+1}", className="nav-link")) for i, item in enumerate(submenu_items)
        ])
    ])

# --- Layout ---
def serve_layout():
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
            generate_nav_link("/logs", "Console", "logs"),
            generate_nav_link("/settings", "Settings", "settings"),
        ]),
        html.Div(className='nav-links auth-links', children=[
            generate_nav_link("/sign_in", "Sign In/Up", "signin"),
            generate_nav_link("/sign_out", "Sign Out", "signout"),
        ])
    ])

    ticker_scroller = html.Div(id="ticker-scroller", children=[
        html.Div(id="ticker-container", children=[
            html.Span("Loading ticker data...", style={"white-space": "nowrap", "display": "inline-block"})
        ], className="ticker-container")
    ], className="ticker-scroller")

    ticker_interval = dcc.Interval(
        id='ticker-interval-component',
        interval=5 * 1000,
        n_intervals=0
    )

    footer = html.Footer(children=[
        html.Div(style={"display": "flex", "align-items": "center", "gap": "8px"}, children=[
            html.Span("© 2025 Ramana Ambore, FRM, CFA Level 3 Candidate"),
            html.Img(src="/assets/ramana.jpg", alt="Ramana Ambore")
        ])
    ])

    return html.Div([
        header,
        dash.page_container,  # <--- this is the KEY CHANGE!!
        ticker_scroller,
        ticker_interval,
        footer,
    ])

# Set the layout
app.layout = serve_layout

# --- Ticker Update Logic ---
current_ticker_text = ''
max_ticker_length = 200 #arbitrary

@app.callback(
    Output('ticker-container', 'children'),
    Input('ticker-interval-component', 'n_intervals')
)
def update_ticker(n):
    global current_ticker_text
    global max_ticker_length

    try:
        # Fetch latest tick data from backend every X intervals (e.g., every 50 intervals)
        if n % 50 == 0:
            response = requests.get("http://127.0.0.1:5000/get_ticks")
            response.raise_for_status()
            tick_data = response.json()

            # Create new ticker chunk
            new_ticker_chunk = ' '.join([f"{symbol.split(':')[0]} {price} {change:.2f} | "
                                         for symbol, (price, change) in tick_data.items()])

            # Add new ticker chunk to the right
            current_ticker_text += new_ticker_chunk

        # Trim the text from the left if it exceeds the maximum length
        if len(current_ticker_text) > max_ticker_length:
            current_ticker_text = current_ticker_text[-max_ticker_length:]  # Keep the rightmost part

        # Return wrapped inside a span, with inline styles for no wrap
        return html.Span(current_ticker_text, style={"white-space": "nowrap", "display": "inline-block"}, className="ticker-content")

    except Exception as e:
        print(f"Error fetching ticker data: {e}")
        return html.Span("Error loading ticker data.", style={"white-space": "nowrap", "display": "inline-block"}, className="ticker-content")

if __name__ == '__main__':
    app.run_server(debug=True)
