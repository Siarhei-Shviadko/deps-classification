import logging
from typing import Any

from deps_message_flow.commands.consumer import (
    CommandWithDestination,
    CommandWithDestinationBuilder,
)
from deps_message_flow.sagas.orchestration import SagaData

from ..shared import (
    CreateDocumentFromFile,
    Destination,
    Error,
    ErrorType,
    PerformParsing,
    PerformUnification,
    State,
)

__all__ = ["BatchFileClassificationSagaData"]


class BatchFileClassificationSagaData(SagaData):
    def __init__(
        self,
        batch_id: str,
        file_id: str,
        tenant_id: str,
        group_id: str,
        file_path: str,
        document_name: str,
        replies_channel: str,
        engine: str | None = None,
        language: str | None = None,
        llm_type: str | None = None,
        parsing_features: list[str] | None = None,
        needs_unifier: bool = False,
        needs_extraction: bool = False,
        assigned_to_me: bool = False,
        metadata: dict[str, Any] | None = None,
        start_processing: bool = False,
        *,
        document_id: str | None = None,
        document_type_id: str | None = None,
        current_state: State = State.UNIFICATION,
        error: Error | None = None,
    ) -> None:
        self.batch_id = batch_id
        self.file_id = file_id
        self.tenant_id = tenant_id
        self.group_id = group_id
        self.file_path = file_path
        self.engine = engine
        self.language = language
        self.llm_type = llm_type
        self.parsing_features = parsing_features
        self.needs_unifier = needs_unifier
        self.needs_extraction = needs_extraction
        self.assigned_to_me = assigned_to_me
        self.metadata = metadata
        self.start_processing = start_processing
        self.replies_channel = replies_channel

        self.document_name = document_name
        self.document_id = document_id
        self.document_type_id = document_type_id

        self.current_state = current_state
        self.error = error

        self._logger = logging.getLogger(self.__class__.__name__)

    def is_invoke_next_step(self) -> bool:
        return self.error is None

    def perform_document_creation(self) -> CommandWithDestination:
        return (
            CommandWithDestinationBuilder.send(
                CreateDocumentFromFile(
                    document_name=self.document_name,
                    group_id=self.group_id,
                    file_path=self.file_path,
                    document_type_id=self.document_type_id,
                    parsing_features=self.parsing_features,
                    invoke_unifier=self.needs_unifier,
                    invoke_extraction=self.needs_extraction,
                    engine=self.engine,
                    language=self.language,
                    llm_type=self.llm_type,
                    metadata=self.metadata,
                    assigned_to_me=self.assigned_to_me,
                    start_processing=self.start_processing,
                ),
            )
            .to(Destination.DOCUMENT_SERVICE)
            .build()
        )

    def perform_unification(self) -> CommandWithDestination:
        return (
            CommandWithDestinationBuilder.send(PerformUnification(self.file_id, [self.file_path]))
            .to(Destination.UNIFIER_SERVICE)
            .build()
        )

    def perform_parsing(self) -> CommandWithDestination:
        parsing_features = self.parsing_features if self.parsing_features else ["text"]

        return (
            CommandWithDestinationBuilder.send(
                PerformParsing(
                    tenant_id=self.tenant_id,
                    document_id=self.file_id,
                    files=[self.file_path],
                    engine=self.engine,
                    language=self.language,
                    features=parsing_features,
                ),
            )
            .to(Destination.PARSING_SERVICE)
            .build()
        )

    def set_saga_state(self, state: State) -> None:
        if self.error is None:
            self.current_state = state
        else:
            raise RuntimeError

    def to_dict(self) -> dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "file_id": self.file_id,
            "tenant_id": self.tenant_id,
            "group_id": self.group_id,
            "file_path": self.file_path,
            "document_name": self.document_name,
            "engine": self.engine,
            "language": self.language,
            "llm_type": self.llm_type,
            "parsing_features": self.parsing_features,
            "needs_unifier": self.needs_unifier,
            "needs_extraction": self.needs_extraction,
            "assigned_to_me": self.assigned_to_me,
            "metadata": self.metadata,
            "start_processing": self.start_processing,
            "document_id": self.document_id,
            "document_type_id": self.document_type_id,
            "current_state": self.current_state.value,
            "error_type": self.error.type.value if self.error is not None else None,
            "error_message": self.error.message if self.error is not None else None,
            "replies_channel": self.replies_channel,
        }

    @classmethod
    def from_dict(cls, raw_data: dict[str, Any]) -> "BatchFileClassificationSagaData":
        return cls(
            batch_id=raw_data["batch_id"],
            file_id=raw_data["file_id"],
            file_path=raw_data["file_path"],
            tenant_id=raw_data["tenant_id"],
            group_id=raw_data["group_id"],
            document_name=raw_data["document_name"],
            engine=raw_data["engine"],
            language=raw_data["language"],
            llm_type=raw_data["llm_type"],
            parsing_features=raw_data["parsing_features"],
            needs_unifier=raw_data["needs_unifier"],
            needs_extraction=raw_data["needs_extraction"],
            assigned_to_me=raw_data["assigned_to_me"],
            metadata=raw_data["metadata"],
            start_processing=raw_data["start_processing"],
            document_id=raw_data["document_id"],
            document_type_id=raw_data["document_type_id"],
            current_state=State(raw_data["current_state"]),
            error=(
                Error(ErrorType(raw_data["error_type"]), raw_data["error_message"])
                if raw_data.get("error_type") is not None
                else None
            ),
            replies_channel=raw_data["replies_channel"],
        )
