from datetime import datetime, timedelta
from dateutil import tz
import constants
import dates
import files
import push
import util


@time_trigger("cron(0 7,18 * * *)")
def toggle_butterfly_night_light():
    if datetime.now().hour < 12:
        switch.turn_on(entity_id="switch.butterfly_night_light")
    else:
        switch.turn_off(entity_id="switch.butterfly_night_light")


@event_trigger("sleepy_time")
def ios_shortcut_sleepy_time():
    if files.read("zones", [person.emily, "near_home"], False):
        turn_on_sound_machine()


@event_trigger("wakeup_time")
def ios_shortcut_wakeup_time():
    if 6 <= datetime.now().hour < 17:
        turn_off_sound_machine()


@event_trigger("ios.action_fired", "actionName=='Sound On'")
def turn_on_sound_machine(**kwargs):
    switch.turn_on(entity_id="switch.ellies_sound_machine")


@event_trigger("ios.action_fired", "actionName=='Sound Off'")
def turn_off_sound_machine(**kwargs):
    switch.turn_off(entity_id="switch.ellies_sound_machine")


@state_trigger("switch.ellies_sound_machine=='on'")
def sleep_time():
    media_player.volume_set(entity_id=constants.SPEAKER_GROUP, volume_level=0.3)


@time_trigger("cron(30 8,19 * * *)")
def feed_chelsea_notification():
    if binary_sensor.chelsea_cabinet_sensor.last_changed.astimezone(tz.tzlocal()) < datetime.now().astimezone(tz.tzlocal()) - timedelta(hours=2):
        noti = push.Notification(
            title="Feed Beth",
            message=f"Don't forget Chelsea's {'breakfast' if datetime.now().hour < 12 else 'dinner'}",
            tag="feed_chelsea",
            group="feed_chelsea",
            priority="time-sensitive",
            target="marshall" if person.marshall == "home" and person.emily != "home" else "all",
        )
        noti.send()


@state_trigger("binary_sensor.chelsea_cabinet_sensor=='on'")
def chelsea_double_meal_warning():
    now = datetime.now().astimezone(tz.tzlocal())
    last_opened = binary_sensor.chelsea_cabinet_sensor.last_changed.astimezone(tz.tzlocal())
    if now - timedelta(hours=2) < last_opened < now - timedelta(minutes=2):
        noti = push.Notification(
            title="Beth Already Ate!",
            message=f"Don't let her trick you. Double check before feeding Beth {'breakfast' if datetime.now().hour < 12 else 'dinner'}",
            tag="double_feed_warning",
            group="double_feed_warning",
            priority="time-sensitive",
            target="marshall" if person.marshall == "home" and person.emily != "home" else "all",
        )
        noti.send()


@time_trigger("startup")
@state_trigger("binary_sensor.chelsea_cabinet_sensor")
def clear_feed_chelsea_notification():
    noti = push.Notification(tag="feed_chelsea")
    noti.clear()


@state_trigger("switch.space_heater=='on'")
def space_heater_auto_off():
    task.sleep(3 * 60 * 60)
    switch.turn_off(entity_id="switch.space_heater")


@state_trigger("person.marshall", "person.emily")
def notify_on_zone_change(**kwargs):
    name = state.getattr(kwargs["var_name"])["friendly_name"]
    task.unique(f"{name.lower()}_zone_notify")

    if pyscript.vars.suppress_zone_noti[name]:
        pyscript.vars.suppress_zone_noti[name] = False

    elif util.get_pref(f"{name} Zone Notifications") == "On":
        new_zone = files.read("zones", [kwargs["value"]])
        if "debounce" in new_zone:
            pyscript.vars.suppress_zone_noti[name] = True
            task.sleep(new_zone["debounce"])
            pyscript.vars.suppress_zone_noti[name] = False

        new_prefix = new_zone["prefix"] if "prefix" in new_zone else ""
        old_prefix = files.read("zones", [kwargs["old_value"], "prefix"], "")

        if not files.read("zones", [kwargs["value"], "is_region"], False):
            message = f"{name} arrived at {new_prefix}{kwargs['value']}"

            if new_zone == "home" and pyscript.vars.left_home_timestamp[name].day == datetime.now().day:
                message += f" after {dates.format_duration(pyscript.vars.left_home_timestamp[name])}"

        elif not files.read("zones", [kwargs["old_value"], "is_region"], False):
            message = f"{name} left {old_prefix}{kwargs['old_value']}"

            if kwargs["old_value"].last_changed.astimezone(tz.tzlocal()).day == datetime.now().day:
                message += f" after {dates.format_duration(kwargs['old_value'].last_changed)}"
            if kwargs["old_value"] == "home":
                pyscript.vars.left_home_timestamp[name] = datetime.now()

        elif kwargs["value"] != "not_home":
            message = f"{name} is in {new_prefix}{kwargs['value']}"
        else:
            message = f"{name} left {old_prefix}{kwargs['old_value']}"

        noti = push.Notification(
            message=message,
            group="notify_on_zone_change",
            tag="notify_on_zone_change",
            target="emily" if name == "Marshall" else "marshall",
        )
        noti.send()


@time_trigger("cron(0 5 * * *)")
def clear_zone_change_notifications():
    noti = push.Notification(tag="notify_on_zone_change")
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
