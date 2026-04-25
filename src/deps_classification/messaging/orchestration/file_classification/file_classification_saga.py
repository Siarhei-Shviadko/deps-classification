import logging

from deps_message_flow.commands.common import Command
from deps_message_flow.messaging.producer import IMessageProducer
from deps_message_flow.sagas.orchestration_simple_dsl import SimpleSaga

from ...commands.classify_file import ClassifyFileReply
from ..shared import (
    CreateDocumentFromFileReply,
    ErrorType,
    PerformParsingReply,
    PerformUnificationReply,
    SagaReplyBuilder,
)
from .file_classification_handlers import FileClassificationHandlers as Handlers
from .file_classification_saga_data import FileClassificationSagaData as SagaData
from .file_classification_steps import FileClassificationSagaSteps as Steps

__all__ = ["FileClassificationSaga"]


class FileClassificationSaga(SimpleSaga[SagaData]):
    def __init__(self, steps: Steps, message_producer: IMessageProducer) -> None:
        self._message_producer = message_producer

        self._saga_definition = (
            # Unification
            self.step()
            .invoke_participant(SagaData.perform_unification)
            .on_reply(PerformUnificationReply, Handlers.evaluate_error_from_reply)
            # Parsing
            .step()
            .invoke_local(steps.set_parsing_state)
            .step()
            .invoke_participant(SagaData.perform_parsing, predicate=SagaData.is_invoke_next_step)
            .on_reply(PerformParsingReply, Handlers.evaluate_error_from_reply)
            # Classification
            .step()
            .invoke_local(steps.set_classification_state)
            .step()
            .invoke_local(steps.classify)
            # # Document creation
            .step()
            .invoke_local(steps.set_document_creation_state)
            .step()
            .invoke_local(steps.upload_blob_for_document)
            .with_compensation(steps.delete_blob_for_document)
            .step()
            .invoke_participant(SagaData.perform_document_creation, predicate=SagaData.is_invoke_next_step)
            .on_reply(CreateDocumentFromFileReply, Handlers.evaluate_document_creation_reply)
            .step()
            .invoke_local(steps.set_completed_state)
            .build()
        )

        self._logger = logging.getLogger(self.__class__.__name__)

    def on_saga_completed_successfully(self, saga_id: str, data: SagaData) -> None:
        self._logger.info(
            "File Classification Saga for file `%s` completed successfully, classified as `%s`",
            data.file_id,
            data.document_type_id,
        )

        self._send_reply(
            reply=ClassifyFileReply(
                file_id=data.file_id,
                document_id=data.document_id,
                document_name=data.document_name,
                document_type_id=data.document_type_id,
            ),
            routing_info=data.routing_info,
        )

    def on_saga_rolled_back(self, saga_id: str, data: SagaData) -> None:
        self._send_failure_reply(saga_id, data, "is rolled back")

    def on_saga_failed(self, saga_id: str, data: SagaData) -> None:
        self._send_failure_reply(saga_id, data, "is failed")

    def _send_failure_reply(self, saga_id: str, data: SagaData, reason: str) -> None:
        error_message = f"Saga: {saga_id} for file: {data.file_id} {reason}"
        self._logger.warning(error_message)

        self._send_reply(
            reply=ClassifyFileReply(
                file_id=data.file_id,
                document_name=data.document_name,
                error_type=data.error.type.value if data.error else ErrorType.SYSTEM.value,
                error_message=data.error.message if data.error else error_message,
            ),
            routing_info=data.routing_info,
        )

    def _send_reply(self, reply: Command, routing_info: dict[str, str]) -> None:
        destination, message = SagaReplyBuilder.for_routing_info(routing_info).with_success(reply)
        self._message_producer.send(destination=destination, message=message)
