from datetime import datetime, timedelta
from dateutil import tz
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..modules import dates, util
    from ..modules.dummy import *
    from ..modules.files import File
    from ..modules.push import Notification
else:
    import dates
    from files import File
    from push import Notification
    import util


@state_trigger("pyscript.chelsea_next_fixture.blink==True")
def chelsea_kickoff_notification():
    competition = pyscript.chelsea_next_fixture.competition
    opponent = pyscript.chelsea_next_fixture.home_team if pyscript.chelsea_next_fixture.home_team != "Chelsea" else pyscript.chelsea_next_fixture.away_team
    location = calendar.chelsea_fixtures.location
    message = f"The {competition} match against {opponent} is about to kick off at {location}"
    noti = Notification(
        title="Chelsea Kickoff",
        message=message[4:] if "the the" in message.lower() else message,
        tag="chelsea_match",
        group="chelsea_match",
        priority="time-sensitive",
        target="marshall",
    )
    noti.send()


@time_trigger("cron(0 7,18 * * *)")
def toggle_butterfly_night_light():
    if datetime.now().hour < 12:
        switch.turn_on(entity_id="switch.butterfly_night_light")
    else:
        switch.turn_off(entity_id="switch.butterfly_night_light")


@event_trigger("emily_good_morning")
def emily_good_morning():
    emily_near_home = File("zones").read([person.emily, "near_home"], False)
    is_day_time = 6 <= datetime.now().hour < 17
    
    if emily_near_home and is_day_time:
        switch.turn_on(entity_id="switch.ellies_sound_machine")
        

@time_trigger("cron(0 8,20 * * *)")
def feed_chelsea_notification():
    last_opened = binary_sensor.chelsea_cabinet_sensor.last_changed.astimezone(tz.tzlocal())
    if last_opened < datetime.now().astimezone(tz.tzlocal()) - timedelta(hours=2):
        noti = Notification(
            title="Feed Beth",
            message=f"Don't forget Chelsea's {'breakfast' if datetime.now().hour < 12 else 'dinner'}",
            tag="feed_chelsea",
            group="feed_chelsea",
            priority="time-sensitive",
            target="marshall" if person.marshall == "home" and person.emily != "home" else "all",
        )
        noti.send()


@time_trigger("startup")
@state_trigger("binary_sensor.chelsea_cabinet_sensor")
def clear_feed_chelsea_notification():
    noti = Notification(tag="feed_chelsea")
    noti.clear()


@state_trigger("person.marshall", "person.emily")
def notify_on_zone_change(**kwargs):
    name = state.getattr(kwargs["var_name"])["friendly_name"]
    old_zone = kwargs["old_value"]
    old_data = File("zones").read([old_zone])
    old_prefix = old_data.get("prefix", "")
    new_zone = kwargs["value"]
    new_data = File("zones").read([new_zone])
    new_prefix = new_data.get("prefix", "")

    task.unique(f"{name.lower()}_zone_notify")

    if util.get_pref(f"{name} Zone Notifications") != "On":
        return

    if old_zone == pyscript.vars.zone_debounce[name]:
        pyscript.vars.zone_debounce[name] = None
        return

    if "debounce" in new_data:
        pyscript.vars.zone_debounce[name] = new_zone
        task.sleep(new_data["debounce"])
        pyscript.vars.zone_debounce[name] = None

    if not new_data.get("is_region"):
        message = f"{name} arrived at {new_prefix}{new_zone}"
        if new_zone == "home":
            duration = dates.format_duration(pyscript.vars.left_home_timestamp[name])
            message += f" after {duration}"
            noti = Notification(
                message=f"You were away for {duration}",
                group="summary_on_zone_change",
                tag="summary_on_zone_change",
                target=name.lower(),
                priority="passive"
            )
            noti.send()

    elif not old_data.get("is_region"):
        duration = dates.format_duration(kwargs['old_value'].last_changed)
        message = f"{name} left {old_prefix}{old_zone} after {duration}"
        if old_zone == "home":
            pyscript.vars.left_home_timestamp[name] = datetime.now()
        elif util.get_pref(f"{name} Zone Summary Notifications") == "On":
            noti = Notification(
                message=f"You spent {duration} at {old_prefix}{old_zone}",
                group="summary_on_zone_change",
                tag="summary_on_zone_change",
                target=name.lower(),
                priority="passive"
            )
            noti.send()

    elif new_zone != "not_home":
        message = f"{name} is in {new_prefix}{new_zone}"

    else:
        message = f"{name} left {old_prefix}{old_zone}"

    noti = Notification(
        message=message,
        group="notify_on_zone_change",
        tag="notify_on_zone_change",
        target="emily" if name == "Marshall" else "marshall",
        )
    noti.send()


@time_trigger("cron(0 5 * * *)")
def clear_zone_change_notifications():
    noti = Notification(tag="notify_on_zone_change")
    noti.clear()


@time_trigger("startup")
def persist_complication_emily_location():
    state.persist(
        "pyscript.complication_emily_location",
        default_value="",
        default_attributes={"inner": "", "outer": ""},
    )


@state_trigger("person.emily")
def complication_emily_location_update():
    pyscript.complication_emily_location.inner = util.zone_short_name(person.emily)
    pyscript.complication_emily_location.outer = dates.parse_timestamp(output_format="time")
