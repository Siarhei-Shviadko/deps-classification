from typing import Protocol

from .types import ClassificationRequest, RawClassificationResponse

__all__ = ["IPromptedClassifier"]


class IPromptedClassifier(Protocol):
    def classify_document(
        self,
        document_id: str,
        llm_reference: str,
        dt_classification_request: ClassificationRequest,
        custom_instructions: str,
        grouping_factor: int | None = None,
        temperature: int | None = None,
    ) -> RawClassificationResponse:
        pass
