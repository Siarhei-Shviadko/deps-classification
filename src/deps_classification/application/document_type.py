import logging

from deps_message_flow.events.publisher import DomainEventPublisher

from deps_classification.constants import CLASSIFICATION_DESTINATION
from deps_classification.domain.model import DocumentTypeDeleted
from deps_classification.infrastructure.unit_of_work import AbstractUnitOfWork

from .retry_transaction import retry_on_transaction_error

__all__ = ["DocumentTypeService"]


class DocumentTypeService:
    def __init__(
        self,
        unit_of_work: AbstractUnitOfWork,
        domain_event_publisher: DomainEventPublisher,
    ) -> None:
        self._uow = unit_of_work
        self._domain_event_publisher = domain_event_publisher
        self._logger = logging.getLogger(self.__class__.__name__)

    @retry_on_transaction_error()
    def delete(self, document_type_id: str) -> str:
        with self._uow:
            self._uow.document_types.delete(document_type_id)
            self._uow.commit()

        self._logger.info("Document Type %s is deleted.", document_type_id)

        return document_type_id

    def delete_and_republish(self, document_type_id: str, original_event: DocumentTypeDeleted) -> str:
        self.delete(document_type_id)

        self._publish_event(document_type_id, original_event)

        self._logger.info("Published classifier deletion event for document type %s", document_type_id)

        return document_type_id

    def _publish_event(self, document_type_id: str, original_event: DocumentTypeDeleted) -> None:
        self._domain_event_publisher.publish(
            aggregate_type=CLASSIFICATION_DESTINATION,
            aggregate_id=document_type_id,
            domain_events=[original_event],
        )
