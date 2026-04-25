from deps_classification.domain.exceptions import GroupNotFound
from deps_classification.domain.model import (
    GenAIClassifierDisplayInfo,
    IQueryGenAIClassifierRepository,
    IQueryGroupRepository,
)

__all__ = ["QueryGenAIClassifierService"]


class QueryGenAIClassifierService:
    def __init__(
        self,
        query_gen_ai_classifier_repository: IQueryGenAIClassifierRepository,
        query_group_repository: IQueryGroupRepository,
    ) -> None:
        self._query_gen_ai_classifier_repository = query_gen_ai_classifier_repository
        self._query_group_repository = query_group_repository

    def find_all_of_group(self, group_id: str, tenant_id: str) -> list[GenAIClassifierDisplayInfo]:
        if not self._query_group_repository.exists_group_of_id(group_id=group_id, tenant_id=tenant_id):
            raise GroupNotFound(group_id)

        return self._query_gen_ai_classifier_repository.find_all_classifier_display_info_of_group(
            group_id=group_id,
            tenant_id=tenant_id,
        )

    def find_all_of_document_type(self, document_type_id: str, tenant_id: str) -> list[GenAIClassifierDisplayInfo]:
        return self._query_gen_ai_classifier_repository.find_all_classifier_display_info_of_document_type(
            document_type_id=document_type_id,
            tenant_id=tenant_id,
        )
