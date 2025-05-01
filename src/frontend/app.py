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
            html.Img(src="assets/logo1.png", alt="Rambo Logo"),
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
TICKER_UPDATE_FREQUENCY = 50
BASE_INTERVAL = 500
SCROLL_SPEED_MULTIPLIER = 1
max_ticker_length = 0

url = "http://127.0.0.1:5000/get_ticks"

scroll_refresh =True
@app.callback(
    Output('ticker-container', 'children'),
    Input('ticker-interval-component', 'n_intervals'),

)
def update_ticker(n):
    """
    Updates the ticker text.
    """
    global current_ticker_text
    global TICKER_UPDATE_FREQUENCY
    global BASE_INTERVAL
    global SCROLL_SPEED_MULTIPLIER
    global max_ticker_length
    global scroll_refresh

    try:
        if n % TICKER_UPDATE_FREQUENCY == 0:
            response = requests.get(url)
            response.raise_for_status()
            tick_data = response.json()

            ticker_items = []
            for idx, (symbol, (price, change)) in enumerate(tick_data.items()):
                is_last = (idx == len(tick_data) - 1)
                # Python (Dash HTML) update
                change_color_class = (
                    "ticker-change-zero" if change == 0 else
                    "ticker-change-negative" if change < 0 else
                    "ticker-last-change" if is_last else
                    "ticker-change"
                )
                formatted_change = (
                    "+0.0" if round(change, 2) == 0
                    else f"{change:+.2f}".rstrip("0").rstrip(".")
                )
                item = html.Span([
                    html.Span(symbol.split(':')[0], className="ticker-symbol"),
                    html.Span(f"{price}", className="ticker-price"),
                    html.Span(formatted_change, className=change_color_class),
                ], className="ticker-item")

                ticker_items.append(item)

            new_ticker_chunk = ticker_items
            if scroll_refresh:
                current_ticker_text = new_ticker_chunk
                scroll_refresh = False

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
            )
        )

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return (
            html.Span(
                "An unexpected error occurred.",
                style={"white-space": "nowrap", "display": "inline-block"},
                className="scroll-ticker"
            )
        )


if __name__ == '__main__':
    app.run_server(debug=True)
