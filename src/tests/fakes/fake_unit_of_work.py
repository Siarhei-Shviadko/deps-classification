from deps_classification.infrastructure.unit_of_work import AbstractUnitOfWork

__all__ = ["FakeUnitOfWork"]


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(
        self,
        users,
        gen_ai_classifiers,
    ) -> None:
        self.users = users
        self.gen_ai_classifiers = gen_ai_classifiers

    def __enter__(self) -> None:
        pass

    def commit(self):
        pass

    def rollback(self):
        pass
