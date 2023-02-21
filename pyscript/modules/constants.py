ASSET_COLOR_THRESHOLD = 10.0
ASSET_ACTIVE_THRESHOLD = 5.0

STOCKS_CONFIG = {
    "row_1": {
        "symbol": "spy",
        "icon": "mdi:bank",
        "public": {
            "price": False,
            "price_prec": 0,
            "cents": False,
            "change": True,
            "change_prec": 2,
        },
        "private": {
            "price": True,
            "price_prec": 2,
            "cents": False,
            "change": False,
            "change_prec": 0,
        },
    },
    "row_2": {
        "symbol": "googl",
        "icon": "mdi:google",
        "public": {
            "price": True,
            "price_prec": 0,
            "cents": False,
            "change": True,
            "change_prec": 0,
        },
        "private": {
            "price": True,
            "price_prec": 2,
            "cents": False,
            "change": False,
            "change_prec": 0,
        },
    },
    "row_3": {
        "symbol": "astr",
        "icon": "mdi:rocket-launch",
        "public": {
            "price": True,
            "price_prec": 2,
            "cents": False,
            "change": True,
            "change_prec": 0,
        },
        "private": {
            "price": True,
            "price_prec": 2,
            "cents": False,
            "change": False,
            "change_prec": 0,
        },
    },
}

CRYPTO_DISPLAY_SYMBOLS = {"row_1": "btc", "row_2": "eth", "row_3": "vet"}
CRYPTO_DISPLAY_ICONS = {
    "row_1": "mdi:bitcoin",
    "row_2": "mdi:ethereum",
    "row_3": "mdi:cosine-wave",
}
