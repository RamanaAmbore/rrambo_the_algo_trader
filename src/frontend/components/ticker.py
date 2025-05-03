import requests
from dash import html, dcc

from src.frontend.settings.config import TICKER_CONFIG
from src.helpers.logger import get_logger


logger = get_logger(__name__)
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
