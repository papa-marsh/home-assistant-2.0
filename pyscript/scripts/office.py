from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from dateutil.tz import tzlocal

if TYPE_CHECKING:
    from ..modules import dates
    from ..modules.dummy import *
    from ..modules.push import Notification
else:
    import dates
    from push import Notification


@state_trigger("person.emily == 'home'")
def meeting_active_notification():
    if pyscript.entity_card_office == "Busy":
        noti = Notification(
            target="emily",
            title="Heads Up",
            message="Dad's in a meeting",
            tag="meeting_active",
            group="meeting_active",
            priority="time-sensitive",
        )
        noti.send()


@state_trigger("pyscript.entity_card_office == 'Busy'")
def meeting_active_notification_retroactive():
    two_min_ago = (dates.now() - timedelta(minutes=2)).astimezone(tzlocal())
    if person.emily == "home" and person.emily.last_changed < two_min_ago:
        meeting_active_notification()


@time_trigger("startup")
@state_trigger("pyscript.entity_card_office == 'Available'")
def clear_meeting_active_notification():
    noti = Notification(tag="meeting_active")
    noti.clear()


@time_trigger("startup")
@state_trigger("media_player.playstation_4", "media_player.playstation_4.source")
def toggle_playstation_fans():
    ignore_list = ["Amazon Prime Video", "Netflix"]
    source = state.getattr("media_player.playstation_4").get("source", None)

    if media_player.playstation_4 == "playing" and source not in ignore_list:
        switch.turn_on(entity_id="switch.playstation_fans")
    else:
        switch.turn_off(entity_id="switch.playstation_fans")


@time_trigger("startup")
def persist_entity_card_office():
    state.persist(
        "pyscript.entity_card_office",
        default_value="Available",
        default_attributes={
            "name": "Office",
            "state_icon": "mdi:cloud",
            "active": False,
            "blink": False,
            "row_1_icon": "mdi:thermometer-water",
            "row_1_value": "",
            "row_1_color": "default",
            "row_2_icon": "mdi:stop",
            "row_2_value": "",
            "row_2_color": "default",
            "row_3_icon": "mdi:web-clock",
            "row_3_value": "",
            "row_3_color": "default",
            "staging": {},
        },
    )


@service("pyscript.office_tap")
def entity_card_tap():
    if pyscript.entity_card_office.blink:
        pyscript.entity_card_office.blink = False
    else:
        if pyscript.entity_card_office.active:
            state.set(
                "pyscript.entity_card_office",
                value="Available",
                active=False,
                state_icon="mdi:cloud",
            )
            switch.turn_off(entity_id="switch.office_door_led")
        else:
            state.set(
                "pyscript.entity_card_office",
                value="Busy",
                active=True,
                state_icon="mdi:headset",
            )
            switch.turn_on(entity_id="switch.office_door_led")


@service("pyscript.office_hold")
def entity_card_hold():
    switch.toggle(entity_id="switch.space_heater")


@service("pyscript.office_dtap")
def entity_card_dtap():
    switch.toggle(entity_id="switch.office_air_conditioner_switch")


@time_trigger("startup")
@state_trigger(
    "sensor.office_ambient_sensor_temperature", "sensor.office_ambient_sensor_humidity", "switch.space_heater"
)
def entity_card_update_row_1():
    if sensor.office_ambient_sensor_temperature in ["unknown", "unavailable"]:
        pyscript.entity_card_office.row_1_value = "Offline"
    else:
        temp = float(sensor.office_ambient_sensor_temperature)
        humidity = float(sensor.office_ambient_sensor_humidity)
        pyscript.entity_card_office.row_1_value = f"{temp:.0f}° · {humidity:.0f}%"

    pyscript.entity_card_office.row_1_icon = "mdi:radiator" if switch.space_heater == "on" else "mdi:thermometer-water"


@time_trigger("startup")
@state_trigger("media_player.office", "media_player.office.volume_level")
def entity_card_update_row_2():
    volume = round(media_player.office.volume_level * 100)
    icon = {
        "playing": "mdi:play",
        "paused": "mdi:pause",
        "idle": "mdi:stop",
    }
    pyscript.entity_card_office.row_2_value = f"{volume}%"
    pyscript.entity_card_office.row_2_icon = icon.get(media_player.office, "mdi:alert-circle")


@time_trigger("startup", "cron(* * * * *)")
def entity_card_update_row_3():
    utc_time = datetime.utcnow().strftime("%-I:%M %p")
    pyscript.entity_card_office.row_3_icon = "mdi:web-clock"
    pyscript.entity_card_office.row_3_value = utc_time


@time_trigger("cron(20 8 * * 1-5)")
def daily_review_blink_on():
    pyscript.entity_card_office.blink = True
