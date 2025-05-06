import dash
from dash import html, dcc
import uuid

def create_popup(
    title,
    message_content,
    buttons_config={},
    additional_content=None,
    popup_class="standard-popup",
    message_class="popup-message",
    id_prefix=None,
    closable=False
):
    """
    Creates a reusable popup window component with auto-generated IDs

    Parameters:
    - title (str): Title text for the popup window
    - message_content: Content to display (string or Dash component)
    - buttons_config (dict): Dictionary of buttons in format:
                             {"Label": "/path", ...} for links
                             {"Label": {"type": "callback"}, ...} for callback buttons
                             {"Label": {"type": "submit", "form": "form-id"}, ...} for form submission
    - additional_content: Optional additional content to display below the message
    - popup_class (str): Additional CSS class for the popup window for custom styling
    - message_class (str): CSS class for the message container
    - id_prefix (str): Optional prefix for all generated IDs (defaults to 'popup-{random}')
    - closable (bool): Whether to add a close button to the popup

    Returns:
    - Dash component representing the popup window with auto-generated IDs
    """
    # Generate a unique ID prefix if none provided
    if id_prefix is None:
        id_prefix = f"popup-{str(uuid.uuid4())[:8]}"

    # Component IDs
    popup_id = f"{id_prefix}-container"
    window_id = f"{id_prefix}-window"
    title_id = f"{id_prefix}-title"
    message_id = f"{id_prefix}-message"
    close_id = f"{id_prefix}-close"
    additional_id = f"{id_prefix}-additional" if additional_content else None
    buttons_container_id = f"{id_prefix}-buttons" if buttons_config else None

    # If message is just a string, wrap it in a paragraph tag
    if isinstance(message_content, str):
        message_content = html.P(message_content, className="popup-text", id=f"{id_prefix}-text")

    # Create the main message container
    message_container = html.Div(
        id=message_id,
        className=message_class,
        children=message_content
    )

    # Create additional content if provided
    additional_container = None
    if additional_content:
        additional_container = html.Div(
            id=additional_id,
            className="popup-additional-content",
            children=additional_content
        )

    # Create buttons from config dictionary
    buttons = []
    for i, (label, config) in enumerate(buttons_config.items()):
        button_id = f"{id_prefix}-button-{i}"

        if isinstance(config, str):
            # It's a link path
            buttons.append(
                html.Div(
                    dcc.Link(
                        label,
                        href=config,
                        className="popup-button",
                        refresh=False,
                        id=button_id
                    ),
                    className="popup-button-container",
                    id=f"{button_id}-container"
                )
            )
        elif isinstance(config, dict):
            if config.get("type") == "callback":
                # It's a callback button
                buttons.append(
                    html.Div(
                        html.Button(
                            label,
                            id=config.get("id", button_id),
                            className="popup-button",
                            n_clicks=0
                        ),
                        className="popup-button-container",
                        id=f"{button_id}-container"
                    )
                )
            elif config.get("type") == "submit":
                # It's a form submit button
                buttons.append(
                    html.Div(
                        html.Button(
                            label,
                            id=button_id,
                            className="popup-button popup-submit-button",
                            n_clicks=0,
                            type="submit",
                            form=config.get("form")
                        ),
                        className="popup-button-container",
                        id=f"{button_id}-container"
                    )
                )

    # Only add button container if there are buttons
    button_container = None
    if buttons:
        button_container = html.Div(
            id=buttons_container_id,
            className="popup-buttons-container",
            children=buttons
        )

    # Create title bar with optional close button
    title_children = [html.Span(title, className="popup-title-text")]

    if closable:
        title_children.append(
            html.Button(
                "×",
                id=close_id,
                className="popup-close-button",
                n_clicks=0
            )
        )

    title_bar = html.Div(
        id=title_id,
        className="popup-title-bar",
        children=title_children
    )

    # Build the popup window
    popup_children = [title_bar, message_container]

    # Add additional content if it exists
    if additional_container:
        popup_children.append(additional_container)

    # Add button container if it exists
    if button_container:
        popup_children.append(button_container)

    # Create the final popup structure
    return html.Div(
        id=popup_id,
        className="home-background",
        children=[
            html.Div(
                className="popup-container",
                children=[
                    html.Div(
                        id=window_id,
                        className=f"popup-window {popup_class}",
                        children=popup_children
                    )
                ]
            )
        ]
    )