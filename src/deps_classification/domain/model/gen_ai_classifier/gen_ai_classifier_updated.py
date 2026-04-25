from dataclasses import dataclass

from ..shared import Event

__all__ = ["GenAIClassifierUpdated"]


@dataclass
class GenAIClassifierUpdated(Event):
    id: str
    tenant_id: str
    group_id: str
    document_type_id: str
    prompt: str
    llm_type: str
    name: str
