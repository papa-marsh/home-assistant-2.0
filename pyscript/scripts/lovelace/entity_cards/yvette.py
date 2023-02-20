state.persist(
    "pyscript.entity_card_yvette",
    default_value="Unknown",
    default_attributes={
        "name": "Yvette",
        "state_icon": "mdi:car-electric",
        "active": False,
        "blink": False,
        "row_1": {
            "icon": "mdi:battery",
            "value": "Unknown",
            "color": "default",
        },
        "row_2": {
            "icon": "mdi:lock",
            "value": "Unknown",
            "color": "default",
        },
        "row_3": {
            "icon": "mdi:thermometer",
            "value": "Unknown",
            "color": "default",
        },
    },
)


@service("lovelace.yvette_tap")
def yvette_tap():
    return


@service("lovelace.yvette_hold")
def yvette_hold():
    return


@service("lovelace.yvette_dtap")
def yvette_dtap():
    return
