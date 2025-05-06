# src/frontend/pages/orders.py

import dash
from dash import html, dcc, callback, Input, Output, State

from src.frontend.components.popup_component import create_popup

dash.register_page(__name__, path='/orders')

def layout():
    # Return a div that will be filled by the callback
    return html.Div(id='orders-content')

@callback(
    Output('orders-content', 'children'),
    Input('url', 'pathname'),
    State('auth-store', 'data')
)
def render_orders_content(pathname, auth_data):
    # Check if user is authenticated
    is_authenticated = auth_data and auth_data.get('authenticated', False)
    
    if not is_authenticated:
        # Return authentication required popup using the same approach as sign_out.py
        return create_popup(
            title="Authentication Required",
            message_content="You need to log in to place orders and monitor trades.",
            buttons_config={"Sign In": "/sign_in", "Return to Home": "/"}
        )
    
    # If authenticated, show the actual orders page content
    return html.Div([
        html.H1("Orders", className="page-title"),
        html.Div("Welcome to your orders dashboard. Here you can place and monitor your trading orders."),
        
        # Orders content goes here
        html.Div([
            # Order form
            html.Div([
                html.H3("Place New Order"),
                html.Div([
                    html.Label("Symbol"),
                    dcc.Input(id="order-symbol", type="text", placeholder="e.g., AAPL")
                ], className="form-group"),
                
                html.Div([
                    html.Label("Order Type"),
                    dcc.Dropdown(
                        id="order-type",
                        options=[
                            {"label": "Market", "value": "market"},
                            {"label": "Limit", "value": "limit"},
                            {"label": "Stop", "value": "stop"}
                        ],
                        value="market"
                    )
                ], className="form-group"),
                
                html.Div([
                    html.Label("Side"),
                    dcc.RadioItems(
                        id="order-side",
                        options=[
                            {"label": "Buy", "value": "buy"},
                            {"label": "Sell", "value": "sell"}
                        ],
                        value="buy",
                        inline=True
                    )
                ], className="form-group"),
                
                html.Div([
                    html.Label("Quantity"),
                    dcc.Input(id="order-quantity", type="number", min=0, step=1)
                ], className="form-group"),
                
                html.Button("Place Order", id="submit-order", className="form-button")
            ], className="order-form"),
            
            # Order history
            html.Div([
                html.H3("Recent Orders"),
                html.Div(id="orders-table", children=[
                    # This will be populated by a callback in a real app
                    html.P("No recent orders to display.")
                ])
            ], className="order-history")
        ], className="orders-container")
    ], className="page-container")