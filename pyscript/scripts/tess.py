from datetime import datetime
from dateutil import tz

import secrets
import constants
import dates
import push
import util


@state_trigger("binary_sensor.tess_charger", "climate.tess_hvac_climate_system")
def update_watch_complication():
    push.update_complications(target="marshall")


@util.require_pref_check("Tess Drive Critical", "On", reset=True)
@state_trigger("binary_sensor.tess_parking_brake=='off'")
def send_critical_on_drive():
    noti = push.Notification(
        title="Tess In Drive",
        message="Parking brake is off and Tess is in drive",
        target="marshall",
        priority="critical",
        tag="tess_drive_critical",
        group="tess_drive_critical",
    )
    noti.send()


@state_trigger("binary_sensor.tess_charger=='off'")
def reset_charge_limit():
    task.unique("tess_charge_if_low")
    if pyscript.vars.clear_charge_to_max:
        util.set_pref("Tess Charge To Max", "Off")
        pyscript.vars.clear_charge_to_max = False

    default_limit = util.get_pref("Tess Charge Limit", value_only=True)
    if int(number.tess_charge_limit) != int(default_limit):
        number.set_value(entity_id="number.tess_charge_limit", value=default_limit)
        noti = push.Notification(
            title="Charge Limit Reset",
            message=f"Tess charge limit has been reset to {default_limit}%",
            target="marshall",
            tag="tess_charge_limit_reset",
            group="tess_charge_limit_reset",
        )
        noti.send()


@service("pyscript.tess_charge_to_max")
def charge_to_max():
    noti = push.Notification(
        title="Charging to Max",
        message="Tess has started charging to 100%",
        target="all",
        tag="charge_to_max",
        group="charge_to_max",
    )
    if binary_sensor.tess_charger == "on":
        number.set_value(entity_id="number.tess_charge_limit", value=100)
        task.sleep(60)
        switch.turn_on(entity_id="switch.tess_charger")
        pyscript.vars.clear_charge_to_max = True
    else:
        noti.title = ("Command Failed",)
        noti.message = ("Can't charge to max because Tess is not plugged in",)

    noti.send()


@state_trigger("binary_sensor.tess_charger=='on'")
def charge_if_low():
    if device_tracker.tess_location_tracker == "home":
        task.unique("tess_charge_if_low")
        if int(sensor.tess_battery) < constants.YVETTE_LOW_THRESHOLD:
            switch.turn_on(entity_id="switch.tess_charger")
            while int(sensor.tess_battery) < constants.YVETTE_LOW_THRESHOLD:
                if datetime.now().hour >= 23:
                    return
                task.sleep(60)
            switch.turn_off(entity_id="switch.tess_charger")


@time_trigger("cron(0 20 * * *)")
def charge_reminder():
    if (
        device_tracker.tess_location_tracker == "home"
        and binary_sensor.tess_charger == "off"
        and int(sensor.tess_battery) < int(number.tess_charge_limit) - 10
    ):
        noti = push.Notification(
            title="Tess is Unplugged",
            message=f"Heads up - Tess is unplugged with {sensor.tess_battery}% battery",
            target="all",
            tag="tess_unplugged",
            group="tess_unplugged",
            priority="time-sensitive",
        )
        noti.send()


@state_trigger("binary_sensor.tess_charger=='on'")
def clear_charge_reminder():
    noti = push.Notification(tag="tess_unplugged")
    noti.clear()


@time_trigger("startup")
@state_trigger(
    "switch.tess_sentry_mode",
    "device_tracker.tess_location_tracker",
)
def sentry_off_at_in_laws():
    if (
        switch.tess_sentry_mode == "on"
        and device_tracker.tess_location_tracker == state.getattr(secrets.IN_LAWS_ZONE)["friendly_name"]
    ):
        switch.turn_off(entity_id="switch.tess_sentry_mode")


@event_trigger("ios.action_fired", "actionName=='Tess Air'")
def ios_tess_air(**kwargs):
    if climate.tess_hvac_climate_system == "off":
        pyscript.entity_card_tess.blink = True
    task.sleep(1)
    climate.turn_on(entity_id="climate.tess_hvac_climate_system")


@event_trigger("ios.action_fired", "actionName=='Seat Heat'")
def ios_seat_heat(**kwargs):
    if climate.tess_hvac_climate_system == "heat_cool":
        select.select_option(entity_id="select.tess_heated_seat_rear_left", option="High")
    else:
        noti = push.Notification(
            title="Command Failed",
            message="Tess climate must be on to turn on seat heater",
            target="emily",
            tag="command_failed_seat_heater",
            group="command_failed_seat_heater",
            priority="time-sensitive",
        )
        noti.send()


@util.require_ios_action_unlock
@event_trigger("ios.action_fired", "actionName=='Frunk'")
def ios_frunk(**kwargs):
    cover.open_cover(entity_id="cover.tess_frunk")


@time_trigger("startup")
def persist_complication_tess():
    state.persist(
        "pyscript.complication_tess",
        default_value="",
        default_attributes={"leading": "", "outer": "", "trailing": "", "gauge": 0},
    )


@time_trigger("startup")
@state_trigger("lock.tess_doors")
def complication_leading():
    pyscript.complication_tess.leading = "🔒" if lock.tess_doors == "locked" else ""


@time_trigger("startup")
@state_trigger("sensor.tess_battery", "climate.tess_hvac_climate_system")
def complication_outer():
    pyscript.complication_tess.outer = f"{sensor.tess_battery}"
    pyscript.complication_tess.outer += "❄️" if climate.tess_hvac_climate_system == "heat_cool" else "%"


@time_trigger("startup")
@state_trigger("binary_sensor.tess_charger")
def complication_trailing():
    pyscript.complication_tess.trailing = "⚡️" if binary_sensor.tess_charger == "on" else ""


@time_trigger("startup")
@state_trigger("sensor.tess_battery", "number.tess_charge_limit")
def complication_gauge():
    pyscript.complication_tess.gauge = int(sensor.tess_battery) / int(number.tess_charge_limit)


@time_trigger("startup")
def persist_entity_card_tess():
    state.persist(
        "pyscript.entity_card_tess",
        default_value="",
        default_attributes={
            "name": "Tess",
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


@service("pyscript.tess_tap")
def entity_card_tap():
    if pyscript.entity_card_tess.active:
        climate.turn_off(entity_id="climate.tess_hvac_climate_system")
        pyscript.entity_card_tess.active = False
    else:
        climate.turn_on(entity_id="climate.tess_hvac_climate_system")
        pyscript.entity_card_tess.active = True

    pyscript.entity_card_tess.blink = True
    trigger_info = task.wait_until(state_trigger="climate.tess_hvac_climate_system", timeout=60)
    if trigger_info["trigger_type"] == "timeout":
        pyscript.entity_card_tess.blink = False
        pyscript.entity_card_tess.active = not pyscript.entity_card_tess.active


@service("pyscript.tess_hold")
def entity_card_hold():
    return


@service("pyscript.tess_dtap")
def entity_card_dtap():
    return


@time_trigger("startup")
@state_trigger(
    "binary_sensor.tess_parking_brake",
    "climate.tess_hvac_climate_system",
    "update.tess_software_update",
)
def entity_card_update_state():
    if binary_sensor.tess_parking_brake == "off":
        pyscript.entity_card_tess = "Driving"
        pyscript.entity_card_tess.state_icon = "mdi:road-variant"
        pyscript.entity_card_tess.active = True
    elif climate.tess_hvac_climate_system == "heat_cool":
        pyscript.entity_card_tess = "Air On"
        pyscript.entity_card_tess.state_icon = "mdi:fan"
        pyscript.entity_card_tess.active = True
    else:
        pyscript.entity_card_tess = "Air Off"
        pyscript.entity_card_tess.state_icon = "mdi:car-electric"
        pyscript.entity_card_tess.active = False

    if (
        update.tess_software_update == "on"
        and "(Waiting on Wi-Fi)" not in update.tess_software_update.latest_version
        and binary_sensor.tess_parking_brake != "off"
        and climate.tess_hvac_climate_system != "heat_cool"
    ):
        pyscript.entity_card_tess.state_icon = "mdi:update"


@state_trigger("climate.tess_hvac_climate_system")
def entity_card_clear_blink():
    pyscript.entity_card_tess.blink = False


@time_trigger("startup")
@state_trigger(
    "sensor.tess_battery",
    "binary_sensor.tess_charger",
    "binary_sensor.tess_charging",
)
def entity_card_update_row_1():
    if sensor.tess_battery in ["unknown", "unavailable"]:
        pyscript.entity_card_tess.row_1_icon = "mdi:battery-unknown"
    else:
        pyscript.entity_card_tess.row_1_value = f"{sensor.tess_battery}%"
        pyscript.entity_card_tess.row_1_icon = util.battery_icon(
            battery=int(sensor.tess_battery),
            charging=binary_sensor.tess_charger == "on",
            upper_limit=int(number.tess_charge_limit),
        )


@time_trigger("startup")
@state_trigger(
    "lock.tess_doors",
    "binary_sensor.tess_parking_brake",
    "device_tracker.tess_location_tracker",
    "device_tracker.tess_destination_location_tracker",
)
def entity_card_update_row_2():
    if device_tracker.tess_location_tracker == "home":
        pyscript.entity_card_tess.row_2_value = "Home"
        pyscript.entity_card_tess.row_2_icon = "mdi:home"
        pyscript.entity_card_tess.row_2_color = "default"
    elif lock.tess_doors in ["unknown", "unavailable"]:
        pyscript.entity_card_tess.row_2_value = "Unknown"
        pyscript.entity_card_tess.row_2_icon = "mdi:lock-question"
    elif binary_sensor.tess_parking_brake == "on" or device_tracker.tess_destination_location_tracker == "unknown":
        pyscript.entity_card_tess.row_2_value = lock.tess_doors
        pyscript.entity_card_tess.row_2_icon = "mdi:lock" if lock.tess_doors == "locked" else "mdi:lock-open-variant"
        pyscript.entity_card_tess.row_2_color = "red" if lock.tess_doors != "locked" else "default"
    else:
        pyscript.entity_card_tess.row_2_value = util.zone_short_name(device_tracker.tess_destination_location_tracker)
        pyscript.entity_card_tess.row_2_icon = "mdi:navigation"
        pyscript.entity_card_tess.row_2_color = "default"


@time_trigger("startup")
@state_trigger(
    "climate.tess_hvac_climate_system.current_temperature",
    "binary_sensor.tess_parking_brake",
    "sensor.tess_arrival_time",
)
def entity_card_update_row_3():
    current_temp = climate.tess_hvac_climate_system.current_temperature
    if climate.tess_hvac_climate_system in ["unknown", "unavailable"]:
        pyscript.entity_card_tess.row_3_icon = "mdi:thermometer-off"
    else:
        try:
            delta = dates.parse_timestamp(sensor.tess_arrival_time) - datetime.now().astimezone(tz.tzlocal())
            eta = delta.days * 86400 + delta.seconds
        except Exception:
            eta = 0

        if binary_sensor.tess_parking_brake == "on" or eta <= 0:
            pyscript.entity_card_tess.row_3_value = f"{current_temp}° F"
            pyscript.entity_card_tess.row_3_icon = "mdi:thermometer"
            pyscript.entity_card_tess.row_3_color = "red" if current_temp and current_temp >= 105 else "default"
        else:
            pyscript.entity_card_tess.row_3_value = f"{eta//60} minutes"
            pyscript.entity_card_tess.row_3_icon = "mdi:map-clock"
            task.unique("tess_eta_update_loop")
            task.sleep(30)
            entity_card_update_row_3()
