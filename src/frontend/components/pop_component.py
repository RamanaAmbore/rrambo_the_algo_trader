import dash
from dash import html, dcc

def create_popup(title, message_content, buttons_config, additional_content=None):
    """
    Creates a reusable popup window component
    
    Parameters:
    - title (str): Title text for the popup window
    - message_content: Content to display (string or Dash component)
    - buttons_config (dict): Dictionary of button labels and their paths
                            Format: {"Button Label": "/path/to/link", ...}
    - additional_content: Optional additional content to display below the message
    
    Returns:
    - Dash component representing the popup window
    """
    
    # Create buttons from config dictionary - using dcc.Link instead of html.A
    buttons = []
    for label, path in buttons_config.items():
        buttons.append(
            html.Div(
                dcc.Link(
                    label,
                    href=path,
                    className="popup-button",
                    # Set refresh=False to ensure client-side navigation
                    refresh=False
                ),
                style={"display": "flex", "justifyContent": "center", "width": "100%"}
            )
        )
    
    # Check if message_content is a string and convert to paragraph if it is
    if isinstance(message_content, str):
        message_content = html.P(message_content, className="popup-message")
    
    # Build content children list
    content_children = [message_content]
    
    # Add additional content if provided
    if additional_content:
        content_children.append(additional_content)
    
    # Add button container only if there are buttons
    if buttons:
        content_children.append(
            html.Div(
                buttons,
                className="popup-button-container",
                style={"display": "flex", "justifyContent": "center", "width": "100%"}
            )
        )
    
    # Build the popup window
    return html.Div(
        className="home-background",
        children=[
            html.Div(
                className="popup-container",
                children=[
                    html.Div(
                        className="popup-window",
                        style={"width": "400px"},  # Make width customizable if needed
                        children=[
                            # Title bar
                            html.Div(
                                className="popup-title-bar",
                                children=title
                            ),
                            # Content
                            html.Div(
                                className="popup-content",
                                children=content_children,
                                style={"textAlign": "center"}
                            )
                        ]
                    )
                ]
            )
        ]
    )