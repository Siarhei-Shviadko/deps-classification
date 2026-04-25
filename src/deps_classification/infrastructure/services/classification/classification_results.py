import json
import logging

from deps_classification.domain.model import GenAIClassifier

from .types import (
    INSIGHT_KEY,
    T_UNKNOWN,
    UNKNOWN,
    DocumentTypeCode,
    RawClassificationResponse,
)

__all__ = ["ClassificationResult"]


class ClassificationResult:
    def __init__(
        self,
        for_classifiers: list[GenAIClassifier],
        response: RawClassificationResponse,
    ) -> None:
        self.available_doc_types = {classifier.document_type_id() for classifier in for_classifiers}
        self.response = response

        self._logger = logging.getLogger(self.__class__.__name__)

    @classmethod
    def handling_response(
        cls,
        for_classifiers: list[GenAIClassifier],
        response: RawClassificationResponse,
    ) -> "ClassificationResult":
        return cls(for_classifiers, response)

    def identify_document_type(self) -> DocumentTypeCode | T_UNKNOWN:
        response = self.response["elements"][INSIGHT_KEY]["content"]  # type: ignore

        try:
            parsed = json.loads(response)
        except json.JSONDecodeError:
            self._logger.error(f"Can't decode response for classification. AI Fusion responed with `{response}`")
            return UNKNOWN

        if "category_id" not in parsed:
            self._logger.warning("Classification responded with invalid structure! Setting 'Unknown' as document type.")
            return UNKNOWN
        if parsed["category_id"] is None:
            return UNKNOWN
        if parsed["category_id"] not in self.available_doc_types:
            self._logger.warning(
                "Classification responded with invalid document type! Setting 'Unknown' as document type.",
            )
            return UNKNOWN

        return parsed["category_id"]
