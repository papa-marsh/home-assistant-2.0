from datetime import date, datetime, timedelta
import format
import util

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
def home_tap():
    return


@service("lovelace.home_hold")
def home_hold():
    return


@service("lovelace.home_dtap")
def home_dtap():
    pyscript.entity_card_office.staging["last_bin_day"] = date.today()
    pyscript.entity_card_office.blink = False
    update_row_3()


@time_trigger("startup")
@state_trigger(
    "climate.thermostat.current_temperature", "climate.thermostat.hvac_action"
)
def update_row_1():
    pyscript.entity_card_home.row_1_value = (
        f"{climate.thermostat.hvac_action} - {climate.thermostat.current_temperature}°"
    )


@time_trigger("startup")
@state_trigger("climate.thermostat.current_humidity")
def update_row_2():
    pyscript.entity_card_home.row_2_value = (
        f"{round(climate.thermostat.current_humidity)}%"
    )


@time_trigger("startup", "cron(*/15 0,18 * * *)")
def update_row_3():
    now = datetime.today()
    next_bin_day = get_next_bin_day()
    if next_bin_day == now.date() and now.hour >= 18:
        pyscript.entity_card_home.blink = True
    pyscript.entity_card_home.row_3_value = format.date_countdown(next_bin_day)


def get_next_bin_day():
    next_bin_day = util.get_next_weekday("mon")
    if "last_bin_day" not in pyscript.entity_card_home.staging:
        pyscript.entity_card_home.staging["last_bin_day"] = date.today() - timedelta(
            days=7
        )
    if next_bin_day <= pyscript.entity_card_home.staging["last_bin_day"]:
        next_bin_day += timedelta(days=7)

    return next_bin_day
