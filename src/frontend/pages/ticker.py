# pages/ticker.py
from dash import dash_table, dcc
import dash
from dash.dependencies import Output, Input
import requests

dash.register_page(__name__, path='/ticker')

def layout():
    return html.Div([
        html.H3("Live Ticker Data"),
        dash_table.DataTable(
            id='ticks-table',
            columns=[
                {"name": "Instrument Token", "id": "instrument_token"},
                {"name": "Last Price", "id": "last_price"},
                {"name": "Timestamp", "id": "timestamp"}
            ],
            data=[],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'},
            style_header={
                'backgroundColor': '#1e1e2f',
                'color': 'white',
                'fontWeight': 'bold'
            }
        ),
        dcc.Interval(id='interval-component', interval=1000, n_intervals=0)
    ])

@dash.callback(
    Output('ticks-table', 'data'),
    Input('interval-component', 'n_intervals')
)
def update_ticks_callback(n):
    try:
        response = requests.get('http://127.0.0.1:5000/get_ticks')
        response.raise_for_status()
        data = response.json()
        return data if data else []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching ticks: {e}")
        return []