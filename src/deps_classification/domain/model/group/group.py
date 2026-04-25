from ..shared import EntityId, Event, Guard, ImmutableCheck, TenantId
from .document_type_removed import DocumentTypesRemoved
from .group_id import GroupId

__all__ = ["Group"]


class Group:
    id = Guard[GroupId](GroupId, ImmutableCheck())
    tenant_id = Guard[TenantId](TenantId, ImmutableCheck())
    document_types = Guard[list[EntityId]](list, ImmutableCheck())
    is_deleted = Guard[bool](bool)

    def __init__(
        self,
        id_: str,
        tenant_id: str,
        document_types: list[str],
        *,
        is_deleted: bool = False,
        events: list[Event] | None = None,
    ) -> None:
        self.id = GroupId(id_)
        self.tenant_id = TenantId(tenant_id)
        self.document_types = [EntityId(document_type) for document_type in document_types]

        self.is_deleted = is_deleted
        self.events = events or []

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and other.id == self.id

    def __repr__(self) -> str:
        return "\n".join(
            (
                f"<class '{self.__class__.__name__}':",
                f"{self.id = },",
                f"{self.tenant_id = },",
                f"{self.document_types = }>",
            ),
        )

    def delete(self) -> None:
        self.is_deleted = True

    def add_document_types(self, document_types_ids: list[str]) -> None:
        for document_type_id in document_types_ids:
            if (entity_id := EntityId(document_type_id)) in self.document_types:
                continue

            self.document_types.append(entity_id)

    def remove_document_types(self, document_types_ids: list[str]) -> None:
        for document_type_id in document_types_ids:
            if (entity_id := EntityId(document_type_id)) in self.document_types:
                self.document_types.remove(entity_id)

        self.events.append(
            DocumentTypesRemoved(
                id=self.id(),
                tenant_id=self.tenant_id(),
                document_type_ids=document_types_ids,
            ),
        )
