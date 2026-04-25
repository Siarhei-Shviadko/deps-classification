import random
from typing import Any

from deps_classification.infrastructure.services import (
    ClassificationRequest,
    IPromptedClassifier,
    RawClassificationResponse,
)

__all__ = ["FakeAIFusionProxy"]


class FakeAIFusionProxy(IPromptedClassifier):
    def __init__(self) -> None:
        self.saved_response: Any = None

    def classify_document(
        self,
        document_id: str,
        llm_reference: str,
        dt_classification_request: ClassificationRequest,
        custom_instructions: str,
        grouping_factor: int | None = None,
        temperature: int | None = None,
    ) -> RawClassificationResponse:
        if self.saved_response is None:
            random_dt_id = random.choice(list(dt_classification_request.keys()))
            self.saved_response = {  # type: ignore
                "elements": {
                    "insight-code": {
                        "content": random_dt_id,
                        "reasoning": "reasoning",
                        "confidence": 0.0,
                    },
                },
            }

        return self.saved_response  # type: ignore
