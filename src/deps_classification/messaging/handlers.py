import logging

from dependency_injector.wiring import Provide, inject
from deps_message_flow.commands.common import (
    CommandMessageHeaders,
    CommandReplyOutcome,
    ReplyMessageHeaders,
)
from deps_message_flow.commands.consumer import CommandMessage
from deps_message_flow.events.subscriber.domain_event_envelope import (
    DomainEventEnvelope,
)

from deps_classification.application import (
    CommandGenAIClassifierService,
    DocumentProcessingService,
    DocumentTypeService,
    GroupService,
)
from deps_classification.containers import Containers
from deps_classification.domain.model import (
    DocumentTypeDeleted,
    DocumentTypesAdded,
    DocumentTypesRemoved,
    GroupCreated,
    GroupDeleted,
)
from deps_classification.messaging import (
    ClassifyBatchFile,
    ClassifyDocument,
    ClassifyFile,
    GetGroupsReply,
)

logger = logging.getLogger(__name__)


__all__ = [
    "group_created_handler",
    "group_deleted_handler",
    "document_types_added_handler",
    "document_types_removed_handler",
    "group_document_types_removed_handler",
    "document_type_deleted_handler",
    "classification_document_type_deleted_handler",
    "classify_document_handler",
    "classify_file_handler",
    "get_groups_reply_handler",
    "classify_batch_file_handler",
]


def is_command_successful(command_message: CommandMessage) -> bool:
    return (
        command_message.message.get_required_header(ReplyMessageHeaders.REPLY_OUTCOME)
        == CommandReplyOutcome.SUCCESS.name
    )


@inject
def group_created_handler(
    dee: DomainEventEnvelope[GroupCreated],
    group_service: GroupService = Provide[Containers.group_service],
):
    group_service.create(
        group_id=dee.event.id,
        tenant_id=dee.event.tenant_id,
        document_type_ids=dee.event.document_type_ids,
    )


@inject
def group_deleted_handler(
    dee: DomainEventEnvelope[GroupDeleted],
    group_service: GroupService = Provide[Containers.group_service],
):
    group_service.delete(
        group_id=dee.event.id,
        tenant_id=dee.event.tenant_id,
    )


@inject
def document_types_added_handler(
    dee: DomainEventEnvelope[DocumentTypesAdded],
    group_service: GroupService = Provide[Containers.group_service],
):
    group_service.add_document_types(
        group_id=dee.event.id,
        tenant_id=dee.event.tenant_id,
        document_type_ids=dee.event.document_type_ids,
    )


@inject
def document_types_removed_handler(
    dee: DomainEventEnvelope[DocumentTypesRemoved],
    group_service: GroupService = Provide[Containers.group_service],
):
    group_service.remove_document_types(
        group_id=dee.event.id,
        tenant_id=dee.event.tenant_id,
        document_type_ids=dee.event.document_type_ids,
    )


@inject
def group_document_types_removed_handler(
    dee: DomainEventEnvelope[DocumentTypesRemoved],
    gen_ai_classification_service: CommandGenAIClassifierService = Provide[
        Containers.command_gen_ai_classifier_service
    ],
):
    gen_ai_classification_service.delete_for_group_document_types(
        group_id=dee.event.id,
        tenant_id=dee.event.tenant_id,
        document_type_ids=dee.event.document_type_ids,
    )


@inject
def get_groups_reply_handler(  # noqa: WPS463
    command_message: CommandMessage[GetGroupsReply],
    group_service: GroupService = Provide[Containers.group_service],
):
    if is_command_successful(command_message):
        group_service.save_all(command_message.command.groups)
    else:
        logger.error(f"Failed to get groups. Command headers: {command_message.message.headers}")


@inject
def document_type_deleted_handler(  # noqa: WPS463
    dee: DomainEventEnvelope[DocumentTypeDeleted],
    document_type_service: DocumentTypeService = Provide[Containers.document_type_service],
):
    document_type_service.delete_and_republish(
        document_type_id=dee.event.document_type,
        original_event=dee.event,
    )


@inject
def classification_document_type_deleted_handler(
    dee: DomainEventEnvelope[DocumentTypeDeleted],
    command_gen_ai_classifier_service: CommandGenAIClassifierService = Provide[
        Containers.command_gen_ai_classifier_service
    ],
    tenant_id: str = Provide[Containers.current_user_tenant],
):
    command_gen_ai_classifier_service.delete_for_document_type(
        document_type_id=dee.event.document_type,
        tenant_id=tenant_id,
    )


@inject
def classify_document_handler(
    command_message: CommandMessage[ClassifyDocument],
    document_processing_service: DocumentProcessingService = Provide[Containers.document_processing_service],
):
    command = command_message.command

    document_processing_service.process_document(
        document_id=command.document_id,
        tenant_id=command.tenant_id,
        group_id=command.group_id,
        files=command.files,
        engine=command.engine,
        language=command.language,
        parsing_features=command.parsing_features,
    )


@inject
def classify_file_handler(
    command_message: CommandMessage[ClassifyFile],
    tenant_id: str = Provide[Containers.current_user_tenant],
    document_processing_service: DocumentProcessingService = Provide[Containers.document_processing_service],
):
    command = command_message.command

    document_processing_service.classify_file(
        file_id=command.file_id,
        tenant_id=tenant_id,
        file_path=command.file_path,
        file_name=command.file_name,
        group_id=command.group_id,
        engine=command.engine,
        language=command.language,
        parsing_features=command.parsing_features,
        llm_type=command.llm_type,
        needs_unifier=command.needs_unifier,
        needs_extraction=command.needs_extraction,
        assigned_to_me=command.assigned_to_me,
        metadata=command.metadata,
        label_ids=command.label_ids,
        start_processing=command.start_processing,
        routing_info=command_message.correlation_headers,
    )


def classify_batch_file_handler(
    command_message: CommandMessage[ClassifyBatchFile],
    tenant_id: str = Provide[Containers.current_user_tenant],
    document_processing_service: DocumentProcessingService = Provide[Containers.document_processing_service],
):
    command = command_message.command

    document_processing_service.classify_batch_file(
        batch_id=command.batch_id,
        file_id=command.file_id,
        tenant_id=tenant_id,
        file_path=command.file_path,
        file_name=command.file_name,
        group_id=command.group_id,
        engine=command.engine,
        language=command.language,
        parsing_features=command.parsing_features,
        llm_type=command.llm_type,
        needs_unifier=command.needs_unifier,
        needs_extraction=command.needs_extraction,
        assigned_to_me=command.assigned_to_me,
        metadata=command.metadata,
        start_processing=command.start_processing,
        replies_channel=command_message.message.headers[CommandMessageHeaders.REPLY_TO],
    )
