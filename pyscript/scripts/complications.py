from datetime import datetime


@time_trigger("startup")
def persist_complication_yvette():
    state.persist(
        "pyscript.complication_yvette",
        default_value=datetime.now(),
        default_attributes={"leading": "", "outer": "", "trailing": "", "gauge": 0},
    )


@time_trigger("startup")
@state_trigger("lock.yvette_doors")
def yvette_leading():
    pyscript.complication_yvette.leading = "🔒" if lock.yvette_doors == "locked" else ""


@time_trigger("startup")
@state_trigger("sensor.yvette_battery")
def yvette_outer():
    pyscript.complication_yvette.outer = f"{sensor.yvette_battery}%"


@time_trigger("startup")
@state_trigger("binary_sensor.yvette_charging")
def yvette_trailing():
    pyscript.complication_yvette.trailing = (
        "⚡️" if binary_sensor.yvette_charging == "on" else ""
    )


@time_trigger("startup")
@state_trigger("sensor.yvette_battery", "number.yvette_charge_limit")
def yvette_gauge():
    pyscript.complication_yvette.gauge = int(sensor.yvette_battery) / int(
        number.yvette_charge_limit
    )
