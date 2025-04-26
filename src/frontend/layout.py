# src/frontend/layout.py

from dash import html, dcc

layout = html.Div([
    html.Div(className="navbar", children=[
        html.Img(src="assets/logo.png"),
    ]),
    dcc.Tabs(id="tabs", value='tab-ticks', children=[
        dcc.Tab(
            label='Live Ticker Data',
            value='tab-ticks',
            className='tab-headings',
            selected_style={
                'borderTop': '4px solid #636b69',
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