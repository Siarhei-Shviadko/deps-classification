from sqlalchemy import Column, and_, delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from deps_classification.domain.model import (
    GenAIClassifierDisplayInfo,
    IQueryGenAIClassifierRepository,
)
from deps_classification.extras import DatabaseSession

from ..tables import gen_ai_classifier_table
from .gen_ai_classifier_info_mapper import GenAIClassifiersInfoMapper

__all__ = ["QueryGenAIClassifierRepository"]


class QueryGenAIClassifierRepository(IQueryGenAIClassifierRepository):
    def __init__(self, database: DatabaseSession) -> None:
        self._db = database

    def find_all_classifier_display_info_of_group(
        self,
        group_id: str,
        tenant_id: str,
    ) -> list[GenAIClassifierDisplayInfo]:
        query = select(
            [
                gen_ai_classifier_table.c.gen_ai_classifier_id,
                gen_ai_classifier_table.c.document_type_id,
                gen_ai_classifier_table.c.prompt,
                gen_ai_classifier_table.c.llm_type,
                gen_ai_classifier_table.c.name,
            ],
        ).where(
            and_(
                gen_ai_classifier_table.c.group_id == group_id,
                gen_ai_classifier_table.c.tenant_id == tenant_id,
            ),
        )

        with self._db.connection() as conn:
            return GenAIClassifiersInfoMapper.from_gen_ai_classifier_rows(conn.execute(query).fetchall())

    def find_all_classifier_display_info_of_document_type(
        self,
        document_type_id: str,
        tenant_id: str,
    ) -> list[GenAIClassifierDisplayInfo]:
        query = select(
            [
                gen_ai_classifier_table.c.gen_ai_classifier_id,
                gen_ai_classifier_table.c.document_type_id,
                gen_ai_classifier_table.c.prompt,
                gen_ai_classifier_table.c.llm_type,
                gen_ai_classifier_table.c.name,
            ],
        ).where(
            and_(
                gen_ai_classifier_table.c.document_type_id == document_type_id,
                gen_ai_classifier_table.c.tenant_id == tenant_id,
            ),
        )

        with self._db.connection() as conn:
            return GenAIClassifiersInfoMapper.from_gen_ai_classifier_rows(conn.execute(query).fetchall())
