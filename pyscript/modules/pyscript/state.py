"""
Type stubs for PyScript state module.
These are dummy implementations to help with type checking and IntelliSense.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from ..entities.domain import Domain


class StateVal(str):
    """Class for representing the value and attributes of a state variable."""

    @property
    def entity_id(self) -> str: ...

    @property
    def last_updated(self) -> datetime: ...

    @property
    def last_changed(self) -> datetime: ...

    @property
    def last_reported(self) -> datetime: ...


def get(name: str) -> Any:
    """Get the current state of an entity or one of its attributes"""
    ...


def set(
    name: str,
    value: Any | None = None,
    new_attributes: dict | None = None,
    **kwargs: Any,
) -> None:
    """
    Set a state variable and/or optional attributes in hass.
    Overwrite the entire attribute dict with `new_attributes`
    or individual attributes via `kwargs`
    """
    ...


def getattr(name: str) -> Dict[str, Any]:
    """Get all attributes of an entity as a dict"""
    ...


def setattr(name: str, value: Any) -> None:
    """Set an attribute using `domain.entity.attribute` format"""
    ...


def exist(name: str) -> bool:
    """Check if an entity exists"""
    ...


def names(domain: "Domain" | None = None) -> list[str]:
    """Get all entity names, optionally filtered by domain"""
    ...


def delete(name: str) -> None:
    """Delete a state variable or one of its attributes"""
    ...


def persist(
    entity_id: str,
    default_value: Any | None = None,
    default_attributes: Dict[str, Any] | None = None,
) -> None:
    """Preserve a pyscript domain entity's value and attributes across HASS restarts"""
    ...
