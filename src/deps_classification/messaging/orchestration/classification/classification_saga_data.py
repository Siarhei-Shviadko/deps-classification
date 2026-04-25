from typing import Any, Optional

from deps_message_flow.commands.consumer import (
    CommandWithDestination,
    CommandWithDestinationBuilder,
)
from deps_message_flow.sagas.orchestration import SagaData

from ..shared import (
    Destination,
    Error,
    ErrorType,
    PerformParsing,
    PerformUnification,
    Status,
)
from .commands import UpdateDocumentState
from .events import DocumentClassificationCompleted

__all__ = ["ClassificationSagaData"]


class ClassificationSagaData(SagaData):
    def __init__(
        self,
        document_id: str,
        tenant_id: str,
        group_id: str,
        files: list[str],
        engine: Optional[str] = None,
        language: Optional[str] = None,
        parsing_features: Optional[list[str]] = None,
        *,
        document_type_id: str | None = None,
        current_status: Status = Status.UNIFICATION,
        error: Optional[Error] = None,
    ) -> None:
        super().__init__(entity_id=document_id)

        self.document_id = document_id
        self.tenant_id = tenant_id
        self.group_id = group_id
        self.files = files
        self.engine = engine
        self.language = language
        self.parsing_features = parsing_features

        self.document_type_id = document_type_id

        self.current_status = current_status
        self.error = error

    @property
    def classification_completed_event(self) -> DocumentClassificationCompleted:
        return DocumentClassificationCompleted(
            tenant_id=self.tenant_id,
            document_id=self.document_id,
            document_type_id=self.document_type_id,
        )

    def is_invoke_next_step(self) -> bool:
        return self.error is None

    def is_invoke_update(self) -> bool:
        return self.current_status not in {Status.FAILURE, Status.POSTPONED}

    def is_local_step_failed(self) -> bool:
        return self.error is not None and self.current_status not in {Status.FAILURE, Status.POSTPONED}

    def set_unification_state(self) -> CommandWithDestination:
        self.current_status = Status.UNIFICATION

        return (
            CommandWithDestinationBuilder.send(
                UpdateDocumentState(
                    self.document_id,
                    self.current_status.value,
                    self.error,
                ),
            )
            .to(Destination.DOCUMENT_SERVICE)
            .build()
        )

    def perform_unification(self) -> CommandWithDestination:
        return (
            CommandWithDestinationBuilder.send(PerformUnification(self.document_id, self.files))
            .to(Destination.UNIFIER_SERVICE)
            .build()
        )

    def set_parsing_state(self) -> CommandWithDestination:
        if self.error is not None:
            self.current_status = Status.FAILURE if self.error.is_system else Status.POSTPONED
        else:
            self.current_status = Status.PARSING

        return (
            CommandWithDestinationBuilder.send(
                UpdateDocumentState(
                    self.document_id,
                    self.current_status.value,
                    self.error,
                ),
            )
            .to(Destination.DOCUMENT_SERVICE)
            .build()
        )

    def perform_parsing(self) -> CommandWithDestination:
        return (
            CommandWithDestinationBuilder.send(
                PerformParsing(
                    tenant_id=self.tenant_id,
                    document_id=self.document_id,
                    files=self.files,
                    engine=self.engine,
                    language=self.language,
                    features=self.parsing_features,
                ),
            )
            .to(Destination.PARSING_SERVICE)
            .build()
        )

    def set_classification_state(self) -> CommandWithDestination:
        if self.error is not None:
            self.current_status = Status.FAILURE if self.error.is_system else Status.POSTPONED
        else:
            self.current_status = Status.CLASSIFICATION

        return (
            CommandWithDestinationBuilder.send(
                UpdateDocumentState(
                    self.document_id,
                    self.current_status.value,
                    self.error,
                ),
            )
            .to(Destination.DOCUMENT_SERVICE)
            .build()
        )

    def set_error_state(self) -> CommandWithDestination:
        self.current_status = Status.FAILURE if self.error.is_system else Status.POSTPONED

        return (
            CommandWithDestinationBuilder.send(
                UpdateDocumentState(
                    self.document_id,
                    self.current_status.value,
                    self.error,
                ),
            )
            .to(Destination.DOCUMENT_SERVICE)
            .build()
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "tenant_id": self.tenant_id,
            "group_id": self.group_id,
            "files": self.files,
            "engine": self.engine,
            "language": self.language,
            "parsing_features": self.parsing_features,
            "document_type_id": self.document_type_id,
            "current_status": self.current_status.value,
            "error_type": self.error.type.value if self.error is not None else None,
            "error_message": self.error.message if self.error is not None else None,
        }

    @classmethod
    def from_dict(cls, raw_data: dict[str, Any]) -> "ClassificationSagaData":
        return cls(
            document_id=raw_data["document_id"],
            tenant_id=raw_data["tenant_id"],
            group_id=raw_data["group_id"],
            files=raw_data["files"],
            engine=raw_data["engine"],
            language=raw_data["language"],
            parsing_features=raw_data["parsing_features"],
            document_type_id=raw_data["document_type_id"],
            current_status=Status(raw_data["current_status"]),
            error=(
                Error(ErrorType(raw_data["error_type"]), raw_data["error_message"])
                if raw_data["error_type"] is not None and raw_data["error_message"] is not None
                else None
            ),
        )
