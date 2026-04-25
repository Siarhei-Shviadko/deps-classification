import logging

from deps_classification.infrastructure.services import UNKNOWN, ClassificationService

from ..shared import ErrorType, State
from .handlers import BatchFileClassificationHandlers
from .saga_data import BatchFileClassificationSagaData

__all__ = ["BatchFileClassificationSagaSteps"]


class BatchFileClassificationSagaSteps:
    def __init__(self, classification_service: ClassificationService) -> None:
        self._classification_service = classification_service

        self._logger = logging.getLogger(self.__class__.__name__)

    def set_parsing_state(self, data: BatchFileClassificationSagaData) -> None:
        data.set_saga_state(state=State.PARSING)

    def set_classification_state(self, data: BatchFileClassificationSagaData) -> None:
        data.set_saga_state(state=State.CLASSIFICATION)

    def set_document_creation_state(self, data: BatchFileClassificationSagaData) -> None:
        data.set_saga_state(state=State.DOCUMENT_CREATION)

    def set_completed_state(self, data: BatchFileClassificationSagaData) -> None:
        data.set_saga_state(state=State.COMPLETED)

    def classify(self, data: BatchFileClassificationSagaData) -> None:
        classified_document_type_id = self._classification_service.classify(
            document_id=data.file_id,
            tenant_id=data.tenant_id,
            document_type_group_id=data.group_id,
        )

        if classified_document_type_id is UNKNOWN:
            data.error = BatchFileClassificationHandlers.build_error(
                state=data.current_state,
                type_=ErrorType.BUSINESS,
                message="Document type is not classified",
            )
        else:
            data.document_type_id = classified_document_type_id
