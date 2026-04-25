from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError


def test_gen_ai_classifier_of_id_success(unit_of_work, gen_ai_classifier_1, add_gen_ai_classifiers):
    assert (
        unit_of_work.gen_ai_classifiers.gen_ai_classifier_of_id(
            gen_ai_classifier_1.id(), gen_ai_classifier_1.tenant_id()
        )
        == gen_ai_classifier_1
    )


def test_gen_ai_classifier_of_id_not_found(unit_of_work, tenant_id):
    assert unit_of_work.gen_ai_classifiers.gen_ai_classifier_of_id("non_existent_id", tenant_id) is None


def test_save_success(unit_of_work, gen_ai_classifier_1):
    unit_of_work.gen_ai_classifiers.save(gen_ai_classifier_1)

    assert (
        unit_of_work.gen_ai_classifiers.gen_ai_classifier_of_id(
            gen_ai_classifier_1.id(), gen_ai_classifier_1.tenant_id()
        )
        == gen_ai_classifier_1
    )


def test_save_name_group_id_unique_constraint_violated__error(unit_of_work, gen_ai_classifier_1, gen_ai_classifier_2):
    gen_ai_classifier_2.name = gen_ai_classifier_1.name

    unit_of_work.gen_ai_classifiers.save(gen_ai_classifier_1)

    with pytest.raises(IntegrityError):
        unit_of_work.gen_ai_classifiers.save(gen_ai_classifier_2)


def test_delete_success(unit_of_work, gen_ai_classifier_1, add_gen_ai_classifiers):
    unit_of_work.gen_ai_classifiers.delete_all([gen_ai_classifier_1])

    assert (
        unit_of_work.gen_ai_classifiers.gen_ai_classifier_of_id(
            gen_ai_classifier_1.id(), gen_ai_classifier_1.tenant_id()
        )
        is None
    )


def test_update_success(unit_of_work, gen_ai_classifier_1, add_gen_ai_classifiers):
    new_prompt, new_llm_type, new_name = uuid4().hex, uuid4().hex, uuid4().hex
    gen_ai_classifier_1.update(prompt=new_prompt, llm_type=new_llm_type, name=new_name)

    unit_of_work.gen_ai_classifiers.save(gen_ai_classifier_1)

    updated_classifier = unit_of_work.gen_ai_classifiers.gen_ai_classifier_of_id(
        gen_ai_classifier_1.id(), gen_ai_classifier_1.tenant_id()
    )

    assert updated_classifier.prompt == new_prompt
    assert updated_classifier.llm_type == new_llm_type
    assert updated_classifier.name == new_name


def test_has_gen_ai_classifier_for_group_success(unit_of_work, gen_ai_classifier_1, add_gen_ai_classifiers):
    assert unit_of_work.gen_ai_classifiers.has_gen_ai_classifier_for_group(
        gen_ai_classifier_1.group_id(), gen_ai_classifier_1.tenant_id(), gen_ai_classifier_1.document_type_id()
    )


def test_has_gen_ai_classifier_for_group_not_found(unit_of_work, tenant_id, group_1):
    assert not unit_of_work.gen_ai_classifiers.has_gen_ai_classifier_for_group(
        group_1.id(), tenant_id, "non_existent_document_type_id"
    )


def test_has_gen_ai_classifier_with_name_success(unit_of_work, gen_ai_classifier_1, add_gen_ai_classifiers):
    assert unit_of_work.gen_ai_classifiers.has_gen_ai_classifier_with_name(
        gen_ai_classifier_1.name, gen_ai_classifier_1.group_id(), gen_ai_classifier_1.tenant_id()
    )


def test_has_gen_ai_classifier_with_name_not_found(unit_of_work, tenant_id, group_1):
    assert not unit_of_work.gen_ai_classifiers.has_gen_ai_classifier_with_name(
        "non_existent_gen_ai_classifier_name", group_1.id(), tenant_id
    )


def test_gen_ai_classifiers_of_ids_success(unit_of_work, gen_ai_classifier_1, add_gen_ai_classifiers):
    gen_ai_classifier_ids = [gen_ai_classifier_1.id()]
    classifiers = unit_of_work.gen_ai_classifiers.gen_ai_classifiers_of_ids(
        gen_ai_classifier_ids, gen_ai_classifier_1.tenant_id()
    )

    assert len(classifiers) == 1
    assert classifiers[0] == gen_ai_classifier_1


def test_gen_ai_classifiers_of_ids_not_found(unit_of_work, tenant_id):
    classifiers = unit_of_work.gen_ai_classifiers.gen_ai_classifiers_of_ids(["non_existent_id"], tenant_id)

    assert len(classifiers) == 0


def test_gen_ai_classifiers_of_group__success(
    unit_of_work, tenant_id, group_1, group_1_document_types, test_gen_ai_classifiers, add_gen_ai_classifiers
):
    classifiers = unit_of_work.gen_ai_classifiers.gen_ai_classifiers_of_group(
        group_1.id(), tenant_id, [group_1_document_types[0]]
    )

    assert len(classifiers) == 1
    assert classifiers[0] == test_gen_ai_classifiers[0]


def test_gen_ai_classifiers_of_group__without_ids__success(
    unit_of_work, tenant_id, group_1, test_gen_ai_classifiers, add_gen_ai_classifiers
):
    classifiers = unit_of_work.gen_ai_classifiers.gen_ai_classifiers_of_group(group_1.id(), tenant_id)

    assert len(classifiers) == len(test_gen_ai_classifiers)
    assert classifiers[0] == test_gen_ai_classifiers[0]
    assert classifiers[1] == test_gen_ai_classifiers[1]
