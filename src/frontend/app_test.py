import logging

import dash
import requests
from dash import dcc, html, clientside_callback
from dash.dependencies import Input, Output

from src.frontend.helpers.index_string import index_string
from src.frontend.helpers.template_utils import footer, header
from src.helpers.logger import get_logger

logger = get_logger(__name__)

# --- Ticker Update Logic ---
current_ticker_items = []
duration_per_item = 10
duration_multiplier = 300
len_current_ticker = 0
scroll_duration = 0
check_duration = 50
url = "http://127.0.0.1:5000/get_ticks"

# --- Initialize Dash App ---
app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    assets_folder='./assets',
    title="Rambo-the-Algo",
    update_title='Rambo-the-algo',
)
app.index_string = index_string
app._favicon = "favicon.ico"


# --- Layout ---
def serve_layout():
    ticker_scroller = html.Div(
        id="ticker-scroller",
        children=[
            html.Div(
                id="ticker-container",
                children=[
                    html.Span(
                        "Loading ticker data...",
                        id="scrollTicker",
                        style={"white-space": "nowrap", "display": "inline-block"},
                        className="scroll-ticker"
                    )
                ],
                className="ticker-container left-to-right"
            ),
            dcc.Store(id="ticker-scroll-complete"),
            html.Div(id="dummy-div", style={"display": "none"}),
            html.Script("""
                window.addEventListener("load", function () {
                    const ticker = document.getElementById("scrollTicker");
                    const dummy = document.getElementById("dummy-div");
                    if (ticker && dummy) {
                        ticker.addEventListener("animationend", () => {
                            dummy.innerText = new Date().toISOString();
                        });
                    }
                });
            """)
        ],
        className="ticker-scroller"
    )

    ticker_interval = dcc.Interval(id='ticker-interval-component', interval=50, n_intervals=0)

    return html.Div([header, dash.page_container, ticker_scroller, ticker_interval, footer])


app.layout = serve_layout()


# --- Clientside Callback ---
clientside_callback(
    """
    function(dummyText) {
        return true;
    }
    """,
    Output("ticker-scroll-complete", "data"),
    Input("dummy-div", "children"),
)


# --- Server Callback: Re-populate ticker on scroll end ---
@app.callback(
    Output('scrollTicker', 'children'),
    Output('scrollTicker', 'style'),
    Input('ticker-scroll-complete', 'data'),
    prevent_initial_call=True
)
def update_ticker(n):

    try:
        if not current_ticker_items:
            logger.info('next_ticker_items empty')
            set_ticker_items()

        return current_ticker_items, {
            "white-space": "nowrap",
            "display": "inline-block",
            "animation": f"scroll-ticker {scroll_duration}ms linear 1",
        }

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return html.Span(
            "An unexpected error occurred.",
            style={"white-space": "nowrap", "display": "inline-block"},
            className="scroll-ticker"
        )

def set_ticker_items():
    global current_ticker_items, len_current_ticker, scroll_duration

    response = requests.get(url)
    response.raise_for_status()
    api_tick_data = response.json()

    next_ticker_items_local = []
    if api_tick_data:
        for idx, (symbol, (price, change)) in enumerate(api_tick_data.items()):
            # Python (Dash HTML) update
            change_color_class = (
                "ticker-change-zero" if change == 0 else
                "ticker-change-negative" if change < 0 else
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

            next_ticker_items_local.append(item)

    logger.info(f"Input Ticker size: {len(api_tick_data)}, Formatted: {len(next_ticker_items_local)}")
    current_ticker_items = next_ticker_items_local
    len_current_ticker = len(current_ticker_items)
    scroll_duration = duration_per_item * len_current_ticker * duration_multiplier


if __name__ == '__main__':
    app.run(debug=True)