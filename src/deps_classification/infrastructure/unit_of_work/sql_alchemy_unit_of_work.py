from sqlalchemy.orm import Session

from deps_classification.extras import DatabaseSession

from ..repositories import (
    UoWCommandDocumentTypeRepository,
    UoWCommandGenAIClassifierRepository,
    UoWCommandGroupRepository,
)
from .abstract_unit_of_work import AbstractUnitOfWork

__all__ = ["SqlAlchemyUnitOfWork"]


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    _session: Session

    def __init__(self, database_session: DatabaseSession) -> None:
        self._database_session = database_session

    def __enter__(self) -> None:
        with self._database_session.connect() as session:
            self._session = session

            self.groups = UoWCommandGroupRepository(session)
            self.gen_ai_classifiers = UoWCommandGenAIClassifierRepository(session)
            self.document_types = UoWCommandDocumentTypeRepository(session)

    def commit(self):
        self._session.commit()

    def rollback(self):
        self._session.rollback()
