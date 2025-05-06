import dash
from dash import html, dcc, clientside_callback, callback
from dash.dependencies import Input, Output, State
import flask

from src.frontend.components.footer import FooterComponent
from src.frontend.components.header import HeaderComponent
from src.frontend.components.ticker import TickerComponent
from src.frontend.helpers.index_string import index_string
from src.frontend.settings.config import APP_CONFIG
from src.helpers.logger import get_logger
from src.frontend.utils.auth_manager import AuthManager
from src.frontend.utils.content_protection import protected_page_content

logger = get_logger(__name__)

# Initialize server 
server = flask.Flask(__name__)
server.secret_key = APP_CONFIG.get('SECRET_KEY', 'MUDwBJY5aNTU_SF1hgYAPbB2n6mBSYggNqK8jeZwHSo=')
# Set session cookie to expire in 7 days (in seconds)
server.config['PERMANENT_SESSION_LIFETIME'] = 7 * 24 * 60 * 60

# API URL configuration
API_BASE_URL = APP_CONFIG.get('API_BASE_URL')

# Initialize components
ticker = TickerComponent()

# Initialize Dash app with Flask server
app = dash.Dash(
    __name__,
    server=server,
    use_pages=True,
    suppress_callback_exceptions=True,
    assets_folder=APP_CONFIG['ASSETS_FOLDER'],
    title=APP_CONFIG['TITLE'],
    update_title=APP_CONFIG['UPDATE_TITLE'],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
    ],
)
app.index_string = index_string
app._favicon = APP_CONFIG['FAVICON']


def create_layout():
    return html.Div([
        # Global dcc.Store for authentication state
        dcc.Store(id='auth-store', storage_type='session'),
        
        # dcc.Location for navigation
        dcc.Location(id='url', refresh=False),
        
        # Main app components
        HeaderComponent.create(),
        
        # Authentication status div (hidden)
        html.Div(id='auth-status', style={'display': 'none'}),
        
        # Protected content container
        html.Div(id='protected-content-container'),
        
        # Page container
        dash.page_container,
        
        # Other components
        ticker.create_scroller(),
        FooterComponent.create()
    ])


app.layout = create_layout()

# Register component callbacks
HeaderComponent.register_callbacks(app)

# Initialize AuthManager with our app and API URL
auth_manager = AuthManager(app, API_BASE_URL)

# Ticker update callback
@app.callback(
    Output('scrollText', 'children'),
    Input('ticker-scroll-complete', 'data'),
    prevent_initial_call=True
)
def update_ticker(_):
    return ticker.update_ticker_data()


# Clientside callback for ticker
clientside_callback(
    """
    function(dummyText) {
        return true;
    }
    """,
    Output("ticker-scroll-complete", "data"),
    Input("dummy-div", "children"),
)

# Protected content callback
@callback(
    Output('protected-content-container', 'children'),
    Input('url', 'pathname'),
    State('auth-store', 'data')
)
def render_protected_content(pathname, auth_data):
    """
    Renders protected content based on current pathname and auth status
    """
    # Use the content_protection helper to determine if we need to show a protection popup
    return protected_page_content(pathname, auth_data)

# Run the application
if __name__ == '__main__':
    app.run(debug=True, port=8050)