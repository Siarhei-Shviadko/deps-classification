import logging

from deps_classification.infrastructure.services import UNKNOWN, ClassificationService

from .classification_saga_data import ClassificationSagaData

__all__ = ["ClassificationSagaSteps"]


class ClassificationSagaSteps:
    def __init__(self, classification_service: ClassificationService) -> None:
        self._classification_service = classification_service

        self._logger = logging.getLogger(self.__class__.__name__)

    def classify(self, data: ClassificationSagaData) -> None:
        classified_document_type_id = self._classification_service.classify(
            document_id=data.document_id,
            tenant_id=data.tenant_id,
            document_type_group_id=data.group_id,
        )

        if classified_document_type_id is not UNKNOWN:
            data.document_type_id = classified_document_type_id
