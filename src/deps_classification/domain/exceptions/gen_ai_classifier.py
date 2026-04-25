from .base import AlreadyExistsError, NotFoundError

__all__ = ["GenAIClassifierNotFound", "GenAIClassifierAlreadyExists", "GenAIClassifierWithNameAlreadyExists"]


class GenAIClassifierNotFound(NotFoundError):
    code = "gen_ai_classifier_not_found"

    def __init__(self, gen_ai_classifier_id: str) -> None:
        super().__init__(f"GenAIClassifier with id `{gen_ai_classifier_id}` not found.")


class GenAIClassifierAlreadyExists(AlreadyExistsError):
    code = "gen_ai_classifier_already_exists"

    def __init__(self, group_id: str) -> None:
        super().__init__(f"GenAIClassifier for Group with id `{group_id}` already exists.")


class GenAIClassifierWithNameAlreadyExists(AlreadyExistsError):
    code = "gen_ai_classifier_with_name_already_exists"

    def __init__(self, name: str) -> None:
        super().__init__(f"Classifier with name `{name}` already exists.")
