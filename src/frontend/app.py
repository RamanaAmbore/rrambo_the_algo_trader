import logging

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
        interval=60,
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
        html.Title('RRambo-the-Algo'),
        header,
        dash.page_container,
        ticker_scroller,
        ticker_interval,
        viewport_width_store,
        footer,
    ])


@app.callback(
    Output('ticker-interval-component', 'n_intervals'),
    Input('ticker-interval-component', 'n_intervals')
)
def update_interval(n):
    # Set your threshold here
    if n >= 10000:
        n = 0  # Reset to 0
    return n


# Set the layout
app.layout = serve_layout()

# --- Ticker Update Logic ---
current_ticker_text = ""
max_ticker_length = 0
char_width_in_pixels = 7
TICKER_UPDATE_FREQUENCY = 360
SCROLL_SPEED_BASE_INTERVAL = 60
SCROLL_SPEED_MULTIPLIER = 1
VIEWPORT_WIDTH = 1000
url = "http://127.0.0.1:5000/get_ticks"
first_time = True
wasted_count = 0


@app.callback(
    Output('ticker-container', 'children'),
    Input('ticker-interval-component', 'n_intervals'),
    State('ticker-interval-component', 'interval'),
)
def update_ticker(n, current_interval):
    """
    Updates the ticker text with structured HTML for each stock.
    Initial fetch always happens, then next happens when last item fully scrolls.
    """
    global current_ticker_text
    global SCROLL_SPEED_BASE_INTERVAL
    global SCROLL_SPEED_MULTIPLIER
    global need_refresh

    try:
        ticker_elements = []

        # Always fetch new data when required
        if current_ticker_text is None or need_refresh:
            response = requests.get(url)
            response.raise_for_status()
            tick_data = response.json()
            tick_items = list(tick_data.items())

            for idx, (symbol, (price, change)) in enumerate(tick_items):
                is_last = idx == len(tick_items) - 1

                stock_span = html.Span(
                    symbol.split(":")[0],
                    className="ticker-symbol"
                )

                price_span = html.Span(
                    f"{price}",
                    className="ticker-price"
                )

                change_span = html.Span(
                    f"{change:.2f}%",
                    className="ticker-change"
                )

                separator_span = html.Span(
                    " | ",
                    className="ticker-separator"
                )

                group_span = html.Span(
                    [stock_span, " ", price_span, " ", change_span, separator_span],
                    className="ticker-item",
                    id="last-ticker-item" if is_last else None
                )

                ticker_elements.append(group_span)

            current_ticker_text = ticker_elements
            need_refresh = False

        animation_duration = SCROLL_SPEED_BASE_INTERVAL * len(current_ticker_text) * SCROLL_SPEED_MULTIPLIER

        # Return updated ticker with JavaScript embedded to control the scroll and refresh
        return html.Div([
            html.Span(
                current_ticker_text,
                style={
                    "white-space": "nowrap",
                    "display": "inline-block",
                    "animation": f"scroll-ticker {SCROLL_SPEED_BASE_INTERVAL * len(current_ticker_text) * SCROLL_SPEED_MULTIPLIER}ms linear infinite",
                },
                className="ticker-container"
            ),
            html.Script("""
                  // JavaScript to control ticker scroll and refresh when last item is visible
                  let need_refresh = false;

                  function animateTicker() {
                      const tickerContainer = document.querySelector('.ticker-container');
                      const lastTickerItem = document.querySelector('.last-ticker-item');

                      let start = null;

                      function step(timestamp) {
                          if (!start) start = timestamp;
                          const elapsed = timestamp - start;

                          // Scroll left based on elapsed time
                          tickerContainer.style.transform = `translateX(${-elapsed * 0.05}px)`; // Adjust 0.05 for speed

                          // Check if the last item is leaving the viewport
                          if (lastTickerItem) {
                              const rect = lastTickerItem.getBoundingClientRect();
                              if (rect.right < window.innerWidth) {
                                  need_refresh = true;  // Mark that we need to refresh the data
                              }
                          }

                          // If refresh is needed, fetch new data and reset animation
                          if (need_refresh) {
                              fetchTickerData();  // Fetch new ticker data
                              need_refresh = false;  // Reset the refresh flag
                              start = null;  // Reset animation start time
                          } else {
                              requestAnimationFrame(step);  // Continue the animation
                          }
                      }

                      requestAnimationFrame(step);
                  }

                  // Function to fetch ticker data via an API
                  async function fetchTickerData() {
                      try {
                          const response = await fetch('""" + url + """');  // Replace with your API endpoint
                          const data = await response.json();

                          // Update the ticker with new data
                          updateTicker(data);  // You can call your update function here
                      } catch (error) {
                          console.error("Error fetching ticker data:", error);
                      }
                  }

                  // Initialize ticker animation
                  animateTicker();
              """)
        ])

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return (
            html.Span(
                "An unexpected error occurred.",
                style={"white-space": "nowrap", "display": "inline-block"},
                className="ticker-content"
            )
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
    app.run_server(debug=True, use_reloader=False)

