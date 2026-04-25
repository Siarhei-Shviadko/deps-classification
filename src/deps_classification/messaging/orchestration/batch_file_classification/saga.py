import logging

from deps_message_flow.commands.common import Command, make_message_for_command
from deps_message_flow.events.mappers import JsonMapper
from deps_message_flow.messaging.producer import IMessageProducer
from deps_message_flow.sagas.orchestration_simple_dsl import SimpleSaga

from ...commands import ClassifyBatchFileReply
from ..shared import (
    CreateDocumentFromFileReply,
    ErrorType,
    PerformParsingReply,
    PerformUnificationReply,
)
from .handlers import BatchFileClassificationHandlers as Handlers
from .saga_data import BatchFileClassificationSagaData as SagaData
from .steps import BatchFileClassificationSagaSteps as Steps

__all__ = ["BatchFileClassificationSaga"]


class BatchFileClassificationSaga(SimpleSaga[SagaData]):
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
            .invoke_participant(SagaData.perform_document_creation, predicate=SagaData.is_invoke_next_step)
            .on_reply(CreateDocumentFromFileReply, Handlers.evaluate_document_creation_reply)
            .step()
            .invoke_local(steps.set_completed_state)
            .build()
        )

        self._logger = logging.getLogger(self.__class__.__name__)

    def on_saga_completed_successfully(self, saga_id: str, data: SagaData) -> None:
        self._logger.info(
            "Batch File Classification Saga for file `%s` completed successfully, classified as `%s`",
            data.file_id,
            data.document_type_id,
        )

        self._send_reply(
            reply=ClassifyBatchFileReply(
                batch_id=data.batch_id,
                file_id=data.file_id,
                document_id=data.document_id,
                document_type_id=data.document_type_id,
            ),
            replies_channel=data.replies_channel,
        )

    def on_saga_rolled_back(self, saga_id: str, data: SagaData) -> None:
        self._send_failure_reply(saga_id, data, "is rolled back")

    def on_saga_failed(self, saga_id: str, data: SagaData) -> None:
        self._send_failure_reply(saga_id, data, "is failed")

    def _send_failure_reply(self, saga_id: str, data: SagaData, reason: str) -> None:
        error_message = f"Saga: {saga_id} for file: {data.file_id} {reason}"
        self._logger.warning(error_message)

        self._send_reply(
            reply=ClassifyBatchFileReply(
                batch_id=data.batch_id,
                file_id=data.file_id,
                error_type=data.error.type.value if data.error else ErrorType.SYSTEM.value,
                error_message=data.error.message if data.error else error_message,
            ),
            replies_channel=data.replies_channel,
        )

    def _send_reply(self, reply: Command, replies_channel: str) -> None:
        message = make_message_for_command(
            channel=replies_channel,
            payload=JsonMapper().serialize(reply),
            command_type=reply.__class__.__name__,
            reply_to="NONE",
        )
        self._message_producer.send(destination=replies_channel, message=message)
