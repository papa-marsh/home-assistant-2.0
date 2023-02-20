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
