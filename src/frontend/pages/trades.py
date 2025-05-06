# src/frontend/pages/trades.py

import dash
from dash import html, dcc, callback, Input, Output, State

from src.frontend.components.popup_component import create_popup

dash.register_page(__name__, path='/trades')

def layout():
    # Return a div that will be filled by the callback
    return html.Div(id='trades-content')

@callback(
    Output('trades-content', 'children'),
    Input('url', 'pathname'),
    State('auth-store', 'data')
)
def render_trades_content(pathname, auth_data):
    # Check if user is authenticated
    is_authenticated = auth_data and auth_data.get('authenticated', False)
    
    if not is_authenticated:
        # Return authentication required popup using the same approach as sign_out.py
        return create_popup(
            title="Authentication Required",
            message_content="You need to log in to view and monitor your trades.",
            buttons_config={"Sign In": "/sign_in", "Return to Home": "/"}
        )
    
    # If authenticated, show the actual trades page content
    return html.Div([
        html.H1("Trades", className="page-title"),
        html.Div("Welcome to your trades dashboard. Here you can monitor your completed trades."),
        
        # Trades content goes here
        html.Div([
            # Trade filters
            html.Div([
                html.H3("Filter Trades"),
                html.Div([
                    html.Label("Symbol"),
                    dcc.Input(id="trade-symbol-filter", type="text", placeholder="e.g., AAPL")
                ], className="form-group"),
                
                html.Div([
                    html.Label("Date Range"),
                    dcc.DatePickerRange(
                        id="trade-date-range",
                        start_date_placeholder_text="Start Date",
                        end_date_placeholder_text="End Date"
                    )
                ], className="form-group"),
                
                html.Button("Apply Filters", id="apply-trade-filters", className="form-button")
            ], className="trade-filters"),
            
            # Trade history
            html.Div([
                html.H3("Trade History"),
                html.Div(id="trades-table", children=[
                    # This will be populated by a callback in a real app
                    html.P("No trades to display.")
                ])
            ], className="trade-history")
        ], className="trades-container")
    ], className="page-container")