from datetime import date, datetime, timedelta
from dateutil import tz


def parse_timestamp(timestamp=None, output_format="iso"):
    if not timestamp:
        timestamp = datetime.now()
    elif isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp).astimezone(tz.tzlocal())
    else:
        timestamp = timestamp.astimezone(tz.tzlocal())

    if output_format == "date":
        timestamp = datetime.strftime(timestamp, "%-m/%-d/%y")
    elif output_format == "time":
        timestamp = datetime.strftime(timestamp, "%-I:%M %p")
    elif output_format == "datetime":
        timestamp = datetime.strftime(timestamp, "%-m/%-d/%y %-I:%M %p")

    return timestamp


def format_duration(timestamp, comparison=None, include_seconds=False):
    if isinstance(timestamp, timedelta):
        interval = timestamp
    elif comparison:
        interval = timestamp - comparison
    else:
        interval = timestamp.astimezone(tz.tzlocal()) - datetime.now().astimezone(tz.tzlocal())
    hours, minutes, seconds = str(abs(interval)).split(".")[0].split(":")
    duration = ""

    if "days" in hours:
        days, hours = hours.split(" days, ")
        duration += f"{days}d"
    if hours != "0":
        duration += f"{hours}h"
    if minutes != "00" or hours != "0" or not include_seconds:
        duration += f"{int(minutes)}m"
    if include_seconds:
        duration += f"{int(seconds)}s"

    return duration


def get_next_weekday(day):
    today = date.today()
    day_map = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
    try:
        day = int(day)
    except Exception:
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
