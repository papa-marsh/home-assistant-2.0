import api
import constants
import format
import secrets

state.persist(
    "pyscript.entity_card_crypto",
    default_value="",
    default_attributes={
        "name": "Crypto",
        "state_icon": "mdi:currency-btc",
        "active": False,
        "blink": False,
        "private": False,
        "row_1_icon": constants.CRYPTO_DISPLAY_ICONS["row_1"],
        "row_1_value": "",
        "row_1_color": "default",
        "row_2_icon": constants.CRYPTO_DISPLAY_ICONS["row_2"],
        "row_2_value": "",
        "row_2_color": "default",
        "row_3_icon": constants.CRYPTO_DISPLAY_ICONS["row_3"],
        "row_3_value": "",
        "row_3_color": "default",
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
