from __future__ import annotations


class DomainInvariantError(ValueError):
    """Raised when a domain object is created in an invalid state."""
