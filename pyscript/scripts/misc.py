import dates
import files
import push
import util


@event_trigger("ios.action_fired", "actionName=='Sound Machines On'")
def ios_sound_machines_on(**kwargs):
    switch.turn_on(
        entity_id=["switch.ellies_sound_machine", "switch.master_sound_machine"]
    )


@event_trigger("ios.action_fired", "actionName=='Sound Machines Off'")
def ios_sound_machines_off(**kwargs):
    switch.turn_off(
        entity_id=["switch.ellies_sound_machine", "switch.master_sound_machine"]
    )


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
