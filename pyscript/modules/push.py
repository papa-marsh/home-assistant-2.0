from random import random
from typing import Any, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from . import constants
    from .dummy import *
else:
    import constants


class Notification:
    """
    Comprehensive push notification class.
    Use .add_action() to make the notification actionable.
    'action_data' gets included in the payload when HASS receives an actionable notification's respose.
    Setting sound="passive" will send silently without waking screen.
    """

    def __init__(
        self,
        action_data: Any = None,
        actions: list[dict[str, Any]] = None,
        group: str | None = None,
        message: str = "",
        priority: Literal["passive", "active", "time-sensitive" "critical"] = "active",
        sound: str = constants.NOTI_SOUND,
        tag: str | None = None,
        target: Literal["marshall", "emily", "all"] = "marshall",
        title: str = "",
    ) -> None:
        self.action_data = action_data
        self.actions = actions or []
        self.group = group or str(random())
        self.message = message
        self.priority = priority
        self.sound = sound
        self.tag = tag or str(random())
        self.target = target
        self.title = title

    def _stage(self) -> None:
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

    def send(self, target: Literal["marshall", "emily", "all"] | None = None) -> None:
        """
        Stages notification data and calls the HASS native notify service.
        """
        if target:
            self.target = target
        self._stage()
        call_notify_service(self.target, self.payload)

    def clear(self) -> None:
        """
        Attempts to clear any notifications with this instance's tag.
        """
        payload = {"message": "clear_notification", "data": {"tag": self.tag}}
        call_notify_service(target="all", payload=payload)

    def add_action(
        self,
        id: str,
        title: str,
        destructive: bool = False,
        nav_view: str | None = None,
        input: bool = False,
        require_auth: bool = False,
    ) -> None:
        """
        Adds an action to the push notification with which a user can send back a response.
        'id' is a unique identifier. 'title' is what's shown on the button itself.
        Set input=True to allow a text input response after pressing the button.
        'nav_view' can be used to bring user to a specific tab in the HA app (eg. "home").
        """
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


def call_notify_service(target: Literal["marshall", "emily", "all"], payload: dict) -> None:
    """
    Directly call the native HASS notify service with a given push notification payload.
    """
    if target in ["marshall", "all"]:
        notify.mobile_app_marshalls_iphone(**payload)
    if target in ["emily", "all"]:
        notify.mobile_app_emily_s_iphone(**payload)


def update_location(target: Literal["marshall", "emily", "all"] = "all") -> None:
    """
    Attempt to retrieve the location data of a given user from their HA app.
    """
    payload = {"message": "request_location_update"}
    call_notify_service(target, payload)


def update_complications(target: Literal["marshall", "emily", "all"] = "all") -> None:
    """
    Attempt to update the Apple Watch complications for a given user.
    """
    payload = {"message": "update_complications"}
    call_notify_service(target, payload)


def debug(message: str = "Placeholder message") -> None:
    """
    Simple notification intended for quick developer debugging.
    """
    noti = Notification(
        title="Debug",
        message=message,
        group="debug",
        target="marshall",
    )
    noti.send()
