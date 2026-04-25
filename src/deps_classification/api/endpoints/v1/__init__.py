from fastapi import APIRouter

from .document_types import *
from .gen_ai_classifiers import *
from .groups import *

__all__ = ["v1_router"]


v1_router = APIRouter()

v1_router.include_router(prefix="/v1", router=gen_ai_classifiers_router)
v1_router.include_router(prefix="/v1", router=groups_router)
v1_router.include_router(prefix="/v1", router=document_types_router)
