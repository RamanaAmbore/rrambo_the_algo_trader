# pages/auth.py
from dash import html
import dash
from dash.dependencies import Output, Input # Import Output, Input if you plan to use callbacks here.

dash.register_page(__name__, path='/auth')

def layout(pathname=None):
    """
    Layout for the authentication page (sign in, sign up, sign out).

    Args:
        pathname (str, optional): The current pathname.  Dash will provide this.
            Defaults to None.
    """
    # Inline CSS for the background style.  Using a dictionary is also valid
    # but sometimes more verbose for simple styles.  Make sure the url path is correct!
    background_style = """
        background-image: url("/assets/loading.gif") !important;
        background-size: cover;  /* cover the whole area */
        background-position: center;
        background-repeat: no-repeat;
        height: 100vh;          /* full viewport height */
        width: 100vw;           /* full viewport width */
        overflow: hidden;         /* prevent scrollbars */
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        text-align: center;
        margin: 0;
        padding: 0;
        position: fixed;       /* important for full page overlay */
        top: 0;
        left: 0;
        z-index: -1;          /* Ensure background is behind other elements */
    """

    #  Conditional content based on pathname
    if pathname == '/signin':
        content = html.Div([
            html.H1("Sign In"),
            html.P("Sign In form goes here."),
            # Add Sign In form components here (dcc.Input, dcc.Button, etc.)
        ])
    elif pathname == '/signup':
        content = html.Div([
            html.H1("Sign Up"),
            html.P("Sign Up form goes here."),
            # Add Sign Up form components
        ])
    elif pathname == '/signout':
        content = html.Div([
            html.H1("Sign Out"),
            html.P("Content for Sign Out confirmation/message goes here."),
            # Add Sign Out components
        ])
    else:
        content = html.Div([
            html.H1("Authentication"),
            html.P("Select an authentication option."),
        ])

    #  Wrap the content.  The background style is applied to a *separate* div.
    return html.Div(
        [
            html.Div(style=background_style),  # The background div
            html.Div(
                id="auth-page-content-container",
                style={
                    "position": "relative",  # So content is above the background
                    "z-index": 10,             # A higher z-index
                    "padding": "20px",       # Add padding so content is not at the edge
                    "background-color": "rgba(255, 255, 255, 0.8)",  # Optional:  Make content box semi-transparent
                    "border-radius": "10px", # Optional: rounded corners
                },
                children=content,
            ),
        ]
    )
