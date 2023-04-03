import dates
import files


@event_trigger("mobile_app_notification_action", "action=='test'")
def push_action_placeholder(**kwargs):
    log.warning(kwargs)


@event_trigger("ios.action_fired", "actionName=='test'")
def ios_action_placeholder(**kwargs):
    log.warning(kwargs)


@time_trigger("startup")
def persist_complication_emily_location():
    state.persist(
        "pyscript.complication_emily_location",
        default_value="",
        default_attributes={"inner": "", "outer": ""},
    )


@state_trigger("person.emily")
def complication_emily_location_update():
    pyscript.complication_emily_location.inner = files.zone_short_name(person.emily)
    pyscript.complication_emily_location.outer = dates.parse_timestamp(
        output_format="time"
    )
