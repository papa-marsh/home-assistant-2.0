from datetime import date, datetime, timedelta
from dateutil import tz
import constants
import dates
import push


@state_trigger("cover.east_stall", "cover.west_stall")
def garage_open_notification(**kwargs):
    if kwargs["value"] == "open" and kwargs["old_value"] == "closed":
        task.unique(f"{stall}_stall_left_open")
        task.sleep(10 * 60)
        garage_open_notification_loop(
            stall=kwargs["var_name"].split(".")[1].split("_")[0],
            open_time=dates.parse_timestamp(format="time"),
            silent=False,
        )


@event_trigger(
    "mobile_app_notification_action",
    "action in ['silence_east_stall', 'silence_wast_stall']",
)
def silence_garage_open_notification(**kwargs):
    task.unique(f"{kwargs['action_data']['stall']}_stall_left_open")
    task.sleep(10 * 60)
    garage_open_notification_loop(
        stall=kwargs["action_data"]["stall"],
        open_time=kwargs["action_data"]["open_time"],
        silent=True,
    )


@event_trigger(
    "mobile_app_notification_action",
    "action in ['close_east_stall', 'close_wast_stall']",
)
def close_garage_from_notification(**kwargs):
    cover.close_cover(entity_id=f"cover.{kwargs['action_data']['stall']}_stall")


@state_trigger("cover.east_stall=='closed'", "cover.west_stall=='closed'")
def clear_garage_open_notification(**kwargs):
    if kwargs["value"] == "closed" and kwargs["old_value"] == "closed":
        stall = kwargs["var_name"].split(".")[1].split("_")[0]
        task.unique(f"{stall}_stall_left_open")
        noti = push.Notification(tag=f"{stall}_stall_left_open")
        noti.clear()


def garage_open_notification_loop(stall, open_time, silent):
    task.unique(f"{stall}_stall_left_open")
    noti = push.Notification(
        title=f"{stall.capitalize()} Stall Open",
        tag=f"{stall}_stall_left_open",
        group=f"{stall}_stall_left_open",
        target="marshall",  # TODO
        sound="none" if silent else constants.NOTI_SOUND,
        action_data={"stall": stall, "open_time": open_time},
    )
    noti.add_action(
        id=f"silence_{stall}_stall",
        title="Silence",
    )
    noti.add_action(
        id=f"close_{stall}_stall",
        title="Close Garage",
        destructive=True,
    )
    while True:
        if not noti:
            noti.message = f"{'Emily' if stall == 'west' else 'Marshall'}'s garage stall has been open since {open_time}"
            noti.send()
            task.sleep(10 * 60)


@state_trigger("person.marshall", "person.emily")
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


@state_trigger(
    "binary_sensor.front_door_sensor",
    "binary_sensor.garage_door_sensor",
    "binary_sensor.service_door_sensor",
    "binary_sensor.slider_door_sensor",
)
def door_open_critical_notification(**kwargs):
    if kwargs["value"] == "on" and kwargs["old_value"] == "off":
        target = None
        if (
            person.marshall not in ["home", "East Grand Rapids"]
            and person.emily != "home"
        ):
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
    pyscript.entity_card_home.row_2_value = (
        f"{round(climate.thermostat.current_humidity)}%"
    )


@time_trigger("startup", "cron(0 0,19 * * *)")
def entity_card_update_row_3():
    now = datetime.today()
    next_bin_day = get_next_bin_day()
    if next_bin_day == now.date() and now.hour >= 18:
        pyscript.entity_card_home.blink = True
    pyscript.entity_card_home.row_3_value = dates.date_countdown(next_bin_day)


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
