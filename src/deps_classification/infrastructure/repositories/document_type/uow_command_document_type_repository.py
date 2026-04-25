from sqlalchemy import delete
from sqlalchemy.orm import Session

from deps_classification.domain.model import ICommandDocumentTypeRepository

from ..tables import group_document_types_table

__all__ = ["UoWCommandDocumentTypeRepository"]


class UoWCommandDocumentTypeRepository(ICommandDocumentTypeRepository):
    def __init__(self, connection: Session) -> None:
        self._connection = connection

    def delete(self, document_type_id: str) -> None:
        delete_command = delete(group_document_types_table).where(
            group_document_types_table.c.document_type_id == document_type_id,
        )

        self._connection.execute(delete_command)
