import dash
from dash import dcc, html, dash_table
import requests
from dash.dependencies import Input, Output
import pandas as pd

# Initialize the Dash app
app = dash.Dash(__name__)

# Layout of the app
app.layout = html.Div([
    html.H1("Live Ticker Data"),
    html.Div([
        dash_table.DataTable(
            id='ticks-table',
            columns=[
                {"name": "Instrument Token", "id": "instrument_token"},
                {"name": "Last Price", "id": "last_price"},
                {"name": "Timestamp", "id": "timestamp"}
            ],
            data=[]  # Initially empty, will be populated dynamically
        ),
        # Interval component to refresh the data every 5 seconds (5000 ms)
        dcc.Interval(
            id='interval-component',
            interval=5000,  # Time in milliseconds, i.e., 5 seconds
            n_intervals=0  # Initial number of intervals is 0
        )
    ])
])

# Function to fetch data from the backend
def fetch_ticks():
    try:
        response = requests.get('http://127.0.0.1:5000/get_ticks')
        response.raise_for_status()
        return response.json()  # Returns the JSON data from the backend
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

# Callback to update the table dynamically
@app.callback(
    Output('ticks-table', 'data'),
    Input('interval-component', 'n_intervals')  # Trigger every time the interval elapses
)
def update_ticks_table(n):
    ticks_data = fetch_ticks()  # Get the data from the backend
    if ticks_data:
        # Convert the data to a pandas DataFrame and then to a list of dictionaries
        df = pd.DataFrame(ticks_data)
        return df.to_dict('records')  # Returns data in a format Dash can use
    else:
        return []

if __name__ == '__main__':
    app.run_server(debug=True)

