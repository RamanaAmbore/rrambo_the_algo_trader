# pages/watchlist.py
import dash
from dash import html

dash.register_page(__name__, path='/watchlist')


def layout():
    return html.Div([
        html.H1("Watchlist"),
        html.P("This is the base Watchlist page. Select a specific watchlist from the menu."),
        # Add general watchlist content here
    ])
