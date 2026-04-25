from datetime import datetime
from typing import Optional

from ..shared import (
    EntityId,
    Event,
    FormatCheck,
    Guard,
    ImmutableCheck,
    LengthCheck,
    TenantId,
)
from .gen_ai_classifier_deleted import GenAIClassifierDeleted
from .gen_ai_classifier_updated import GenAIClassifierUpdated

__all__ = ["GenAIClassifier", "GEN_AI_CLASSIFIER_NAME_MAX_LENGTH"]

GEN_AI_CLASSIFIER_NAME_MAX_LENGTH = 120


class GenAIClassifier:  # noqa: WPS230
    id = Guard[EntityId](EntityId, ImmutableCheck())
    tenant_id = Guard[TenantId](TenantId, ImmutableCheck())
    group_id = Guard[EntityId](EntityId, ImmutableCheck())
    document_type_id = Guard[EntityId](EntityId, ImmutableCheck())
    prompt = Guard[str](str, LengthCheck())
    llm_type = Guard[str](str, LengthCheck())
    created_at = Guard[datetime](datetime, ImmutableCheck())
    updated_at = Guard[datetime](datetime)
    name = Guard[str](
        str,
        LengthCheck(max_length=GEN_AI_CLASSIFIER_NAME_MAX_LENGTH),
        FormatCheck(r"^(?![- ]+)(?!.*[- ]+$)[\w-]+( [\w-]+)*$"),
    )

    def __init__(
        self,
        id_: str,
        tenant_id: str,
        group_id: str,
        document_type_id: str,
        prompt: str,
        llm_type: str,
        created_at: datetime,
        updated_at: datetime,
        name: str,
        *,
        events: list[Event] | None = None,
    ) -> None:
        self.id = EntityId(id_)
        self.tenant_id = TenantId(tenant_id)
        self.group_id = EntityId(group_id)
        self.document_type_id = EntityId(document_type_id)

        self.prompt = prompt
        self.llm_type = llm_type

        self.created_at = created_at
        self.updated_at = updated_at

        self.name = name

        self.events = events or []

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and other.id == self.id

    def __repr__(self) -> str:
        return "\n".join(
            (
                f"<class '{self.__class__.__name__}':",
                f"{self.id = },",
                f"{self.tenant_id = },",
                f"{self.group_id = },",
                f"{self.document_type_id = },",
                f"{self.prompt = },",
                f"{self.llm_type = },",
                f"{self.created_at = },",
                f"{self.updated_at = },",
                f"{self.name = }",
            ),
        )

    def update(self, prompt: Optional[str], llm_type: Optional[str], name: Optional[str]) -> None:
        self.prompt = prompt if prompt is not None else self.prompt
        self.llm_type = llm_type if llm_type is not None else self.llm_type
        self.name = name if name is not None else self.name

        self.events.append(
            GenAIClassifierUpdated(
                id=self.id(),
                tenant_id=self.tenant_id(),
                group_id=self.group_id(),
                document_type_id=self.document_type_id(),
                prompt=prompt,
                llm_type=llm_type,
                name=name,
            ),
        )

        self.updated_at = datetime.now()

    def delete(self) -> None:
        self.events.append(
            GenAIClassifierDeleted(
                id=self.id(),
                tenant_id=self.tenant_id(),
                group_id=self.group_id(),
                document_type_id=self.document_type_id(),
            ),
        )
