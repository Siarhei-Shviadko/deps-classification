from typing import Any
from uuid import uuid4

from deps_message_flow.commands.common import (
    CommandMessageHeaders,
    CommandReplyOutcome,
    Failure,
    ReplyMessageHeaders,
    Success,
)
from deps_message_flow.events.mappers import JsonMapper
from deps_message_flow.messaging.common import IMessage
from deps_message_flow.messaging.producer import MessageBuilder

__all__ = ["SagaReplyBuilder"]


class SagaReplyBuilder:
    def __init__(self, routing_info: dict[str, str]) -> None:
        self._routing_info = routing_info
        self._destination = self._extract_destination()

    @classmethod
    def for_routing_info(cls, routing_info: dict[str, str]) -> "SagaReplyBuilder":
        return cls(routing_info)

    def with_success(self, reply: Any = Success()) -> tuple[str, IMessage]:
        return self._destination, (
            MessageBuilder.with_payload(JsonMapper().serialize(reply))
            .with_header(ReplyMessageHeaders.REPLY_OUTCOME, CommandReplyOutcome.SUCCESS.value)
            .with_header(ReplyMessageHeaders.REPLY_TYPE, reply.__class__.__name__)
            .with_header(IMessage.ID, uuid4().hex)
            .with_extra_headers("", self._routing_info)
            .build()
        )

    def with_failure(self, reply: Any = Failure()) -> tuple[str, IMessage]:
        return self._destination, (
            MessageBuilder.with_payload(JsonMapper().serialize(reply))
            .with_header(ReplyMessageHeaders.REPLY_OUTCOME, CommandReplyOutcome.FAILURE.value)
            .with_header(ReplyMessageHeaders.REPLY_TYPE, reply.__class__.__name__)
            .with_header(IMessage.ID, uuid4().hex)
            .with_extra_headers("", self._routing_info)
            .build()
        )

    def _extract_destination(self) -> str:
        return self._routing_info.get(CommandMessageHeaders.in_reply(CommandMessageHeaders.REPLY_TO))
