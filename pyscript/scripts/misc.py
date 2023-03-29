@event_trigger("mobile_app_notification_action", "action=='test'")
def push_action_placeholder(**kwargs):
    log.warning(kwargs)


@event_trigger("ios.action_fired", "actionName=='test'")
def ios_action_placeholder(**kwargs):
    log.warning(kwargs)


@time_trigger("startup")
@state_trigger("media_player.playstation_4")
def update_playstation_fans():
    if media_player.playstation_4 == "playing":
        switch.turn_on(entity_id="switch.playstation_fans")
    else:
        switch.turn_off(entity_id="switch.playstation_fans")


@time_trigger("cron(0 * * * *)")
def restart_ssh_addon():
    hassio.addon_restart(addon="a0d7b954_ssh")
