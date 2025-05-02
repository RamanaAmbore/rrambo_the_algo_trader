# --- Configuration ---
from dash import dcc, html

CDN_LINKS = {
    "home": "https://cdn-icons-png.freepik.com/256/8784/8784978.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid",
    "market": "https://cdn-icons-png.freepik.com/256/2254/2254981.png?ga=GA1.1.1753840782.1745663557&semt=ais_hybrid",
    "watchlist": "https://cdn-icons-png.freepik.com/256/15597/15597823.png?ga=GA1.1.1753840782.1745663557&semt=ais_hybrid",
    "holdings": "https://cdn-icons-png.freepik.com/256/17063/17063555.png?ga=GA1.1.1753840782.1745663557&semt=ais_hybrid",
    "positions": "https://cdn-icons-png.freepik.com/256/7169/7169336.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid",
    "orders": "https://cdn-icons-png.freepik.com/256/10319/10319450.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid",
    "trades": "https://cdn-icons-png.freepik.com/256/8155/8155692.png?ga=GA1.1.1753840782.1745663557&semt=ais_hybrid",
    "logs": "https://cdn-icons-png.freepik.com/256/14872/14872554.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid",
    "settings": "https://cdn-icons-png.freepik.com/256/14668/14668098.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid",
    "signin": "https://cdn-icons-png.freepik.com/256/10908/10908421.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid",
    "signout": "https://cdn-icons-png.freepik.com/256/4476/4476505.png?ga=GA1.1.707069739.1745760056&semt=ais_hybrid",
}


# --- Navigation Helpers ---
def generate_nav_link(href, label, icon_key):
    """Generates a navigation link with an icon and label."""
    return dcc.Link(
        html.Div([
            html.Img(src=CDN_LINKS[icon_key], alt=label, width="20", height="20"),
            label
        ]),
        href=href,
        className="nav-link"
    )


def generate_submenu(label, submenu_items):
    """Generates a submenu with a label and a list of items."""
    return html.Div(
        className="nav-item",
        children=[
            html.Div(
                [html.Img(src=CDN_LINKS[label], alt=label, width="20", height="20"), label],
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
                generate_submenu("watchlist", ["Watchlist 1", "Watchlist 2"]),
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
