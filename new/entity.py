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

    def __init__(self, entity: str) -> None:
        entity_split = entity.split(".")
        if len(entity_split) != 2:
            raise ValueError("Entity string must adhere to `<domain>.<name`> format")

        self.domain = entity_split[0]
        self.name = entity_split[1]

        if self.domain not in Domain:
            raise ValueError("Invalid domain string")

    def perform_action(self, action: Action, **kwargs: dict) -> dict:
        return service.call(self.domain, str(action), self.full_name, **kwargs)
