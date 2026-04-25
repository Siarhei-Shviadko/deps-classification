import enum

__all__ = ["Status"]


class Status(enum.Enum):
    NEW = "new"
    UNIFICATION = "unification"
    PARSING = "parsing"
    CLASSIFICATION = "identification"

    FAILURE = "failed"
    POSTPONED = "postponed"

    COMPLETED = "completed"
