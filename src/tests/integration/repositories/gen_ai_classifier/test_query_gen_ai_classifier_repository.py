from deps_classification.domain.model import (
    GenAIClassifier,
    GenAIClassifierDisplayInfo,
    Group,
    IQueryGenAIClassifierRepository,
)


def test_find_display_info_of_group(
    query_gen_ai_classifier_repository: IQueryGenAIClassifierRepository,
    group_1: Group,
    add_groups,
    add_gen_ai_classifiers,
    test_gen_ai_classifiers_display_infos: list[GenAIClassifierDisplayInfo],
):
    display_infos = query_gen_ai_classifier_repository.find_all_classifier_display_info_of_group(
        group_id=group_1.id(), tenant_id=group_1.tenant_id()
    )

    assert len(display_infos) == len(test_gen_ai_classifiers_display_infos)

    sorted_display_infos = sorted(display_infos, key=lambda x: x["gen_ai_classifier_id"])
    sorted_expected = sorted(test_gen_ai_classifiers_display_infos, key=lambda x: x["gen_ai_classifier_id"])

    for display_info, expected_display_info in zip(sorted_display_infos, sorted_expected):
        assert display_info == expected_display_info


def test_find_display_info_of_document_type(
    query_gen_ai_classifier_repository: IQueryGenAIClassifierRepository,
    group_1: Group,
    add_groups,
    add_gen_ai_classifiers,
    gen_ai_classifier_1: GenAIClassifier,
):
    display_infos = query_gen_ai_classifier_repository.find_all_classifier_display_info_of_document_type(
        document_type_id=group_1.document_types[0](), tenant_id=group_1.tenant_id()
    )

    assert len(display_infos) == 1

    assert display_infos[0]["gen_ai_classifier_id"] == gen_ai_classifier_1.id()
    assert display_infos[0]["document_type_id"] == gen_ai_classifier_1.document_type_id()
    assert display_infos[0]["prompt"] == gen_ai_classifier_1.prompt
    assert display_infos[0]["llm_type"] == gen_ai_classifier_1.llm_type
    assert display_infos[0]["name"] == gen_ai_classifier_1.name
