# pages/home.py
import dash
from dash import html

dash.register_page(__name__, path='/')

def layout():
    return html.Div(
        className="home-background",
        children=[
            html.Div(
                className="home-content",
                children=[
                    html.H1("Rambo-the-Algo - Option Strategy meets speed"),
                    html.P("This platform leverages a robust architecture, featuring a Flask backend and a responsive Dash frontend. "
                           "Real-time data is streamed via WebSocket connections, managed with asynchronous techniques to maximize efficiency. "
                           "The system employs multi-threading to handle concurrent operations, ensuring production-grade algorithmic trading capabilities."),
                    html.P("– Ramana Ambore, FRM and CFA Level 3 candidate", className="signature")
                ]
            )
        ]
    )





















