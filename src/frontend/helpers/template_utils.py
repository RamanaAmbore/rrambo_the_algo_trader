# --- Configuration ---
from dash import dcc, html, Output, Input

footer = html.Footer(
    children=[
        html.Div(

            children=[
                html.Span("© 2025 Ramana Ambore, FRM, CFA Level 3 Candidate"),
                html.Img(src="/assets/ramana.jpg", alt="Ramana Ambore")
            ]
        )
    ]
)

header = html.Div(
    className='navbar',
    children=[
        html.Img(src="assets/logo1.png", alt="Rambo Logo"),
        html.Div(
            className='nav-links',
            children=[
                dcc.Link(html.Div("Home"), href="/", className="nav-link"),
                dcc.Link(html.Div("Market"), href="/market", className="nav-link"),
                dcc.Link(html.Div("Watchlist"), href="/watchlist", className="nav-link"),
                dcc.Link(html.Div("Holdings"), href="/holdings", className="nav-link"),
                dcc.Link(html.Div("Positions"), href="/positions", className="nav-link"),
                dcc.Link(html.Div("Orders"), href="/orders", className="nav-link"),
                dcc.Link(html.Div("Trades"), href="/trades", className="nav-link"),
                dcc.Link(html.Div("Console"), href="/logs", className="nav-link"),
                dcc.Link(html.Div("Settings"), href="/settings", className="nav-link"),
                dcc.Link(html.Div("Sign In/Up"), href="/sign_in", className="nav-link"),
                dcc.Link(html.Div("Sign Out"), href="/sign_out", className="nav-link"),
            ]
        )
    ]
)


