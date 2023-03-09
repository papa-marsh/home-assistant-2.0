@event_trigger("mobile_app_notification_action", "action=='test'")
def placeholder(**kwargs):
    log.warning(kwargs)
