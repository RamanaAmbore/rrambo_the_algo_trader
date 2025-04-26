import dash
from dash import dcc, html, dash_table
import requests
from dash.dependencies import Input, Output
import pandas as pd

app = dash.Dash(__name__, title="rambo-the-algo", assets_folder='./assets', suppress_callback_exceptions=True)
app._favicon = "favicon.ico"

# Custom HTML and CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>rambo-the-algo</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                margin: 0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f4f4f9;
                color: #1e1e1e;
            }

            .navbar {
                background-color: #f8f9fa;
                padding: 12px 24px;
                color: #1e1e1e;
                display: flex;
                align-items: center;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            }

            .navbar img {
                height: 50px;
                margin-right: 16px;
            }

            .navbar span {
                font-size: 1.4em;
                font-weight: bold;
            }

            .tab-headings {
                background-color: #e5e7eb;
                padding: 10px 20px;
                border-bottom: 1px solid #d1d5db;
                font-weight: 600;
                color: #1e1e1e;
            }

            th {
                background-color: #e5e7eb !important;
                color: #1e1e1e !important;
                font-weight: 600;
                padding: 10px;
            }

            #loader-wrapper {
                position: fixed;
                top: 0; left: 0;
                width: 100vw; height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                background-color: #ffffff;
                z-index: 9999;
                flex-direction: column;
            }

            #loader-wrapper img {
                width: 100vw;
                height: 100vh;
                object-fit: fill;
                position: absolute;
                top: 0;
                left: 0;
                z-index: -1;
            }

            #loader-text {
                color: #1e1e1e;
                font-size: 2em;
                font-weight: bold;
                text-shadow: 1px 1px 4px rgba(255, 255, 255, 0.8);
                z-index: 10000;
            }

            /* Override default Dash tab highlight */
            .dash-tabs-container .tab--selected {
                border-top: 4px solid #8cbdc4 !important;
                background-color: #ffffff !important;
                color: #1e1e1e !important;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div id="loader-wrapper">
            <img src="/assets/loading.gif" alt="Loading...">
            <div id="loader-text">Loading...</div>
        </div>

        <div id="react-entry-point">
            {%app_entry%}
        </div>

        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>

        <script>
            window.addEventListener('load', function () {
                setTimeout(function () {
                    const loader = document.getElementById('loader-wrapper');
                    if (loader) loader.style.display = 'none';
                }, 2000); // 2 seconds delay
            });
        </script>
    </body>
</html>
'''

app.layout = html.Div([
    html.Div(className="navbar", children=[
        html.Img(src="assets/logo.png"),
    ]),
    dcc.Tabs(id="tabs", value='tab-ticks', children=[
        dcc.Tab(
            label='Live Ticker Data',
            value='tab-ticks',
            className='tab-headings',
            selected_style={
                'borderTop': '4px solid #102d33',
                'backgroundColor': '#ffffff',
                'color': '#1e1e1e',
                'fontWeight': 'bold'
            }
        ),
        dcc.Tab(
            label='System Logs',
            value='tab-logs',
            className='tab-headings',
            selected_style={
                'borderTop': '4px solid #1e1e1e',
                'backgroundColor': '#ffffff',
                'color': '#1e1e1e',
                'fontWeight': 'bold'
            }
        )
    ]),
    html.Div(id='tabs-content')
])

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



