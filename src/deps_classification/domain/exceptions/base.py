__all__ = ["ClassificationException", "NotFoundError", "IllegalArgument"]


class ClassificationException(Exception):
    code = "classification_exception"


class BusinessException(ClassificationException):
    code = "business_exception"


class NotFoundError(ClassificationException):
    code = "not_found_error"


class AlreadyExistsError(ClassificationException):
    code = "already_created_error"


class IllegalArgument(ClassificationException):
    code = "illegal_argument"
