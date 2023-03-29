import constants
from datetime import date


def date_countdown(target, short=False):
    today = date.today()

    if (target - today).days == 0:
        countdown = "0" if short else "Today"
    elif (target - today).days == 1:
        countdown = "1" if short else "Tomorrow"
    else:
        countdown = str((target - today).days)
        if not short:
            countdown += " Days"

    return countdown


def colloquial_date(target, short=False, ordinals=False):
    today = date.today()
    ord_map = {"1": "st", "2": "nd", "3": "rd"}

    if (target - today).days == 0:
        output = "Today"
    elif (target - today).days == 1:
        output = "Tomorrow"
    elif 2 <= (target - today).days < 7:
        output = target.strftime("%a") if short else target.strftime("%A")
    else:
        output = target.strftime("%b %-d") if short else target.strftime("%B %-d")
        if ordinals:
            output += ord_map[output[-1]] if output[-1] in ord_map else "th"

    return output


def asset_price(price, precision=2, cents=False, k_suffix=False):
    price = float(price)
    if cents:
        output = f"{price*100:.{precision}f} ¢"
    else:
        if k_suffix:
            output = f"${price/1000:,.{precision}f}k"
        else:
            output = f"${price:,.{precision}f}"

    return output


def asset_change(change, precision=2, percent_formatted=False):
    change = float(change)
    if not percent_formatted:
        change = 100

    sign = "+" if change >= 0 else ""
    return f"{sign}{change:.{precision}f}%"


def asset_color(change, percent_formatted=False):
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
