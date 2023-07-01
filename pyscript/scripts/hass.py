import os
import constants
import files
import push
import util


@time_trigger("cron(0 0 * * *)")
def backup_files():
    for file in [f for f in os.listdir(constants.BASE_FILE_PATH)]:
        if ".yaml" in file:
            file_name = file.split(".yaml")[0]
            files.overwrite(f"backups/{file_name}", files.read(file_name))


@service("lovelace.populate_preferences")
@time_trigger("startup")
def populate_preferences():
    input_select.set_options(
        entity_id="input_select.preference_selector",
        options=[pref for pref in files.read(file_name="preferences")],
        blocking=True,
    )
    input_select.select_first(
        entity_id="input_select.preference_selector",
        blocking=True,
    )


@state_trigger("input_select.preference_selector")
def populate_preference_options(**kwargs):
    pref = util.get_pref(kwargs["value"], value_only=False)
    pyscript.vars.preference_value_mutex = True
    input_select.set_options(
        entity_id="input_select.preference_value",
        options=pref["options"],
        blocking=True,
    )
    input_select.select_option(
        entity_id="input_select.preference_value", option=pref["value"], blocking=True
    )
    pyscript.vars.preference_value_mutex = False


@state_trigger("input_select.preference_value")
def set_preference_value(**kwargs):
    if not pyscript.vars.preference_value_mutex:
        util.set_pref(
            input_select.preference_selector,
            str(kwargs["value"]),
        )


@time_trigger("cron(0 5 * * *)")
def reset_preferences():
    reset = ""
    prefs = files.read(file_name="preferences")
    log.warning(prefs)
    for pref in prefs:
        if "default" in prefs[pref] and prefs[pref]["value"] != prefs[pref]["default"]:
            log.warning("here")
            util.set_pref(pref, prefs[pref]["default"])
            reset += f", {pref}"
    if reset:
        noti = push.Notification(
            title="Preferences Reset",
            message=f"The following preferences were reset to default: {reset[2:]}",
            tag="prefs_reset",
            group="prefs_reset",
            target="marshall",
        )
        noti.send()
        populate_preferences()


@time_trigger("startup")
def persist_vars():
    state.persist(
        "pyscript.vars",
        default_value="",
        default_attributes={"pyscript.vars.sleepy_time_timestamp": ""},
    )
    pyscript.vars.ios_actions_unlocked = False
    pyscript.vars.preference_value_mutex = False


@event_trigger("ios.action_fired", "actionName=='Unlock Actions'")
def ios_unlock_actions(**kwargs):
    state.setattr(f"pyscript.vars.ios_actions_unlocked", True)
    task.sleep(10)
    state.setattr(f"pyscript.vars.ios_actions_unlocked", False)


@time_trigger("cron(*/10 * * * *)")
def cast_to_displays(reset=False):
    task.unique("cast_to_displays")
    for display in constants.NEST_DISPLAYS:
        if state.get(display) == "on" and reset:
            media_player.turn_off(entity_id=display)
            task.sleep(5)
        if state.get(display) == "off" or reset:
            media_player.turn_on(entity_id=display)
            task.sleep(5)
            media_player.turn_off(entity_id=display)
            task.sleep(5)
            service.call("shell_command", f"cast_to_{display.split('.')[1]}")
            task.sleep(30)


@time_trigger("cron(0 3 * * *)")
@service("pyscript.reset_displays")
def reset_displays():
    cast_to_displays(reset=True)


@time_trigger("startup")
def persist_entity_card_hass():
    state.persist(
        "pyscript.entity_card_hass",
        default_value="Unknown",
        default_attributes={
            "name": "HASS",
            "state_icon": "mdi:home-assistant",
            "active": False,
            "blink": False,
            "row_1_icon": "mdi:store",
            "row_1_value": "",
            "row_1_color": "default",
            "row_2_icon": "mdi:z-wave",
            "row_2_value": "",
            "row_2_color": "default",
            "row_3_icon": "mdi:thermometer",
            "row_3_value": "",
            "row_3_color": "default",
            "internet_up": True,
        },
    )


@service("lovelace.hass_tap")
def entity_card_tap():
    return


@service("lovelace.hass_hold")
def entity_card_hold():
    return


@service("lovelace.hass_dtap")
def entity_card_dtap():
    return


@time_trigger("startup")
@state_trigger(
    "update.home_assistant_core_update",
    "update.home_assistant_operating_system_update",
    "update.home_assistant_supervisor_update",
    "pyscript.entity_card_hass.internet_up",
)
def entity_card_update_state():
    pyscript.entity_card_hass = update.home_assistant_core_update.installed_version[2:]

    if pyscript.entity_card_hass.internet_up:
        pyscript.entity_card_hass.blink = False

    if not pyscript.entity_card_hass.internet_up:
        pyscript.entity_card_hass.state_icon = "mdi:web-off"
        pyscript.entity_card_hass.blink = True

    elif (
        update.home_assistant_core_update == "on"
        or update.home_assistant_operating_system_update == "on"
        or update.home_assistant_supervisor_update == "on"
    ):
        pyscript.entity_card_hass.state_icon = "mdi:update"
        pyscript.entity_card_hass.active = True

    else:
        pyscript.entity_card_hass.state_icon = "mdi:home-assistant"
        pyscript.entity_card_hass.active = False


@time_trigger("startup")
@state_trigger("sensor.hacs")
def entity_card_update_row_1():
    value = f"{sensor.hacs} Update"
    if sensor.hacs != "1":
        value += "s"

    pyscript.entity_card_hass.row_1_value = value


@time_trigger("startup")
@state_trigger("binary_sensor.z_wave_js_running")
def entity_card_update_row_2():
    pyscript.entity_card_hass.row_2_value = (
        "Running" if binary_sensor.z_wave_js_running == "on" else "Not Running"
    )


@time_trigger("startup")
@state_trigger("sensor.cpu_temperature")
def entity_card_update_row_3():
    pyscript.entity_card_hass.row_3_value = f"{sensor.cpu_temperature} °F"
    pyscript.entity_card_hass.row_3_color = (
        "red" if float(sensor.cpu_temperature) >= 120 else "default"
    )


@time_trigger("startup", "cron(* * * * *)")
def get_internet_status():
    hostnames = ["google.com", "apple.com", "bing.com"]
    for hostname in hostnames:
        if os.system(f"ping -c 1 {hostname}") == 0:
            pyscript.entity_card_hass.internet_up = True
            break
    else:
        pyscript.entity_card_hass.internet_up = False
