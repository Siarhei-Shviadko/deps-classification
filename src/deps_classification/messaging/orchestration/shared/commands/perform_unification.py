from dataclasses import dataclass
from typing import Any, Optional

from deps_message_flow.commands.common import Command

from .command_with_error import CommandWithError

__all__ = ["PerformUnification", "PerformUnificationReply"]

CommonDict = dict[str, Any]


@dataclass
class PerformUnification(Command):
    document_id: str
    files: list[str]
    document_type_id: Optional[str] = None


@dataclass
class PerformUnificationReply(CommandWithError):
    error_type: Optional[str] = None
    error_message: Optional[str] = None

    @property
    def has_error(self) -> bool:
        return self.error_type is not None
