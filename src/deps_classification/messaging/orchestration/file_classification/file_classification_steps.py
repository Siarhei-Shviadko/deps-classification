import logging
from pathlib import Path
from uuid import uuid4

from deps_object_storage import ObjectStorage

from deps_classification.infrastructure.services import UNKNOWN, ClassificationService

from ..shared import ErrorType, State
from .file_classification_handlers import FileClassificationHandlers
from .file_classification_saga_data import FileClassificationSagaData

__all__ = ["FileClassificationSagaSteps"]


class FileClassificationSagaSteps:
    def __init__(self, classification_service: ClassificationService, storage: ObjectStorage) -> None:
        self._classification_service = classification_service
        self._storage = storage

        self._logger = logging.getLogger(self.__class__.__name__)

    def set_parsing_state(self, data: FileClassificationSagaData) -> None:
        data.set_saga_state(state=State.PARSING)

    def set_classification_state(self, data: FileClassificationSagaData) -> None:
        data.set_saga_state(state=State.CLASSIFICATION)

    def set_document_creation_state(self, data: FileClassificationSagaData) -> None:
        data.set_saga_state(state=State.DOCUMENT_CREATION)

    def set_completed_state(self, data: FileClassificationSagaData) -> None:
        data.set_saga_state(state=State.COMPLETED)

    def classify(self, data: FileClassificationSagaData) -> None:
        classified_document_type_id = self._classification_service.classify(
            document_id=data.file_id,
            tenant_id=data.tenant_id,
            document_type_group_id=data.group_id,
        )

        if classified_document_type_id is UNKNOWN:
            data.error = FileClassificationHandlers.build_error(
                state=data.current_state,
                type_=ErrorType.BUSINESS,
                message="Document type is not classified",
            )
        else:
            data.document_type_id = classified_document_type_id

    def upload_blob_for_document(self, data: FileClassificationSagaData) -> None:
        data.file_path = self._storage.upload(
            path=self._generate_unique_file_name(data.file_path),
            content=self._storage.download(data.file_path),
            replace_if_exists=True,
        )

    def delete_blob_for_document(self, data: FileClassificationSagaData) -> None:
        self._storage.delete(data.file_path)

    @staticmethod
    def _generate_unique_file_name(file_name: str) -> str:
        return uuid4().hex + Path(file_name).suffix
