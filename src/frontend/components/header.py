from dash import html, dcc
import dash
from src.frontend.settings.config import NAV_LINKS


class HeaderComponent:
    @staticmethod
    def create():
        return html.Div([
            dcc.Location(id='url', refresh=False),
            html.Div(
                className='navbar',
                children=[
                    html.Img(src="assets/logo1.png", alt="Rambo Logo"),
                    html.Div(
                        className='nav-links',
                        children=[
                            dcc.Link(
                                html.Div(
                                    link_text,
                                    id={'type': 'nav-link', 'index': href},
                                ),
                                href=href,
                                className="nav-link"
                            )
                            for link_text, href in NAV_LINKS
                        ]
                    )
                ]
            )
        ])

    @staticmethod
    def register_callbacks(app):
        @app.callback(
            [dash.Output({'type': 'nav-link', 'index': href}, 'className')
             for link_text, href in NAV_LINKS],
            dash.Input('url', 'pathname')
        )
        def update_active_links(pathname):
            return ['nav-link active' if pathname == href else 'nav-link'
                    for link_text, href in NAV_LINKS]