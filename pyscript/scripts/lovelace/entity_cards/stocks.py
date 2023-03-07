import api
import constants
import format
import secrets


@time_trigger("startup")
def persist_entity_card_stocks():
    state.persist(
        "pyscript.entity_card_stocks",
        default_value="",
        default_attributes={
            "name": "Stocks",
            "state_icon": "mdi:finance",
            "active": False,
            "blink": False,
            "private": False,
            "row_1_icon": constants.STOCKS_CONFIG["row_1"]["icon"],
            "row_1_value": "",
            "row_1_color": "default",
            "row_2_icon": constants.STOCKS_CONFIG["row_2"]["icon"],
            "row_2_value": "",
            "row_2_color": "default",
            "row_3_icon": constants.STOCKS_CONFIG["row_3"]["icon"],
            "row_3_value": "",
            "row_3_color": "default",
            "staging": {},
        },
    )


@service("lovelace.stocks_tap")
def stocks_tap():
    populate_card(not pyscript.entity_card_stocks.private)
    task.sleep(5)
    populate_card(private=False)


@service("lovelace.stocks_hold")
def stocks_hold():
    return


@service("lovelace.stocks_dtap")
def stocks_dtap():
    service.call("lovelace", "stocks_tap")
    service.call("lovelace", "crypto_tap")


@time_trigger("startup", "cron(*/5 9-17 * * 1-5)")
def stage_and_populate():
    stage_entity()
    task.sleep(5)
    populate_card(private=False)


def stage_entity():
    staging = {
        "balance": secrets.STOCKS_BALANCE,
        "spy_week": api.get_stock_week_change(symbol="SPY"),
        "total": secrets.STOCKS_BALANCE,
    }

    for symbol in secrets.STOCKS_QTY:
        quote = api.get_stock_quote(symbol=symbol)
        staging[symbol.lower()] = {
            "price": quote["current"],
            "change": quote["change"],
        }
        staging["total"] += quote["current"] * secrets.STOCKS_QTY[symbol]

    pyscript.entity_card_stocks.staging = staging


def populate_card(private=False):
    visibility = "private" if private else "public"
    active = False

    if visibility == "public":
        pyscript.entity_card_stocks = format.asset_change(
            pyscript.entity_card_stocks.staging["spy_week"], percent_formatted=True
        )
    else:
        pyscript.entity_card_stocks = format.asset_price(
            pyscript.entity_card_stocks.staging["total"], precision=0
        )

    for row in range(1, 4):
        config = constants.STOCKS_CONFIG[f"row_{row}"][visibility]
        symbol = constants.STOCKS_CONFIG[f"row_{row}"]["symbol"]
        icon = constants.STOCKS_CONFIG[f"row_{row}"]["icon"]
        staged = pyscript.entity_card_stocks.staging[symbol]
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

        state.setattr(f"pyscript.entity_card_stocks.row_{row}_value", value)
        state.setattr(f"pyscript.entity_card_stocks.row_{row}_icon", icon)
        state.setattr(f"pyscript.entity_card_stocks.row_{row}_color", color)

    pyscript.entity_card_stocks.active = active
    pyscript.entity_card_stocks.private = private
