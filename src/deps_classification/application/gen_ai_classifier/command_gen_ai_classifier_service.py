import logging
from typing import Optional

from deps_message_flow.events.publisher import DomainEventPublisher

from deps_classification.constants import CLASSIFICATION_DESTINATION
from deps_classification.domain.exceptions import (
    GenAIClassifierAlreadyExists,
    GenAIClassifierNotFound,
    GenAIClassifierWithNameAlreadyExists,
    GroupWithDocumentTypeNotFound,
)
from deps_classification.domain.model import GenAIClassifier, GenAIClassifierFactory
from deps_classification.infrastructure.unit_of_work import AbstractUnitOfWork

from ..retry_transaction import retry_on_transaction_error

__all__ = ["CommandGenAIClassifierService"]


class CommandGenAIClassifierService:
    def __init__(
        self,
        unit_of_work: AbstractUnitOfWork,
        domain_event_publisher: DomainEventPublisher,
    ) -> None:
        self._uow = unit_of_work
        self._domain_event_publisher = domain_event_publisher

        self._logger = logging.getLogger(self.__class__.__name__)

    @retry_on_transaction_error()
    def create(
        self,
        group_id: str,
        tenant_id: str,
        document_type_id: str,
        prompt: str,
        llm_type: str,
        name: str,
    ) -> GenAIClassifier:
        with self._uow:
            self._check_gen_ai_classifier_name(name, group_id, tenant_id)
            self._check_gen_ai_classifier_for_group(group_id, tenant_id, document_type_id)
            self._check_group_with_document_type(group_id, document_type_id)

            gen_ai_classifier = GenAIClassifierFactory.create(
                tenant_id=tenant_id,
                group_id=group_id,
                document_type_id=document_type_id,
                prompt=prompt,
                llm_type=llm_type,
                name=name,
            )

            self._uow.gen_ai_classifiers.save(gen_ai_classifier)

            self._uow.commit()

        self._logger.info("GenAIClassifier with id `%s` is saved.", gen_ai_classifier.id())

        return gen_ai_classifier

    @retry_on_transaction_error()
    def update(
        self,
        gen_ai_classifier_id: str,
        tenant_id: str,
        prompt: Optional[str],
        llm_type: Optional[str],
        name: Optional[str],
    ) -> GenAIClassifier:
        with self._uow:
            gen_ai_classifier = self._find_gen_ai_classifier(
                gen_ai_classifier_id=gen_ai_classifier_id,
                tenant_id=tenant_id,
            )

            group_id = gen_ai_classifier.group_id.value
            if name and gen_ai_classifier.name != name:
                self._check_gen_ai_classifier_name(name, group_id, tenant_id)

            if all(value_to_update is None for value_to_update in (prompt, llm_type, name)):
                return gen_ai_classifier

            gen_ai_classifier.update(prompt=prompt, llm_type=llm_type, name=name)

            self._uow.gen_ai_classifiers.save(gen_ai_classifier)
            self._uow.commit()

        self._logger.info("GenAIClassifier with id `%s` is updated.", gen_ai_classifier.id())

        return gen_ai_classifier

    @retry_on_transaction_error()
    def delete(
        self,
        gen_ai_classifier_ids: list[str],
        tenant_id: str,
    ) -> list[GenAIClassifier]:
        with self._uow:
            gen_ai_classifiers = self._uow.gen_ai_classifiers.gen_ai_classifiers_of_ids(
                gen_ai_classifier_ids,
                tenant_id,
            )

            for gen_ai_classifier in gen_ai_classifiers:
                gen_ai_classifier.delete()

            self._uow.gen_ai_classifiers.delete_all(gen_ai_classifiers)
            self._uow.commit()

        self._logger.info("GenAIClassifiers with ids `%s` are deleted.", gen_ai_classifier_ids)

        return gen_ai_classifiers

    @retry_on_transaction_error()
    def delete_for_group_document_types(
        self,
        group_id: str,
        tenant_id: str,
        document_type_ids: list[str],
    ) -> list[GenAIClassifier]:
        with self._uow:
            gen_ai_classifiers = self._uow.gen_ai_classifiers.gen_ai_classifiers_of_group(
                group_id,
                tenant_id,
                document_type_ids,
            )

            for gen_ai_classifier in gen_ai_classifiers:
                gen_ai_classifier.delete()

            self._uow.gen_ai_classifiers.delete_all(gen_ai_classifiers)
            self._uow.commit()

        self._logger.info(
            "Group (`%s`) GenAIClassifiers for Document Types `%s` are deleted.",
            group_id,
            document_type_ids,
        )

        return gen_ai_classifiers

    @retry_on_transaction_error()
    def delete_for_document_type(
        self,
        document_type_id: str,
        tenant_id: str,
    ) -> list[GenAIClassifier]:
        with self._uow:
            gen_ai_classifiers = self._uow.gen_ai_classifiers.gen_ai_classifiers_of_document_type(
                document_type_id,
                tenant_id,
            )

            for gen_ai_classifier in gen_ai_classifiers:
                gen_ai_classifier.delete()

            self._uow.gen_ai_classifiers.delete_all(gen_ai_classifiers)
            self._uow.commit()

        self._logger.info(
            "Document Type (`%s`) GenAIClassifiers are deleted.",
            document_type_id,
        )

        return gen_ai_classifiers

    def _check_gen_ai_classifier_name(self, name: str, group_id: str, tenant_id: str) -> None:
        if self._uow.gen_ai_classifiers.has_gen_ai_classifier_with_name(name, group_id, tenant_id):
            raise GenAIClassifierWithNameAlreadyExists(name=name)

    def _check_gen_ai_classifier_for_group(self, group_id: str, tenant_id: str, document_type_id: str) -> None:
        if self._uow.gen_ai_classifiers.has_gen_ai_classifier_for_group(group_id, tenant_id, document_type_id):
            raise GenAIClassifierAlreadyExists(group_id=group_id)

    def _check_group_with_document_type(self, group_id: str, document_type_id: str) -> None:
        if not self._uow.groups.has_group_with_document_type(group_id, document_type_id):
            raise GroupWithDocumentTypeNotFound(group_id=group_id, document_type_id=document_type_id)

    def _find_gen_ai_classifier(self, gen_ai_classifier_id: str, tenant_id: str) -> GenAIClassifier:
        if (
            gen_ai_classifier := self._uow.gen_ai_classifiers.gen_ai_classifier_of_id(gen_ai_classifier_id, tenant_id)
        ) is None:
            raise GenAIClassifierNotFound(gen_ai_classifier_id=gen_ai_classifier_id)

        return gen_ai_classifier

    def _publish_events(self, gen_ai_classifier: GenAIClassifier) -> None:
        self._domain_event_publisher.publish(
            aggregate_type=CLASSIFICATION_DESTINATION,
            aggregate_id=gen_ai_classifier.id(),
            domain_events=gen_ai_classifier.events,
        )
