from datetime import date, datetime, timedelta
import dates


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
    update_row_3()


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
    pyscript.entity_card_home.row_1_value = (
        f"{climate.thermostat.hvac_action} - {climate.thermostat.current_temperature}°"
    )


@time_trigger("startup")
@state_trigger("climate.thermostat.current_humidity")
def entity_card_update_row_2():
    pyscript.entity_card_home.row_2_value = (
        f"{round(climate.thermostat.current_humidity)}%"
    )


@time_trigger("startup", "cron(*/15 0,18 * * *)")
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
