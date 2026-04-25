import json

import pytest
from deps_message_flow.sagas.testing_support import *
from more_itertools import first

from deps_classification.messaging import (
    CreateDocumentFromFile,
    CreateDocumentFromFileReply,
    Destination,
    FileClassificationSagaData,
    PerformParsing,
    PerformUnification,
    State,
)


@pytest.mark.usefixtures(
    "add_gen_ai_classifiers",
    "fake_ai_fusion_proxy_with_success_response",
    "add_object_to_storage",
)
def test_file_classification__success(
    file_classification_saga_data: FileClassificationSagaData,
    suts_file_classification,
    message_producer_mock,
    fake_object_storage,
    file_path,
    file_id,
    tenant_id,
    files,
    engine,
    parsing_features,
    document_name,
    group_id,
    document_type_id,
    document_id,
):
    suts = (
        suts_file_classification.expect()
        .command(PerformUnification(file_id, [file_path]))
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                tenant_id=tenant_id,
                document_id=file_id,
                files=files,
                engine=engine,
                language=file_classification_saga_data.language,
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
                invoke_unifier=file_classification_saga_data.needs_unifier,
                invoke_extraction=file_classification_saga_data.needs_extraction,
                engine=engine,
                language=file_classification_saga_data.language,
                llm_type=file_classification_saga_data.llm_type,
                metadata=file_classification_saga_data.metadata,
                assigned_to_me=file_classification_saga_data.assigned_to_me,
                start_processing=file_classification_saga_data.start_processing,
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

    assert payload["file_id"] == file_id
    assert payload["document_id"] == document_id
    assert payload["document_type_id"] == document_type_id
    assert payload["error_type"] is None
    assert payload["error_message"] is None
    assert len(fake_object_storage.storage) == 2


def test_file_classification__unification__failure(
    suts_file_classification,
    file_path,
    file_id,
    message_producer_mock,
):
    suts = (
        suts_file_classification.expect()
        .command(PerformUnification(file_id, [file_path]))
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .failure_reply()
        .expect_rolled_back()
    )

    assert suts.saga_data["current_state"] == State.UNIFICATION
    assert first(message_producer_mock.sent_messages)


def test_file_classification__classification__failure(
    file_classification_saga_data: FileClassificationSagaData,
    suts_file_classification,
    message_producer_mock,
    file_path,
    file_id,
    tenant_id,
    files,
    engine,
    parsing_features,
):
    suts = (
        suts_file_classification.expect()
        .command(PerformUnification(file_id, [file_path]))
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                tenant_id=tenant_id,
                document_id=file_id,
                files=files,
                engine=engine,
                language=file_classification_saga_data.language,
                features=parsing_features,
            )
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply()
        .expect_rolled_back()
    )

    assert suts.saga_data["current_state"] == State.CLASSIFICATION
    assert first(message_producer_mock.sent_messages)


def test_file_classification__parsing__failure(
    file_classification_saga_data: FileClassificationSagaData,
    suts_file_classification,
    message_producer_mock,
    file_path,
    file_id,
    tenant_id,
    files,
    engine,
    parsing_features,
):
    suts = (
        suts_file_classification.expect()
        .command(PerformUnification(file_id, [file_path]))
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                tenant_id=tenant_id,
                document_id=file_id,
                files=files,
                engine=engine,
                language=file_classification_saga_data.language,
                features=parsing_features,
            )
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .failure_reply()
        .expect_rolled_back()
    )

    assert suts.saga_data["current_state"] == State.PARSING
    assert first(message_producer_mock.sent_messages)


@pytest.mark.usefixtures(
    "add_gen_ai_classifiers",
    "fake_ai_fusion_proxy_with_success_response",
    "add_object_to_storage",
)
def test_file_classification__document_creation__failure(
    file_classification_saga_data: FileClassificationSagaData,
    suts_file_classification,
    message_producer_mock,
    fake_object_storage,
    file_path,
    file_id,
    tenant_id,
    files,
    engine,
    parsing_features,
    document_name,
    group_id,
    document_type_id,
):
    suts = (
        suts_file_classification.expect()
        .command(PerformUnification(file_id, [file_path]))
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                tenant_id=tenant_id,
                document_id=file_id,
                files=files,
                engine=engine,
                language=file_classification_saga_data.language,
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
                invoke_unifier=file_classification_saga_data.needs_unifier,
                invoke_extraction=file_classification_saga_data.needs_extraction,
                engine=engine,
                language=file_classification_saga_data.language,
                llm_type=file_classification_saga_data.llm_type,
                metadata=file_classification_saga_data.metadata,
                assigned_to_me=file_classification_saga_data.assigned_to_me,
                start_processing=file_classification_saga_data.start_processing,
            ),
        )
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .failure_reply()
        .expect_rolled_back()
    )

    assert suts.saga_data["current_state"] == State.DOCUMENT_CREATION
    assert first(message_producer_mock.sent_messages)
    assert len(fake_object_storage.storage) == 1
