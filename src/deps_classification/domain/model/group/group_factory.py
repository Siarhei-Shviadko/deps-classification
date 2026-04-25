from .group import Group

__all__ = ["GroupFactory"]


class GroupFactory:
    @classmethod
    def create(cls, id_: str, tenant_id: str, document_types: list[str]) -> Group:
        return Group(
            id_=id_,
            tenant_id=tenant_id,
            document_types=document_types,
        )
