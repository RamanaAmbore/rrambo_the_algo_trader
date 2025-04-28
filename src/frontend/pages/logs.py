# pages/holdings.py
import dash
from dash import html

dash.register_page(__name__, path='/logs')


def layout():
    return html.Div([
        html.H1("console"),
        html.P("Content for Holdings goes here."),
        # Add components for Holdings
    ])