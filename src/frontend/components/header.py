from dash import html, dcc, Input, Output, callback_context
import dash
from src.frontend.settings.config import NAV_LINKS

class HeaderComponent:
    @staticmethod
    def create():
        return html.Div([
            dcc.Location(id='url', refresh=False),

            # Add overlay div for closing menu when clicking outside
            html.Div(id="menu-overlay", className="menu-overlay"),

            html.Div([
                # Logo and hamburger container (left side)
                html.Div([
                    html.Div("\u2630", className="hamburger-icon", id="hamburger-icon"),
                    html.Div(html.Img(src="assets/logo1.png", alt="Rambo Logo"), className="logo-container"),
                ], className="logo-hamburger-container"),

                # Nav items container (center aligned on large screens)
                html.Div(
                    html.Div(  # Nav items wrapper
                        id="nav-items",
                        className="nav-items",
                        children=[
                            dcc.Link(
                                html.Div(text, id={'type': 'nav-item', 'index': href}),
                                href=href,
                                className="nav-item"
                            )
                            for text, href in NAV_LINKS
                        ]
                    ),
                    className="nav-items-container"
                )
            ], className="navbar")
        ])

    @staticmethod
    def register_callbacks(app):
        @app.callback(
            [Output({'type': 'nav-item', 'index': href}, 'className') for text, href in NAV_LINKS],
            Input('url', 'pathname')
        )
        def update_active_links(pathname):
            return ['nav-item active' if pathname == href else 'nav-item'
                    for text, href in NAV_LINKS]

        @app.callback(
            [Output('nav-items', 'className'),
             Output('menu-overlay', 'className')],
            [Input('hamburger-icon', 'n_clicks'),
             Input('menu-overlay', 'n_clicks')],
            prevent_initial_call=True
        )
        def toggle_nav_links(hamburger_clicks, overlay_clicks):
            ctx = callback_context
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

            # Check current state of menu
            current_classes = ctx.states.get('nav-items.className', 'nav-items')
            is_open = 'show' in current_classes

            # If hamburger is clicked, toggle menu
            if trigger_id == 'hamburger-icon':
                if is_open:
                    return 'nav-items', 'menu-overlay'  # Hide menu and overlay
                else:
                    return 'nav-items show', 'menu-overlay show'  # Show menu and overlay

            # If overlay is clicked, always close the menu
            elif trigger_id == 'menu-overlay':
                return 'nav-items', 'menu-overlay'  # Hide menu and overlay

            # Default case (should not happen)
            return current_classes, 'menu-overlay' if is_open else 'menu-overlay'
