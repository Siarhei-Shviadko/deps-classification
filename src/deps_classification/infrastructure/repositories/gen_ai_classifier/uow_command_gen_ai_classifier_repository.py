from sqlalchemy import Column, and_, delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from deps_classification.domain.model import (
    GenAIClassifier,
    ICommandGenAIClassifierRepository,
)

from ..tables import gen_ai_classifier_table
from .gen_ai_classifier_mapper import GenAIClassifierMapper

__all__ = ["UoWCommandGenAIClassifierRepository"]


class UoWCommandGenAIClassifierRepository(ICommandGenAIClassifierRepository):
    def __init__(self, connection: Session) -> None:
        self._connection = connection

    @property
    def gen_ai_classifier_table(self) -> list[Column]:
        return [
            gen_ai_classifier_table.c.gen_ai_classifier_id,
            gen_ai_classifier_table.c.tenant_id,
            gen_ai_classifier_table.c.group_id,
            gen_ai_classifier_table.c.document_type_id,
            gen_ai_classifier_table.c.prompt,
            gen_ai_classifier_table.c.llm_type,
            gen_ai_classifier_table.c.created_at,
            gen_ai_classifier_table.c.updated_at,
            gen_ai_classifier_table.c.name,
        ]

    def gen_ai_classifier_of_id(self, gen_ai_classifier_id: str, tenant_id: str) -> GenAIClassifier | None:
        query = select(*self.gen_ai_classifier_table).where(
            and_(
                gen_ai_classifier_table.c.gen_ai_classifier_id == gen_ai_classifier_id,
                gen_ai_classifier_table.c.tenant_id == tenant_id,
            ),
        )

        result = self._connection.execute(query).mappings().fetchone()
        if result is None:
            return None

        return GenAIClassifierMapper.from_dict(result)

    def gen_ai_classifiers_of_ids(self, gen_ai_classifier_ids: list[str], tenant_id: str) -> list[GenAIClassifier]:
        query = select(*self.gen_ai_classifier_table).where(
            and_(
                gen_ai_classifier_table.c.gen_ai_classifier_id.in_(gen_ai_classifier_ids),
                gen_ai_classifier_table.c.tenant_id == tenant_id,
            ),
        )

        results = self._connection.execute(query).mappings().fetchall()
        return [GenAIClassifierMapper.from_dict(result) for result in results]

    def gen_ai_classifiers_of_group(
        self,
        group_id: str,
        tenant_id: str,
        document_type_ids: list[str] | None = None,
    ) -> list[GenAIClassifier]:
        query = select(*self.gen_ai_classifier_table).where(
            and_(
                gen_ai_classifier_table.c.group_id == group_id,
                gen_ai_classifier_table.c.tenant_id == tenant_id,
            ),
        )

        if document_type_ids is not None:
            query = query.where(gen_ai_classifier_table.c.document_type_id.in_(document_type_ids))

        results = self._connection.execute(query).mappings().fetchall()
        return [GenAIClassifierMapper.from_dict(result) for result in results]

    def gen_ai_classifiers_of_document_type(
        self,
        document_type_id: str,
        tenant_id: str,
    ) -> list[GenAIClassifier]:
        query = select(*self.gen_ai_classifier_table).where(
            and_(
                gen_ai_classifier_table.c.document_type_id == document_type_id,
                gen_ai_classifier_table.c.tenant_id == tenant_id,
            ),
        )

        results = self._connection.execute(query).mappings().fetchall()

        return [GenAIClassifierMapper.from_dict(result) for result in results]

    def has_gen_ai_classifier_for_group(self, group_id: str, tenant_id: str, document_type_id: str) -> bool:
        query = select(gen_ai_classifier_table.c.gen_ai_classifier_id).where(
            and_(
                gen_ai_classifier_table.c.group_id == group_id,
                gen_ai_classifier_table.c.tenant_id == tenant_id,
                gen_ai_classifier_table.c.document_type_id == document_type_id,
            ),
        )

        result = self._connection.execute(query).fetchone()
        return result is not None

    def has_gen_ai_classifier_with_name(self, name: str, group_id: str, tenant_id: str) -> bool:
        query = select(gen_ai_classifier_table.c.gen_ai_classifier_id).where(
            and_(
                gen_ai_classifier_table.c.name == name,
                gen_ai_classifier_table.c.group_id == group_id,
                gen_ai_classifier_table.c.tenant_id == tenant_id,
            ),
        )

        result = self._connection.execute(query).fetchone()
        return result is not None

    def save(self, gen_ai_classifier: GenAIClassifier) -> None:
        data = GenAIClassifierMapper.to_dict(gen_ai_classifier)

        insert_command = insert(gen_ai_classifier_table).values(data)
        update_command = insert_command.on_conflict_do_update(
            index_elements=[gen_ai_classifier_table.c.gen_ai_classifier_id],
            set_=data,
        )

        self._connection.execute(update_command)

    def delete_all(self, gen_ai_classifiers: list[GenAIClassifier]) -> None:
        if not gen_ai_classifiers:
            return

        tenant_id = gen_ai_classifiers[0].tenant_id()
        gen_ai_classifier_ids = [gen_ai_classifier.id() for gen_ai_classifier in gen_ai_classifiers]

        delete_command = delete(gen_ai_classifier_table).where(
            and_(
                gen_ai_classifier_table.c.gen_ai_classifier_id.in_(gen_ai_classifier_ids),
                gen_ai_classifier_table.c.tenant_id == tenant_id,
            ),
        )

        self._connection.execute(delete_command)

    def erase_all_gen_ai_classifiers(self) -> None:
        self._connection.execute(delete(gen_ai_classifier_table))
