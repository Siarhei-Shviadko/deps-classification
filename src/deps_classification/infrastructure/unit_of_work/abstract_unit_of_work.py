import abc

from deps_classification.domain.model import (
    ICommandDocumentTypeRepository,
    ICommandGenAIClassifierRepository,
    ICommandGroupRepository,
)

__all__ = ["AbstractUnitOfWork"]


class AbstractUnitOfWork(abc.ABC):
    groups: ICommandGroupRepository
    gen_ai_classifiers: ICommandGenAIClassifierRepository
    document_types: ICommandDocumentTypeRepository

    def __exit__(self, *args):
        self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError
