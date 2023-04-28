import os
import constants


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
        default_value="Unkown",
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
