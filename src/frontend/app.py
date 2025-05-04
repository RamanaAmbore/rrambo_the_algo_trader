import dash
from dash import html, clientside_callback
from dash.dependencies import Input, Output

from src.frontend.components.footer import FooterComponent
from src.frontend.components.header import HeaderComponent
from src.frontend.components.ticker import TickerComponent
from src.frontend.helpers.index_string import index_string
from src.frontend.settings.config import APP_CONFIG
from src.helpers.logger import get_logger

logger = get_logger(__name__)

# Initialize components
ticker = TickerComponent()
app = dash.Dash(
    __name__,
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
        HeaderComponent.create(),
        dash.page_container,
        ticker.create_scroller(),
        FooterComponent.create()
    ])


app.layout = create_layout()

HeaderComponent.register_callbacks(app)

@app.callback(
    Output('scrollText', 'children'),
    Input('ticker-scroll-complete', 'data'),
    prevent_initial_call=True
)
def update_ticker(_):
    return ticker.update_ticker_data()


# Clientside callback setup remains the same
clientside_callback(
    """
    function(dummyText) {
        return true;
    }
    """,
    Output("ticker-scroll-complete", "data"),
    Input("dummy-div", "children"),
)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
