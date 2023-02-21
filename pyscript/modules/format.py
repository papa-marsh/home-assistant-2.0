import constants


def format_asset_price(price, precision=2, cents=False):
    price = float(price)
    if cents:
        return f"{price*100:.{precision}f}¢"
    else:
        return f"${price:,.{precision}f}"


def format_asset_change(change, precision=2, percent_formatted=False):
    change = float(change)
    if not percent_formatted:
        change = 100

    sign = "+" if change >= 0 else ""
    return f"{sign}{change:.{precision}f}%"


def get_asset_color(change, percent_formatted=False):
    change = float(change)
    if not percent_formatted:
        change *= 100

    if change >= constants.ASSET_COLOR_THRESHOLD:
        return "green"
    elif change <= constants.ASSET_COLOR_THRESHOLD * -1:
        return "red"
    else:
        return "default"


def get_asset_card_active(change_list):
    pass
