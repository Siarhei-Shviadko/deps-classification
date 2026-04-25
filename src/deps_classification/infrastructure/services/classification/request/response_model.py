from pydantic import BaseModel, Field

__all__ = ["ClassificationResponseModel"]


class ClassificationResponseModel(BaseModel):
    reasoning: str = Field(
        ...,
        description="Step by step reasoning, explaining why the document was classified into the category.",
    )
    category_id: str | None = Field(
        None,
        description="The ID of the category that the document was classified into. "
        "If the document was not classified into any category, this field will be None.",
    )
    confidence: float = Field(..., description="The confidence score of the classification. From 0 to 100.")
