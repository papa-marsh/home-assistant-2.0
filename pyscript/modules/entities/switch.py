from enum import StrEnum, auto

from .entity import Entity


class SwitchAction(StrEnum):
    TURN_ON = auto()
    TURN_OFF = auto()
    TOGGLE = auto()


class Switch(Entity):
    def turn_on(self) -> None:
        self.perform_action(SwitchAction.TURN_ON)

    def turn_off(self) -> None:
        self.perform_action(SwitchAction.TURN_OFF)

    def turn_toggle(self) -> None:
        self.perform_action(SwitchAction.TOGGLE)
