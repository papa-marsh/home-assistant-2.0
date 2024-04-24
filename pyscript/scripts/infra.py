import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..modules import constants, dates, util
    from ..modules.dummy import *
    from ..modules.files import File
    from ..modules.push import Notification
else:
    import constants
    import dates
    from files import File
    from push import Notification
    import util


@time_trigger("startup")
def persist_vars():
    state.persist(
        "pyscript.vars",
        default_value="",
        default_attributes={
            "clear_charge_to_max": False,
            "left_home_timestamp": {"Marshall": None, "Emily": None},
            "bathroom_floor_push_target": None,
            "bathroom_floor_end_time": None,
        },
    )
    pyscript.vars.ios_actions_unlocked = False
    pyscript.vars.preference_value_mutex = False
    pyscript.vars.suppress_zone_noti = {"Marshall": False, "Emily": False}
    pyscript.vars.zone_debounce = {"Marshall":  None, "Emily": None}
    pyscript.vars.sonos_last_reload = dates.now()


@time_trigger("cron(*/15 * * * *)")
def pref_trigger_handler():
    pref_list = File("preferences").read()
    now = dates.parse_timestamp(output_format="time")
    for pref in pref_list:
        if pref_list[pref]["value"] == now and "service" in pref_list[pref]:
            service.call("pyscript", pref_list[pref]["service"])


@time_trigger("cron(0 1 * * *)")
def backup_files():
    for file in os.listdir(constants.BASE_FILE_PATH):
        if ".yaml" in file:
            file_name = file.split(".yaml")[0]
            File(f"backups/{file_name}").overwrite(File(file_name).read())


@service("pyscript.populate_preferences")
@time_trigger("startup")
def populate_preferences():
    input_select.set_options(
        entity_id="input_select.preference_selector",
        options=[pref for pref in File("preferences").read()],
        blocking=True,
    )
    input_select.select_first(
        entity_id="input_select.preference_selector",
        blocking=True,
    )


@state_trigger("input_select.preference_selector")
def populate_preference_options(**kwargs):
    pref = util.get_pref(kwargs["value"], value_only=False)
    pyscript.vars.preference_value_mutex = True
    input_select.set_options(
        entity_id="input_select.preference_value",
        options=pref["options"],
        blocking=True,
    )
    input_select.select_option(
        entity_id="input_select.preference_value",
        option=pref["value"],
        blocking=True,
    )
    pyscript.vars.preference_value_mutex = False


@state_trigger("input_select.preference_value")
def set_preference_value(**kwargs):
    if not pyscript.vars.preference_value_mutex:
        util.set_pref(input_select.preference_selector, str(kwargs["value"]))


@time_trigger("cron(0 7 * * *)")
def reset_preferences():
    reset = ""
    prefs = File("preferences").read()
    for pref in prefs:
        if "default" in prefs[pref] and prefs[pref]["value"] != prefs[pref]["default"]:
            util.set_pref(pref, prefs[pref]["default"])
            reset += f", {pref}"
    if reset:
        noti = Notification(
            title="Preferences Reset",
            message=f"The following preferences were reset to default: {reset[2:]}",
            tag="prefs_reset",
            group="prefs_reset",
            target="marshall",
        )
        noti.send()
        populate_preferences()


@event_trigger("ios.action_fired", "actionName=='Unlock Actions'")
def ios_unlock_actions(**__):
    state.setattr("pyscript.vars.ios_actions_unlocked", True)
    task.sleep(10)
    state.setattr("pyscript.vars.ios_actions_unlocked", False)
