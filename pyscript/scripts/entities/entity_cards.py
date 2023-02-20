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

state.persist(
    "pyscript.entity_card_stocks",
    default_value="Unkown",
    default_attributes={
        "name": "Stocks",
        "state_icon": "mdi:finance",
        "active": False,
        "blink": False,
        "row_1": {
            "icon": "mdi:bank",
            "value": "Unknown",
            "color": "default",
        },
        "row_2": {
            "icon": "mdi:google",
            "value": "Unknown",
            "color": "default",
        },
        "row_3": {
            "icon": "mdi:rocket-launch",
            "value": "Unknown",
            "color": "default",
        },
    },
)

state.persist(
    "pyscript.entity_card_crypto",
    default_value="Unkown",
    default_attributes={
        "name": "Crypto",
        "state_icon": "mdi:currency-btc",
        "active": False,
        "blink": False,
        "row_1": {
            "icon": "mdi:bitcoin",
            "value": "Unknown",
            "color": "default",
        },
        "row_2": {
            "icon": "mdi:ethereum",
            "value": "Unknown",
            "color": "default",
        },
        "row_3": {
            "icon": "mdi:cosine-wave",
            "value": "Unknown",
            "color": "default",
        },
    },
)

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
