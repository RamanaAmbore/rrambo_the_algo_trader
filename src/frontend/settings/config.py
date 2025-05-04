APP_CONFIG = {
    'TITLE': "Rambo, the Algo",
    'UPDATE_TITLE': 'Rambo-the-algo',
    'FAVICON': "favicon.ico",
    'ASSETS_FOLDER': './assets'
}

# Configuration Constants
TICKER_CONFIG = {
    'DURATION_PER_ITEM': 10,
    'DURATION_MULTIPLIER': 300,
    'API_URL': "http://127.0.0.1:5000/get_ticks"
}


# ... your existing config ...

NAV_LINKS = [
    ("Home", "/"),
    ("Market", "/market"),
    ("Watchlist", "/watchlist"),
    ("Holdings", "/holdings"),
    ("Positions", "/positions"),
    ("Orders", "/orders"),
    ("Trades", "/trades"),
    ("Console", "/logs"),
    ("Settings", "/settings"),
    ("Sign In/Up", "/sign_in"),
    ("Sign Out", "/sign_out")
]