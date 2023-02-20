state.persist(
    "pyscript.entity_card_hass",
    default_value="Unkown",
    default_attributes={
        "name": "HASS",
        "state_icon": "mdi:home-assistant",
        "active": False,
        "blink": False,
        "row_1": {
            "icon": "mdi:store",
            "value": "Unknown",
            "color": "default",
        },
        "row_2": {
            "icon": "mdi:z-wave",
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


@service("lovelace.hass_tap")
def hass_tap():
    return


@service("lovelace.hass_hold")
def hass_hold():
    return


@service("lovelace.hass_dtap")
def hass_dtap():
    return
