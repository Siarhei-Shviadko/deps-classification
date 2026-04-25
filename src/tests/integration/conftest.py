import uuid
from datetime import datetime

import pytest
from deps_message_flow.events.subscriber.domain_event_envelope import (
    DomainEventEnvelope,
)

from deps_classification.constants import (
    CLASSIFICATION_DESTINATION,
    DOCUMENT_TYPE_DESTINATION,
)
from deps_classification.domain.model import DocumentTypeDeleted, GenAIClassifier
from tests.fakes.fake_domain_event_publisher import FakeDomainEventPublisher
from tests.fakes.fake_events import EventMessageHeaders, FakeMessage


@pytest.fixture
def unit_of_work(containers):
    return containers.unit_of_work()


@pytest.fixture(autouse=True)
def empty_unit_of_work(unit_of_work):
    try:
        with unit_of_work:
            unit_of_work.groups.erase_all_groups()
            unit_of_work.gen_ai_classifiers.erase_all_gen_ai_classifiers()
            unit_of_work.commit()

        yield

        with unit_of_work:
            unit_of_work.groups.erase_all_groups()
            unit_of_work.gen_ai_classifiers.erase_all_gen_ai_classifiers()
            unit_of_work.commit()
    except Exception:
        pass


@pytest.fixture()
def query_gen_ai_classifier_repository(repositories):
    return repositories.query_gen_ai_classifier()


@pytest.fixture()
def query_group_repository(repositories):
    return repositories.query_group()


@pytest.fixture()
def add_groups(unit_of_work, test_groups):
    with unit_of_work:
        for group in test_groups:
            unit_of_work.groups.save(group)

        unit_of_work.commit()

        yield


@pytest.fixture()
def add_gen_ai_classifiers(unit_of_work, test_gen_ai_classifiers):
    with unit_of_work:
        for test_gen_ai_classifier in test_gen_ai_classifiers:
            unit_of_work.gen_ai_classifiers.save(test_gen_ai_classifier)

        unit_of_work.commit()

        yield


@pytest.fixture
def domain_event_publisher():
    return FakeDomainEventPublisher()


@pytest.fixture
def document_type_service(containers, domain_event_publisher):
    service = containers.document_type_service()
    service._domain_event_publisher = domain_event_publisher
    return service


@pytest.fixture
def test_gen_ai_classifier(group_1, group_1_document_types):
    current_time = datetime.now()
    return GenAIClassifier(
        id_=str(uuid.uuid4()),
        tenant_id=group_1.tenant_id(),
        document_type_id=group_1_document_types[0],
        group_id=group_1.id(),
        name="TestClassifier",
        prompt="Test prompt",
        llm_type="gpt-4",
        created_at=current_time,
        updated_at=current_time,
    )


@pytest.fixture
def add_gen_ai_classifier(unit_of_work, test_gen_ai_classifier):
    with unit_of_work:
        unit_of_work.gen_ai_classifiers.save(test_gen_ai_classifier)
        unit_of_work.commit()
        yield


@pytest.fixture
def document_type_deleted_event(group_1, group_1_document_types):
    document_type_id = group_1_document_types[0]
    tenant_id = group_1.tenant_id()
    return DocumentTypeDeleted(document_type=document_type_id, tenant=tenant_id)


@pytest.fixture
def document_type_deleted_message(group_1, group_1_document_types, document_type_deleted_event):
    document_type_id = group_1_document_types[0]
    tenant_id = group_1.tenant_id()

    headers = {
        EventMessageHeaders.AGGREGATE_TYPE: DOCUMENT_TYPE_DESTINATION,
        EventMessageHeaders.EVENT_TYPE: "DocumentTypeDeleted",
        EventMessageHeaders.TENANT_ID: tenant_id,
        "ID": str(uuid.uuid4()),
    }

    return FakeMessage(headers=headers)


@pytest.fixture
def document_type_deleted_event_envelope(
    document_type_deleted_message, document_type_deleted_event, group_1_document_types
):
    document_type_id = group_1_document_types[0]
    event_id = document_type_deleted_message.get_id()

    return DomainEventEnvelope(
        message=document_type_deleted_message,
        aggregate_type=DOCUMENT_TYPE_DESTINATION,
        aggregate_id=document_type_id,
        event_id=event_id,
        event=document_type_deleted_event,
    )


@pytest.fixture
def classification_document_type_deleted_event_envelope(
    document_type_deleted_event_envelope, document_type_deleted_message
):
    document_type_deleted_message.set_header(EventMessageHeaders.AGGREGATE_TYPE, CLASSIFICATION_DESTINATION)

    return DomainEventEnvelope(
        message=document_type_deleted_message,
        aggregate_type=CLASSIFICATION_DESTINATION,
        aggregate_id=document_type_deleted_event_envelope.aggregate_id,
        event_id=document_type_deleted_event_envelope.event_id,
        event=document_type_deleted_event_envelope.event,
    )
