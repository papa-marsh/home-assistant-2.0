from datetime import date, datetime, timedelta
from dateutil import tz
from typing import Literal, Optional


def parse_timestamp(timestamp: Optional[str | datetime] = None, output_format: Literal["iso", "date", "time", "datetime"] = "iso") -> str:
    """
    Returns formatted string of date/time from the given timestamp or ISO string.
    'output_format' can be "iso" (default), "date", "time", or "datetime".
    """
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


def format_duration(timestamp: timedelta | datetime, comparison: Optional[datetime] = None, include_seconds: bool = False) -> str:
    """
    Returns formatted string for the time interval between 'timestamp' and 'comparison' (default is now).
    If 'timestamp' is an interval, 'comparison' is ignored.
    Supports negative internvals, but does not include a negative sign.
    """
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


def get_next_weekday(day: Literal["mon", "tue", "wed", "thu", "fri", "sat", "sun"]) -> date:
    """
    Given a weekday, returns a date object for the next occurance of that weekday.
    Includes the current day (eg. If today is Monday, then get_next_weekday("mon") = date.today().)
    """
    DAYS = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}

    today = date.today()
    day = DAYS[day]

    next_weekday = today + timedelta((day - today.weekday()) % 7)

    return next_weekday


def date_countdown(target: date, short: bool = False) -> str:
    """
    Returns a formatted "countdown" until a given date.
    If short=False: Returns "Today", "Tomorrow", or "X Days".
    If short=True: Only return an integer.
    """
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


def colloquial_date(target: date, short: bool = False, ordinals: bool = False) -> str:
    """
    Returns the "friendly" way to reference a future date (eg. "Today", "Tomorrow", "Friday").
    If target date is more than a week away, return month & date (eg. "March 19(th)").
    If short=True, shorten weekday/month names.
    """
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
            last_char = output[-1]
            output += ord_map[last_char] if last_char in ord_map else "th"

    return output
