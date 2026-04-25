from typing import Self

from pydantic import Field

from deps_classification.domain.model import GenAIClassifierDisplayInfo

from ..configured_base_serializer import ConfiguredResponseSerializer

__all__ = ["GetGenAIClassifiersOfGroupResponse"]


class GenAIClassifierDisplay(ConfiguredResponseSerializer):
    gen_ai_classifier_id: str = Field(..., alias="genAiClassifierId")
    document_type_id: str = Field(..., alias="documentTypeId")
    prompt: str
    llm_type: str = Field(..., alias="llmType")
    name: str


class GetGenAIClassifiersOfGroupResponse(ConfiguredResponseSerializer):
    gen_ai_classifiers: list[GenAIClassifierDisplay] = Field(..., alias="genAiClassifiers")

    @classmethod
    def from_classifiers_list(cls, gen_ai_classifiers: list[GenAIClassifierDisplayInfo]) -> Self:
        return cls(
            gen_ai_classifiers=[
                GenAIClassifierDisplay(
                    gen_ai_classifier_id=gen_ai_classifier["gen_ai_classifier_id"],
                    document_type_id=gen_ai_classifier["document_type_id"],
                    prompt=gen_ai_classifier["prompt"],
                    llm_type=gen_ai_classifier["llm_type"],
                    name=gen_ai_classifier["name"],
                )
                for gen_ai_classifier in gen_ai_classifiers
            ],
        )
