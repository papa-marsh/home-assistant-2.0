"""
Type stubs for PyScript service module.
These are dummy implementations to help with type checking and IntelliSense.
"""

from typing import Any, Dict


def call(
    domain: str,
    service: str,
    entity_id: str | list[str] | None = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Call a Home Assistant service."""
    ...


def has_service(domain: str, service: str) -> bool:
    """Check if a service exists."""
    ...


def list_services(domain: str | None = None) -> Dict[str, Any]:
    """List available services."""
    ...
