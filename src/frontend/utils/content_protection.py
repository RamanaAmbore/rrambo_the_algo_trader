from dash import html
from src.frontend.components.popup_component import create_popup

def protected_page_content(pathname, auth_data):
    """
    Helper function to generate content for protected pages
    
    Args:
        pathname: The current path
        auth_data: Authentication data from the auth store
        
    Returns:
        A popup component if access is denied, otherwise None to render the normal content
    """
    is_authenticated = auth_data and auth_data.get('authenticated', False)
    
    if not is_authenticated and pathname in ['/orders', '/trades', '/dashboard']:
        # Return a popup for unauthenticated users
        return create_popup(
            title="Authentication Required",
            message_content=html.Div([
                "You need to log in to place orders and monitor trades.",
                html.Br(),
                html.Br(),
                "Please sign in to access this feature."
            ], style={'textAlign': 'center'}),
            buttons_config={"Sign In": "/sign_in", "Return to Home": "/"},
            additional_content=None
        )
    
    # For authenticated users, return None to render the normal page content
    return None