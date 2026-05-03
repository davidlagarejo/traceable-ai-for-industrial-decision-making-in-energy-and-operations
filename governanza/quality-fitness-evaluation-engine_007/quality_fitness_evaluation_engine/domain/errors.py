from __future__ import annotations


class DomainInvariantError(ValueError):
    """Raised when a domain object is built in an invalid state."""
