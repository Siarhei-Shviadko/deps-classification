import json
import uuid

import pytest
from deps_message_flow.messaging.producer import IMessageProducer
from deps_message_flow.sagas.testing_support import *
from deps_object_storage import ObjectStorage
from faker.proxy import Faker

from deps_classification.messaging import (
    ClassificationSaga,
    ClassificationSagaData,
    ClassificationSagaSteps,
    Error,
    ErrorType,
)
from deps_classification.messaging.orchestration import (
    BatchFileClassificationSaga,
    BatchFileClassificationSagaData,
    BatchFileClassificationSagaSteps,
    FileClassificationSaga,
    FileClassificationSagaData,
    FileClassificationSagaSteps,
)
from tests.fakes import FakeObjectStorageProxy


@pytest.fixture
def document_id():
    return uuid.uuid4().hex


@pytest.fixture
def routing_info():
    return {"test": "routing info"}


@pytest.fixture
def tenant_id():
    return uuid.uuid4().hex


@pytest.fixture
def files():
    return [uuid.uuid4().hex, uuid.uuid4().hex]


@pytest.fixture
def engine():
    return uuid.uuid4().hex


@pytest.fixture
def parsing_features():
    return [uuid.uuid4().hex]


@pytest.fixture
def file_id():
    return uuid.uuid4().hex


@pytest.fixture
def file_path():
    return f"/files/{uuid.uuid4().hex}.pdf"


@pytest.fixture
def document_name():
    return f"test_document_{uuid.uuid4().hex}.pdf"


@pytest.fixture
def message_producer_mock():
    class FakeMessageProducer(IMessageProducer):
        def __init__(self):
            self.sent_messages = []

        def send(self, destination, message):
            self.sent_messages.append((destination, message))

    return FakeMessageProducer()


@pytest.fixture
def object_storage_mock():
    return FakeObjectStorageProxy()


@pytest.fixture
def suts(
    document_id,
    tenant_id,
    group_1,
    files,
    engine,
    parsing_features,
    fake_domain_event_publisher,
    add_gen_ai_classifiers,
    classification_service,
) -> SagaUnitTestSupport:
    return SagaUnitTestSupport.given().saga(
        ClassificationSaga(
            domain_event_publisher=fake_domain_event_publisher,
            steps=ClassificationSagaSteps(classification_service=classification_service),
        ),
        ClassificationSagaData(
            document_id,
            tenant_id,
            group_1.id(),
            files,
            engine,
            parsing_features,
        ),
    )


@pytest.fixture
def file_classification_steps_system_error():
    class StepsWithSystemError(FileClassificationSagaSteps):
        def __init__(self):
            ...

        def classify(self, data: FileClassificationSagaData):
            data.error = Error(ErrorType.SYSTEM, "Some error")

    return StepsWithSystemError()


@pytest.fixture
def file_classification_steps_business_error():
    class StepsWithBusinessError(FileClassificationSagaSteps):
        def __init__(self):
            ...

        def classify(self, data: FileClassificationSagaData):
            data.error = Error(ErrorType.BUSINESS, "Some error")

    return StepsWithBusinessError()


@pytest.fixture
def file_classification_saga_data(
    file_id,
    tenant_id,
    group_1,
    file_path,
    document_name,
    engine,
    parsing_features,
    routing_info,
) -> FileClassificationSagaData:
    return FileClassificationSagaData(
        file_id=file_id,
        tenant_id=tenant_id,
        group_id=group_1.id(),
        file_path=file_path,
        document_name=document_name,
        engine=engine,
        parsing_features=parsing_features,
        routing_info=routing_info,
    )


@pytest.fixture
def suts_file_classification(
    message_producer_mock,
    fake_object_storage,
    classification_service,
    file_classification_saga_data,
) -> SagaUnitTestSupport:
    return SagaUnitTestSupport.given().saga(
        saga=FileClassificationSaga(
            steps=FileClassificationSagaSteps(
                classification_service=classification_service,
                storage=fake_object_storage,
            ),
            message_producer=message_producer_mock,
        ),
        saga_data=file_classification_saga_data,
    )


@pytest.fixture
def add_object_to_storage(fake_object_storage: ObjectStorage, file_path, faker: Faker):
    fake_object_storage.upload(path=file_path, content=faker.binary(64), replace_if_exists=True)


@pytest.fixture
def fake_ai_fusion_proxy_with_success_response(fake_ai_fusion_proxy, document_type_id) -> None:
    fake_ai_fusion_proxy.saved_response = {
        "elements": {
            "insight-code": {
                "content": json.dumps(
                    {
                        "category_id": document_type_id,
                        "confidence": 0.0,
                        "reasoning": "reasoning",
                    },
                ),
            },
        },
    }


@pytest.fixture
def batch_id():
    return uuid.uuid4().hex


@pytest.fixture
def replies_channel():
    return "test_replies_channel"


@pytest.fixture
def batch_file_classification_saga_data(
    batch_id,
    file_id,
    tenant_id,
    group_1,
    file_path,
    document_name,
    engine,
    parsing_features,
    replies_channel,
) -> BatchFileClassificationSagaData:
    return BatchFileClassificationSagaData(
        batch_id=batch_id,
        file_id=file_id,
        tenant_id=tenant_id,
        group_id=group_1.id(),
        file_path=file_path,
        document_name=document_name,
        engine=engine,
        parsing_features=parsing_features,
        replies_channel=replies_channel,
    )


@pytest.fixture
def suts_batch_file_classification(
    message_producer_mock,
    classification_service,
    batch_file_classification_saga_data,
) -> SagaUnitTestSupport:
    return SagaUnitTestSupport.given().saga(
        saga=BatchFileClassificationSaga(
            steps=BatchFileClassificationSagaSteps(classification_service=classification_service),
            message_producer=message_producer_mock,
        ),
        saga_data=batch_file_classification_saga_data,
    )
