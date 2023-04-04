from datetime import datetime
from dateutil import tz
import dates
import files
import util


# @state_trigger("person.marshall", "person.emily", "pyscript.debug2")
# def garage_auto_open(**kwargs):
#     trigger = kwargs["var_name"]
#     pyscript.debug.old_val = kwargs["old_value"]
#     pyscript.debug = trigger


@event_trigger("ios.action_fired", "actionName=='Yvette Climate On'")
def ios_climate_on(**kwargs):
    climate.turn_on(entity_id="climate.yvette_hvac_climate_system")


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
def entity_card_tap():
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
def entity_card_hold():
    return


@service("lovelace.yvette_dtap")
def entity_card_dtap():
    return


@time_trigger("startup")
@state_trigger(
    "binary_sensor.yvette_parking_brake",
    "climate.yvette_hvac_climate_system",
    "update.yvette_software_update",
)
def entity_card_update_state():
    if binary_sensor.yvette_parking_brake == "off":
        pyscript.entity_card_yvette = "Driving"
        pyscript.entity_card_yvette.state_icon = "mdi:road-variant"
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
    if update.yvette_software_update == "on":
        pyscript.entity_card_yvette.state_icon = "mdi:update"


@time_trigger("startup")
@state_trigger("sensor.yvette_battery", "binary_sensor.yvette_charger")
def entity_card_update_row_1():
    pyscript.entity_card_yvette.row_1_value = f"{sensor.yvette_battery}%"
    pyscript.entity_card_yvette.row_1_icon = util.battery_icon(
        battery=int(sensor.yvette_battery),
        charging=binary_sensor.yvette_charger == "on",
        upper_limit=int(number.yvette_charge_limit),
    )


@time_trigger("startup")
@state_trigger(
    "lock.yvette_doors",
    "binary_sensor.yvette_parking_brake",
    "device_tracker.yvette_destination_location_tracker",
)
def entity_card_update_row_2():
    if (
        binary_sensor.yvette_parking_brake == "on"
        or device_tracker.yvette_destination_location_tracker == "unknown"
    ):
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
    else:
        pyscript.entity_card_yvette.row_2_value = files.zone_short_name(
            device_tracker.yvette_destination_location_tracker
        )
        pyscript.entity_card_yvette.row_2_icon = "mdi:navigation"
        pyscript.entity_card_yvette.row_2_color = "default"


@time_trigger("startup")
@state_trigger(
    "climate.yvette_hvac_climate_system.current_temperature",
    "binary_sensor.yvette_parking_brake",
    "sensor.yvette_arrival_time",
)
def entity_card_update_row_3():
    try:
        delta = dates.parse_timestamp(
            sensor.yvette_arrival_time
        ) - datetime.now().astimezone(tz.tzlocal())
        eta = delta.days * 86400 + delta.seconds
    except:
        eta = 0
    if binary_sensor.yvette_parking_brake == "on" or eta <= 0:
        pyscript.entity_card_yvette.row_3_value = (
            f"{climate.yvette_hvac_climate_system.current_temperature}° F"
        )
        pyscript.entity_card_yvette.row_3_icon = "mdi:thermometer"
        pyscript.entity_card_yvette.row_3_color = (
            "red"
            if climate.yvette_hvac_climate_system.current_temperature >= 100
            else "default"
        )
    else:
        pyscript.entity_card_yvette.row_3_value = f"{eta//60} minutes"
        pyscript.entity_card_yvette.row_3_icon = "mdi:map-clock"
        task.unique("yvette_eta_update_loop")
        task.sleep(30)
        entity_card_update_row_3()


@time_trigger("startup")
def persist_complication_yvette():
    state.persist(
        "pyscript.complication_yvette",
        default_value="",
        default_attributes={"leading": "", "outer": "", "trailing": "", "gauge": 0},
    )


@time_trigger("startup")
@state_trigger("lock.yvette_doors")
def complication_leading():
    pyscript.complication_yvette.leading = "🔒" if lock.yvette_doors == "locked" else ""


@time_trigger("startup")
@state_trigger("sensor.yvette_battery")
def complication_outer():
    pyscript.complication_yvette.outer = f"{sensor.yvette_battery}%"


@time_trigger("startup")
@state_trigger("binary_sensor.yvette_charging")
def complication_trailing():
    pyscript.complication_yvette.trailing = (
        "⚡️" if binary_sensor.yvette_charging == "on" else ""
    )


@time_trigger("startup")
@state_trigger("sensor.yvette_battery", "number.yvette_charge_limit")
def complication_gauge():
    pyscript.complication_yvette.gauge = int(sensor.yvette_battery) / int(
        number.yvette_charge_limit
    )