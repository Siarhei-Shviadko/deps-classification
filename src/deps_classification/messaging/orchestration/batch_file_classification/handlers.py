from ..shared import (
    CommandWithError,
    CreateDocumentFromFileReply,
    Error,
    ErrorType,
    State,
)
from .saga_data import BatchFileClassificationSagaData

__all__ = ["BatchFileClassificationHandlers"]


class BatchFileClassificationHandlers:
    @staticmethod
    def evaluate_error_from_reply(
        data: BatchFileClassificationSagaData,
        reply: CommandWithError,
    ) -> None:
        if reply.has_error:
            data.error = BatchFileClassificationHandlers.build_error(
                state=data.current_state,
                type_=reply.error_type,
                message=reply.error_message,
            )

    @staticmethod
    def evaluate_document_creation_reply(
        data: BatchFileClassificationSagaData,
        reply: CreateDocumentFromFileReply,
    ) -> None:
        if reply.has_error:
            data.error = BatchFileClassificationHandlers.build_error(
                state=data.current_state,
                type_=reply.error_type,
                message=reply.error_message,
            )
        else:
            data.document_id = reply.document_id

    @staticmethod
    def build_error(state: State, type_: str, message: str) -> Error:
        return Error(type_=ErrorType(type_), message=f"Error in {state.for_message()} state. Reasoning: {message}")
