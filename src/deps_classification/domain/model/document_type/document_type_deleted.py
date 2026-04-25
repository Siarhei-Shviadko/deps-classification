from dataclasses import dataclass

from ..shared import Event

__all__ = ["DocumentTypeDeleted"]


@dataclass
class DocumentTypeDeleted(Event):
    document_type: str
    tenant: str
