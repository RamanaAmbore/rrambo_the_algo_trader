# --- Configuration ---
from dash import dcc, html, Output, Input


# --- Navigation Helpers ---
def generate_nav_link(href, label):
    """Generates a navigation link with a label."""
    return dcc.Link(
        html.Div(label),
        href=href,
        className="nav-link"
    )


def generate_submenu(label, submenu_items):
    """Generates a submenu with a label and a list of items."""
    return html.Div(
        className="nav-item",
        children=[
            html.Div(label,
                     className="nav-link-btn"
                     ),
            html.Ul(
                className="nav-submenu",
                children=[
                    html.Li(dcc.Link(item, href=f"/watchlist/{i + 1}", className="nav-link"))
                    for i, item in enumerate(submenu_items)
                ]
            )
        ]
    )


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
                generate_nav_link("/", "Home", ),
                generate_nav_link("/market", "Market", ),
                generate_nav_link("watchlist", "Watchlist", ),
                generate_nav_link("/holdings", "Holdings", ),
                generate_nav_link("/positions", "Positions", ),
                generate_nav_link("/orders", "Orders", ),
                generate_nav_link("/trades", "Trades", ),
                generate_nav_link("/logs", "Console", ),
                generate_nav_link("/settings", "Settings", ),
                generate_nav_link("/sign_in", "Sign In/Up", ),
                generate_nav_link("/sign_out", "Sign Out", ),
            ]
        )
    ]
)


