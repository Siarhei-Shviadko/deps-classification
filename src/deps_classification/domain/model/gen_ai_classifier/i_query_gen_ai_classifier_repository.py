from typing import Protocol

from .gen_ai_classifier_display_info import GenAIClassifierDisplayInfo

__all__ = ["IQueryGenAIClassifierRepository"]


class IQueryGenAIClassifierRepository(Protocol):
    def find_all_classifier_display_info_of_group(
        self,
        group_id: str,
        tenant_id: str,
    ) -> list[GenAIClassifierDisplayInfo]:
        pass

    def find_all_classifier_display_info_of_document_type(
        self,
        document_type_id: str,
        tenant_id: str,
    ) -> list[GenAIClassifierDisplayInfo]:
        pass
