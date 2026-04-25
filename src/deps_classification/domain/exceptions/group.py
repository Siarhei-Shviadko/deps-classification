from .base import NotFoundError

__all__ = ["GroupNotFound", "GroupWithDocumentTypeNotFound"]


class GroupNotFound(NotFoundError):
    code = "group_not_found"

    def __init__(self, group_id: str) -> None:
        super().__init__(f"Group with id `{group_id}` not found.")


class GroupWithDocumentTypeNotFound(NotFoundError):
    code = "group_with_document_type_not_found"

    def __init__(self, group_id: str, document_type_id: str) -> None:
        super().__init__(f"Group `{group_id}` with Document Type `{document_type_id}` not found.")
