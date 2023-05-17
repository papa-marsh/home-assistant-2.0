from datetime import datetime, timedelta
from dateutil import tz
import dates
import files
import push
import util


@event_trigger("sleepy_time")
def ios_shortcut_sleepy_time():
    switch.turn_on(
        entity_id=["switch.ellies_sound_machine", "switch.master_sound_machine"]
    )


@event_trigger("wakeup_time")
def ios_shortcut_wakeup_time():
    if 6 <= datetime.now().hour < 4:
        switch.turn_off(
            entity_id=["switch.ellies_sound_machine", "switch.master_sound_machine"]
        )


@time_trigger("cron(0 9,19 * * *)")
def feed_chelsea_notification():
    if binary_sensor.chelsea_cabinet_sensor.last_changed.astimezone(
        tz.tzlocal()
    ) < datetime.now().astimezone(tz.tzlocal()) - timedelta(hours=2):
        noti = push.Notification(
            title="Feed Beth",
            message="Don't forget to feed Chelsea",
            tag="feed_chelsea",
            group="feed_chelsea",
            priority="time-sensitive",
            target="all",
        )
        noti.send()


@state_trigger("binary_sensor.chelsea_cabinet_sensor == 'off'")
def water_chelsea_notification():
    noti = push.Notification(
        title="Water Beth",
        message="Don't forget Chelsea's water",
        tag="water_chelsea",
        group="water_chelsea",
        priority="time-sensitive",
        target="emily",
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
    new_prefix = files.read("zones", [kwargs["value"], "prefix"], "")
    old_prefix = files.read("zones", [kwargs["old_value"], "prefix"], "")

    if not files.read("zones", [kwargs["value"], "is_region"], False):
        message = f"{name} arrived at {new_prefix}{kwargs['value']}"
    elif not files.read("zones", [kwargs["old_value"], "is_region"], False):
        message = f"{name} left {old_prefix}{kwargs['old_value']}"
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
    pyscript.complication_emily_location.outer = dates.parse_timestamp(
        output_format="time"
    )
