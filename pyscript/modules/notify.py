from random import random


class NotificationPayload:
    priority_list = ["passive", "active", "time-sensitive", "critical"]

    def __init__(self, **kwargs):
        self.message = kwargs["message"] if "message" in kwargs else None
        self.title = kwargs["title"] if "title" in kwargs else None
        self.group = kwargs["group"] if "group" in kwargs else str(random())
        self.tag = kwargs["tag"] if "tag" in kwargs else str(random())
        self.priority = kwargs["priority"] if "priority" in kwargs else 1
        self.silent = kwargs["silent"] if "silent" in kwargs else False

    def send(self, target):
        self.payload = {
            "message": self.message,
            "title": self.title,
            "data": {
                "group": self.group,
                "tag": self.tag,
                "push": {
                    "sound": "none" if self.silent else "3rdParty_Failure_Haptic.caf",
                    "interruption-level": self.priority_list[self.priority],
                },
            },
        }

        if target.lower() in ["marshall", "all"]:
            notify.mobile_app_marshalls_iphone(**self.payload)
        elif target.lower() in ["emily", "all"]:
            notify.mobile_app_emily_s_iphone(**self.payload)

    def clear(self, target="all"):
        self.payload = {"message": "clear_notification", "data": {"tag": self.tag}}
        self.send(self)
