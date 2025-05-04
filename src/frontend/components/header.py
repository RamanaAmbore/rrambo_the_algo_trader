from dash import html, dcc, Input, Output, callback_context
import dash
from src.frontend.settings.config import NAV_LINKS

class HeaderComponent:
    @staticmethod
    def create():
        return html.Div([
            dcc.Location(id='url', refresh=False),

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
            Output('nav-items', 'className'),
            Input('hamburger-icon', 'n_clicks'),
            prevent_initial_call=True
        )
        def toggle_nav_links(n):
            triggered = callback_context.triggered
            if not triggered:
                return 'nav-items'

            current_classes = callback_context.states.get('nav-items.className', '')
            if 'show' in current_classes:
                return 'nav-items'  # Hide
            else:
                return 'nav-items show'  # Show