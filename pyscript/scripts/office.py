from datetime import date
import push


@event_trigger("wakeup_time")
@state_trigger("person.emily == 'home'")
def meeting_active_notification():
    if pyscript.entity_card_office == "Busy":
        noti = push.Notification(
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
    noti = push.Notification(tag="meeting_active")
    noti.clear()


@time_trigger("startup")
@state_trigger("media_player.playstation_4")
def update_playstation_fans():
    if media_player.playstation_4 == "playing":
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


@service("pyscript.office_tap")
def entity_card_tap():
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


@service("pyscript.office_hold")
def entity_card_hold():
    pyscript.entity_card_office.staging["last_timecard"] = date.today()
    pyscript.entity_card_office.blink = False


@service("pyscript.office_dtap")
def entity_card_dtap():
    media_player.media_play_pause(entity_id="media_player.office")


@time_trigger("startup")
@state_trigger("media_player.office")
def entity_card_update_row_1():
    pyscript.entity_card_office.row_1_value = media_player.office


@time_trigger("startup")
@state_trigger("media_player.office", "media_player.office.volume_level")
def entity_card_update_row_2():
    pyscript.entity_card_office.row_2_value = f"{round(media_player.office.volume_level * 100)}%"


def entity_card_update_row_3():
    ...
