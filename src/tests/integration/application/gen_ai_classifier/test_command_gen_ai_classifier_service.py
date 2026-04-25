import pytest

from deps_classification.domain.exceptions import (
    GenAIClassifierAlreadyExists,
    GenAIClassifierNotFound,
    GenAIClassifierWithNameAlreadyExists,
    GroupWithDocumentTypeNotFound,
)


def test_create_gen_ai_classifier_success(command_gen_ai_classifier_service, group_1, tenant_id, add_groups):
    classifier = command_gen_ai_classifier_service.create(
        group_id=group_1.id(),
        tenant_id=tenant_id,
        document_type_id=group_1.document_types[0](),
        prompt="Test prompt",
        llm_type="Test llm_type",
        name="Test name",
    )
    assert classifier is not None
    assert classifier.prompt == "Test prompt"
    assert classifier.llm_type == "Test llm_type"
    assert classifier.name == "Test name"


def test_create_gen_ai_classifier_already_exists(
    command_gen_ai_classifier_service, gen_ai_classifier_1, tenant_id, add_groups, add_gen_ai_classifiers
):
    with pytest.raises(GenAIClassifierAlreadyExists):
        command_gen_ai_classifier_service.create(
            group_id=gen_ai_classifier_1.group_id(),
            tenant_id=tenant_id,
            document_type_id=gen_ai_classifier_1.document_type_id(),
            prompt="Test prompt",
            llm_type="Test llm_type",
            name="Test name",
        )


def test_create_gen_ai_classifier_with_name_already_exists(
    command_gen_ai_classifier_service, gen_ai_classifier_1, tenant_id, add_groups, add_gen_ai_classifiers
):
    with pytest.raises(GenAIClassifierWithNameAlreadyExists):
        command_gen_ai_classifier_service.create(
            group_id=gen_ai_classifier_1.group_id(),
            tenant_id=tenant_id,
            document_type_id=gen_ai_classifier_1.document_type_id(),
            prompt="Test prompt",
            llm_type="Test llm_type",
            name=gen_ai_classifier_1.name,
        )


def test_create_gen_ai_classifier_group_not_found(command_gen_ai_classifier_service, tenant_id, add_gen_ai_classifiers):
    with pytest.raises(GroupWithDocumentTypeNotFound):
        command_gen_ai_classifier_service.create(
            group_id="non_existent_group",
            tenant_id=tenant_id,
            document_type_id="non_existent_document_type",
            prompt="Test prompt",
            llm_type="Test llm_type",
            name="Test name",
        )


def test_update_classifier_success(
    command_gen_ai_classifier_service, gen_ai_classifier_1, tenant_id, add_gen_ai_classifiers
):
    updated_classifier = command_gen_ai_classifier_service.update(
        gen_ai_classifier_id=gen_ai_classifier_1.id(),
        tenant_id=tenant_id,
        prompt="Updated prompt",
        llm_type="Updated llm_type",
        name="Updated name",
    )
    assert updated_classifier.prompt == "Updated prompt"
    assert updated_classifier.llm_type == "Updated llm_type"
    assert updated_classifier.name == "Updated name"


def test_update_classifier_not_found(command_gen_ai_classifier_service, tenant_id):
    with pytest.raises(GenAIClassifierNotFound):
        command_gen_ai_classifier_service.update(
            gen_ai_classifier_id="non_existent_classifier",
            tenant_id=tenant_id,
            prompt="Updated prompt",
            llm_type="Updated llm_type",
            name="Updated name",
        )


def test_update_classifier_with_name_already_exists(
    command_gen_ai_classifier_service, gen_ai_classifier_1, tenant_id, add_gen_ai_classifiers
):
    updated_classifier = command_gen_ai_classifier_service.update(
        gen_ai_classifier_id=gen_ai_classifier_1.id(),
        tenant_id=tenant_id,
        prompt="Updated prompt",
        llm_type="Updated llm_type",
        name=gen_ai_classifier_1.name,
    )

    assert updated_classifier.id() == gen_ai_classifier_1.id()
    assert updated_classifier.prompt == "Updated prompt"
    assert updated_classifier.llm_type == "Updated llm_type"
    assert updated_classifier.name == gen_ai_classifier_1.name


def test_update_classifier_with_name_already_exists__error(
    command_gen_ai_classifier_service, gen_ai_classifier_1, gen_ai_classifier_2, tenant_id, add_gen_ai_classifiers
):
    with pytest.raises(GenAIClassifierWithNameAlreadyExists):
        command_gen_ai_classifier_service.update(
            gen_ai_classifier_id=gen_ai_classifier_1.id(),
            tenant_id=tenant_id,
            prompt="Updated prompt",
            llm_type="Updated llm_type",
            name=gen_ai_classifier_2.name,
        )


def test_delete_gen_ai_classifier_success(
    command_gen_ai_classifier_service, gen_ai_classifier_1, tenant_id, add_gen_ai_classifiers
):
    deleted_classifiers = command_gen_ai_classifier_service.delete(
        gen_ai_classifier_ids=[gen_ai_classifier_1.id()], tenant_id=tenant_id
    )
    assert gen_ai_classifier_1 in deleted_classifiers


def test_delete_for_group_document_types_success(
    command_gen_ai_classifier_service,
    tenant_id,
    group_1,
    group_1_document_types,
    test_gen_ai_classifiers,
    add_gen_ai_classifiers,
):
    deleted_classifiers = command_gen_ai_classifier_service.delete_for_group_document_types(
        group_1.id(),
        tenant_id,
        group_1_document_types,
    )
    sorted_expected = sorted(test_gen_ai_classifiers, key=lambda c: c.id())
    sorted_deleted = sorted(deleted_classifiers, key=lambda c: c.id())
    assert sorted_expected == sorted_deleted
