import uuid

import pytest

from deps_classification.application.gen_ai_classifier import (
    QueryGenAIClassifierService,
)
from deps_classification.domain.exceptions import GroupNotFound
from deps_classification.domain.model import (
    GenAIClassifier,
    GenAIClassifierDisplayInfo,
    Group,
)


def test_find_all_of_group___success(
    query_gen_ai_classifier_service: QueryGenAIClassifierService,
    group_1: Group,
    add_groups,
    add_gen_ai_classifiers,
    test_gen_ai_classifiers_display_infos: list[GenAIClassifierDisplayInfo],
):
    display_infos = query_gen_ai_classifier_service.find_all_of_group(
        group_id=group_1.id(),
        tenant_id=group_1.tenant_id(),
    )

    assert len(display_infos) == len(test_gen_ai_classifiers_display_infos)

    display_infos = sorted(display_infos, key=lambda classifier: classifier["name"])
    test_gen_ai_classifiers_display_infos = sorted(
        test_gen_ai_classifiers_display_infos, key=lambda classifier: classifier["name"]
    )

    for display_info, expected_display_info in zip(display_infos, test_gen_ai_classifiers_display_infos):
        assert display_info == expected_display_info


def test_find_all_of_group___group_does_not_exist(
    query_gen_ai_classifier_service: QueryGenAIClassifierService,
    add_gen_ai_classifiers,
    test_gen_ai_classifiers_display_infos,
):
    with pytest.raises(GroupNotFound):
        query_gen_ai_classifier_service.find_all_of_group(group_id=uuid.uuid4().hex, tenant_id=uuid.uuid4().hex)


def test_find_all_of_document_type__success(
    query_gen_ai_classifier_service: QueryGenAIClassifierService,
    group_1: Group,
    add_groups,
    add_gen_ai_classifiers,
    gen_ai_classifier_1: GenAIClassifier,
):
    display_infos = query_gen_ai_classifier_service.find_all_of_document_type(
        document_type_id=group_1.document_types[0](),
        tenant_id=group_1.tenant_id(),
    )

    assert len(display_infos) == 1

    assert display_infos[0]["gen_ai_classifier_id"] == gen_ai_classifier_1.id()
    assert display_infos[0]["document_type_id"] == gen_ai_classifier_1.document_type_id()
    assert display_infos[0]["prompt"] == gen_ai_classifier_1.prompt
    assert display_infos[0]["llm_type"] == gen_ai_classifier_1.llm_type
    assert display_infos[0]["name"] == gen_ai_classifier_1.name
