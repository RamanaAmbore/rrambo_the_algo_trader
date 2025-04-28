import dash
from dash import html, dcc

dash.register_page(__name__, path='/sign_in')


def layout():
    # Background style for the page
    background_style = {
        "backgroundImage": 'url("/assets/loading.gif")',
        "backgroundSize": "cover",  # cover the whole area
        "backgroundPosition": "center",
        "backgroundRepeat": "no-repeat",
        "height": "100vh",  # full viewport height
        "width": "100vw",  # full viewport width
        "overflow": "hidden",  # prevent scrollbars
        "position": "fixed",  # fix background to viewport
        "top": "0",
        "left": "0",
        "zIndex": "-1"  # Ensure background is behind other elements
    }

    # Modal styling
    modal_style = {
        "position": "fixed",
        "top": "50%",
        "left": "50%",
        "transform": "translate(-50%, -50%)",
        "backgroundColor": "white",
        "padding": "20px",
        "boxShadow": "0px 4px 6px rgba(0, 0, 0, 0.1)",
        "zIndex": "1000",
        "display": "none"  # Initially hidden
    }

    # Modal background overlay
    overlay_style = {
        "position": "fixed",
        "top": "0",
        "left": "0",
        "width": "100vw",
        "height": "100vh",
        "backgroundColor": "rgba(0, 0, 0, 0.5)",
        "zIndex": "999",  # Overlay layer
        "display": "none"  # Initially hidden
    }

    return html.Div([
        # Background style
        html.Div(style=background_style),

        # Modal overlay (darkened background)
        html.Div(id="modal-overlay", style=overlay_style),

        # Modal window content
        html.Div(id="signin-modal", style=modal_style, children=[
            html.H2("Sign In"),
            dcc.Input(id="username", placeholder="Username", type="text", className="form-control mb-3"),
            dcc.Input(id="password", placeholder="Password", type="password", className="form-control mb-3"),
            html.Button("Sign In", id="sign-in-button", className="btn btn-success w-100"),
            html.Div(id="sign-in-message", className="mt-3"),
            html.P("Don't have an account?"),
            dcc.Link("Sign Up", href="/sign-up", className="btn btn-link"),
            html.Button("Close", id="close-modal", className="btn btn-danger")
        ]),

        # Button to trigger the modal (can be hidden or shown as needed)
        html.Button("Sign In", id="open-signin-modal", className="btn btn-primary"),

        # JavaScript to handle modal open/close logic
        html.Script("""
            // Show the modal when the 'Sign In' button is clicked
            document.getElementById('open-signin-modal').addEventListener('click', function() {
                document.getElementById('signin-modal').style.display = 'block';
                document.getElementById('modal-overlay').style.display = 'block';
            });

            // Close the modal when the 'Close' button is clicked
            document.getElementById('close-modal').addEventListener('click', function() {
                document.getElementById('signin-modal').style.display = 'none';
                document.getElementById('modal-overlay').style.display = 'none';
            });

            // Close the modal when the overlay is clicked
            document.getElementById('modal-overlay').addEventListener('click', function() {
                document.getElementById('signin-modal').style.display = 'none';
                document.getElementById('modal-overlay').style.display = 'none';
            });
        """)
    ])
