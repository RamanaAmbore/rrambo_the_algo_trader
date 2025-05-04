import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from src.frontend.components.pop_component import create_popup

dash.register_page(__name__, path='/sign_in')

def layout():
    # Create the sign-in form content without duplicating title
    signin_form = html.Div([
        # Input fields
        dcc.Input(
            type="text",
            placeholder="User Name/Email Id",
            className="form-input",
            style={
                "width": "90%",
                "margin-left": "auto",
                "margin-right": "auto",
                "display": "block"
            }
        ),
        dcc.Input(
            type="password",
            placeholder="Password",
            className="form-input",
            style={
                "width": "90%", 
                "margin-left": "auto",
                "margin-right": "auto",
                "display": "block"
            }
        ),
        
        # Submit button - centered
        html.Div(
            html.Button(
                "Submit", 
                id="signin-button", 
                className="form-button",
                style={
                    "margin": "15px auto",
                    "display": "block"
                }
            ),
            style={
                "display": "flex",
                "justifyContent": "center",
                "width": "100%"
            }
        ),
        
        # Sign up link
        html.Div(
            children=[
                "Don't have an account? ",
                html.A("Sign up here.", href="/sign_up", className="form-footer-link")
            ],
            className="popup-footer-text",
            style={
                "marginTop": "15px", 
                "fontSize": "0.9rem",
                "textAlign": "center"
            }
        )
    ])
    
    # Use our popup component with an empty buttons_config
    return create_popup(
        title="Sign In",
        message_content=signin_form,
        buttons_config={},
        additional_content=None
    )