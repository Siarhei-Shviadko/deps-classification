import json

import pytest
from deps_message_flow.sagas.testing_support import *

from deps_classification.messaging import (
    ClassificationSaga,
    ClassificationSagaData,
    ClassificationSagaSteps,
    Destination,
    Error,
    ErrorType,
    Status,
)
from deps_classification.messaging.orchestration import (
    DocumentClassificationCompleted,
    PerformParsing,
    PerformUnification,
    UpdateDocumentState,
)
from tests.fakes import FakeAIFusionProxy


@pytest.mark.usefixtures("add_gen_ai_classifiers")
def test_classification__success(
    suts,
    document_id,
    files,
    tenant_id,
    engine,
    parsing_features,
    fake_domain_event_publisher,
    gen_ai_classifier_1,
    fake_ai_fusion_proxy: FakeAIFusionProxy,
):
    fake_ai_fusion_proxy.saved_response = {
        "elements": {
            "insight-code": {
                "content": json.dumps(
                    {
                        "category_id": gen_ai_classifier_1.document_type_id(),
                        "confidence": 0.0,
                        "reasoning": "reasoning",
                    },
                ),
            },
        },
    }

    suts = (
        suts.expect()
        .command(UpdateDocumentState(document_id, Status.UNIFICATION.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformUnification(
                document_id=document_id,
                document_type_id=None,
                files=files,
            )
        )
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.PARSING.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                tenant_id=tenant_id,
                document_id=document_id,
                files=files,
                engine=engine,
                features=parsing_features,
            ),
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply()
    )

    saga_data = suts.saga_data
    assert Status.CLASSIFICATION == Status(saga_data["current_status"])

    suts = (
        suts.expect()
        .command(UpdateDocumentState(document_id, Status.CLASSIFICATION.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )

    assert fake_domain_event_publisher.last_published
    assert fake_domain_event_publisher.last_published.events == [
        DocumentClassificationCompleted(
            tenant_id=tenant_id,
            document_id=document_id,
            document_type_id=gen_ai_classifier_1.document_type_id(),
        )
    ]


def test_classification__failure(
    document_id,
    group_id,
    files,
    tenant_id,
    engine,
    parsing_features,
    fake_domain_event_publisher,
):
    document_type_id = None

    class Steps(ClassificationSagaSteps):
        def __init__(self) -> None:
            ...

        def classify(self, data: ClassificationSagaData):
            data.error = Error(ErrorType.SYSTEM, "Some error")

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            ClassificationSaga(
                domain_event_publisher=fake_domain_event_publisher,
                steps=Steps(),
            ),
            ClassificationSagaData(
                document_id,
                tenant_id,
                group_id,
                files,
                engine,
                parsing_features,
            ),
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.UNIFICATION.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformUnification(
                document_id,
                document_type_id,
                files,
            )
        )
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.PARSING.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                tenant_id=tenant_id,
                document_id=document_id,
                files=files,
                engine=engine,
                features=parsing_features,
            ),
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply()
    )

    saga_data = suts.saga_data
    assert Status.CLASSIFICATION == Status(saga_data["current_status"])

    suts = (
        suts.expect()
        .command(UpdateDocumentState(document_id, Status.CLASSIFICATION.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.FAILURE.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )

    saga_data = suts.saga_data
    assert Status.FAILURE == Status(saga_data["current_status"])

    assert fake_domain_event_publisher.last_published is None


def test_classification__postponed(
    document_id,
    group_id,
    files,
    tenant_id,
    engine,
    parsing_features,
    fake_domain_event_publisher,
):
    document_type_id = None

    class Steps(ClassificationSagaSteps):
        def __init__(self):
            ...

        def classify(self, data: ClassificationSagaData):
            data.error = Error(ErrorType.BUSINESS, "Some error")

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            ClassificationSaga(
                domain_event_publisher=fake_domain_event_publisher,
                steps=Steps(),
            ),
            ClassificationSagaData(
                document_id,
                tenant_id,
                group_id,
                files,
                engine,
                parsing_features,
            ),
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.UNIFICATION.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformUnification(
                document_id,
                document_type_id,
                files,
            )
        )
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.PARSING.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                tenant_id=tenant_id,
                document_id=document_id,
                files=files,
                engine=engine,
                features=parsing_features,
            ),
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply()
    )

    saga_data = suts.saga_data
    assert Status.CLASSIFICATION == Status(saga_data["current_status"])

    suts = (
        suts.expect()
        .command(UpdateDocumentState(document_id, Status.CLASSIFICATION.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.POSTPONED.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )

    saga_data = suts.saga_data
    assert Status.POSTPONED == Status(saga_data["current_status"])

    assert fake_domain_event_publisher.last_published is None
