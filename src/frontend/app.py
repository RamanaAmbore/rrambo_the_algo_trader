import dash
from dash import dcc, html, dash_table
import requests
import pandas as pd
from dash.dependencies import Input, Output

index_string = '''
<!DOCTYPE html>
<html>
 <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>rambo-the-algo</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                margin: 0;
                font-family: 'Arial', sans-serif; /* More professional font */
                background-color: #ffffff;
                color: #333333;
            }

            .navbar {
                background-color: #f0f1f1;
                padding: 10px 15px; /* Reduced horizontal padding */
                color: #333333;
                display: flex;
                align-items: center;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                border-bottom: 1px solid #f0f1f1;
                flex-direction: row;
            }

            .navbar img {
                height: 45px;
                margin-right: 10px; /* Reduced margin-right */
            }

            .nav-links {
                display: flex;
                gap: 12px; /* Reduced gap */
                margin-left: auto;
            }

            .nav-links a {
                color: #333333;
                text-decoration: none;
                font-weight: 500;
                padding: 6px 10px; /* Slightly reduced padding */
                border-radius: 4px;
                transition: background-color 0.2s ease;
                display: flex;
                align-items: center;
                gap: 6px; /* Reduced gap */
                font-size: 0.9em; /* Reduced font size */
            }

            .nav-links a:hover {
                background-color: #d0d0d0;
            }

            .nav-links a.active {
                background-color: #308ac7;
                color: #ffffff;
            }

            .nav-links a img {
                width: 20px;
                height: 20px;
            }

            th {
                background-color: #f6f7f7 !important;
                color: #333333 !important;
                font-weight: 600;
                padding: 8px 10px;
                border: 1px solid #f0f1f1 !important;
            }

            td {
                border: 1px solid #f0f1f1 !important;
                padding: 6px 10px;
            }

            table {
                border: 1px solid #f0f1f1 !important;
                border-collapse: collapse;
            }

            #loader-wrapper {
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
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
                color: #333333;
                font-size: 2em;
                font-weight: bold;
                text-shadow: 1px 1px 4px rgba(255, 255, 255, 0.8);
                z-index: 10000;
            }

            footer {
                position: fixed;
                bottom: 0;
                width: 100%;
                background-color: #f0f1f1;
                padding: 6px 16px;
                text-align: center;
                font-size: 0.8em;
                color: #555;
                box-shadow: 0 -1px 4px rgba(0, 0, 0, 0.1);
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 6px;
                z-index: 1000;
            }

            footer img {
                width: 30px;
                height: 30px;
                border-radius: 50%;
                object-fit: cover;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
            }
            .hidden {
                display: none;
            }

            .page-content {
                padding: 20px;
                margin-bottom: 40px;
            }

        </style>
    </head>
    <body>
        <div id="loader-wrapper">
            <img src="/assets/loading.gif" alt="Loading...">
            <div id="loader-text">Loading...</div>
        </div>

        <div class="navbar">
            <img src="assets/logo.png" alt="Rambo Logo">
<div class="nav-links">
    <a href="#" data-page="watchlist">
        <img src="https://cdn-icons-png.freepik.com/256/6410/6410297.png?ga=GA1.1.1753840782.1745663557&semt=ais_hybrid" alt="Market" width="20" height="20"> Market
    </a>
    <a href="#" data-page="watchlist">
        <img src="https://cdn-icons-png.freepik.com/256/15597/15597823.png?ga=GA1.1.1753840782.1745663557&semt=ais_hybrid" alt="Watchlist" width="20" height="20"> Watchlist
    </a>
    <a href="#" data-page="holdings">
        <img src="https://cdn-icons-png.freepik.com/256/17063/17063555.png?ga=GA1.1.1753840782.1745663557&semt=ais_hybrid" alt="Holdings" width="20" height="20"> Holdings
    </a>
    <a href="#" data-page="positions">
        <img src="https://cdn-icons-png.freepik.com/256/16136/16136534.png?ga=GA1.1.1753840782.1745663557&semt=ais_hybrid" alt="Positions" width="20" height="20"> Positions
    </a>
    <a href="#" data-page="trades">
        <img src="https://cdn-icons-png.freepik.com/256/8155/8155692.png?ga=GA1.1.1753840782.1745663557&semt=ais_hybrid" alt="Trades" width="20" height="20"> Trades
    </a>
    <a href="#" data-page="orders">
        <img src="https://cdn-icons-png.freepik.com/256/9154/9154980.png?ga=GA1.1.1753840782.1745663557&semt=ais_hybrid" alt="Orders" width="20" height="20"> Orders
    </a>
    <a href="#" data-page="ticker">
        <img src="https://cdn-icons-png.freepik.com/256/2254/2254981.png?ga=GA1.1.1753840782.1745663557&semt=ais_hybrid" alt="Ticker" width="20" height="20"> Ticker
    </a>
    <a href="#" data-page="system-logs">
        <img src="https://cdn-icons-png.freepik.com/256/3924/3924724.png?ga=GA1.1.1753840782.1745663557&semt=ais_hybrid" alt="System Logs" width="20" height="20"> Logs
    </a>
    <a href="#" data-page="settings">
        <img src="https://cdn-icons-png.freepik.com/256/4031/4031425.png?ga=GA1.1.1753840782.1745663557&semt=ais_hybrid" alt="Settings" width="20" height="20"> Settings
    </a>
</div>

        </div>

        <div id="react-entry-point">
            {%app_entry%}
        </div>
        <div class="page-content" id="main-content">
             <div id="default-page" >
                <h1>Welcome to rambo-the-algo</h1>
                <p>Select a section from the navigation bar to view data.</p>
            </div>
            <div id="ticker-content" class="hidden">
                <dash_table.DataTable(
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
                )
                <dcc.Interval(id='interval-component', interval=5000, n_intervals=0)
            </div>
            <div id="system-logs-content" class="hidden">
                <h3>System Logs</h3>
                <pre id='logs-content' style='whiteSpace: pre-wrap; background-color: #f9f9f9; padding: 10px;'></pre>
            </div>
            <div id="watchlist-content" class="hidden">
                 <h1>Watchlist</h1>
                 <p>Content for Watchlist.</p>
            </div>
            <div id="holdings-content" class="hidden">
                <h1>Holdings</h1>
                <p>Content for Holdings.</p>
            </div>
            <div id="positions-content" class="hidden">
                <h1>Positions</h1>
                <p>Content for Positions.</p>
            </div>
             <div id="trades-content" class="hidden">
                <h1>Trades</h1>
                <p>Content for Trades.</p>
            </div>
            <div id="orders-content" class="hidden">
                <h1>Orders</h1>
                <p>Content for Orders.</p>
            </div>
            <div id="settings-content" class="hidden">
                <h1>Settings</h1>
                <p>Content for Settings.</p>
            </div>
        </div>

        <footer>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span>© 2025 Ramana Ambore, FRM, CFA Level 3 Candidate</span>
                <img src="/assets/ramana.jpg" alt="Ramana Ambore" />
            </div>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>

        <script>
            window.addEventListener('load', function () {
                setTimeout(function () {
                    const loader = document.getElementById('loader-wrapper');
                    if (loader) loader.style.display = 'none';
                     document.querySelector('[data-page="ticker"]').classList.add('active');
                    showPage('ticker');
                }, 2000);
                document.querySelectorAll('.nav-links a').forEach(link => {
                    link.addEventListener('click', function() {
                        document.querySelectorAll('.nav-links a').forEach(a => a.classList.remove('active'));
                        this.classList.add('active');
                        const page = this.dataset.page;
                        showPage(page);
                    });
                });
            });

            function showPage(page) {
                document.querySelectorAll('.page-content > div').forEach(div => div.classList.add('hidden'));
                const pageContent = document.getElementById(page + '-content');
                if (pageContent) {
                    pageContent.classList.remove('hidden');
                }
                 if (page === 'ticker') {
                    updateTicks();
                } else if (page === 'system-logs') {
                    updateLogs();
                }
            }

            function updateTicks() {
                fetch('http://127.0.0.1:5000/get_ticks')
                .then(response => response.json())
                .then(data => {
                    if (data && data.length > 0) {
                        Dash.updateData(
                            'ticks-table',
                            data
                        );
                    }
                })
                .catch(error => console.error('Error fetching ticks:', error));
            }

           function updateLogs() {
                fetch('http://127.0.0.1:5000/get_logs')
                    .then(response => response.text())
                    .then(text => {
                        document.getElementById('logs-content').textContent = text;
                    })
                    .catch(error => console.error('Error fetching logs:', error));
            }

        </script>
    </body>
</html>
'''

app = dash.Dash(__name__, title="rambo-the-algo", assets_folder='./assets', suppress_callback_exceptions=True)
app._favicon = "favicon.ico"
app.index_string = index_string


@app.callback(
    Output('ticks-table', 'data'),
    Input('interval-component', 'n_intervals')
)
def update_ticks_callback(n):
    # This callback will not be used, the data is updated directly by javascript.
    return []

if __name__ == '__main__':
    app.run_server(debug=True)
