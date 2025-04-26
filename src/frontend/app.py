# src/frontend/app.py

import dash
from dash import dcc, html, dash_table
import requests
import pandas as pd
from dash.dependencies import Input, Output

from index_string import index_string
from src.frontend.layout import layout

app = dash.Dash(__name__, title="rambo-the-algo", assets_folder='./assets', suppress_callback_exceptions=True)
app._favicon = "favicon.ico"
app.index_string = index_string
app.layout = layout

def fetch_ticks():
    try:
        response = requests.get('http://127.0.0.1:5000/get_ticks')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching tick data: {e}")
        return []

def fetch_logs():
    try:
        response = requests.get('http://127.0.0.1:5000/get_logs')
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching logs: {e}")
        return "Error fetching logs."

@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-ticks':
        return html.Div([
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
            dcc.Interval(id='interval-component', interval=5000, n_intervals=0)
        ])
    elif tab == 'tab-logs':
        return html.Div([
            html.H3("Log Output"),
            html.Pre(id='logs-content', style={'whiteSpace': 'pre-wrap', 'backgroundColor': '#f9f9f9', 'padding': '10px'})
        ])

@app.callback(Output('ticks-table', 'data'),
              Input('interval-component', 'n_intervals'))
def update_ticks(n):
    ticks_data = fetch_ticks()
    return pd.DataFrame(ticks_data).to_dict('records') if ticks_data else []

@app.callback(Output('logs-content', 'children'),
              Input('tabs', 'value'))
def update_logs(tab):
    if tab == 'tab-logs':
        return fetch_logs()
    return dash.no_update

if __name__ == '__main__':
    app.run_server(debug=True)



