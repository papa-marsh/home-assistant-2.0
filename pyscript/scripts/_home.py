from datetime import timedelta
from typing import TYPE_CHECKING

from dateutil.tz import tzlocal

if TYPE_CHECKING:
    from ..modules import constants, dates, secrets, util
    from ..modules.dummy import *
    from ..modules.files import File
    from ..modules.push import Notification
else:
    import secrets

    import constants
    import dates
    import util
    from files import File
    from push import Notification


# MARK: Sprinklers


# @time_trigger("startup")
# def persist_sprinklers():
#     state.persist(
#         "pyscript.sprinklers",
#         default_value="",
#         default_attributes={
#             "run_program": False,
#             "skip_next": False,
#             "running": False,
#             "triggered_manually": False,
#         },
#     )


# @service("sprinklers.run_program")
# def sprinklers_run_program():
#     if pyscript.sprinklers.run_program:
#         return

#     task.unique("sprinklers_program")
#     program = {1: 5, 2: 15, 3: 5, 4: 15, 5: 15}
#     total = sum(program.values())
#     message = f"Sprinkler program has started and will run for {total} minutes"

#     for zone in program:
#         minutes = program[zone]
#         message += f"\nZone {zone}: {minutes} minutes"

#     noti = Notification(
#         title="Sprinklers Running",
#         message=f"Sprinkler program has started and will run for {total} minutes",
#         group="sprinkler_program_running",
#         target="marshall",
#     )
#     noti.send()

#     pyscript.sprinklers.run_program = True
#     for zone in program:
#         minutes = program[zone]
#         sprinklers_run_zone(zone, minutes)
#         task.sleep(minutes * 60)


# @service("sprinklers.skip_next")
# def sprinklers_skip_next():
#     pyscript.sprinklers.skip_next = True if not pyscript.sprinklers.skip_next else False


# @service("sprinklers.stop_all")
# def sprinklers_stop_all():
#     task.unique("sprinklers_program")
#     service.call("switch", "turn_off", entity_id=sprinkler_zone_entities())


# @service("sprinklers.run_zone")
# def sprinklers_run_zone(zone: int, minutes: int):
#     pyscript.sprinklers.triggered_manually = True
#     rainbird.start_irrigation(entity_id=f"switch.rain_bird_sprinkler_{zone}", duration=minutes)


# @time_trigger("startup")
# @state_trigger(
#     "switch.rain_bird_sprinkler_1",
#     "switch.rain_bird_sprinkler_2",
#     "switch.rain_bird_sprinkler_3",
#     "switch.rain_bird_sprinkler_4",
#     "switch.rain_bird_sprinkler_5",
# )
# def set_sprinkler_state():
#     task.unique("set_sprinkler_state")
#     any_running = any([state.get(entity) == "on" for entity in sprinkler_zone_entities()])
#     if any_running:
#         pyscript.sprinklers.running = True
#         task.sleep(5)
#         pyscript.sprinklers = dates.now()
#     else:
#         pyscript.sprinklers.running = False
#         task.sleep(5)
#         pyscript.sprinklers.run_program = False
#         pyscript.sprinklers.triggered_manually = False


# @state_trigger("switch.rain_bird_sprinkler_1=='on'")
# def sprinkler_skip_program():
#     if not pyscript.sprinklers.skip_next or 5 <= dates.now().hour < 20 or pyscript.sprinklers.triggered_manually:
#         return

#     sprinklers_stop_all()
#     pyscript.sprinklers.skip_next = False

#     noti = Notification(
#         title="Sprinklers Skipped",
#         message=f"Sprinkler program skipped",
#         target="marshall",
#     )
#     noti.send()


# def sprinkler_zone_entities():
#     return [f"switch.rain_bird_sprinkler_{i}" for i in range(1, 8)]


# MARK: Door Open


# @state_trigger(
#     "cover.east_stall",
#     "cover.west_stall",
#     "binary_sensor.front_door_sensor",
#     "binary_sensor.garage_door_sensor",
#     "binary_sensor.service_door_sensor",
#     "binary_sensor.slider_door_sensor",
# )
# def door_open_notification(**kwargs):
#     if kwargs["value"] in ["open", "on"] and kwargs["old_value"] in ["closed", "off"]:
#         id = kwargs["var_name"].split(".")[1].replace("_sensor", "")
#         name = state.getattr(kwargs["var_name"])["friendly_name"].replace(" Sensor", "")
#         open_time = dates.now()
#         task.unique(f"{id}_left_open")
#         task.sleep(10 * 60)
#         door_open_notification_loop(
#             id=id,
#             name=name,
#             open_time=open_time,
#             silent=id == "slider_door",
#         )


# @util.require_pref_check("Door Open Reminder Notifications", "On")
# def door_open_notification_loop(id, name, open_time, silent):
#     task.unique(f"{id}_left_open")
#     noti = Notification(
#         title=f"{'Garage' if 'stall' in id else 'Door'} Open",
#         tag=f"{id}_left_open",
#         group=f"{id}_left_open",
#         target="all",
#         sound="none" if silent else constants.NOTI_SOUND,
#         priority="active" if silent else "time-sensitive",
#         action_data={"id": id, "name": name, "open_time": open_time},
#     )
#     if not silent:
#         noti.add_action(
#             id=f"silence_{id}",
#             title="Silence",
#         )
#     noti.add_action(
#         id=f"turn_off_{id}",
#         title="Turn Off",
#     )
#     if "stall" in id:
#         noti.add_action(
#             id=f"close_{id}",
#             title=f"Close {name}",
#             destructive=True,
#         )
#     while True:
#         duration = (dates.now() - open_time.astimezone(tzlocal())).seconds // 60
#         noti.message = f"{name} has been open for {duration} minutes"
#         if duration in [10, 30, 60, 90, 120, 150, 180]:
#             noti.send()
#         task.sleep(10 * 60)


# @event_trigger(
#     "mobile_app_notification_action",
#     "action in ['silence_east_stall', 'silence_wast_stall', 'silence_front_door', 'silence_garage_door', 'silence_service_door', 'silence_slider_door', 'silence_refrigerator_door']",
# )
# def silence_door_open_notification(**kwargs):
#     task.unique(f"{kwargs['action_data']['id']}_left_open")
#     task.sleep(10 * 60)
#     door_open_notification_loop(
#         id=kwargs["action_data"]["id"],
#         name=kwargs["action_data"]["name"],
#         open_time=dates.parse_timestamp(kwargs["action_data"]["open_time"]),
#         silent=True,
#     )


# @event_trigger(
#     "mobile_app_notification_action",
#     "action in ['turn_off_east_stall', 'turn_off_wast_stall', 'turn_off_front_door', 'turn_off_garage_door', 'turn_off_service_door', 'turn_off_slider_door', 'turn_off_refrigerator_door']",
# )
# def turn_off_door_open_notification(**kwargs):
#     id = kwargs["action_data"]["id"]
#     task.unique(f"{id}_left_open")


# @event_trigger(
#     "mobile_app_notification_action",
#     "action in ['close_east_stall', 'close_wast_stall']",
# )
# def close_garage_from_notification(**kwargs):
#     id = kwargs["action_data"]["id"]
#     name = kwargs["action_data"]["name"]
#     task.unique(f"{id}_left_open")
#     cover.close_cover(entity_id=f"cover.{id}")
#     task.sleep(30)
#     if state.get(f"cover.{id}") == "open":
#         noti = Notification(
#             title="Command Failed",
#             tag=f"{id}_left_open",
#             group=f"{id}_left_open",
#             target="all",
#             priority="time-sensitive",
#             message=f"{name} failed to close",
#         )
#         noti.send()


# @state_trigger(
#     "cover.east_stall=='closed'",
#     "cover.west_stall=='closed'",
#     "binary_sensor.front_door_sensor=='off'",
#     "binary_sensor.garage_door_sensor=='off'",
#     "binary_sensor.service_door_sensor=='off'",
#     "binary_sensor.slider_door_sensor=='off'",
#     "binary_sensor.refrigerator_door_sensor=='off'",
# )
# def clear_door_open_notification(**kwargs):
#     if kwargs["value"] in ["closed", "off"] and kwargs["old_value"] in ["open", "on"]:
#         id = kwargs["var_name"].split(".")[1].replace("_sensor", "")
#         task.unique(f"{id}_left_open")
#         noti = Notification(tag=f"{id}_left_open")
#         noti.clear()


# @state_trigger("person.marshall", "device_tracker.nyx_location_tracker")
# def nyx_garage_auto_open(**kwargs):
#     now = dates.now()
#     location = device_tracker.nyx_location_tracker
#     if (
#         kwargs["value"] == "home"
#         and kwargs["old_value"] not in ["home", "unavailable"]
#         and cover.west_stall == "closed"
#         and 6 <= now.hour < 23
#         and (now - cover.west_stall.last_changed).seconds > 180
#         and (location != "home" or (now - location.last_changed).seconds < 180)
#         and File("zones").read([location, "near_home"], False)
#     ):
#         cover.open_cover(entity_id=f"cover.west_stall")


# @state_trigger("person.emily", "device_tracker.tess_location_tracker")
# def tess_garage_auto_open(**kwargs):
#     now = dates.now()
#     location = device_tracker.tess_location_tracker
#     if (
#         kwargs["value"] == "home"
#         and kwargs["old_value"] not in ["home", "unavailable"]
#         and cover.east_stall == "closed"
#         and 6 <= now.hour < 23
#         and (now - cover.east_stall.last_changed).seconds > 180
#         and (location != "home" or (now - location.last_changed).seconds < 180)
#         and File("zones").read([location, "near_home"], False)
#     ):
#         cover.open_cover(entity_id=f"cover.east_stall")

# @util.require_ios_action_unlock
# @event_trigger("ios.action_fired", "actionName=='East Stall'")
# @event_trigger("ios.action_fired", "actionName=='West Stall'")
# def ios_garage_stall(**kwargs):
#     triggered_by = "emily" if kwargs["sourceDeviceID"] == "emilys_iphone" else "marshall"
#     triggered_from = state.get(f"person.{triggered_by}")
#     if File("zones").read([triggered_from, "near_home"], False):
#         stall = kwargs["actionName"].split(" ")[0].lower()
#         cover.toggle(entity_id=f"cover.{stall}_stall")
#     else:
#         noti = Notification(
#             title="Command Failed",
#             message="You must be closer to home to control the garage with your watch",
#             target=triggered_by,
#             tag="command_failed_ios_garage",
#             group="command_failed_ios_garage",
#             priority="time-sensitive",
#         )
#         noti.send()

# MARK: Critical Notifications


# @util.require_pref_check("Door Open Critical Notifications", "On")
# @state_trigger(
#     "binary_sensor.front_door_sensor",
#     "binary_sensor.garage_door_sensor",
#     "binary_sensor.service_door_sensor",
#     "binary_sensor.slider_door_sensor",
# )
# def door_open_critical_notification(**kwargs):
#     if kwargs["value"] == "on" and kwargs["old_value"] == "off":
#         target = None
#         exception = person.marshall == "East Grand Rapids" and person.emily == secrets.IN_LAWS_ZONE
#         if person.marshall != "home" and person.emily != "home" and not exception:
#             target = "all"
#         elif 1 <= dates.now().hour < 6:
#             target = "marshall"

#         if target:
#             door = state.getattr(kwargs["var_name"])["friendly_name"].split(" ")[0]
#             noti = Notification(
#                 title=f"{door} Door Open",
#                 message=f"{door} door opened at {dates.parse_timestamp(output_format='time')}",
#                 tag=f"{door}_critical",
#                 group=f"{door}_critical",
#                 priority="critical",
#                 target=target,
#             )
#             noti.send()


# @event_trigger("bathroom_floor")
# @event_trigger("ios.action_fired", "actionName=='Bathroom Floor'")
# def heat_bathroom_floor(**kwargs):
#     if kwargs["event_type"] == "ios.action_fired":
#         caller = "emily" if kwargs["sourceDeviceID"] == "emilys_iphone" else "marshall"
#     else:
#         caller = kwargs["caller"]

#     duration = int(util.get_pref("Bathroom Floor Heat Minutes", value_only=True))
#     end_time = dates.now() + timedelta(minutes=duration)
#     pyscript.vars.bathroom_floor_push_target = caller
#     pyscript.vars.bathroom_floor_end_time = dates.parse_timestamp(end_time, output_format="time")

#     climate.set_temperature(entity_id="climate.bathroom_floor_thermostat", temperature=85)
#     task.sleep(duration)
#     climate.set_preset_mode(entity_id="climate.bathroom_floor_thermostat", preset_mode="auto")


# @state_trigger("int(climate.bathroom_floor_thermostat.current_temperature) >= 80")
# def heat_bathroom_floor_ready():
#     if pyscript.vars.bathroom_floor_push_target:
#         noti = Notification(
#             title="Bathroom Ready",
#             message=f"The floor is warmed up until {pyscript.vars.bathroom_floor_end_time}!",
#             tag="ios_bathroom_floor_ready",
#             group="ios_bathroom_floor_ready",
#             priority="time-sensitive",
#             target=pyscript.vars.bathroom_floor_push_target,
#         )
#         noti.send()
#         pyscript.vars.bathroom_floor_push_target = None


@time_trigger("startup")
def persist_entity_card_home():
    state.persist(
        "pyscript.entity_card_home",
        default_value="",
        default_attributes={
            "name": "Home",
            "state_icon": "mdi:home",
            "active": False,
            "blink": False,
            "row_1_icon": "mdi:thermometer-water",
            "row_1_value": "",
            "row_1_color": "default",
            "row_2_icon": "mdi:hvac",
            "row_2_value": "",
            "row_2_color": "default",
            "row_3_icon": "mdi:dog",
            "row_3_value": "",
            "row_3_color": "default",
            "staging": {},
        },
    )


@service("pyscript.home_tap")
def entity_card_tap():
    pyscript.entity_card_home.blink = False


@service("pyscript.home_hold")
def entity_card_hold():
    pyscript.entity_card_home.blink = False


@service("pyscript.home_dtap")
def entity_card_dtap():
    toggle = {"red": "default", "default": "red"}
    pyscript.entity_card_home.row_3_color = toggle[pyscript.entity_card_home.row_3_color]


@time_trigger("startup")
@state_trigger(
    "binary_sensor.garage_door_sensor",
    "binary_sensor.front_door_sensor",
    "binary_sensor.service_door_sensor",
    "binary_sensor.slider_door_sensor",
)
def entity_card_update_state():
    doors = ["garage", "front", "service", "slider"]

    open_count = 0
    output = "All Shut"

    for door in doors:
        if state.get(f"binary_sensor.{door}_door_sensor") == "on":
            open_count += 1
            output = door

    pyscript.entity_card_home = output if open_count < 2 else f"{open_count} Doors"

    if open_count > 0:
        pyscript.entity_card_home.state_icon = "mdi:door-open"
        pyscript.entity_card_home.active = True
    else:
        pyscript.entity_card_home.state_icon = "mdi:home"
        pyscript.entity_card_home.active = False


@time_trigger("startup")
@state_trigger("climate.thermostat.current_temperature", "climate.thermostat.current_humidity")
def entity_card_update_row_1():
    if climate.thermostat in ["unknown", "unavailable"]:
        pyscript.entity_card_home.row_1_value = "Offline"
        pyscript.entity_card_office.row_1_icon = "mdi:thermometer-off"
    else:
        temp = climate.thermostat.current_temperature
        humidity = climate.thermostat.current_humidity
        pyscript.entity_card_home.row_1_value = f"{temp:.0f}° · {humidity:.0f}%"
        pyscript.entity_card_home.row_1_icon = "mdi:thermometer-water"


@time_trigger("startup")
@state_trigger(
    "climate.thermostat",
    "climate.thermostat.hvac_action",
    "climate.thermostat.temperature",
    "climate.thermostat.current_temperature",
)
def entity_card_update_row_2():
    if climate.thermostat in ["unknown", "unavailable"]:
        pyscript.entity_card_home.row_2_value = "Offline"
        pyscript.entity_card_home.row_2_icon = "mdi:hvac"
    else:
        mode = climate.thermostat
        action = state.getattr("climate.thermostat").get("hvac_action", "off")
        temp = int(climate.thermostat.current_temperature)
        preset = climate.thermostat.temperature
        icon = {"cool": "mdi:snowflake", "heat": "mdi:fire", "off": "mdi:hvac-off"}
        value = f"{action}" if temp == preset or not preset else f"{action} ({preset}°)"
        pyscript.entity_card_home.row_2_value = value
        pyscript.entity_card_home.row_2_icon = icon[mode]


@state_trigger("binary_sensor.chelsea_cabinet_sensor=='on'")
def entity_card_update_row_3():
    pyscript.entity_card_home.row_3_color = "default"
    pyscript.entity_card_home.row_3_value = dates.parse_timestamp(output_format="time")


@time_trigger("cron(0 18 * * 1)")
def entity_card_blink():
    pyscript.entity_card_home.blink = True


@time_trigger("cron(0 7,19 * * *)")
def entity_card_feed_chelsea():
    last_opened = binary_sensor.chelsea_cabinet_sensor.last_changed.astimezone(tzlocal())
    if last_opened < dates.now() - timedelta(minutes=60):
        pyscript.entity_card_home.row_3_color = "red"
