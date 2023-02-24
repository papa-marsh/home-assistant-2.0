class Notification:
    def __init__(self, **kwargs):
        messsage = kwargs["message"] if "message" in kwargs else ""
        title = kwargs["title"] if "title" in kwargs else "Home Assistant"
        subtitle = kwargs["subtitle"] if "subtitle" in kwargs else None
        group = kwargs["group"] if "group" in kwargs else None
        tag = kwargs["tag"] if "tag" in kwargs else None
        priority = kwargs["priority"] if "priority" in kwargs else None

    def set_payload():
        pass


def notify(message):
    return
