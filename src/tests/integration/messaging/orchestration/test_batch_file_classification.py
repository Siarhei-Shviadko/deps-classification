import json

import pytest
from deps_message_flow.sagas.testing_support import *
from more_itertools import first

from deps_classification.messaging import (
    BatchFileClassificationSagaData,
    CreateDocumentFromFile,
    CreateDocumentFromFileReply,
    Destination,
    PerformParsing,
    PerformUnification,
    State,
)


@pytest.mark.usefixtures(
    "add_gen_ai_classifiers",
    "fake_ai_fusion_proxy_with_success_response",
    "add_object_to_storage",
)
def test_batch_file_classification__success(
    batch_file_classification_saga_data: BatchFileClassificationSagaData,
    suts_batch_file_classification,
    message_producer_mock,
    fake_object_storage,
    file_path,
    file_id,
    batch_id,
    tenant_id,
    engine,
    parsing_features,
    document_name,
    group_id,
    document_type_id,
    document_id,
):
    suts = (
        suts_batch_file_classification.expect()
        .command(PerformUnification(file_id, [file_path]))
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                tenant_id=tenant_id,
                document_id=file_id,
                files=[file_path],
                engine=engine,
                language=batch_file_classification_saga_data.language,
                features=parsing_features,
            )
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            CreateDocumentFromFile(
                document_name=document_name,
                group_id=group_id,
                file_path=file_path,
                document_type_id=document_type_id,
                parsing_features=parsing_features,
                invoke_unifier=batch_file_classification_saga_data.needs_unifier,
                invoke_extraction=batch_file_classification_saga_data.needs_extraction,
                engine=engine,
                language=batch_file_classification_saga_data.language,
                llm_type=batch_file_classification_saga_data.llm_type,
                metadata=batch_file_classification_saga_data.metadata,
                assigned_to_me=batch_file_classification_saga_data.assigned_to_me,
                start_processing=batch_file_classification_saga_data.start_processing,
            ),
        )
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply(CreateDocumentFromFileReply(document_id=document_id))
        .expect_completed_successfully()
    )

    assert suts.saga_data["current_state"] == State.COMPLETED
    _, message = first(message_producer_mock.sent_messages)
    payload = json.loads(message.payload)

    assert payload["batch_id"] == batch_id
    assert payload["file_id"] == file_id
    assert payload["document_id"] == document_id
    assert payload["document_type_id"] == document_type_id
    assert payload["error_type"] is None
    assert payload["error_message"] is None
    assert len(fake_object_storage.storage) == 1


def test_batch_file_classification__unification__failure(
    suts_batch_file_classification,
    file_path,
    file_id,
    batch_id,
    message_producer_mock,
):
    suts = (
        suts_batch_file_classification.expect()
        .command(PerformUnification(file_id, [file_path]))
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .failure_reply()
        .expect_rolled_back()
    )

    assert suts.saga_data["current_state"] == State.UNIFICATION
    _, message = first(message_producer_mock.sent_messages)
    payload = json.loads(message.payload)

    assert payload["batch_id"] == batch_id
    assert payload["file_id"] == file_id
    assert payload["error_type"] is not None


def test_batch_file_classification__classification__failure(
    batch_file_classification_saga_data: BatchFileClassificationSagaData,
    suts_batch_file_classification,
    message_producer_mock,
    file_path,
    file_id,
    batch_id,
    tenant_id,
    engine,
    parsing_features,
):
    suts = (
        suts_batch_file_classification.expect()
        .command(PerformUnification(file_id, [file_path]))
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                tenant_id=tenant_id,
                document_id=file_id,
                files=[file_path],
                engine=engine,
                language=batch_file_classification_saga_data.language,
                features=parsing_features,
            )
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply()
        .expect_rolled_back()
    )

    assert suts.saga_data["current_state"] == State.CLASSIFICATION
    _, message = first(message_producer_mock.sent_messages)
    payload = json.loads(message.payload)

    assert payload["batch_id"] == batch_id
    assert payload["file_id"] == file_id
    assert payload["error_type"] is not None


def test_batch_file_classification__parsing__failure(
    batch_file_classification_saga_data: BatchFileClassificationSagaData,
    suts_batch_file_classification,
    message_producer_mock,
    file_path,
    file_id,
    batch_id,
    tenant_id,
    engine,
    parsing_features,
):
    suts = (
        suts_batch_file_classification.expect()
        .command(PerformUnification(file_id, [file_path]))
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                tenant_id=tenant_id,
                document_id=file_id,
                files=[file_path],
                engine=engine,
                language=batch_file_classification_saga_data.language,
                features=parsing_features,
            )
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .failure_reply()
        .expect_rolled_back()
    )

    assert suts.saga_data["current_state"] == State.PARSING
    _, message = first(message_producer_mock.sent_messages)
    payload = json.loads(message.payload)

    assert payload["batch_id"] == batch_id
    assert payload["file_id"] == file_id
    assert payload["error_type"] is not None


@pytest.mark.usefixtures(
    "add_gen_ai_classifiers",
    "fake_ai_fusion_proxy_with_success_response",
    "add_object_to_storage",
)
def test_batch_file_classification__document_creation__failure(
    batch_file_classification_saga_data: BatchFileClassificationSagaData,
    suts_batch_file_classification,
    message_producer_mock,
    fake_object_storage,
    file_path,
    file_id,
    batch_id,
    tenant_id,
    engine,
    parsing_features,
    document_name,
    group_id,
    document_type_id,
):
    suts = (
        suts_batch_file_classification.expect()
        .command(PerformUnification(file_id, [file_path]))
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                tenant_id=tenant_id,
                document_id=file_id,
                files=[file_path],
                engine=engine,
                language=batch_file_classification_saga_data.language,
                features=parsing_features,
            )
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            CreateDocumentFromFile(
                document_name=document_name,
                group_id=group_id,
                file_path=file_path,
                document_type_id=document_type_id,
                parsing_features=parsing_features,
                invoke_unifier=batch_file_classification_saga_data.needs_unifier,
                invoke_extraction=batch_file_classification_saga_data.needs_extraction,
                engine=engine,
                language=batch_file_classification_saga_data.language,
                llm_type=batch_file_classification_saga_data.llm_type,
                metadata=batch_file_classification_saga_data.metadata,
                assigned_to_me=batch_file_classification_saga_data.assigned_to_me,
                start_processing=batch_file_classification_saga_data.start_processing,
            ),
        )
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .failure_reply()
        .expect_rolled_back()
    )

    assert suts.saga_data["current_state"] == State.DOCUMENT_CREATION
    _, message = first(message_producer_mock.sent_messages)
    payload = json.loads(message.payload)

    assert payload["batch_id"] == batch_id
    assert payload["file_id"] == file_id
    assert payload["error_type"] is not None
    assert len(fake_object_storage.storage) == 1
