import constants


def get_battery_icon(battery, charging=False, ev_offset=False):
    if 0 < battery < 1:
        battery *= 100
    if ev_offset:
        battery *= 100 / 85
    battery = min(battery, 100)

    icon = "mdi:battery-charging-" if charging else "mdi:battery-"
    icon += str(round(battery / 10) * 10)

    return "battery" if icon == "battery-100" else icon


def format_asset_price(price, precision=2, cents=False, k_suffix=False):
    price = float(price)
    if cents:
        return f"{price*100:.{precision}f} ¢"
    else:
        if k_suffix:
            return f"${price/1000:,.{precision}f}k"
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
