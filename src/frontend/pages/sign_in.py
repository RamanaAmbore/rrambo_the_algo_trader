import dash
from dash import html, dcc

dash.register_page(__name__, path='/sign_in')

def layout():
    return html.Div( className="home-background-no-man", children=[
        html.H1("Welcome to rambo-the-algo"),
        html.P("Select a section from the navigation bar to view data."),
    ])

