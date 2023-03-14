@event_trigger("mobile_app_notification_action", "action=='test'")
def push_action_placeholder(**kwargs):
    log.warning(kwargs)


@event_trigger("ios.action_fired", "actionName=='test'")
def ios_action_placeholder(**kwargs):
    log.warning(kwargs)
