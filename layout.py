import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

def create_layout(stock_options):
    return html.Div([
        dbc.Navbar(
            dbc.Container([
                html.A("RRambo, the algo trader", className="navbar-brand text-white"),
                dbc.Nav([dbc.NavItem(dbc.NavLink("Home", href="#", className="text-white")),
                         dbc.NavItem(dbc.NavLink("Market Data", href="#", className="text-white")),
                         dbc.NavItem(dbc.NavLink("Portfolio", href="#", className="text-white"))],
                        className="ms-auto")
            ]),
            color="primary", dark=True, className="mb-3"
        ),
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Label("Select Stock"),
                    dcc.Dropdown(
                        id='stock-dropdown',
                        options=stock_options,
                        value=stock_options[0]['value'] if stock_options else None,
                        clearable=False,
                        className="mb-3"
                    ),
                    html.Div(id='stock-info', className="p-3 border rounded bg-light")
                ], width=3, className="bg-secondary p-3 text-white rounded"),
                dbc.Col([
                    dcc.Tabs(id='tabs', value='historical', children=[
                        dcc.Tab(label='Historical Data', value='historical', className="small-tab"),
                        dcc.Tab(label='Live Data', value='live', className="small-tab")
                    ], className="custom-tabs"),
                    dcc.Loading(dcc.Graph(id='market-graph'), type='circle')
                ], width=9)
            ])
        ])
    ])