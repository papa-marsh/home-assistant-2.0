from enum import StrEnum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pyscript import service


class Domain(StrEnum):
    CALENDAR = auto()
    CLIMATE = auto()
    COVER = auto()
    FAN = auto()
    LIGHT = auto()
    LOCK = auto()
    MEDIA_PLAYER = auto()
    SWITCH = auto()


class Action(StrEnum):
    TURN_ON = auto()
    TURN_OFF = auto()
    TOGGLE = auto()

    GET_EVENTS = auto()

    SET_HVAC_MODE = auto()
    SET_FAN_MODE = auto()
    SET_TEMPERATURE = auto()


class Entity:
    domain: Domain
    name: str

    @property
    def full_name(self) -> str:
        return f"{self.domain}.{self.name}"

    def perform_action(self, action: Action, **kwargs: dict) -> dict:
        service.call(self.domain, str(action), self.full_name, **kwargs)
