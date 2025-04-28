# pages/sign_in.py
import dash
from dash import html, dcc

dash.register_page(__name__, path='/sign_out')

def layout():
    return html.Div([
        html.H2("Sign Out"),
        dcc.Input(id="username", placeholder="Username", type="text"),
        dcc.Input(id="password", placeholder="Password", type="password"),
        html.Button("Sign In", id="sign-in-button"),
        html.Div(id="sign-in-message"),
        html.P("Don't have an account?"),
        dcc.Link("Sign Up", href="/sign-up"),
    ])
