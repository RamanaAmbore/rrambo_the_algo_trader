import dash
import requests
from dash import dcc, html, clientside_callback
from dash.dependencies import Input, Output, MATCH
from src.frontend.helpers.index_string import index_string
from src.helpers.logger import get_logger

# Configuration Constants
TICKER_CONFIG = {
    'DURATION_PER_ITEM': 10,
    'DURATION_MULTIPLIER': 300,
    'API_URL': "http://127.0.0.1:5000/get_ticks"
}

APP_CONFIG = {
    'TITLE': "Rambo-the-Algo",
    'UPDATE_TITLE': 'Rambo-the-algo',
    'FAVICON': "favicon.ico",
    'ASSETS_FOLDER': './assets'
}

logger = get_logger(__name__)

class HeaderComponent:
    @staticmethod
    def create():
        return html.Div(
            className='navbar',
            children=[
                html.Img(src="assets/logo1.png", alt="Rambo Logo"),
                html.Div(
                    className='nav-links',
                    children=[
                        dcc.Link(html.Div(link_text), href=href, className="nav-link")
                        for link_text, href in [
                            ("Home", "/"), ("Market", "/market"),
                            ("Watchlist", "/watchlist"), ("Holdings", "/holdings"),
                            ("Positions", "/positions"), ("Orders", "/orders"),
                            ("Trades", "/trades"), ("Console", "/logs"),
                            ("Settings", "/settings"), ("Sign In/Up", "/sign_in"),
                            ("Sign Out", "/sign_out")
                        ]
                    ]
                )
            ]
        )

class FooterComponent:
    @staticmethod
    def create():
        return html.Footer(
            children=[
                html.Div(
                    children=[
                        html.Span("© 2025 Ramana Ambore, FRM, CFA Level 3 Candidate"),
                        html.Img(src="/assets/ramana.jpg", alt="Ramana Ambore")
                    ]
                )
            ]
        )

class TickerComponent:
    def __init__(self):
        self.items = []
        self.length = 0
        self.scroll_duration = 0

    def create_scroller(self):
        return html.Div(
            id="ticker-scroller",
            children=[
                html.Span("Loading ticker data...", id="scrollText", className="scroll-text"),
                dcc.Store(id="ticker-scroll-complete"),
                html.Div(id="dummy-div", style={"display": "none"})
            ],
            className="ticker-scroller"
        )

    def update_ticker_data(self):
        try:
            response = requests.get(TICKER_CONFIG['API_URL'])
            response.raise_for_status()
            api_tick_data = response.json()
            self.items = self._format_ticker_items(api_tick_data)
            self.length = len(self.items)
            self.scroll_duration = (TICKER_CONFIG['DURATION_PER_ITEM'] *
                                 self.length *
                                 TICKER_CONFIG['DURATION_MULTIPLIER'])
            return [self._create_ticker_span()]
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return [self._create_error_span()]

    def _format_ticker_items(self, api_tick_data):
        formatted_items = []
        for symbol, (price, change) in api_tick_data.items():
            change_color_class = self._get_change_color_class(change)
            formatted_change = self._format_change_value(change)
            item = self._create_ticker_item(symbol, price, formatted_change, change_color_class)
            formatted_items.append(item)
        return formatted_items

    @staticmethod
    def _get_change_color_class(change):
        if change == 0:
            return "ticker-change-zero"
        return "ticker-change-negative" if change < 0 else "ticker-change"

    @staticmethod
    def _format_change_value(change):
        if round(change, 2) == 0:
            return "+0.0"
        return f"{change:+.2f}".rstrip("0").rstrip(".")

    @staticmethod
    def _create_ticker_item(symbol, price, formatted_change, change_color_class):
        return html.Span([
            html.Span(symbol.split(':')[0], className="ticker-symbol"),
            html.Span(f"{price}", className="ticker-price"),
            html.Span(formatted_change, className=change_color_class),
        ], className="ticker-item")

    def _create_ticker_span(self):
        return html.Span(
            self.items,
            id="scrollText",
            style={"animation": f"scroll {self.scroll_duration}ms linear infinite"},
            className="scroll-text"
        )

    @staticmethod
    def _create_error_span():
        return html.Span(
            "An unexpected error occurred.",
            style={"white-space": "nowrap", "display": "inline-block"},
            className="scroll-text"
        )

# Initialize components
ticker = TickerComponent()
app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    assets_folder=APP_CONFIG['ASSETS_FOLDER'],
    title=APP_CONFIG['TITLE'],
    update_title=APP_CONFIG['UPDATE_TITLE'],
)
app.index_string = index_string
app._favicon = APP_CONFIG['FAVICON']

def serve_layout():
    return html.Div([
        HeaderComponent.create(),
        dash.page_container,
        ticker.create_scroller(),
        FooterComponent.create()
    ])

app.layout = serve_layout()

@app.callback(
    Output('scrollText', 'children'),
    Input('ticker-scroll-complete', 'data'),
    prevent_initial_call=True
)
def update_ticker(_):
    return ticker.update_ticker_data()

# Clientside callback setup remains the same
clientside_callback(
    """
    function(dummyText) {
        return true;
    }
    """,
    Output("ticker-scroll-complete", "data"),
    Input("dummy-div", "children"),
)

if __name__ == '__main__':
    app.run(debug=True)