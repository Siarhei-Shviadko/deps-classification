from enum import StrEnum

__all__ = ["State"]


class State(StrEnum):
    UNIFICATION = "unification"
    PARSING = "parsing"
    CLASSIFICATION = "identification"
    DOCUMENT_CREATION = "document_creation"
    COMPLETED = "completed"

    def for_message(self) -> str:
        return self.value.replace("_", " ").capitalize()
