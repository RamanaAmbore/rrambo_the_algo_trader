# index.py or app.py

import dash
from dash import dcc, html, Input, Output, State
import requests
import pandas as pd
import layouts # Import your layout functions

# --- Initialize Dash App ---
# Make sure you have your app initialization here, e.g.:
# app = dash.Dash(__name__, suppress_callback_exceptions=True)
# server = app.server # if deploying

# --- Define Main App Layout ---
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='navbar-placeholder'), # Placeholder for the navbar (if generated dynamically)

    # --- ADD THE TICKER SCROLLER COMPONENT HERE ---
    layouts.create_ticker_scroller(), # Include the ticker scroller structure

    # --- ADD THE GLOBAL INTERVAL FOR THE TICKER SCROLLER ---
    dcc.Interval(
        id='ticker-interval-component',
        interval=5 * 1000,  # Update every 5 seconds (adjust as needed)
        n_intervals=0
    ),
    # --- END TICKER SCROLLER ADDITIONS ---

    html.Div(id='page-content', className='page-content'), # Main content area
    html.Div(id='footer-placeholder'), # Placeholder for the footer (if any)
])

# --- Callback to Update Ticker Scroller Content ---
@app.callback(
    Output('ticker-content', 'children'),
    Input('ticker-interval-component', 'n_intervals')
)
def update_ticker_scroller(n):
    try:
        # Replace with your actual API endpoint for ticker data
        response = requests.get('http://127.0.0.1:5000/get_ticks') # Or a summary endpoint
        response.raise_for_status()
        data = response.json() # Assuming it returns a list of dicts like [{"instrument_token": "...", "last_price": ...}, ...]

        if not data:
            return [html.Span("No ticker data available.")]

        # Format data into spans for the scroller
        ticker_items = []
        # --- Adjust formatting based on your needs ---
        # Example: Displaying Instrument Token and Last Price
        for item in data:
            token = item.get("instrument_token", "N/A")
            price = item.get("last_price", "N/A")
            # You might want to fetch symbol names or calculate change % here if needed
            display_text = f"{token}: {price}"
            ticker_items.append(html.Span(display_text))

        # IMPORTANT: For a seamless scroll, you might need to duplicate the items
        # depending on content width vs container width.
        # Example simple duplication:
        # return ticker_items * 3 # Repeat the list 3 times

        return ticker_items # Return the list of spans

    except requests.exceptions.RequestException as e:
        print(f"Error fetching ticker data for scroller: {e}")
        # Return error message as a span, matching expected children type
        return [html.Span(f"Error loading ticker: {e}")]
    except Exception as e:
        print(f"Error processing ticker data: {e}")
        return [html.Span("Error processing ticker data.")]


# --- Callback for the Ticker Page TABLE (if you keep layout_ticker) ---
# Note: This callback updates the DataTable on the /ticker page
@app.callback(
    Output('ticks-table', 'data'),
    Input('table-interval-component', 'n_intervals') # Use the interval from layout_ticker
)
def update_ticks_table_callback(n):
     try:
        response = requests.get('http://127.0.0.1:5000/get_ticks')
        response.raise_for_status()
        data = response.json()
        # Directly return data suitable for DataTable
        return data if data else []
     except requests.exceptions.RequestException as e:
        print(f"Error fetching ticks for table: {e}")
        return []

# --- Callback to Update Page Content based on URL ---
# (You likely have this already)
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/market':
        return layouts.layout_market()
    elif pathname == '/watchlist':
        return layouts.layout_watchlist()
    elif pathname == '/watchlist/1':
        return layouts.layout_watchlist_1()
    # ... other watchlist routes
    elif pathname == '/holdings':
        return layouts.layout_holdings()
    elif pathname == '/positions':
        return layouts.layout_positions()
    elif pathname == '/trades':
        return layouts.layout_trades()
    elif pathname == '/orders':
        return layouts.layout_orders()
    elif pathname == '/ticker': # Route for the table view
        return layouts.layout_ticker()
    elif pathname == '/settings':
        return layouts.layout_settings()
    elif pathname in ['/signin', '/signup', '/signout']:
         return layouts.layout_auth(pathname)
    #elif pathname == '/logs': # Example if you add logs page
    #    return layouts.layout_system_logs()
    elif pathname == '/': # Home page
        return layouts.layout_home()
    else:
        return '404 - Page not found'

# --- Other callbacks (Navbar, Footer, Auth, etc.) ---
# (Add your existing callbacks here)


# --- Run the app ---
# if __name__ == '__main__':
#     app.run_server(debug=True) # Add host='0.0.0.0' if needed