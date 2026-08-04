"""
Domain Layer - Exceptions.
Pure domain exception hierarchy with ZERO external or framework dependencies.
"""


class DomainError(Exception):
    """Base exception for all domain-level errors."""
    pass


class InvalidVideoError(DomainError):
    """Raised when a Video entity has invalid attributes."""
    pass


class ScheduleError(DomainError):
    """Raised when a ChannelSchedule operation fails constraint checks."""
    pass
