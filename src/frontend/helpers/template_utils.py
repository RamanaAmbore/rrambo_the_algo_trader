# --- Configuration ---
from dash import dcc, html




# --- Navigation Helpers ---
def generate_nav_link(href, label, icon_key):
    """Generates a navigation link with an icon and label."""
    return dcc.Link(
        html.Div(
            label
        ),
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
                generate_nav_link("/", "Home", "home"),
                generate_nav_link("/market", "Market", "market"),
                generate_nav_link("watchlist", "Watchlist","watchlist"),
                generate_nav_link("/holdings", "Holdings", "holdings"),
                generate_nav_link("/positions", "Positions", "positions"),
                generate_nav_link("/orders", "Orders", "orders"),
                generate_nav_link("/trades", "Trades", "trades"),
                generate_nav_link("/logs", "Console", "logs"),
                generate_nav_link("/settings", "Settings", "settings"),
            ]
        ),
        html.Div(
            className='nav-links auth-links',
            children=[
                generate_nav_link("/sign_in", "Sign In/Up", "signin"),
                generate_nav_link("/sign_out", "Sign Out", "signout"),
            ]
        )
    ]
)
