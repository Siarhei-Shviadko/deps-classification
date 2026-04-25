import logging

from deps_message_flow.events.publisher import DomainEventPublisher
from deps_message_flow.sagas.orchestration_simple_dsl import SimpleSaga

from deps_classification.constants import DOCUMENTS_EXCHANGER

from ..shared import (
    PerformParsingReply,
    PerformUnificationReply,
    SagaFailed,
    SagaRolledBack,
)
from .classification_handlers import ClassificationHandlers as Handlers
from .classification_saga_data import ClassificationSagaData as SagaData
from .classification_steps import ClassificationSagaSteps as Steps

__all__ = ["ClassificationSaga"]


class ClassificationSaga(SimpleSaga[SagaData]):
    def __init__(
        self,
        domain_event_publisher: DomainEventPublisher,
        steps: Steps,
    ) -> None:
        self._domain_event_publisher = domain_event_publisher

        self._saga_definition = (
            # Unification
            self.step()
            .invoke_participant(
                SagaData.set_unification_state,
            )
            .step()
            .invoke_participant(
                SagaData.perform_unification,
            )
            .on_reply(PerformUnificationReply, Handlers.evaluate_error_from_reply)
            # Parsing
            .step()
            .invoke_participant(
                SagaData.set_parsing_state,
                predicate=SagaData.is_invoke_update,
            )
            .step()
            .invoke_participant(
                SagaData.perform_parsing,
                predicate=SagaData.is_invoke_next_step,
            )
            .on_reply(PerformParsingReply, Handlers.evaluate_error_from_reply)
            # Classification
            .step()
            .invoke_participant(
                SagaData.set_classification_state,
                predicate=SagaData.is_invoke_update,
            )
            .step()
            .invoke_local(steps.classify)
            # Document type assignment
            .step()
            .invoke_participant(
                SagaData.set_error_state,
                predicate=SagaData.is_local_step_failed,
            )
            .build()
        )

        self._logger = logging.getLogger(self.__class__.__name__)

    def on_saga_completed_successfully(self, saga_id: str, data: SagaData) -> None:
        self._logger.info(
            "Classification Saga for document `%s` completed successfully, classified as `%s`",
            data.document_id,
            data.document_type_id,
        )

        if data.error is None:
            self._domain_event_publisher.publish(
                DOCUMENTS_EXCHANGER,
                data.document_id,
                [data.classification_completed_event],
            )

    def on_saga_rolled_back(self, saga_id: str, data: SagaData) -> None:
        self._logger.warning(
            "Saga: %s for document %s classification is rolled back",
            saga_id,
            data.document_id,
        )

        raise SagaRolledBack("Document classification saga failed and rolled back")

    def on_saga_failed(self, saga_id: str, data: SagaData) -> None:
        self._logger.error(
            "Saga: %s for document %s classification is failed",
            saga_id,
            data.document_id,
            exc_info=True,
        )

        raise SagaFailed("Document classification saga failed")
