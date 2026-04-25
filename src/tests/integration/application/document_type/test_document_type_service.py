import pytest

from deps_classification.constants import CLASSIFICATION_DESTINATION
from deps_classification.messaging.handlers import (
    classification_document_type_deleted_handler,
    document_type_deleted_handler,
)


def test_delete__success(document_type_service, unit_of_work, group_1, group_1_document_types, add_groups):
    document_type_service.delete(group_1_document_types[0])

    group = unit_of_work.groups.group_of_id(group_1.id(), group_1.tenant_id())

    assert len(group.document_types) == len(group_1.document_types) - 1


def test_delete_and_republish__success(
    document_type_service,
    unit_of_work,
    group_1,
    group_1_document_types,
    add_groups,
    document_type_deleted_event,
    domain_event_publisher,
):
    document_type_id = group_1_document_types[0]

    document_type_service.delete_and_republish(document_type_id, document_type_deleted_event)

    group = unit_of_work.groups.group_of_id(group_1.id(), group_1.tenant_id())
    assert len(group.document_types) == len(group_1.document_types) - 1

    assert domain_event_publisher.last_published is not None
    assert domain_event_publisher.last_published.aggregate_type == CLASSIFICATION_DESTINATION
    assert domain_event_publisher.last_published.aggregate_id == document_type_id
    assert domain_event_publisher.last_published.events == [document_type_deleted_event]


def test_document_type_deleted_handler__deletes_and_republishes(
    document_type_service,
    unit_of_work,
    group_1,
    group_1_document_types,
    add_groups,
    document_type_deleted_event_envelope,
    domain_event_publisher,
):
    original_method = document_type_service.delete_and_republish
    called_with = {}

    def spy_method(document_type_id, original_event):
        called_with["document_type_id"] = document_type_id
        called_with["original_event"] = original_event
        return original_method(document_type_id, original_event)

    document_type_service.delete_and_republish = spy_method

    document_type_deleted_handler(document_type_deleted_event_envelope)

    assert called_with["document_type_id"] == document_type_deleted_event_envelope.event.document_type
    assert called_with["original_event"] == document_type_deleted_event_envelope.event

    assert domain_event_publisher.last_published is not None
    assert domain_event_publisher.last_published.aggregate_type == CLASSIFICATION_DESTINATION


def test_end_to_end_document_type_deletion_with_classifiers(
    document_type_service,
    unit_of_work,
    group_1,
    group_1_document_types,
    add_groups,
    test_gen_ai_classifier,
    add_gen_ai_classifier,
    query_gen_ai_classifier_repository,
    document_type_deleted_event,
    document_type_deleted_event_envelope,
    classification_document_type_deleted_event_envelope,
):
    document_type_id = group_1_document_types[0]
    tenant_id = group_1.tenant_id()

    classifiers_before = query_gen_ai_classifier_repository.find_all_classifier_display_info_of_document_type(
        document_type_id=document_type_id,
        tenant_id=tenant_id,
    )
    assert len(classifiers_before) == 1

    document_type_deleted_handler(document_type_deleted_event_envelope)

    classification_document_type_deleted_handler(classification_document_type_deleted_event_envelope)

    group = unit_of_work.groups.group_of_id(group_1.id(), group_1.tenant_id())
    assert document_type_id not in [dt() for dt in group.document_types]

    classifiers_after = query_gen_ai_classifier_repository.find_all_classifier_display_info_of_document_type(
        document_type_id=document_type_id,
        tenant_id=tenant_id,
    )
    assert len(classifiers_after) == 0
