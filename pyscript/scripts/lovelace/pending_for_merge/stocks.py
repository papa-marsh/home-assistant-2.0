import util

# TODO add 'staging' key to pyscript.entity_card_stocks & crypto
# TODO parameterize row icons at the init level (also figure out way to update without init..?)


# @time(every X minutes)
def stage_entity():
    staging = {
        "balance": secrets.BALANCE,
        "spy_week": util.api.get_stock_week_open(symbol="SPY"),
    }

    for symbol in secrets.QTY:
        quote = util.api.get_stock_quote(symbol=symbol)
        staging[symbol.lower()] = {
            "price": quote["current"],
            "change": quote["change"],
            "qty": secrets.QTY.symbol,
        }

    pyscript.entity_card_stocks.staging = staging
    populate_card_public()


# @(tap if private)
# @(startup)
def populate_card_public():
    pyscript.entity_card_stocks.row_1["value"] = util.misc.format_asset_change(
        pyscript.entity_card_stocks.staging[
            util.constants.STOCK_DISPLAY_SYMBOLS["row_1"]
        ]["change"]
    )
    pyscript.entity_card_stocks.row_2["value"] = util.misc.format_asset_change(
        pyscript.entity_card_stocks.staging[
            util.constants.STOCK_DISPLAY_SYMBOLS["row_2"]
        ]["change"]
    )
    pyscript.entity_card_stocks.row_3["value"] = util.misc.format_asset_change(
        pyscript.entity_card_stocks.staging[
            util.constants.STOCK_DISPLAY_SYMBOLS["row_3"]
        ]["change"]
    )

    pyscript.entity_card_stocks.row_1["color"] = util.misc.get_asset_color(
        pyscript.entity_card_stocks.staging[
            util.constants.STOCK_DISPLAY_SYMBOLS["row_1"]
        ]["change"]
    )
    pyscript.entity_card_stocks.row_2["color"] = util.misc.get_asset_color(
        pyscript.entity_card_stocks.staging[
            util.constants.STOCK_DISPLAY_SYMBOLS["row_2"]
        ]["change"]
    )
    pyscript.entity_card_stocks.row_3["color"] = util.misc.get_asset_color(
        pyscript.entity_card_stocks.staging[
            util.constants.STOCK_DISPLAY_SYMBOLS["row_3"]
        ]["change"]
    )


# @(tap if public)
# @(double tap for stocks & crypto?)
# @(unique threading)
def populate_card_private():
    pyscript.entity_card_stocks.row_1["value"] = util.misc.format_asset_price(
        pyscript.entity_card_stocks.staging[
            util.constants.STOCK_DISPLAY_SYMBOLS["row_1"]
        ]["price"]
    )

    pyscript.entity_card_stocks.row_2["value"] = util.misc.format_asset_price(
        pyscript.entity_card_stocks.staging[
            util.constants.STOCK_DISPLAY_SYMBOLS["row_2"]
        ]["price"]
    )

    pyscript.entity_card_stocks.row_3["value"] = util.misc.format_asset_price(
        pyscript.entity_card_stocks.staging[
            util.constants.STOCK_DISPLAY_SYMBOLS["row_3"]
        ]["price"]
    )

    pyscript.entity_card_stocks.row_1["icon"] = util.constants.STOCK_DISPLAY_ICONS[
        "row_1"
    ]
    pyscript.entity_card_stocks.row_2["icon"] = util.constants.STOCK_DISPLAY_ICONS[
        "row_2"
    ]
    pyscript.entity_card_stocks.row_3["icon"] = util.constants.STOCK_DISPLAY_ICONS[
        "row_3"
    ]
