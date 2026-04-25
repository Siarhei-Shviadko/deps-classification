from pydantic import Field

from deps_classification.domain.model import (
    GEN_AI_CLASSIFIER_NAME_MAX_LENGTH,
    GenAIClassifier,
)

from ..configured_base_serializer import (
    ConfiguredRequestSerializer,
    ConfiguredResponseSerializer,
)

__all__ = ["CreateGenAIClassifierRequest", "CreateGenAIClassifierResponse"]


class CreateGenAIClassifierRequest(ConfiguredRequestSerializer):
    group_id: str = Field(..., alias="groupId", min_length=1)
    document_type_id: str = Field(..., alias="documentTypeId", min_length=1)
    prompt: str = Field(..., min_length=1)
    llm_type: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=GEN_AI_CLASSIFIER_NAME_MAX_LENGTH)


class CreateGenAIClassifierResponse(ConfiguredResponseSerializer):
    id: str

    @classmethod
    def from_domain(cls, gen_ai_classifier: GenAIClassifier) -> "CreateGenAIClassifierResponse":
        return cls(id=gen_ai_classifier.id())
