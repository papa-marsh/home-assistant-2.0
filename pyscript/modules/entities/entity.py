from abc import ABC
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Generic, Type, TypeVar

from .domain import Domain

if TYPE_CHECKING:
    from ..pyscript import service, state
    from ..pyscript.state import StateVal


T = TypeVar("T")


class EntityAttribute(Generic[T]):
    def __set_name__(self, owner: Type["Entity"], name: str) -> None:
        self.name = name

    def __get__(self, obj: "Entity", objtype: Type["Entity"] | None = None) -> T:
        return state.get(f"{obj.entity_id}.{self.name}")  # type: ignore[no-any-return]

    def __set__(self, obj: "Entity", value: T) -> None:
        state.setattr(f"{obj.entity_id}.{self.name}", value=value)


class Entity(ABC):
    domain: Domain
    name: str
    state_obj: "StateVal"

    friendly_name = EntityAttribute[str]()

    def __init__(self, entity: str) -> None:
        entity_split = entity.split(".")
        if len(entity_split) != 2:
            raise ValueError("Entity string must adhere to `<domain>.<name`> format")

        self.domain = Domain(entity_split[0])
        self.name = entity_split[1]
        self.state_obj = eval(self.entity_id)

    @property
    def entity_id(self) -> str:
        return f"{self.domain}.{self.name}"

    @property
    def state(self) -> str:
        """Get the current state of the entity"""
        return state.get(self.entity_id)  # type: ignore[no-any-return]

    @state.setter
    def state(self, value: str) -> None:
        """Set the state of the entity"""
        state.set(self.entity_id, value=value)

    def get_attribute(self, attribute_name: str) -> Any:
        """Get the current value of one of the entity's attributes"""
        state.get(f"{self.entity_id}.{attribute_name}")

    def set_attribute(self, attribute_name: str, value: Any) -> None:
        """Set one of the entity's attributes"""
        state.setattr(f"{self.entity_id}.{attribute_name}", value=value)

    @property
    def exists(self) -> bool:
        """Check if the entity exists in Home Assistant"""
        return state.exist(self.entity_id)

    @property
    def last_changed(self) -> datetime:
        """Get the datetime when the entity state last changed"""
        return self.state_obj.last_changed

    @property
    def last_updated(self) -> datetime:
        """Get the datetime when the entity was last updated"""
        return self.state_obj.last_updated

    @property
    def last_reported(self) -> datetime:
        """Get the datetime when the entity was last reported"""
        return self.state_obj.last_reported

    def perform_action(self, action: StrEnum, **kwargs: Any) -> dict:
        """Perform an action related to the entity"""
        return service.call(self.domain, str(action), self.entity_id, **kwargs)
