import files
import push


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
        else:
            log.error("Couldn't match preference option string to keyword")
    return pref_object["value"] if value_only else pref_object


def set_pref(pref, value):
    if value in ["next", "prev"]:
        pref_object = get_pref(pref, value_only=False)
        try:
            index = pref_object["options"].index(pref_object["value"])
            new_index = (index + 1) if value == "next" else (index - 1)
            if new_index >= len(pref_object["options"]):
                new_index = 0
            elif new_index < 0:
                new_index = len(pref_object["options"]) - 1
            new_value = pref_object["options"][new_index]
        except:
            new_value = pref_object["options"][0]
    else:
        new_value = value

    files.write("preferences", [pref, "value"], new_value)


def require_ios_action_unlock(func):
    def inner(*args, **kwargs):
        if pyscript.vars.ios_actions_unlocked:
            func(*args, **kwargs)
        else:
            noti = push.Notification(
                title="Command Failed",
                message=f"iOS actions must be unlocked before using this command",
                target="all",
                tag="command_failed_ios_action",
                group="command_failed_ios_action",
                priority="time-sensitive",
            )
            noti.send()

    return inner


def require_pref_check(pref, value):
    def decorator(func):
        def inner(*args, **kwargs):
            if get_pref(pref) == value:
                func(*args, **kwargs)

        return inner

    return decorator
