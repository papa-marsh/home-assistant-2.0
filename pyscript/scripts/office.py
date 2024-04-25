from datetime import timedelta
from dateutil.tz import tzlocal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..modules import dates
    from ..modules.dummy import *
    from ..modules.push import Notification
else:
    import dates
    from push import Notification


@time_trigger("cron(0 23 * * *)")
def air_purifier_on():
    medium_setting = 100 * (2 / 3)
    fan.set_percentage(entity_id="fan.office_purifier", percentage=medium_setting)


@time_trigger("cron(0 6 * * *)")
def air_purifier_off():
    fan.turn_off(entity_id="fan.office_purifier")
    if (dates.now() - fan.office_purifier.last_changed).seconds / 3600 > 24:
        noti = Notification(
            target="marshall",
            title="Air Purifier Error",
            message="The air purifier hasn't run in more than 24 hours",
        )
        noti.send()



@time_trigger("cron(*/10 * * * *)")
def space_heater_auto_off():
    two_hours_ago = (dates.now() - timedelta(hours=2)).astimezone(tzlocal())
    if switch.space_heater == "on" and switch.space_heater.last_changed < two_hours_ago:
        switch.turn_off(entity_id="switch.space_heater")


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


@time_trigger("startup")
@state_trigger("pyscript.entity_card_office == 'Available'")
def clear_meeting_active_notification():
    noti = Notification(tag="meeting_active")
    noti.clear()


@time_trigger("startup")
@state_trigger("media_player.playstation_4", "media_player.playstation_4.source")
def toggle_playstation_fans():
    ignore_list = ["Amazon Prime Video", "Netflix"]
    source = media_player.playstation_4.source if "source" in media_player.playstation_4.__dict__ else None

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
            "row_2_icon": "mdi:speaker",
            "row_2_value": "",
            "row_2_color": "default",
            "row_3_icon": "mdi:volume-high",
            "row_3_value": "",
            "row_3_color": "default",
            "staging": {},
        },
    )


@service("pyscript.office_tap")
@event_trigger("office_leds")
def entity_card_tap():
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
    media_player.media_play_pause(entity_id="media_player.office")


@time_trigger("startup")
@state_trigger("sensor.office_ambient_sensor_temperature", "sensor.office_ambient_sensor_humidity", "switch.space_heater")
def entity_card_update_row_1():
    if sensor.office_ambient_sensor_temperature in ["unknown", "unavailable"]:
        pyscript.entity_card_office.row_1_value = "Offline"
        pyscript.entity_card_office.row_1_icon = "mdi:thermometer-off"
    else:
        temp = float(sensor.office_ambient_sensor_temperature)
        humidity = float(sensor.office_ambient_sensor_humidity)
        pyscript.entity_card_office.row_1_value = f"{temp:.0f}° · {humidity:.0f}%"
        pyscript.entity_card_office.row_1_icon = "mdi:radiator" if switch.space_heater == "on" else "mdi:thermometer-water"


@time_trigger("startup")
@state_trigger("media_player.office")
def entity_card_update_row_2():
    pyscript.entity_card_office.row_2_value = media_player.office
    pyscript.entity_card_office.row_2_icon = "mdi:speaker-wireless" if media_player.office == "playing" else "mdi:speaker"


@time_trigger("startup")
@state_trigger("media_player.office", "media_player.office.volume_level")
def entity_card_update_row_3():
    volume = round(media_player.office.volume_level * 100)
    pyscript.entity_card_office.row_3_value = f"{volume}%"
    if volume >= 35:
        pyscript.entity_card_office.row_3_icon = "mdi:volume-high"
    elif volume >= 20:
        pyscript.entity_card_office.row_3_icon = "mdi:volume-medium"
    else:
        pyscript.entity_card_office.row_3_icon = "mdi:volume-low"
