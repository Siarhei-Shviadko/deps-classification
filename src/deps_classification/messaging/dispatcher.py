import logging

from deps_message_flow.commands.consumer import (
    CommandDispatcher,
    CommandHandlersBuilder,
)
from deps_message_flow.events.subscriber import (
    DomainEventDispatcher,
    DomainEventHandlersBuilder,
)
from deps_message_flow.messaging.consumer import IMessageConsumer
from deps_message_flow.messaging.producer import IMessageProducer

from deps_classification.constants import (
    CLASSIFICATION_DESTINATION,
    COMMANDS_CHANNEL,
    COMMANDS_QUEUE,
    COMMANDS_REPLIES_CHANNEL,
    DOCUMENT_TYPE_DESTINATION,
    EVENTS_QUEUE,
    GROUP_DESTINATION,
)
from deps_classification.domain.model import (
    DocumentTypeDeleted,
    DocumentTypesAdded,
    DocumentTypesRemoved,
    GroupCreated,
    GroupDeleted,
)

from .commands import ClassifyBatchFile, ClassifyDocument, ClassifyFile, GetGroupsReply

_logger = logging.getLogger(__name__)


def make_message_dispatcher(subscriber: IMessageConsumer, producer: IMessageProducer) -> IMessageConsumer:
    from deps_classification.messaging.handlers import (  # noqa: WPS433, WPS235
        classification_document_type_deleted_handler,
        classify_batch_file_handler,
        classify_document_handler,
        classify_file_handler,
        document_type_deleted_handler,
        document_types_added_handler,
        document_types_removed_handler,
        get_groups_reply_handler,
        group_created_handler,
        group_deleted_handler,
        group_document_types_removed_handler,
    )

    events_handlers = (
        DomainEventHandlersBuilder.for_aggregate_type(GROUP_DESTINATION)
        .on_event(GroupCreated, group_created_handler)
        .on_event(GroupDeleted, group_deleted_handler)
        .on_event(DocumentTypesAdded, document_types_added_handler)
        .on_event(DocumentTypesRemoved, document_types_removed_handler)
        .and_for_aggregate_type(CLASSIFICATION_DESTINATION)
        .on_event(DocumentTypesRemoved, group_document_types_removed_handler)
        .on_event(DocumentTypeDeleted, classification_document_type_deleted_handler)
        .and_for_aggregate_type(DOCUMENT_TYPE_DESTINATION)
        .on_event(DocumentTypeDeleted, document_type_deleted_handler)
        .for_queue(EVENTS_QUEUE)
        .build()
    )

    commands_handlers = (
        CommandHandlersBuilder.from_channel(COMMANDS_REPLIES_CHANNEL)
        .on_message(GetGroupsReply, get_groups_reply_handler)
        .and_from_channel(COMMANDS_CHANNEL)
        .on_message(ClassifyDocument, classify_document_handler)
        .on_message(ClassifyFile, classify_file_handler)
        .on_message(ClassifyBatchFile, classify_batch_file_handler)
        .for_queue(COMMANDS_QUEUE)
        .build()
    )

    ded = DomainEventDispatcher(events_handlers, subscriber)
    ded.initialize()

    cd = CommandDispatcher(commands_handlers, subscriber, producer)
    cd.initialize()

    _logger.info("Start consuming....")

    return subscriber
