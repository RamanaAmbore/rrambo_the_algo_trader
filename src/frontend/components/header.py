from dash import html, dcc, Input, Output, callback_context
import dash
from src.frontend.settings.config import NAV_LINKS

class HeaderComponent:
    @staticmethod
    def create():
        return html.Div([
        dcc.Location(id='url', refresh=False),

        html.Div([
            html.Div([  # Top bar: logo left, hamburger right
                html.Div(html.Img(src="assets/logo1.png", alt="Rambo Logo"), className="logo-container"),
                html.Div("\u2630", className="hamburger-icon", id="hamburger-icon")
            ], className="top-row"),

            html.Div(  # Nav links section
                id="nav-links",
                className="nav-links",
                children=[
                    dcc.Link(
                        html.Div(text, id={'type': 'nav-link', 'index': href}),
                        href=href,
                        className="nav-link"
                    )
                    for text, href in NAV_LINKS
                ]
            )
        ], className="navbar-row")
    ])

    @staticmethod
    def register_callbacks(app):
        @app.callback(
            [Output({'type': 'nav-link', 'index': href}, 'className') for text, href in NAV_LINKS],
            Input('url', 'pathname')
        )
        def update_active_links(pathname):
            return ['nav-link active' if pathname == href else 'nav-link'
                   for text, href in NAV_LINKS]

        @app.callback(
            Output('nav-links', 'className'),
            Input('hamburger-icon', 'n_clicks'),
            prevent_initial_call=True
        )
        def toggle_nav_links(n):
            triggered = callback_context.triggered
            if not triggered:
                return 'nav-links'

            current_classes = callback_context.states.get('nav-links.className', '')
            if 'show' in current_classes:
                return 'nav-links'  # Hide
            else:
                return 'nav-links show'  # Show