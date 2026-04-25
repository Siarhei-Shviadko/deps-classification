from uuid import uuid4

from deps_message_flow.sagas.testing_support import *

from deps_classification.messaging import Destination, ErrorType, Status
from deps_classification.messaging.orchestration import (
    PerformParsing,
    PerformParsingReply,
    PerformUnification,
    UpdateDocumentState,
)


def test_parsing__success(suts, document_id, files, tenant_id, engine, parsing_features):
    document_type_id = None

    suts = (
        suts.expect()
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
    )

    saga_data = suts.saga_data
    assert Status.PARSING == Status(saga_data["current_status"])

    suts = (
        suts.expect()
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


def test_parsing__failure(suts, document_id, files, tenant_id, engine, parsing_features):
    document_type_id = None

    suts = (
        suts.expect()
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
    )

    saga_data = suts.saga_data
    assert Status.PARSING == Status(saga_data["current_status"])

    suts = (
        suts.expect()
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
        .success_reply(PerformParsingReply(ErrorType.SYSTEM.value, uuid4().hex))
        .expect()
        .command(
            UpdateDocumentState(
                document_id,
                Status.FAILURE.value,
            )
        )
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data
    assert Status.FAILURE == Status(saga_data["current_status"])


def test_parsing__postponed(suts, document_id, files, tenant_id, engine, parsing_features):
    document_type_id = None

    suts = (
        suts.expect()
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
    )

    saga_data = suts.saga_data
    assert Status.PARSING == Status(saga_data["current_status"])

    suts = (
        suts.expect()
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
        .success_reply(PerformParsingReply(ErrorType.BUSINESS.value, uuid4().hex))
        .expect()
        .command(
            UpdateDocumentState(
                document_id,
                Status.FAILURE.value,
            )
        )
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data
    assert Status.POSTPONED == Status(saga_data["current_status"])
