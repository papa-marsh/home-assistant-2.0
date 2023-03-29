from datetime import date, timedelta


def get_next_weekday(day):
    today = date.today()
    day_map = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
    try:
        day = int(day)
    except:
        day = day_map[day.lower()]

    return today + timedelta((day - today.weekday()) % 7)


def battery_icon(battery, charging=False, upper_limit=100):
    if 0 < battery < 1:
        battery *= 100
    battery = min(battery * 100 / upper_limit, 100)

    icon = "mdi:battery-charging-" if charging else "mdi:battery-"
    icon += str(round(battery / 10) * 10)

    return "battery" if icon == "battery-100" else icon


@time_trigger("startup")
def persist_mutex():
    state.persist(
        "pyscript.mutex",
        default_value="",
        default_attributes={},
    )


def mutex(mutex_id, override=False):
    def mutex_decorator(func):
        def inner(*args, **kwargs):
            if (
                mutex_id in pyscript.mutex
                and state.getattr("pyscript.mutex")[mutex_id]
                and not override
            ):
                log.warning(f"Mutex {mutex_id} is already set. Skipping execution")
                return
            state.setattr(f"pyscript.mutex.{mutex_id}", True)
            try:
                output = func(*args, **kwargs)
            except:
                log.warning(f"Exception caught during execution of mutex {mutex_id}")
                output = None
            state.setattr(f"pyscript.mutex.{mutex_id}", False)
            return output

        return inner

    return mutex_decorator
