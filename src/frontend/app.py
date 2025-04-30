import json
import logging
from collections import deque


import dash
import requests
from dash import dcc, html
from dash.dependencies import Input, Output, State

from src.frontend.helpers.constants import CDN_LINKS
from src.frontend.helpers.index_string import index_string

# --- Initialize Dash App ---
app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    assets_folder='./assets',
    title="RRambo-the-Algo",
)
app.index_string = index_string
app._favicon = "favicon.ico"


# --- Navigation Helpers ---
def generate_nav_link(href, label, icon_key):
    """Generates a navigation link with an icon and label."""
    return dcc.Link(
        html.Div([
            html.Img(src=CDN_LINKS[icon_key], alt=label, width="20", height="20"),
            label
        ]),
        href=href,
        className="nav-link"
    )


def generate_submenu(label, submenu_items):
    """Generates a submenu with a label and a list of items."""
    return html.Div(
        className="nav-item",
        children=[
            html.Div(
                [html.Img(src=CDN_LINKS[label], alt=label, width="20", height="20"), label],
                className="nav-link-btn"
            ),
            html.Ul(
                className="nav-submenu",
                children=[
                    html.Li(dcc.Link(item, href=f"/watchlist/{i + 1}", className="nav-link"))
                    for i, item in enumerate(submenu_items)
                ]
            )
        ]
    )


# --- Layout ---
def serve_layout():
    """Defines the main layout of the application."""
    header = html.Div(
        className='navbar',
        children=[
            html.Img(src="assets/logo.png", alt="Rambo Logo"),
            html.Div(
                className='nav-links',
                children=[
                    generate_nav_link("/", "Home", "home"),
                    generate_nav_link("/market", "Market", "market"),
                    generate_submenu("watchlist", ["Watchlist 1", "Watchlist 2"]),
                    generate_nav_link("/holdings", "Holdings", "holdings"),
                    generate_nav_link("/positions", "Positions", "positions"),
                    generate_nav_link("/orders", "Orders", "orders"),
                    generate_nav_link("/trades", "Trades", "trades"),
                    generate_nav_link("/logs", "Console", "logs"),
                    generate_nav_link("/settings", "Settings", "settings"),
                ]
            ),
            html.Div(
                className='nav-links auth-links',
                children=[
                    generate_nav_link("/sign_in", "Sign In/Up", "signin"),
                    generate_nav_link("/sign_out", "Sign Out", "signout"),
                ]
            )
        ]
    )

    ticker_scroller = html.Div(
        id="ticker-scroller",
        children=[
            html.Div(
                id="ticker-container",
                children=[
                    html.Span(
                        "Loading ticker data...",
                        style={"white-space": "nowrap", "display": "inline-block"}
                    )
                ],
                className="ticker-container left-to-right"  # Added class for left-to-right
            )
        ],
        className="ticker-scroller"
    )

    ticker_interval = dcc.Interval(
        id='ticker-interval-component',
        interval=50,
        n_intervals=0
    )

    # Use dcc.Store instead of html.Div for storing data
    viewport_width_store = dcc.Store(id='viewport-width-store', storage_type='memory')

    footer = html.Footer(
        children=[
            html.Div(
                style={"display": "flex", "align-items": "left", "gap": "8px"},
                children=[
                    html.Span("© 2025 Ramana Ambore, FRM, CFA Level 3 Candidate"),
                    html.Img(src="/assets/ramana.jpg", alt="Ramana Ambore")
                ]
            )
        ]
    )

    return html.Div([
        header,
        dash.page_container,
        ticker_scroller,
        ticker_interval,
        viewport_width_store,
        footer,
    ])


# Set the layout
app.layout = serve_layout()

# --- Ticker Update Logic ---
current_ticker_text = ""
max_ticker_length = 10000
char_width_in_pixels = 7
TICKER_UPDATE_FREQUENCY = 50
BASE_INTERVAL = 500
SCROLL_SPEED_MULTIPLIER = 1
VIEWPORT_WIDTH = 1000
url = "http://127.0.0.1:5000/get_ticks"
first_time = True

@app.callback(
    Output('ticker-container', 'children'),
    Output('ticker-interval-component', 'interval'),
    Input('ticker-interval-component', 'n_intervals'),
    State('ticker-interval-component', 'interval'),
    State('viewport-width-store', 'data')
)
def update_ticker(n, current_interval, viewport_width):
    """
    Updates the ticker text.
    """
    global current_ticker_text
    global max_ticker_length
    global char_width_in_pixels
    global TICKER_UPDATE_FREQUENCY
    global BASE_INTERVAL
    global SCROLL_SPEED_MULTIPLIER
    global VIEWPORT_WIDTH

    if viewport_width is not None:
        VIEWPORT_WIDTH = viewport_width

    try:
        if n % TICKER_UPDATE_FREQUENCY == 0:
            response = requests.get(url)
            response.raise_for_status()
            tick_data = response.json()

            new_ticker_chunk = ' '.join(
                [f"{symbol.split(':')[0]} {price} {change:.2f} | "
                 for symbol, (price, change) in tick_data.items()]
            )
            if not current_ticker_text:
                current_ticker_text = new_ticker_chunk
                max_ticker_length = len(current_ticker_text) * 2
            else:
                new_text = current_ticker_text + new_ticker_chunk

                if len(new_text) < max_ticker_length:
                    current_ticker_text = new_text


        # # Calculate visible text length based on viewport width
        # visible_chars = int(VIEWPORT_WIDTH / char_width_in_pixels)
        # ticker_text = "".join(list(current_ticker_text)[:visible_chars])
        ticker_text = current_ticker_text

        return (
            html.Span(
                ticker_text,
                style={
                    "white-space": "nowrap",
                    "display": "inline-block",
                    "animation": f"scroll-ticker 500000ms linear infinite",
                },
                className="scroll-ticker"
            ),
            BASE_INTERVAL
        )

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return (
            html.Span(
                "An unexpected error occurred.",
                style={"white-space": "nowrap", "display": "inline-block"},
                className="ticker-content"
            ),
            BASE_INTERVAL
        )


# --- Client-side callback to get viewport width ---
app.clientside_callback(
    """
    function(n_intervals) {
        return window.innerWidth;
    }
    """,
    Output('viewport-width-store', 'data'),
    Input('ticker-interval-component', 'n_intervals')
)

if __name__ == '__main__':
    app.run_server(debug=True)
