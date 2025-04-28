import dash
from dash import dcc, html
from constants import CDN_LINKS

# Minimal index_string
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
            html.Span("Loading ticker data...")
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
        dash.page_container,   # <--- this is the KEY CHANGE!!
        ticker_scroller,
        ticker_interval,
        footer,
    ])

# Set the layout
app.layout = serve_layout


if __name__ == '__main__':
    app.run_server(debug=True)
