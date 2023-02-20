@state_trigger("sensor.time")
def test():
    pyscript.test2 = int(pyscript.test2) + 1


@service("lovelace.hass_tap")
def hass_tap():
    return


@service("lovelace.hass_hold")
def hass_hold():
    return


@service("lovelace.hass_dtap")
def hass_dtap():
    return
