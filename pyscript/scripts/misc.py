import dates
import files
import push
import util


@event_trigger("mobile_app_notification_action", "action=='test'")
def push_action_placeholder(**kwargs):
    log.warning(kwargs)


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
        target="Emily" if name == "Marshall" else "Marshall",
    )

    noti.send()


@time_trigger("cron(0 5 * * *)")
def clear_zone_change_notifications():
    noti = push.Notification(tag="notify_on_zone_change")
    noti.send()


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
