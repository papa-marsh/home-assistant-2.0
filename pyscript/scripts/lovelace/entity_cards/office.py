state.persist(
    "pyscript.entity_card_office",
    default_value="Available",
    default_attributes={
        "name": "Office",
        "state_icon": "mdi:rocket",
        "active": False,
        "blink": False,
        "row_1": {
            "icon": "mdi:home-assistant",
            "value": "ph",
            "color": "default",
        },
        "row_2": {
            "icon": "mdi:home-assistant",
            "value": "ph",
            "color": "default",
        },
        "row_3": {
            "icon": "mdi:home-assistant",
            "value": "ph",
            "color": "default",
        },
    },
)


@service("lovelace.office_tap")
def office_tap():
    if pyscript.entity_office.active:
        pyscript.entity_office.active = False
        pyscript.entity_office = "Available"
        light.turn_off(entity_id="light.office_door_led")
    else:
        pyscript.entity_office.active = True
        pyscript.entity_office = "Busy"
        light.turn_on(entity_id="light.office_door_led")


@service("lovelace.office_hold")
def office_hold():
    return


@service("lovelace.office_dtap")
def office_dtap():
    return
