import dash
from dash import html
from src.frontend.components.pop_component import create_popup

dash.register_page(__name__, path='/sign_out')

def layout():
    # Simple usage with just a text message
    return create_popup(
        title="Sign Out Status",
        message_content="You are signed out, will not be able place and monitor trades.",
        buttons_config={"Return to Sign In": "/sign_in"}
    )