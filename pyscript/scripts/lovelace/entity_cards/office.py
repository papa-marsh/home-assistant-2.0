from datetime import date
import format
import util

state.persist(
    "pyscript.entity_card_office",
    default_value="Available",
    default_attributes={
        "name": "Office",
        "state_icon": "mdi:rocket-launch",
        "active": False,
        "blink": False,
        "row_1_icon": "mdi:calendar-clock",
        "row_1_value": "",
        "row_1_color": "default",
        "row_2_icon": "mdi:home-assistant",
        "row_2_value": "",
        "row_2_color": "default",
        "row_3_icon": "mdi:home-assistant",
        "row_3_value": "",
        "row_3_color": "default",
        "staging": {},
    },
)


@service("lovelace.office_tap")
def office_tap():
    if pyscript.entity_card_office.active:
        pyscript.entity_card_office.active = False
        pyscript.entity_card_office = "Available"
        light.turn_off(entity_id="light.office_door_led")
    else:
        pyscript.entity_card_office.active = True
        pyscript.entity_card_office = "Busy"
        light.turn_on(entity_id="light.office_door_led")


@service("lovelace.office_hold")
def office_hold():
    return


@service("lovelace.office_dtap")
def office_dtap():
    pyscript.entity_card_office.staging["last_timecard"] = date.today()
    pyscript.entity_card_office.blink = False


@time_trigger("startup", "cron(*/15 * * * *)")
def update_row_1():
    next_timecard = get_next_timecard()
    if next_timecard == date.today():
        pyscript.entity_card_office.blink = True
    pyscript.entity_card_office.row_1_value = format.colloquial_date(next_timecard)


@time_trigger("startup")
# @state_trigger("")
def update_row_2():
    pyscript.entity_card_office.row_2_value = ""


@time_trigger("startup")
# @state_trigger("")
def update_row_3():
    pyscript.entity_card_office.row_3_value = ""


def get_next_timecard():
    next_timecard = util.get_next_weekday("fri")
    if next_timecard.isocalendar().week % 2:
        next_timecard += timedelta(days=7)
    if next_timecard <= pyscript.entity_card_office.staging["last_timecard"]:
        next_timecard += timedelta(days=14)

    return next_timecard
