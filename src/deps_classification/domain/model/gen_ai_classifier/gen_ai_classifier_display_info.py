from typing import TypedDict

__all__ = ["GenAIClassifierDisplayInfo"]


class GenAIClassifierDisplayInfo(TypedDict):
    gen_ai_classifier_id: str
    document_type_id: str
    prompt: str
    llm_type: str
    name: str
