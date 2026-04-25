from ..shared import CommandWithError, Error, ErrorType
from .classification_saga_data import ClassificationSagaData

__all__ = ["ClassificationHandlers"]


class ClassificationHandlers:
    @staticmethod
    def evaluate_error_from_reply(data: ClassificationSagaData, reply: CommandWithError) -> None:
        if reply.has_error:
            data.error = Error(ErrorType(reply.error_type), reply.error_message)
