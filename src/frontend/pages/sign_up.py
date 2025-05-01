import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/sign_up')

def layout():
    return html.Div(
        className="home-background",
        children=[
            html.Div(
                className="form-container",
                children=[
                    html.H2("Sign Up", className="form-title"),
                    dcc.Input(
                        type="text",
                        placeholder="Username",
                        className="form-input"
                    ),
                    dcc.Input(
                        type="email",
                        placeholder="Email Address",
                        className="form-input"
                    ),
                    dcc.Input(
                        type="password",
                        placeholder="Password",
                        className="form-input"
                    ),
                    dcc.Input(
                        type="password",
                        placeholder="Confirm Password",
                        className="form-input"
                    ),
                    html.Button("Sign Up", className="form-button"),
                    html.Div(
                        children=[
                            "Already have an account? ",
                            html.A("Sign in here.", href="/", className="form-footer-link")
                        ]
                    )
                ]
            )
        ]
    )
