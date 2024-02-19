from datetime import datetime
from dateutil import tz
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..modules import dates, files, push, secrets
else:
    import dates
    import files
    import push
    import secrets


def get_calendar_events(days=14, next_only=False, ignore_ongoing=False):
    results = calendar.get_events(entity_id=secrets.FAMILY_CALENDAR, duration={"hours": days * 24})
    if ignore_ongoing:
        events = []
        now = datetime.now().astimezone(tz.tzlocal())
        for event in results[secrets.FAMILY_CALENDAR]["events"]:
            if dates.parse_timestamp(event["start"]) >= now:
                events.append(event)
    else:
        events = results[secrets.FAMILY_CALENDAR]["events"]

    return events[0] if next_only else events


def battery_icon(battery, charging=False, upper_limit=100):
    if 0 < battery < 1:
        battery *= 100
    battery = min(battery * 100 / upper_limit, 100)

    icon = "mdi:battery-charging-" if charging else "mdi:battery-"
    icon += str(round(battery / 10) * 10)

    return "mdi:battery" if icon == "mdi:battery-100" else icon


def zone_short_name(zone):
    return files.read("zones", key_list=[zone, "short_name"], default_value=zone)


def get_pref(pref, value_only=True):
    pref_object = files.read("preferences", key_list=[pref])
    if not value_only and isinstance(pref_object["options"], str):
        if pref_object["options"] == "boolean":
            pref_object["options"] = ["On", "Off"]
        elif pref_object["options"] == "time_15":
            pref_object["options"] = ["Off"] + [
                "{}:{:02d} {}".format((h % 12) if (h % 12) != 0 else 12, m, "AM" if h < 12 else "PM")
                for h in range(24)
                for m in range(0, 60, 15)
            ]
        elif pref_object["options"] == "time_30":
            pref_object["options"] = ["Off"] + [
                "{}:{:02d} {}".format((h % 12) if (h % 12) != 0 else 12, m, "AM" if h < 12 else "PM")
                for h in range(24)
                for m in range(0, 60, 30)
            ]
        elif pref_object["options"] == "time_60":
            pref_object["options"] = ["Off"] + [
                "{}:00 {}".format((h % 12) if (h % 12) != 0 else 12, "AM" if h < 12 else "PM")
                for h in range(24)
            ]
        elif "range(" in pref_object["options"]:
            start, end, inc = pref_object["options"][6:-1].split(",")
            pref_object["options"] = [x for x in range(int(start), int(end), int(inc))]
        else:
            log.error("Couldn't match preference option string to keyword")
    return pref_object["value"] if value_only else pref_object


def set_pref(pref, value):
    pref_object = get_pref(pref, value_only=False)
    if value in ["next", "prev"]:
        try:
            index = pref_object["options"].index(pref_object["value"])
            new_index = (index + 1) if value == "next" else (index - 1)
            if new_index >= len(pref_object["options"]):
                new_index = 0
            elif new_index < 0:
                new_index = len(pref_object["options"]) - 1
            new_value = pref_object["options"][new_index]
        except Exception:
            new_value = pref_object["options"][0]
    elif value == "default" and "default" in pref_object:
        new_value = pref_object["default"]
    else:
        new_value = value

    files.write("preferences", [pref, "value"], new_value)


def require_pref_check(pref, value, reset=False):
    def decorator(func):
        def inner(*args, **kwargs):
            if get_pref(pref) == value:
                func(*args, **kwargs)
                if reset:
                    set_pref(pref, "default")

        return inner

    return decorator


def require_ios_action_unlock(func):
    def inner(*args, **kwargs):
        if pyscript.vars.ios_actions_unlocked:
            func(*args, **kwargs)
        else:
            noti = push.Notification(
                title="Command Failed",
                message="iOS actions must be unlocked before using this command",
                target="emily" if kwargs["sourceDeviceID"] == "emilys_iphone" else "marshall",
                tag="command_failed_ios_action",
                group="command_failed_ios_action",
                priority="time-sensitive",
            )
            noti.send()

    return inner
