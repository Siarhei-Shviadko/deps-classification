from ..generic import RestClientError

__all__ = ["AIFusionProxyRequestError"]


class AIFusionProxyRequestError(RestClientError):
    code = "ai_fusion_proxy_request_error"

    def __init__(self, error_response: str) -> None:
        super().__init__(f"Error while making request to AI Fusion Service. Reason: ```{error_response}```")
