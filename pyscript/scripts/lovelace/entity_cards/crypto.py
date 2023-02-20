state.persist(
    "pyscript.entity_card_crypto",
    default_value="Unkown",
    default_attributes={
        "name": "Crypto",
        "state_icon": "mdi:currency-btc",
        "active": False,
        "blink": False,
        "row_1": {
            "icon": "mdi:bitcoin",
            "value": "Unknown",
            "color": "default",
        },
        "row_2": {
            "icon": "mdi:ethereum",
            "value": "Unknown",
            "color": "default",
        },
        "row_3": {
            "icon": "mdi:cosine-wave",
            "value": "Unknown",
            "color": "default",
        },
        "staging": {},
    },
)


@service("lovelace.crypto_tap")
def crypto_tap():
    return


@service("lovelace.crypto_hold")
def crypto_hold():
    return


@service("lovelace.crypto_dtap")
def crypto_dtap():
    return
