from deps_classification.domain.exceptions import ClassificationException

__all__ = ["RestClientError"]


class RestClientError(ClassificationException):
    code = "rest_client_error"
