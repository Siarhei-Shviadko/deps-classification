from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from deps_classification.application import CommandGenAIClassifierService
from deps_classification.containers import Containers

from ...auth import get_current_user_tenant
from ...endpoint_marker import MarkerRoute
from ...endpoint_visibility import Visibility
from ...serializers import (
    CreateGenAIClassifierRequest,
    CreateGenAIClassifierResponse,
    UpdateClassifierRequest,
)

__all__ = ["gen_ai_classifiers_router"]


gen_ai_classifiers_router = APIRouter(
    prefix="/gen-ai-classifiers",
    tags=["Gen AI Classifiers"],
    route_class=MarkerRoute,
)


@gen_ai_classifiers_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    openapi_extra={"visibility": Visibility.PUBLIC},
    response_model=CreateGenAIClassifierResponse,
)
@inject
def create_gen_ai_classifier(
    create_gen_ai_classifier_request: CreateGenAIClassifierRequest,
    current_tenant: str = Depends(get_current_user_tenant),
    command_gen_ai_classifier_service: CommandGenAIClassifierService = Depends(
        Provide[Containers.command_gen_ai_classifier_service],
    ),
):
    return CreateGenAIClassifierResponse.from_domain(
        command_gen_ai_classifier_service.create(
            group_id=create_gen_ai_classifier_request.group_id,
            tenant_id=current_tenant,
            document_type_id=create_gen_ai_classifier_request.document_type_id,
            prompt=create_gen_ai_classifier_request.prompt,
            llm_type=create_gen_ai_classifier_request.llm_type,
            name=create_gen_ai_classifier_request.name,
        ),
    )


@gen_ai_classifiers_router.patch(
    "/{gen_ai_classifier_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def update_classifier(
    gen_ai_classifier_id: str,
    update_classifier_request: UpdateClassifierRequest,
    current_tenant: str = Depends(get_current_user_tenant),
    command_gen_ai_classifier_service: CommandGenAIClassifierService = Depends(
        Provide[Containers.command_gen_ai_classifier_service],
    ),
):
    command_gen_ai_classifier_service.update(
        gen_ai_classifier_id=gen_ai_classifier_id,
        tenant_id=current_tenant,
        prompt=update_classifier_request.prompt,
        llm_type=update_classifier_request.llm_type,
        name=update_classifier_request.name,
    )


@gen_ai_classifiers_router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def delete_classifiers(
    ids: list[str] = Query(..., alias="id"),
    current_tenant: str = Depends(get_current_user_tenant),
    command_gen_ai_classifier_service: CommandGenAIClassifierService = Depends(
        Provide[Containers.command_gen_ai_classifier_service],
    ),
):
    command_gen_ai_classifier_service.delete(gen_ai_classifier_ids=ids, tenant_id=current_tenant)
