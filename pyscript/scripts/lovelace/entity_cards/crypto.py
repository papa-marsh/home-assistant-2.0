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
        "row_1_icon": constants.CRYPTO_CONFIG["row_1"]["icon"],
        "row_1_value": "",
        "row_1_color": "default",
        "row_2_icon": constants.CRYPTO_CONFIG["row_2"]["icon"],
        "row_2_value": "",
        "row_2_color": "default",
        "row_3_icon": constants.CRYPTO_CONFIG["row_3"]["icon"],
        "row_3_value": "",
        "row_3_color": "default",
        "staging": {},
    },
)


@service("lovelace.crypto_tap")
def crypto_tap():
    populate_card(not pyscript.entity_card_crypto.private)
    task.sleep(5)
    populate_card(private=False)


@service("lovelace.crypto_hold")
def crypto_hold():
    return


@service("lovelace.crypto_dtap")
def crypto_dtap():
    service.call("lovelace", "stocks_tap")
    service.call("lovelace", "crypto_tap")


@time_trigger("startup", "cron(0,30 * * * *)")
def stage_and_populate():
    stage_entity()
    task.sleep(5)
    populate_card(private=False)


def stage_entity():
    response = api.get_crypto_quotes(symbols=[symbol for symbol in secrets.CRYPTO_QTY])

    staging = {
        "btc_week": response["BTC"]["change_week"],
        "total": 0,
    }

    for symbol in secrets.CRYPTO_QTY:
        quote = response[symbol]
        staging[symbol.lower()] = {
            "price": quote["price"],
            "change": quote["change_day"],
        }
        staging["total"] += quote["price"] * secrets.CRYPTO_QTY[symbol]

    pyscript.entity_card_crypto.staging = staging


def populate_card(private=False):
    visibility = "private" if private else "public"
    active = False

    if visibility == "public":
        pyscript.entity_card_crypto = format.asset_change(
            pyscript.entity_card_crypto.staging["btc_week"], percent_formatted=True
        )
    else:
        pyscript.entity_card_crypto = format.asset_price(
            pyscript.entity_card_crypto.staging["total"], precision=0
        )

    for row in range(1, 4):
        config = constants.CRYPTO_CONFIG[f"row_{row}"][visibility]
        symbol = constants.CRYPTO_CONFIG[f"row_{row}"]["symbol"]
        icon = constants.CRYPTO_CONFIG[f"row_{row}"]["icon"]
        staged = pyscript.entity_card_crypto.staging[symbol]
        value = ""

        if abs(staged["change"]) >= constants.ASSET_ACTIVE_THRESHOLD:
            active = True

        if config["price"]:
            value += format.asset_price(
                staged["price"],
                precision=config["price_prec"],
                cents=config["cents"],
                k_suffix=config["k_suffix"],
            )

        if config["price"] and config["change"]:
            value += " ("

        if config["change"]:
            value += format.asset_change(
                staged["change"],
                precision=config["change_prec"],
                percent_formatted=True,
            )

        if config["price"] and config["change"]:
            value += ")"

        color = format.asset_color(staged["change"], percent_formatted=True)

        state.setattr(f"pyscript.entity_card_crypto.row_{row}_value", value)
        state.setattr(f"pyscript.entity_card_crypto.row_{row}_icon", icon)
        state.setattr(f"pyscript.entity_card_crypto.row_{row}_color", color)

    pyscript.entity_card_crypto.active = active
    pyscript.entity_card_crypto.private = private
