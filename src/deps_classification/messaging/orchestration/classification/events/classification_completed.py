from dataclasses import dataclass

from deps_message_flow.events.common import DomainEvent

__all__ = ["DocumentClassificationCompleted"]


@dataclass
class DocumentClassificationCompleted(DomainEvent):
    document_id: str
    tenant_id: str
    document_type_id: str | None
