from typing import Protocol

__all__ = ["ICommandDocumentTypeRepository"]


class ICommandDocumentTypeRepository(Protocol):
    def delete(self, document_type_id: str) -> None:
        pass
