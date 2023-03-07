@time_trigger("startup")
def persist_entity_card_yvette():
    state.persist(
        "pyscript.entity_card_yvette",
        default_value="",
        default_attributes={
            "name": "Yvette",
            "state_icon": "mdi:car-electric",
            "active": False,
            "blink": False,
            "row_1_icon": "mdi:battery",
            "row_1_value": "",
            "row_1_color": "default",
            "row_2_icon": "mdi:lock",
            "row_2_value": "",
            "row_2_color": "default",
            "row_3_icon": "mdi:thermometer",
            "row_3_value": "",
            "row_3_color": "default",
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
