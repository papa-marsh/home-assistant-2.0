from datetime import date, datetime, timedelta
from dateutil import tz


def parse_timestamp(timestamp, output_format="iso"):
    output = datetime.fromisoformat(timestamp).astimezone(tz.tzlocal())

    if output_format == "date":
        output = datetime.strftime(output, "%-m/%-d/%y")
    elif output_format == "time":
        output = datetime.strftime(output, "%-I:%M %p")
    elif output_format == "datetime":
        output = datetime.strftime(output, "%-m/%-d/%y %-I:%M %p")

    return output


def get_next_weekday(day):
    today = date.today()
    day_map = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
    try:
        day = int(day)
    except:
        day = day_map[day.lower()]

    return today + timedelta((day - today.weekday()) % 7)


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
