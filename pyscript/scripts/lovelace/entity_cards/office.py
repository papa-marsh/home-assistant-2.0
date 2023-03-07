from datetime import date, timedelta
import format
import util


@time_trigger("startup")
def persist_entity_card_office():
    state.persist(
        "pyscript.entity_card_office",
        default_value="Available",
        default_attributes={
            "name": "Office",
            "state_icon": "mdi:rocket",
            "active": False,
            "blink": False,
            "row_1_icon": "mdi:speaker",
            "row_1_value": "",
            "row_1_color": "default",
            "row_2_icon": "mdi:volume-high",
            "row_2_value": "",
            "row_2_color": "default",
            "row_3_icon": "mdi:calendar-clock",
            "row_3_value": "",
            "row_3_color": "default",
            "staging": {},
        },
    )


@service("lovelace.office_tap")
def office_tap():
    if pyscript.entity_card_office.active:
        state.set(
            "pyscript.entity_card_office",
            value="Available",
            active=False,
            state_icon="mdi:rocket",
        )
        light.turn_off(entity_id="light.office_door_led")
    else:
        state.set(
            "pyscript.entity_card_office",
            value="Busy",
            active=True,
            state_icon="mdi:headset",
        )
        light.turn_on(entity_id="light.office_door_led")


@service("lovelace.office_hold")
def office_hold():
    pyscript.entity_card_office.staging["last_timecard"] = date.today()
    pyscript.entity_card_office.blink = False
    update_row_3()


@service("lovelace.office_dtap")
def office_dtap():
    media_player.media_play_pause(entity_id="media_player.office")


@time_trigger("startup")
@state_trigger("media_player.office")
def update_row_1():
    pyscript.entity_card_office.row_1_value = media_player.office


@time_trigger("startup")
@state_trigger("media_player.office", "media_player.office.volume_level")
def update_row_2():
    pyscript.entity_card_office.row_2_value = (
        f"{round(media_player.office.volume_level * 100)}%"
    )


@time_trigger("startup", "cron(*/15 3 * * *)")
def update_row_3():
    next_timecard = get_next_timecard()
    if next_timecard == date.today():
        pyscript.entity_card_office.blink = True
    pyscript.entity_card_office.row_3_value = format.colloquial_date(next_timecard)


def get_next_timecard():
    next_timecard = util.get_next_weekday("fri")
    if next_timecard.isocalendar().week % 2:
        next_timecard += timedelta(days=7)
    if "last_timecard" not in pyscript.entity_card_office.staging:
        pyscript.entity_card_office.staging["last_timecard"] = date.today() - timedelta(
            days=14
        )
    elif next_timecard <= pyscript.entity_card_office.staging["last_timecard"]:
        next_timecard += timedelta(days=14)

    return next_timecard
