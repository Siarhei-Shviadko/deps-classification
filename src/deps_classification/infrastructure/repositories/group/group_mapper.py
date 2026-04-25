from typing import Any

from deps_classification.domain.model import Group

__all__ = ["GroupMapper"]


class GroupMapper:
    @staticmethod
    def to_dict(group: Group) -> dict[str, Any]:
        return {
            "group_id": group.id(),
            "tenant_id": group.tenant_id(),
            "is_deleted": group.is_deleted,
        }

    @staticmethod
    def from_dict(rows: list[dict[str, Any]]) -> Group:
        group_data = rows[0]
        return Group(
            id_=group_data["group_id"],
            tenant_id=group_data["tenant_id"],
            is_deleted=group_data["is_deleted"],
            document_types=[row["document_type_id"] for row in rows],
        )
