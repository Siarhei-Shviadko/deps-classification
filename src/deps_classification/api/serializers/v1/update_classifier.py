from typing import Optional

from pydantic import Field

from deps_classification.domain.model import GEN_AI_CLASSIFIER_NAME_MAX_LENGTH

from ..configured_base_serializer import ConfiguredRequestSerializer

__all__ = ["UpdateClassifierRequest"]


class UpdateClassifierRequest(ConfiguredRequestSerializer):
    prompt: Optional[str] = Field(None, min_length=1)
    llm_type: Optional[str] = Field(None, min_length=1)
    name: Optional[str] = Field(None, min_length=1, max_length=GEN_AI_CLASSIFIER_NAME_MAX_LENGTH)
