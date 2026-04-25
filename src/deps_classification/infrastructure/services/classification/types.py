from typing import Any, Literal, TypeAlias, TypedDict

__all__ = [
    "RawClassificationResponse",
    "T_UNKNOWN",
    "UNKNOWN",
    "DocumentTypeCode",
    "INSIGHT_KEY",
    "ClassificationRequest",
    "DocumentTypeClassificationResult",
]

T_UNKNOWN = Literal["!UNKNOWN!"]
UNKNOWN = "!UNKNOWN!"
INSIGHT_KEY = "insight-code"

DocumentTypeCode: TypeAlias = str


class DocumentTypeClassificationResult(TypedDict):
    reasoning: str
    category_id: str | None
    confidence: float | None


class RawClassificationResponse(TypedDict):
    elements: dict[
        Literal["insight-code"],
        dict[Literal["content"], str],  # value is jsonified DocumentTypeClassificationResult
    ]


class RawClassificationWorkflow(TypedDict):
    prompts: list[dict[Literal["content"], str]]
    responseModel: dict[str, Any]  # Structured response with OpenAPI V3 Schema


class RawDocumentTypesClassification(TypedDict):
    workflow: RawClassificationWorkflow


ClassificationRequest: TypeAlias = dict[Literal["insight-code"], RawDocumentTypesClassification]
