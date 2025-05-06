import dash
from dash import html, dcc
from src.frontend.components.popup_component import create_popup

dash.register_page(__name__, path='/sign_in')


def layout():
    # Create the sign-in form content
    signin_form = html.Div([
        # Status message for feedback
        html.Div(id='signin-message', className='auth-message'),

        # Input fields
        dcc.Input(
            id='username-input',
            type="text",
            placeholder="User Name/Email Id",
            className="form-input"
        ),
        dcc.Input(
            id='password-input',
            type="password",
            placeholder="Password",
            className="form-input"
        ),

        # Hidden remember-me input with default value
        html.Div(
            dcc.Input(
                id='remember-me',
                type="hidden",
                value="remember"
            ),
            style={'display': 'none'}
        ),

        # Footer with sign-up link
        html.Div(
            children=[
                "Don't have an account? ",
                dcc.Link("Sign up here.", href="/sign_up", className="form-footer-link")
            ],
            className="popup-footer-text"
        )
    ])

    # Use popup component with a callback button
    return create_popup(
        title="Sign In",
        message_content=signin_form,
        buttons_config={
            "Submit": {
                "type": "callback",
                "id": "signin-submit"
            }
        }
    )