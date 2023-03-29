import util


@time_trigger("startup")
def persist_entity_card_yvette():
    state.persist(
        "pyscript.entity_card_yvette",
        default_value="",
        default_attributes={
            "name": "Yvette",
            "state_icon": "mdi:car-electric",
            "active": False,
            "blink": False,
            "row_1_icon": "mdi:battery",
            "row_1_value": "",
            "row_1_color": "default",
            "row_2_icon": "mdi:lock",
            "row_2_value": "",
            "row_2_color": "default",
            "row_3_icon": "mdi:thermometer",
            "row_3_value": "",
            "row_3_color": "default",
        },
    )


@service("lovelace.yvette_tap")
def yvette_tap():
    if pyscript.entity_card_yvette.active:
        climate.turn_off(entity_id="climate.yvette_hvac_climate_system")
        pyscript.entity_card_yvette.active = False
    else:
        climate.turn_on(entity_id="climate.yvette_hvac_climate_system")
        pyscript.entity_card_yvette.active = True
    pyscript.entity_card_yvette.blink = True
    task.wait_until(state_trigger="climate.yvette_hvac_climate_system", timeout=60)
    if trig_info["trigger_type"] == "timeout":
        pyscript.entity_card_yvette.blink = False
        pyscript.entity_card_yvette.active = not pyscript.entity_card_yvette.active


@service("lovelace.yvette_hold")
def yvette_hold():
    return


@service("lovelace.yvette_dtap")
def yvette_dtap():
    return


@time_trigger("startup")
@state_trigger(
    "binary_sensor.yvette_parking_brake", "climate.yvette_hvac_climate_system"
)
def update_state():
    if binary_sensor.yvette_parking_brake == "off":
        pyscript.entity_card_yvette = (
            str(device_tracker.yvette_destination_location_tracker)
            if device_tracker.yvette_destination_location_tracker != "unknown"
            else "Driving"
        )
        pyscript.entity_card_yvette.state_icon = "mdi:navigation-variant"
        pyscript.entity_card_yvette.active = True
    elif climate.yvette_hvac_climate_system == "heat_cool":
        pyscript.entity_card_yvette = "Air On"
        pyscript.entity_card_yvette.state_icon = "mdi:fan"
        pyscript.entity_card_yvette.active = True
    else:
        pyscript.entity_card_yvette = "Air Off"
        pyscript.entity_card_yvette.state_icon = "mdi:car-electric"
        pyscript.entity_card_yvette.active = False
    pyscript.entity_card_yvette.blink = False


@time_trigger("startup")
@state_trigger("sensor.yvette_battery", "binary_sensor.yvette_charging")
def update_row_1():
    pyscript.entity_card_yvette.row_1_value = f"{sensor.yvette_battery}%"
    pyscript.entity_card_yvette.row_1_icon = util.battery_icon(
        battery=int(sensor.yvette_battery),
        charging=binary_sensor.yvette_charging == "on",
        upper_limit=int(number.yvette_charge_limit),
    )


@time_trigger("startup")
@state_trigger("lock.yvette_doors")
def update_row_2():
    pyscript.entity_card_yvette.row_2_value = lock.yvette_doors
    pyscript.entity_card_yvette.row_2_icon = (
        "mdi:lock" if lock.yvette_doors == "locked" else "mdi:lock-open-variant"
    )
    pyscript.entity_card_yvette.row_2_color = (
        "red"
        if lock.yvette_doors != "locked"
        and device_tracker.yvette_location_tracker != "home"
        else "default"
    )


@time_trigger("startup")
@state_trigger("climate.yvette_hvac_climate_system.current_temperature")
def update_row_3():
    pyscript.entity_card_yvette.row_3_value = (
        f"{climate.yvette_hvac_climate_system.current_temperature}° F"
    )
    pyscript.entity_card_yvette.row_3_color = (
        "red"
        if climate.yvette_hvac_climate_system.current_temperature >= 100
        else "default"
    )
