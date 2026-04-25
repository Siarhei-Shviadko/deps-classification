from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Path, status

from deps_classification.application import QueryGenAIClassifierService
from deps_classification.containers import Containers

from ...auth import get_current_user_tenant
from ...endpoint_marker import MarkerRoute
from ...endpoint_visibility import Visibility
from ...serializers import GetGenAIClassifiersOfGroupResponse

__all__ = ["groups_router"]

groups_router = APIRouter(prefix="/groups", tags=["Gen AI Classifiers"], route_class=MarkerRoute)


@groups_router.get(
    "/{groupId}/gen-ai-classifiers",
    status_code=status.HTTP_200_OK,
    openapi_extra={"visibility": Visibility.PUBLIC},
    response_model=GetGenAIClassifiersOfGroupResponse,
)
@inject
def get_gen_ai_classifiers_of_group(
    group_id: str = Path(..., alias="groupId"),
    current_tenant: str = Depends(get_current_user_tenant),
    query_gen_ai_classifier_service: QueryGenAIClassifierService = Depends(
        Provide[Containers.query_gen_ai_classifier_service],
    ),
):
    return GetGenAIClassifiersOfGroupResponse.from_classifiers_list(
        gen_ai_classifiers=query_gen_ai_classifier_service.find_all_of_group(
            group_id=group_id,
            tenant_id=current_tenant,
        ),
    )
