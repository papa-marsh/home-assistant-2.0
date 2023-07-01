from datetime import date, datetime, timedelta
from dateutil import tz
import constants
import dates
import push
import util


@state_trigger(
    "cover.east_stall",
    "cover.west_stall",
    "binary_sensor.front_door_sensor",
    "binary_sensor.garage_door_sensor",
    "binary_sensor.service_door_sensor",
    "binary_sensor.slider_door_sensor",
)
def door_open_notification(**kwargs):
    if kwargs["value"] in ["open", "on"] and kwargs["old_value"] in ["closed", "off"]:
        id = kwargs["var_name"].split(".")[1].replace("_sensor", "")
        name = state.getattr(kwargs["var_name"])["friendly_name"].replace(" Sensor", "")
        task.unique(f"{id}_left_open")
        task.sleep(10 * 60)
        door_open_notification_loop(
            id=id,
            name=name,
            open_time=datetime.now(),
            silent=False,
        )


def door_open_notification_loop(id, name, open_time, silent):
    task.unique(f"{id}_left_open")
    noti = push.Notification(
        title=f"{'Garage' if 'stall' in id else 'Door'} Open",
        tag=f"{id}_left_open",
        group=f"{id}_left_open",
        target="all",
        sound="none" if silent else constants.NOTI_SOUND,
        priority="active" if silent else "time-sensitive",
        action_data={"id": id, "name": name, "open_time": open_time},
    )

    noti.add_action(
        id=f"ignore_{id}",
        title="Ignore",
    )
    if not silent:
        noti.add_action(
            id=f"silence_{id}",
            title="Silence",
        )
    if "stall" in id:
        noti.add_action(
            id=f"close_{id}",
            title=f"Close {name}",
            destructive=True,
        )
    while True:
        log.warning(f"MTW open_time is {open_time} with type {type(open_time)}")
        noti.message = f"{name} has been open for {(datetime.now() - open_time).seconds // 60} minutes"
        noti.send()
        task.sleep(10 * 60)


@event_trigger(
    "mobile_app_notification_action",
    "action in ['silence_east_stall', 'silence_wast_stall', 'silence_front_door', 'silence_garage_door', 'silence_service_door', 'silence_slider_door']",
)
def silence_door_open_notification(**kwargs):
    task.unique(f"{kwargs['action_data']['id']}_left_open")
    task.sleep(10 * 60)
    door_open_notification_loop(
        id=kwargs["action_data"]["id"],
        name=kwargs["action_data"]["name"],
        open_time=kwargs["action_data"]["open_time"],
        silent=True,
    )


@event_trigger(
    "mobile_app_notification_action",
    "action in ['close_east_stall', 'close_wast_stall']",
)
def close_garage_from_notification(**kwargs):
    id = kwargs["action_data"]["id"]
    name = kwargs["action_data"]["name"]
    task.unique(f"{id}_left_open")
    cover.close_cover(entity_id=f"cover.{id}")
    task.sleep(30)
    if state.get(f"cover.{id}") == "open":
        noti = push.Notification(
            title=f"Command Failed",
            tag=f"{id}_left_open",
            group=f"{id}_left_open",
            target="all",
            priority="time-sensitive",
            message=f"{name} failed to close",
        )
        noti.send()


@state_trigger(
    "cover.east_stall=='closed'",
    "cover.west_stall=='closed'",
    "binary_sensor.front_door_sensor=='off'",
    "binary_sensor.garage_door_sensor=='off'",
    "binary_sensor.service_door_sensor=='off'",
    "binary_sensor.slider_door_sensor=='off'",
)
def clear_door_open_notification(**kwargs):
    if kwargs["value"] in ["open", "on"] and kwargs["old_value"] in ["closed", "off"]:
        id = kwargs["var_name"].split(".")[1].replace("_sensor", "")
        task.unique(f"{id}_left_open")
        noti = push.Notification(tag=f"{id}_left_open")
        noti.clear()


@state_trigger(
    "person.marshall", "person.emily", "device_tracker.yvette_location_tracker"
)
def garage_auto_open(**kwargs):
    now = datetime.now().astimezone(tz.tzlocal())
    if (
        kwargs["value"] == "home"
        and kwargs["old_value"] != "home"
        and cover.east_stall == "closed"
        and 6 <= now.hour < 23
        and (now - cover.east_stall.last_changed).seconds > 300
        and (
            device_tracker.yvette_location_tracker != "home"
            or (now - device_tracker.yvette_location_tracker.last_changed).seconds < 300
        )
    ):
        cover.open_cover(entity_id="cover.east_stall")


@util.require_ios_action_unlock
@event_trigger("ios.action_fired", "actionName=='East Stall'")
@event_trigger("ios.action_fired", "actionName=='West Stall'")
def ios_garage_stall(**kwargs):
    stall = kwargs["actionName"].split(" ")[0].lower()
    cover.toggle(entity_id=f"cover.{stall}_stall")


@state_trigger(
    "binary_sensor.front_door_sensor",
    "binary_sensor.garage_door_sensor",
    "binary_sensor.service_door_sensor",
    "binary_sensor.slider_door_sensor",
)
def door_open_critical_notification(**kwargs):
    if kwargs["value"] == "on" and kwargs["old_value"] == "off":
        target = None
        if person.marshall not in [
            "home",
            "East Grand Rapids",
        ] and person.emily not in ["home", "East Grand Rapids"]:
            target = "all"
        elif 1 <= datetime.now().hour < 6:
            target = "marshall"

        if target:
            door = state.getattr(kwargs["var_name"])["friendly_name"].split(" ")[0]
            noti = push.Notification(
                title=f"{door} Door Open",
                message=f"{door} door opened at {dates.parse_timestamp(output_format='time')}",
                tag=f"{door}_critical",
                group=f"{door}_critical",
                priority="critical",
                target=target,
            )

            noti.send()


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
            "row_1_icon": "mdi:thermometer",
            "row_1_value": "",
            "row_1_color": "default",
            "row_2_icon": "mdi:water",
            "row_2_value": "",
            "row_2_color": "default",
            "row_3_icon": "mdi:delete",
            "row_3_value": "",
            "row_3_color": "default",
            "staging": {},
        },
    )


@service("lovelace.home_tap")
def entity_card_tap():
    return


@service("lovelace.home_hold")
def entity_card_hold():
    pyscript.entity_card_home.staging["last_bin_day"] = date.today()
    pyscript.entity_card_home.blink = False
    entity_card_update_row_3()


@service("lovelace.home_dtap")
def entity_card_dtap():
    pass


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
@state_trigger(
    "climate.thermostat.current_temperature", "climate.thermostat.hvac_action"
)
def entity_card_update_row_1():
    if climate.thermostat == "unavailable":
        pyscript.entity_card_home.row_1_value = "Offline"
    else:
        action = (
            climate.thermostat.hvac_action
            if "hvac_action" in climate.thermostat
            else climate.thermostat
        )
        pyscript.entity_card_home.row_1_value = (
            f"{action} - {climate.thermostat.current_temperature}°"
        )


@time_trigger("startup")
@state_trigger("climate.thermostat.current_humidity")
def entity_card_update_row_2():
    if climate.thermostat == "unavailable":
        pyscript.entity_card_home.row_2_value = "Offline"
    else:
        pyscript.entity_card_home.row_2_value = (
            f"{round(climate.thermostat.current_humidity)}%"
        )


@time_trigger("startup", "cron(0 0,19 * * *)")
@state_trigger("binary_sensor.emily_s_iphone_focus")
def entity_card_update_row_3():
    task.unique("entity_card_update_row_3")
    if binary_sensor.emily_s_iphone_focus == "on" and 9 <= datetime.now().hour < 18:
        pyscript.entity_card_home.row_3_value = dates.format_duration(
            binary_sensor.emily_s_iphone_focus.last_changed
        )
        pyscript.entity_card_home.row_3_icon = "mdi:bed-clock"
        task.sleep(60)
        entity_card_update_row_3()
    else:
        now = datetime.now()
        next_bin_day = get_next_bin_day()
        if next_bin_day == now.date() and now.hour >= 18:
            pyscript.entity_card_home.blink = True
        pyscript.entity_card_home.row_3_value = dates.date_countdown(next_bin_day)
        pyscript.entity_card_home.row_3_icon = "mdi:delete"


def get_next_bin_day():
    next_bin_day = dates.get_next_weekday("mon")
    if "last_bin_day" not in pyscript.entity_card_home.staging:
        pyscript.entity_card_home.staging["last_bin_day"] = date.today() - timedelta(
            days=7
        )
    if isinstance(pyscript.entity_card_home.staging["last_bin_day"], str):
        pyscript.entity_card_home.staging["last_bin_day"] = datetime.strptime(
            pyscript.entity_card_home.staging["last_bin_day"], "%Y-%m-%d"
        ).date()
    if next_bin_day <= pyscript.entity_card_home.staging["last_bin_day"]:
        next_bin_day += timedelta(days=7)

    return next_bin_day
