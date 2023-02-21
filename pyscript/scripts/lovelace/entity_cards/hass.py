state.persist(
    "pyscript.entity_card_hass",
    default_value="Unkown",
    default_attributes={
        "name": "HASS",
        "state_icon": "mdi:home-assistant",
        "active": False,
        "blink": False,
        "row_1_icon": "mdi:store",
        "row_1_value": "",
        "row_1_color": "default",
        "row_2_icon": "mdi:z-wave",
        "row_2_value": "",
        "row_2_color": "default",
        "row_3_icon": "mdi:thermometer",
        "row_3_value": "",
        "row_3_color": "default",
        "staging": {},
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
