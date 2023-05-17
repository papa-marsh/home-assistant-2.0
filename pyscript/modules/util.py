import files


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
