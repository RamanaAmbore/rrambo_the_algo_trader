# pages/home.py
import dash
from dash import html

dash.register_page(__name__, path='/')

def layout():
    return html.Div([
        html.H1("Welcome to rambo-the-algo"),
        html.P("Select a section from the navigation bar to view data."),
    ])





















