import logging

from deps_classification.infrastructure.services.classification import (
    ClassificationRequest,
    IPromptedClassifier,
    RawClassificationResponse,
)

from ..generic import GenericProxy
from .exceptions import AIFusionProxyRequestError

__all__ = ["AIFusionProxy"]


class AIFusionProxy(GenericProxy, IPromptedClassifier):
    url_suffix = "/api/ai-fusion/v1"
    exception = AIFusionProxyRequestError

    def __init__(self, base_url: str, timeout: int = 60, ssl_verify: bool = False) -> None:
        super().__init__(base_url)
        self._timeout = timeout
        self._ssl_verify = ssl_verify

        self._logger = logging.getLogger(self.__class__.__name__)

    def classify_document(
        self,
        document_id: str,
        llm_reference: str,
        dt_classification_request: ClassificationRequest,
        custom_instructions: str,
        grouping_factor: int | None = None,
        temperature: int | None = None,
    ) -> RawClassificationResponse:
        url = f"{self._base_url}{self.url_suffix}/analysis/retrieve-insights"
        data = {
            "documentId": document_id,
            "model": llm_reference,
            "requestedInsights": dt_classification_request,
            "customInstructions": custom_instructions,
            "params": {"temperature": temperature, "groupingFactor": grouping_factor},
        }

        response = self._session.post(url, json=data, timeout=self._timeout, verify=self._ssl_verify)

        self._check_response(response)

        return response.json()
