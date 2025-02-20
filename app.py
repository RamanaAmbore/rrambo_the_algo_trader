import pandas as pd
import dash
from dash import dcc, html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from kiteconnect import KiteConnect
from utils.config_loader import secrets, constants
from utils.logger import logger

# Load credentials from secrets.yaml
API_KEY = secrets["zerodha"]["api_key"]
API_SECRET = secrets["zerodha"]["api_secret"]

# Load settings from constants.yaml
INSTRUMENT_TOKEN = constants["market"]["instrument_token"]
DATA_FETCH_INTERVAL = constants["market"]["data_fetch_interval"]

# Initialize KiteConnect
kite = KiteConnect(api_key=API_KEY)

# Initialize Dash app
app = dash.Dash(__name__)

# Define layout
app.layout = html.Div([
    html.H1("Indian Stock Market - Live Chart", style={'textAlign': 'center'}),

    # Auto-refresh interval (from YAML)
    dcc.Interval(id='interval-component', interval=DATA_FETCH_INTERVAL * 1000, n_intervals=0),

    # Graph for candlestick chart
    dcc.Graph(id='candlestick-chart'),

    html.Div(f"Data updates every {DATA_FETCH_INTERVAL} seconds", style={'textAlign': 'center', 'marginTop': '10px'})
])


# Function to fetch stock market data
def fetch_live_data():
    try:
        to_date = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        from_date = (pd.Timestamp.now() - pd.Timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')

        historical_data = kite.historical_data(INSTRUMENT_TOKEN, from_date, to_date, "5minute")
        df = pd.DataFrame(historical_data)
        logger.info("Fetched market data successfully")
        return df
    except Exception as e:
        logger.error(f"Error fetching market data: {e}")
        return pd.DataFrame()


# Callback function to update chart
@app.callback(
    Output('candlestick-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_chart(n_intervals):
    df = fetch_live_data()

    if df.empty:
        logger.warning("Received empty market data")
        return go.Figure()

    fig = go.Figure(data=[go.Candlestick(
        x=df['date'], open=df['open'], high=df['high'], low=df['low'], close=df['close']
    )])

    fig.update_layout(title="Live Stock Chart", xaxis_title="Time", yaxis_title="Price",
                      xaxis_rangeslider_visible=False)
    return fig


# Run on localhost
if __name__ == '__main__':
    logger.info("Starting Dash app on localhost")
    app.run_server(debug=True, host="127.0.0.1", port=8050)

