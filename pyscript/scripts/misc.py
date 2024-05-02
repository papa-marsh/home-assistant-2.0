from datetime import date, datetime, timedelta
from dateutil.tz import tzlocal
from typing import Literal, TYPE_CHECKING

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
        message=message.replace("The the", "The"),
        tag="chelsea_match",
        group="chelsea_match",
        priority="time-sensitive",
        target="marshall",
    )
    noti.send()


@state_trigger("switch.ellies_sound_machine")
def toggle_butterfly_night_light():
    if switch.ellies_sound_machine == "off":
        switch.turn_on(entity_id="switch.butterfly_night_light")
    else:
        switch.turn_off(entity_id="switch.butterfly_night_light")


@event_trigger("emily_good_morning")
def emily_good_morning():
    if 5 <= dates.now().hour < 17:
        switch.turn_off(entity_id="switch.ellies_sound_machine")
        

@time_trigger("cron(0 8,20 * * *)")
def feed_chelsea_notification():
    last_opened = binary_sensor.chelsea_cabinet_sensor.last_changed.astimezone(tzlocal())
    now = dates.now()
    if last_opened < now - timedelta(hours=2):
        noti = Notification(
            title="Feed Beth",
            message=f"Don't forget Chelsea's {'breakfast' if now.hour < 12 else 'dinner'}",
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
    now = dates.now()
    old_zone = kwargs["old_value"]
    old_data = File("zones").read([old_zone])
    old_prefix = old_data.get("prefix", "")
    new_zone = kwargs["value"]
    new_data = File("zones").read([new_zone])
    new_prefix = new_data.get("prefix", "")

    if old_zone == "home":
        pyscript.vars.left_home_timestamp[name] = now

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
            left_home = dates.parse_timestamp(pyscript.vars.left_home_timestamp[name])
            duration = dates.format_duration(left_home)
            message += f" after {duration}"

            if util.get_pref(f"{name} Zone Summary Notifications") == "On":
                noti = Notification(
                    message=f"You were away for {duration}",
                    group="summary_on_zone_change",
                    tag="summary_on_zone_change",
                    target=name.lower(),
                    priority="passive"
                )
                noti.send()

    elif not old_data.get("is_region"):
        old_zone_entered = dates.parse_timestamp(old_zone.last_changed.astimezone(tzlocal()))
        duration = dates.format_duration(old_zone_entered)
        zone_summary_on = util.get_pref(f"{name} Zone Summary Notifications") == "On"
        too_short_for_update = (now - old_zone_entered).seconds < (5 * 60)

        message = f"{name} left {old_prefix}{old_zone} after {duration}"

        if zone_summary_on and old_zone != "home" and not too_short_for_update:
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


@event_trigger("emily_cycle_started")
def emily_cycle_started(**__):
    add_cycle_event("start")


@event_trigger("emily_cycle_ended")
def emily_cycle_ended(**__):
    add_cycle_event("end")


def add_cycle_event(event_type: Literal["start", "end"]) -> None:
    event_opposite = "end" if event_type == "start" else "start"
    today = str(date.today())
    raw = File("cycle").read(["raw"])
    latest_date = sorted(raw)[-1]
    last_event_type = raw[latest_date]

    if event_type == last_event_type:
        noti = Notification(
            title="Command Failed",
            message=f"Cycle has already {event_type}ed. Press and hold to modify the {event_type} date",
            group="add_cycle_event",
            tag="add_cycle_event",
            target="emily"
        )
        noti.add_action(id="edit_cycle_event_0", title="Today")
        noti.add_action(id="edit_cycle_event_1", title="Yesterday")
        for i in range(2, 7):
            noti.add_action(
                id=f"edit_cycle_event_{i}",
                title=(date.today() - timedelta(days=i)).strftime("%A")
            )

        noti.send()

    elif latest_date == today:
        noti = Notification(
            title="Command Failed",
            message=f"Can't {event_type} cycle today because cycle {event_opposite}ed today. Re-trigger 'Cycle {event_opposite.capitalize()}ed' to edit",
            group="add_cycle_event",
            tag="add_cycle_event",
            target="emily"
        )
        noti.send()

    else:
        File("cycle").write(["raw", today], event_type)


@event_trigger(
    "mobile_app_notification_action",
    "action[:-2] == 'edit_cycle_event'",
)
def edit_cycle_event(**kwargs):
    difference = int(kwargs["action"][-1])
    new_date = date.today() - timedelta(days=difference)
    raw = File("cycle").read(["raw"])
    second_latest_date = datetime.strptime(sorted(raw)[-2], "%Y-%m-%d").date()

    if new_date <= second_latest_date:
        noti = Notification(
            title="Command Failed",
            message="There's a date conflict that will break things. Talk to Marshall to fix it",
            group="add_cycle_event",
            tag="add_cycle_event",
            target="both"
        )
        noti.send()
