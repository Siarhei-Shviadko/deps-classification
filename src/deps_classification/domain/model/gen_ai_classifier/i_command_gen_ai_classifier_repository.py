from typing import Protocol

from .gen_ai_classifier import GenAIClassifier

__all__ = ["ICommandGenAIClassifierRepository"]


class ICommandGenAIClassifierRepository(Protocol):
    def gen_ai_classifier_of_id(self, gen_ai_classifier_id: str, tenant_id: str) -> GenAIClassifier | None:
        pass

    def gen_ai_classifiers_of_ids(self, gen_ai_classifier_ids: list[str], tenant_id: str) -> list[GenAIClassifier]:
        pass

    def gen_ai_classifiers_of_group(
        self,
        group_id: str,
        tenant_id: str,
        document_type_ids: list[str] | None = None,
    ) -> list[GenAIClassifier]:
        pass

    def has_gen_ai_classifier_for_group(self, group_id: str, tenant_id: str, document_type_id: str) -> bool:
        pass

    def has_gen_ai_classifier_with_name(self, name: str, group_id: str, tenant_id: str) -> bool:
        pass

    def save(self, gen_ai_classifier: GenAIClassifier) -> None:
        pass

    def delete_all(self, gen_ai_classifiers: list[GenAIClassifier]) -> None:
        pass
