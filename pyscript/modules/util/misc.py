import constants


def get_asset_color(change):
    if change * 100 >= constants.ASSET_COLOR_THRESHOLD:
        return "green"
    elif change * 100 <= constants.ASSET_COLOR_THRESHOLD * -1:
        return "red"
    else:
        return "default"


def format_asset_price(price, precision=2, cents=False):
    pass


def format_asset_change(change, precision):
    sign = "+" if change >= 0 else "-"
    return sign + str(round((change * 100), precision)) + "%"
