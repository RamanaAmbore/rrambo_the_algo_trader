import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import os

# Update log file path
LOG_FILE_PATH = "../logs/debug.log"

app = dash.Dash(__name__)
app.title = "📊 Ticker Log Viewer"

app.layout = html.Div([
    html.H2("📡 Real-Time Ticker Logs", style={"textAlign": "center", "marginTop": "20px"}),

    html.Div([
        dcc.Interval(id="log-update-interval", interval=3000, n_intervals=0),
        html.Pre(id="log-output", style={
            "height": "80vh",
            "overflowY": "scroll",
            "backgroundColor": "#1e1e1e",
            "color": "#00ff88",
            "padding": "1rem",
            "borderRadius": "8px",
            "whiteSpace": "pre-wrap",
            "fontSize": "14px",
            "fontFamily": "monospace"
        })
    ], style={"margin": "2rem"}),
])


@app.callback(
    Output("log-output", "children"),
    Input("log-update-interval", "n_intervals")
)
def update_logs(n):
    if not os.path.exists(LOG_FILE_PATH):
        return "⚠️ Log file not found."

    with open(LOG_FILE_PATH, "r") as file:
        lines = file.readlines()

    # Show last N lines for performance
    recent_logs = lines[-300:]
    return "".join(recent_logs)


if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
