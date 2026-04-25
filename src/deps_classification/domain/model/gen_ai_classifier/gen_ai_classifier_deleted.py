from dataclasses import dataclass

from ..shared import Event

__all__ = ["GenAIClassifierDeleted"]


@dataclass
class GenAIClassifierDeleted(Event):
    id: str
    tenant_id: str
    group_id: str
    document_type_id: str
