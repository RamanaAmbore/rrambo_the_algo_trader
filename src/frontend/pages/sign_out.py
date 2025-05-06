import dash
from dash import html, dcc
from src.frontend.components.popup_component import create_popup
from src.frontend.utils.auth_utils import clear_user_session

dash.register_page(__name__, path='/sign_out')

def layout():
    # Clear the user session when the sign out page is accessed
    clear_user_session()
    
    # Create signout content
    signout_content = html.Div([
        html.P("You are signed ut, you will not be able to place or monitor trades until you sign in again."),
        
        # Hidden button to trigger sign-out callback
        html.Button("Sign Out", id="signout-btn", n_clicks=0, style={"display": "none"}),
    ])
    
    # Use popup component with buttons
    return create_popup(
        title="Sign Out",
        message_content=signout_content,
        buttons_config={
            "Sign In": "/sign_in"
        }
    )