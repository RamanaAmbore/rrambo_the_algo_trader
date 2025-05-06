import dash
from dash import html, dcc
from src.frontend.components.popup_component import create_popup

dash.register_page(__name__, path='/sign_up')


def layout():
    # Create the sign-up form content
    signup_form = html.Div([
        # Status message for feedback
        html.Div(id='signup-message', className='auth-message'),

        # Input fields
        dcc.Input(
            id='username-input',
            type="text",
            placeholder="User Name",
            className="form-input"
        ),
        dcc.Input(
            id='email-input',
            type="email",
            placeholder="Email Address",
            className="form-input"
        ),
        dcc.Input(
            id='password-input',
            type="password",
            placeholder="Password",
            className="form-input"
        ),
        dcc.Input(
            id='confirm-password-input',
            type="password",
            placeholder="Confirm Password",
            className="form-input"
        ),

        # Hidden terms-checkbox with default value to maintain compatibility
        html.Div(
            dcc.Input(
                id='terms-checkbox',
                type="hidden",
                value="agree"
            ),
            style={'display': 'none'}
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

        # Footer with sign-in link
        html.Div(
            children=[
                "Already have an account? ",
                dcc.Link("Sign in here.", href="/sign_in", className="form-footer-link")
            ],
            className="popup-footer-text"
        )
    ])

    # Use popup component with a callback button
    return create_popup(
        title="Sign Up",
        message_content=signup_form,
        buttons_config={
            "Submit": {
                "type": "callback",
                "id": "signup-submit"
            }
        }
    )