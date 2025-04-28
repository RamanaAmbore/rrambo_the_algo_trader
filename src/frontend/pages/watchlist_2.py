# pages/watchlist_2.py
import dash
from dash import html

dash.register_page(__name__, path='/watchlist/2')
def layout():
    return html.Div([
        html.H1("Watchlist 2"),
        html.P("Content for Watchlist 2 goes here."),
        # Add components for Watchlist 2
    ])
