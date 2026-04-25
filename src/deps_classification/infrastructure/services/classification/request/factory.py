from deps_classification.domain.model import GenAIClassifier

from ..types import INSIGHT_KEY, ClassificationRequest, RawDocumentTypesClassification
from .response_model import ClassificationResponseModel

__all__ = ["ClassificationRequestFactory"]


class ClassificationRequestFactory:
    def __init__(self, classifiers: list[GenAIClassifier]) -> None:
        self.classifiers = classifiers

    @classmethod
    def from_classifiers(cls, classifiers: list[GenAIClassifier]) -> "ClassificationRequestFactory":
        return cls(classifiers)

    def compose_request(self) -> ClassificationRequest:
        return {
            INSIGHT_KEY: self._classification_request(),  # type: ignore
        }

    def _classification_request(self) -> RawDocumentTypesClassification:
        categories_prompts = [
            f"- CategoryId: `{classifier.document_type_id()}`, Category prompt: `{classifier.prompt}`"
            for classifier in self.classifiers
        ]
        categories_description = "\n".join(categories_prompts)
        prompt = f"Classify the document into one of the following categories:\n{categories_description}"

        return {
            "workflow": {
                "prompts": [{"content": prompt}],
                "responseModel": ClassificationResponseModel.schema(),
            },
        }
