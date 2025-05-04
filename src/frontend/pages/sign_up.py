import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/sign_up')

def layout():
    return html.Div(
        className="home-background",
        children=[
            html.Div(
                className="popup-window",
                children=[
                    html.Div("Sign Up", className="popup-title-bar"),
                    html.Div(
                        className="popup-content",
                        children=[
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
                            html.Div(
                                html.Button("Submit", className="popup-button"),
                                style={"display": "flex", "justifyContent": "center"}
                            ),
                            html.Div(
                                children=[
                                    "Already have an account? ",
                                    html.A("Sign in here.", href="/sign_in", className="form-footer-link")
                                ],
                                className="popup-footer-text"
                            )
                        ]
                    )
                ]
            )
        ]
    )