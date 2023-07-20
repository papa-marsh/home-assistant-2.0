from random import random
import constants


class Notification:
    def __init__(self, **kwargs):
        self.action_data = kwargs["action_data"] if "action_data" in kwargs else None
        self.actions = kwargs["actions"] if "actions" in kwargs else []
        self.group = kwargs["group"] if "group" in kwargs else str(random())
        self.message = kwargs["message"] if "message" in kwargs else ""
        self.priority = kwargs["priority"] if "priority" in kwargs else "active"
        self.sound = kwargs["sound"] if "sound" in kwargs else constants.NOTI_SOUND
        self.tag = kwargs["tag"] if "tag" in kwargs else str(random())
        self.target = kwargs["target"] if "target" in kwargs else None
        self.title = kwargs["title"] if "title" in kwargs else ""

    def _stage(self):
        self.payload = {
            "message": self.message,
            "title": self.title,
            "data": {
                "actions": self.actions if self.actions else None,
                "action_data": self.action_data,
                "group": self.group,
                "tag": self.tag,
                "push": {
                    "sound": "none"
                    if self.sound == "none"
                    else {
                        "name": constants.NOTI_CRIT_SOUND
                        if self.priority == "critical"
                        else self.sound
                    },
                    "interruption-level": self.priority,
                },
            },
        }

    def send(self, target=None):
        if target:
            self.target = target
        self._stage()
        call_notify_service(self.target, self.payload)

    def clear(self):
        payload = {"message": "clear_notification", "data": {"tag": self.tag}}
        call_notify_service(target="all", payload=payload)

    def add_action(
        self,
        id,
        title,
        destructive=False,
        nav_view=None,
        input=False,
        require_auth=False,
    ):
        action = {
            "action": id,
            "title": title,
            "authenticationRequired": require_auth,
            "destructive": destructive,
        }

        if nav_view:
            action["uri"] = f"/lovelace-mobile/{nav_view}"

        if input:
            action["behavior"] = "textInput"

        self.actions.append(action)


def call_notify_service(target, payload):
    if target.lower() in ["marshall", "all"]:
        notify.mobile_app_marshalls_iphone(**payload)
    if target.lower() in ["emily", "all"]:
        notify.mobile_app_emily_s_iphone(**payload)


def update_location(target="all"):
    payload = {"message": "request_location_update"}
    call_notify_service(target=target, payload=payload)


def update_complications(target="all"):
    payload = {"message": "update_complications"}
    call_notify_service(target=target, payload=payload)


def debug(message="Placeholder message"):
    payload = {"title": "Debug", "message": message, "group": "debug"}
    call_notify_service(target="marshall", payload=payload)
