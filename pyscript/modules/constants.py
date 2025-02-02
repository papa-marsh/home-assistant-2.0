NOTI_SOUND = "3rdParty_Failure_Haptic.caf"
NOTI_CRIT_SOUND = "3rd_party_critical.caf"

BASE_FILE_PATH = "/config/pyscript/files/"

TESS_LOW_THRESHOLD = 30

NEST_DISPLAYS = [
    "media_player.office_display",
    "media_player.living_room_display",
    "media_player.kitchen_display",
]

MAIN_FLOOR_SPEAKERS = [
    "media_player.living_room",
    "media_player.craft_room",
    "media_player.front_room",
]

ALL_SPEAKERS = [
    *MAIN_FLOOR_SPEAKERS,
    "media_player.basement",
    "media_player.office",
]

ASSET_COLOR_THRESHOLD = 10.0
ASSET_ACTIVE_THRESHOLD = 5.0

STOCKS_CONFIG = {
    "row_1": {
        "symbol": "net",
        "icon": "mdi:cloud",
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
    "row_2": {
        "symbol": "goog",
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
        "symbol": "aapl",
        "icon": "mdi:apple",
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
}

CRYPTO_CONFIG = {
    "row_1": {
        "symbol": "btc",
        "icon": "mdi:bitcoin",
        "public": {
            "price": True,
            "price_prec": 0,
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
