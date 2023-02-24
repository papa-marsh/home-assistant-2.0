state.persist(
    "pyscript.entity_card_hass",
    default_value="Unkown",
    default_attributes={
        "name": "HASS",
        "state_icon": "mdi:raspberry-pi",
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
    },
)


@service("lovelace.hass_tap")
def hass_tap():
    return


@service("lovelace.hass_hold")
def hass_hold():
    return


@service("lovelace.hass_dtap")
def hass_dtap():
    return


@time_trigger("startup")
@state_trigger(
    "update.home_assistant_core_update",
    "update.home_assistant_operating_system_update",
    "update.home_assistant_supervisor_update",
    state_check_now=True,
)
def update_state():
    pyscript.entity_card_hass = update.home_assistant_core_update.installed_version[2:]

    if (
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
def update_row_1():
    value = f"{sensor.hacs} Update"
    if sensor.hacs != "1":
        value += "s"

    pyscript.entity_card_hass.row_1_value = value


@time_trigger("startup")
@state_trigger("binary_sensor.z_wave_js_running")
def update_row_2():
    pyscript.entity_card_hass.row_2_value = (
        "Running" if binary_sensor.z_wave_js_running == "on" else "Not Running"
    )


@time_trigger("startup")
@state_trigger("sensor.cpu_temperature")
def update_row_3():
    pyscript.entity_card_hass.row_3_value = f"{sensor.cpu_temperature} °F"
    pyscript.entity_card_hass.row_3_color = (
        "red" if float(sensor.cpu_temperature) >= 120 else "default"
    )
