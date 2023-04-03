NOTI_SOUND = "3rdParty_Failure_Haptic.caf"
NOTI_CRIT_SOUND = "3rd_party_critical.caf"

BASE_FILE_PATH = "/config/pyscript/files/"

SPEAKER_GROUP = [
    "media_player.basement",
    "media_player.living_room",
    "media_player.craft_room",
    "media_player.front_room",
]

SOCCER_CRESTS = [
    "Arsenal",
    "Aston Villa",
    "Bournemouth",
    "Brentford",
    "Brighton and Hove Albion",
    "Burnley",
    "Chelsea",
    "Crystal Palace",
    "Everton",
    "Fulham",
    "Leeds United",
    "Leicester City",
    "Liverpool",
    "Manchester City",
    "Manchester United",
    "Newcastle United",
    "Norwich City",
    "Nottingham Forest",
    "Southampton",
    "Tottenham Hotspur",
    "Watford",
    "West Ham United",
    "Wolverhampton Wanderers",
]

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
            "price_prec": 3,
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
