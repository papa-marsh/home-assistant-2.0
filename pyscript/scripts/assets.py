import api
import constants
import secrets


@time_trigger("startup")
def persist_entity_card_crypto():
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


@service("pyscript.crypto_tap")
def crypto_entity_card_tap():
    crypto_populate_card(not pyscript.entity_card_crypto.private)
    task.sleep(5)
    crypto_populate_card(private=False)


@service("pyscript.crypto_hold")
def crypto_entity_card_hold():
    return


@service("pyscript.crypto_dtap")
def crypto_entity_card_dtap():
    service.call("pyscript", "stocks_tap")
    service.call("pyscript", "crypto_tap")


@time_trigger("startup", "cron(0,30 * * * *)")
def crypto_stage_and_populate():
    crypto_stage_entity()
    task.sleep(5)
    crypto_populate_card(private=False)


def crypto_stage_entity():
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


def crypto_populate_card(private=False):
    visibility = "private" if private else "public"
    active = False

    if visibility == "public":
        pyscript.entity_card_crypto = format_change(
            pyscript.entity_card_crypto.staging["btc_week"], percent_formatted=True
        )
    else:
        pyscript.entity_card_crypto = format_price(
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
            value += format_price(
                staged["price"],
                precision=config["price_prec"],
                cents=config["cents"],
                k_suffix=config["k_suffix"],
            )

        if config["price"] and config["change"]:
            value += " ("

        if config["change"]:
            value += format_change(
                staged["change"],
                precision=config["change_prec"],
                percent_formatted=True,
            )

        if config["price"] and config["change"]:
            value += ")"

        color = format_color(staged["change"], percent_formatted=True)

        state.setattr(f"pyscript.entity_card_crypto.row_{row}_value", value)
        state.setattr(f"pyscript.entity_card_crypto.row_{row}_icon", icon)
        state.setattr(f"pyscript.entity_card_crypto.row_{row}_color", color)

    pyscript.entity_card_crypto.active = active
    pyscript.entity_card_crypto.private = private


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


@service("pyscript.stocks_tap")
def stocks_entity_card_tap():
    stocks_populate_card(not pyscript.entity_card_stocks.private)
    task.sleep(5)
    stocks_populate_card(private=False)


@service("pyscript.stocks_hold")
def stocks_entity_card_hold():
    return


@service("pyscript.stocks_dtap")
def stocks_entity_card_dtap():
    service.call("pyscript", "stocks_tap")
    service.call("pyscript", "crypto_tap")


@time_trigger("startup", "cron(*/5 9-17 * * 1-5)")
def stocks_stage_and_populate():
    stocks_stage_entity()
    task.sleep(5)
    stocks_populate_card(private=False)


def stocks_stage_entity():
    try:
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

    except:
        log.error("Exception caught while staging stocks entity")


def stocks_populate_card(private=False):
    visibility = "private" if private else "public"
    active = False

    if visibility == "public":
        pyscript.entity_card_stocks = format_change(
            pyscript.entity_card_stocks.staging["spy_week"], percent_formatted=False
        )
    else:
        pyscript.entity_card_stocks = format_price(
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
            value += format_price(
                staged["price"],
                precision=config["price_prec"],
                cents=config["cents"],
                k_suffix=config["k_suffix"],
            )

        if config["price"] and config["change"]:
            value += " ("

        if config["change"]:
            value += format_change(
                staged["change"],
                precision=config["change_prec"],
                percent_formatted=True,
            )

        if config["price"] and config["change"]:
            value += ")"

        color = format_color(staged["change"], percent_formatted=True)

        state.setattr(f"pyscript.entity_card_stocks.row_{row}_value", value)
        state.setattr(f"pyscript.entity_card_stocks.row_{row}_icon", icon)
        state.setattr(f"pyscript.entity_card_stocks.row_{row}_color", color)

    pyscript.entity_card_stocks.active = active
    pyscript.entity_card_stocks.private = private


def format_price(price, precision=2, cents=False, k_suffix=False):
    price = float(price)
    if cents:
        output = f"{price*100:.{precision}f} ¢"
    else:
        if k_suffix:
            output = f"${price/1000:,.{precision}f}k"
        else:
            output = f"${price:,.{precision}f}"

    return output


def format_change(change, precision=2, percent_formatted=False):
    change = float(change)
    if not percent_formatted:
        change *= 100

    sign = "+" if change >= 0 else ""
    return f"{sign}{change:.{precision}f}%"


def format_color(change, percent_formatted=False):
    change = float(change)
    if not percent_formatted:
        change *= 100

    if change >= constants.ASSET_COLOR_THRESHOLD:
        color = "green"
    elif change <= constants.ASSET_COLOR_THRESHOLD * -1:
        color = "red"
    else:
        color = "default"

    return color
