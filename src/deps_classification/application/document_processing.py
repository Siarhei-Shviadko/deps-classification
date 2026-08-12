import logging
from typing import Any, Optional

from deps_message_flow.sagas.orchestration import Saga, SagaInstanceFactory

from deps_classification.messaging import (
    BatchFileClassificationSaga,
    BatchFileClassificationSagaData,
    ClassificationSaga,
    ClassificationSagaData,
    FileClassificationSaga,
    FileClassificationSagaData,
)

__all__ = ["DocumentProcessingService"]


class DocumentProcessingService:
    def __init__(
        self,
        saga_instance_factory: SagaInstanceFactory,
        sagas: list[Saga],
    ) -> None:
        self._sagas = {saga.__class__: saga for saga in sagas}
        self._saga_instance_factory = saga_instance_factory

        self._logger = logging.getLogger(self.__class__.__name__)

    def process_document(
        self,
        document_id: str,
        tenant_id: str,
        group_id: str,
        files: list[str],
        engine: Optional[str] = None,
        language: Optional[str] = None,
        parsing_features: Optional[list[str]] = None,
    ) -> None:
        data = ClassificationSagaData(
            document_id=document_id,
            tenant_id=tenant_id,
            group_id=group_id,
            files=files,
            engine=engine,
            language=language,
            parsing_features=parsing_features,
        )

        si = self._saga_instance_factory.create(
            self._sagas[ClassificationSaga],
            data,
        )

        self._logger.info("Processing of document %s is started with saga %s.", document_id, si.saga_id)

    def classify_file(
        self,
        file_id: str,
        tenant_id: str,
        file_path: str,
        file_name: str,
        group_id: str,
        routing_info: dict[str, str],
        parsing_features: list[str] | None = None,
        engine: str | None = None,
        language: str | None = None,
        llm_type: str | None = None,
        needs_unifier: bool = False,
        needs_extraction: bool = False,
        assigned_to_me: bool = False,
        metadata: dict[str, Any] | None = None,
        label_ids: list[str] | None = None,
        start_processing: bool = False,
    ) -> None:
        data = FileClassificationSagaData(
            file_id=file_id,
            tenant_id=tenant_id,
            file_path=file_path,
            document_name=file_name,
            group_id=group_id,
            engine=engine,
            language=language,
            parsing_features=parsing_features,
            llm_type=llm_type,
            needs_unifier=needs_unifier,
            needs_extraction=needs_extraction,
            assigned_to_me=assigned_to_me,
            metadata=metadata,
            label_ids=label_ids,
            start_processing=start_processing,
            routing_info=routing_info,
        )

        si = self._saga_instance_factory.create(
            self._sagas[FileClassificationSaga],
            data,
        )

        self._logger.info("Classification of file %s is started with saga %s.", file_id, si.saga_id)

    def classify_batch_file(
        self,
        batch_id: str,
        file_id: str,
        tenant_id: str,
        file_path: str,
        file_name: str,
        group_id: str,
        replies_channel: str,
        parsing_features: list[str] | None = None,
        engine: str | None = None,
        language: str | None = None,
        llm_type: str | None = None,
        needs_unifier: bool = False,
        needs_extraction: bool = False,
        assigned_to_me: bool = False,
        metadata: dict[str, Any] | None = None,
        start_processing: bool = False,
    ) -> None:
        data = BatchFileClassificationSagaData(
            batch_id=batch_id,
            file_id=file_id,
            tenant_id=tenant_id,
            file_path=file_path,
            document_name=file_name,
            group_id=group_id,
            engine=engine,
            language=language,
            parsing_features=parsing_features,
            llm_type=llm_type,
            needs_unifier=needs_unifier,
            needs_extraction=needs_extraction,
            assigned_to_me=assigned_to_me,
            metadata=metadata,
            start_processing=start_processing,
            replies_channel=replies_channel,
        )

        si = self._saga_instance_factory.create(
            self._sagas[BatchFileClassificationSaga],
            data,
        )

        self._logger.info("Classification of batch file %s is started with saga %s.", file_id, si.saga_id)
