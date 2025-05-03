# pages/sign_in.py
import dash
from dash import html, dcc

dash.register_page(__name__, path='/sign_out')

def layout():
    return html.Div( className="home-background", children=[
        html.H1("Signout page"),
    ])

