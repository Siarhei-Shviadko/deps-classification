from ..shared import (
    CommandWithError,
    CreateDocumentFromFileReply,
    Error,
    ErrorType,
    State,
)
from .file_classification_saga_data import FileClassificationSagaData

__all__ = ["FileClassificationHandlers"]


class FileClassificationHandlers:
    @staticmethod
    def evaluate_error_from_reply(data: FileClassificationSagaData, reply: CommandWithError) -> None:
        if reply.has_error:
            data.error = FileClassificationHandlers.build_error(
                state=data.current_state,
                type_=reply.error_type,
                message=reply.error_message,
            )

    @staticmethod
    def evaluate_document_creation_reply(data: FileClassificationSagaData, reply: CreateDocumentFromFileReply) -> None:
        if reply.has_error:
            data.error = FileClassificationHandlers.build_error(
                state=data.current_state,
                type_=reply.error_type,
                message=reply.error_message,
            )
        else:
            data.document_id = reply.document_id

    @staticmethod
    def build_error(state: State, type_: str, message: str) -> Error:
        return Error(type_=ErrorType(type_), message=f"Error in {state.for_message()} state. Reasoning: {message}")
