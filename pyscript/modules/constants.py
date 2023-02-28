ASSET_COLOR_THRESHOLD = 10.0
ASSET_ACTIVE_THRESHOLD = 5.0

NOTI_SOUND = "3rdParty_Failure_Haptic.caf"
NOTI_CRIT_SOUND = "3rd_party_critical.caf"

STOCKS_CONFIG = {
    "row_1": {
        "symbol": "spy",
        "icon": "mdi:bank",
        "public": {
            "price": False,
            "price_prec": 0,
            "cents": False,
            "k_suffix": False,
            "change": True,
            "change_prec": 2,
        },
        "private": {
            "price": True,
            "price_prec": 2,
            "cents": False,
            "k_suffix": False,
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
            "k_suffix": False,
            "change": True,
            "change_prec": 0,
        },
        "private": {
            "price": True,
            "price_prec": 2,
            "cents": False,
            "k_suffix": False,
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
            "k_suffix": False,
            "change": True,
            "change_prec": 0,
        },
        "private": {
            "price": True,
            "price_prec": 2,
            "cents": False,
            "k_suffix": False,
            "change": False,
            "change_prec": 0,
        },
    },
}

CRYPTO_CONFIG = {
    "row_1": {
        "symbol": "btc",
        "icon": "mdi:bitcoin",
        "public": {
            "price": True,
            "price_prec": 1,
            "cents": False,
            "k_suffix": True,
            "change": True,
            "change_prec": 0,
        },
        "private": {
            "price": True,
            "price_prec": 0,
            "cents": False,
            "k_suffix": False,
            "change": False,
            "change_prec": 0,
        },
    },
    "row_2": {
        "symbol": "eth",
        "icon": "mdi:ethereum",
        "public": {
            "price": True,
            "price_prec": 1,
            "cents": False,
            "k_suffix": True,
            "change": True,
            "change_prec": 0,
        },
        "private": {
            "price": True,
            "price_prec": 0,
            "cents": False,
            "k_suffix": False,
            "change": False,
            "change_prec": 0,
        },
    },
    "row_3": {
        "symbol": "vet",
        "icon": "mdi:cosine-wave",
        "public": {
            "price": True,
            "price_prec": 1,
            "cents": True,
            "k_suffix": False,
            "change": True,
            "change_prec": 0,
        },
        "private": {
            "price": True,
            "price_prec": 2,
            "cents": True,
            "k_suffix": False,
            "change": False,
            "change_prec": 0,
        },
    },
}
