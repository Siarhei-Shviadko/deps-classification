from dataclasses import dataclass
from typing import Any

from deps_message_flow.commands.common import Command

__all__ = ["ClassifyFile", "ClassifyFileReply"]


@dataclass
class ClassifyFile(Command):
    file_id: str
    file_name: str
    file_path: str
    group_id: str
    engine: str | None = None
    language: str | None = None
    parsing_features: list[str] | None = None
    llm_type: str | None = None
    needs_unifier: bool = False
    needs_extraction: bool = False
    assigned_to_me: bool = False
    metadata: dict[str, Any] | None = None
    label_ids: list[str] | None = None
    start_processing: bool = False


@dataclass
class ClassifyFileReply(Command):
    file_id: str
    document_id: str | None = None
    document_name: str | None = None
    document_type_id: str | None = None
    error_type: str | None = None
    error_message: str | None = None
