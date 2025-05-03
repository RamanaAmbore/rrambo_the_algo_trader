from dash import html, dcc, Input, Output
import dash
from src.frontend.settings.config import NAV_LINKS

class HeaderComponent:
    @staticmethod
    def create():
        return html.Div([
            dcc.Location(id='url', refresh=False),

            html.Div([
                html.Div("\u2630", className="hamburger-icon", id="hamburger-icon"),  # Hamburger icon
                html.Div(
                    className='navbar',  # Sidebar navbar
                    id='navbar',
                    children=[
                        html.Img(src="assets/logo1.png", alt="Rambo Logo"),
                        html.Div(
                            className='nav-links',
                            id='nav-links',
                            children=[
                                dcc.Link(
                                    html.Div(text, id={'type': 'nav-link', 'index': href}),
                                    href=href,
                                    className="nav-link"
                                )
                                for text, href in NAV_LINKS
                            ]
                        )
                    ]
                )
            ], className="sidebar-wrapper")
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
            Output('navbar', 'className'),
            Input('hamburger-icon', 'n_clicks'),
            prevent_initial_call=True
        )
        def toggle_navbar(n):
            return 'navbar show' if n % 2 != 0 else 'navbar'