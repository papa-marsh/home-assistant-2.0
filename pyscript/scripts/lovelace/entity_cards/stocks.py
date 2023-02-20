import api
import constants
import misc
import secrets


state.persist(
    "pyscript.entity_card_stocks",
    default_value="Unkown",
    default_attributes={
        "name": "Stocks",
        "state_icon": "mdi:finance",
        "active": False,
        "blink": False,
        "row_1": {
            "icon": constants.STOCK_DISPLAY_ICONS["row_1"],
            "value": "Unknown",
            "color": "default",
        },
        "row_2": {
            "icon": constants.STOCK_DISPLAY_ICONS["row_2"],
            "value": "Unknown",
            "color": "default",
        },
        "row_3": {
            "icon": constants.STOCK_DISPLAY_ICONS["row_3"],
            "value": "Unknown",
            "color": "default",
        },
        "staging": {},
    },
)


@service("lovelace.stocks_tap")
def stocks_tap():
    return


@service("lovelace.stocks_hold")
def stocks_hold():
    return


@service("lovelace.stocks_dtap")
def stocks_dtap():
    return


# TODO parameterize row icons at the init level (also figure out way to update without init..?)


# @time(every X minutes)
def stage_entity():
    staging = {
        "balance": secrets.STOCK_BALANCE,
        "spy_week": api.get_stock_week_open(symbol="SPY"),
    }

    for symbol in secrets.STOCK_QTY:
        quote = api.get_stock_quote(symbol=symbol)
        staging[symbol.lower()] = {
            "price": quote["current"],
            "change": quote["change"],
            "qty": secrets.STOCK_QTY[symbol],
        }

    pyscript.entity_card_stocks.staging = staging
    populate_card_public()


stage_entity()


# @(tap if private)
# @(startup)
def populate_card_public():
    pyscript.entity_card_stocks.row_1["value"] = misc.format_asset_change(
        pyscript.entity_card_stocks.staging[constants.STOCK_DISPLAY_SYMBOLS["row_1"]][
            "change"
        ]
    )
    pyscript.entity_card_stocks.row_2["value"] = misc.format_asset_change(
        pyscript.entity_card_stocks.staging[constants.STOCK_DISPLAY_SYMBOLS["row_2"]][
            "change"
        ]
    )
    pyscript.entity_card_stocks.row_3["value"] = misc.format_asset_change(
        pyscript.entity_card_stocks.staging[constants.STOCK_DISPLAY_SYMBOLS["row_3"]][
            "change"
        ]
    )

    pyscript.entity_card_stocks.row_1["color"] = misc.get_asset_color(
        pyscript.entity_card_stocks.staging[constants.STOCK_DISPLAY_SYMBOLS["row_1"]][
            "change"
        ]
    )
    pyscript.entity_card_stocks.row_2["color"] = misc.get_asset_color(
        pyscript.entity_card_stocks.staging[constants.STOCK_DISPLAY_SYMBOLS["row_2"]][
            "change"
        ]
    )
    pyscript.entity_card_stocks.row_3["color"] = misc.get_asset_color(
        pyscript.entity_card_stocks.staging[constants.STOCK_DISPLAY_SYMBOLS["row_3"]][
            "change"
        ]
    )


# @(tap if public)
# @(double tap for stocks & crypto?)
# @(unique threading)
def populate_card_private():
    pyscript.entity_card_stocks.row_1["value"] = misc.format_asset_price(
        pyscript.entity_card_stocks.staging[constants.STOCK_DISPLAY_SYMBOLS["row_1"]][
            "price"
        ]
    )

    pyscript.entity_card_stocks.row_2["value"] = misc.format_asset_price(
        pyscript.entity_card_stocks.staging[constants.STOCK_DISPLAY_SYMBOLS["row_2"]][
            "price"
        ]
    )

    pyscript.entity_card_stocks.row_3["value"] = misc.format_asset_price(
        pyscript.entity_card_stocks.staging[constants.STOCK_DISPLAY_SYMBOLS["row_3"]][
            "price"
        ]
    )

    pyscript.entity_card_stocks.row_1["icon"] = constants.STOCK_DISPLAY_ICONS["row_1"]
    pyscript.entity_card_stocks.row_2["icon"] = constants.STOCK_DISPLAY_ICONS["row_2"]
    pyscript.entity_card_stocks.row_3["icon"] = constants.STOCK_DISPLAY_ICONS["row_3"]
