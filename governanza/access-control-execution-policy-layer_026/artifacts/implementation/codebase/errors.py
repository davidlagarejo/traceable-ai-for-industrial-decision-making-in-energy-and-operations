"""Typed errors for motor_026 access policy evaluation."""

from __future__ import annotations


class AccessPolicyError(Exception):
    """Base class for access policy layer errors."""


class AccessPolicyInputError(AccessPolicyError, ValueError):
    """Raised when an input cannot be evaluated as a governed request."""


class UnsafePolicyOutputError(AccessPolicyError, RuntimeError):
    """Raised when a generated output would violate the motor contract."""

