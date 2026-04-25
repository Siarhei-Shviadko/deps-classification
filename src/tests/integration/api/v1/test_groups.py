import uuid
from http import HTTPStatus

from starlette.testclient import TestClient

from deps_classification.constants import V1_API_PREFIX
from deps_classification.domain.model import GenAIClassifierDisplayInfo, Group


def test_get_gen_ai_classifiers_of_group__ok(
    client: TestClient,
    group_1: Group,
    test_gen_ai_classifiers_display_infos: list[GenAIClassifierDisplayInfo],
    add_groups,
    add_gen_ai_classifiers,
):
    url = f"{V1_API_PREFIX}/groups/{group_1.id()}/gen-ai-classifiers"

    response = client.get(url)

    assert response.status_code == HTTPStatus.OK

    display_infos = sorted(response.json()["genAiClassifiers"], key=lambda classifier: classifier["name"])
    test_gen_ai_classifiers_display_infos = sorted(
        test_gen_ai_classifiers_display_infos, key=lambda classifier: classifier["name"]
    )

    for display_info, expected_display_info in zip(display_infos, test_gen_ai_classifiers_display_infos):
        assert display_info["genAiClassifierId"] == expected_display_info["gen_ai_classifier_id"]
        assert display_info["documentTypeId"] == expected_display_info["document_type_id"]
        assert display_info["prompt"] == expected_display_info["prompt"]
        assert display_info["llmType"] == expected_display_info["llm_type"]
        assert display_info["name"] == expected_display_info["name"]


def test_get_gen_ai_classifiers_of_group__group_does_not_exist__not_found(
    client: TestClient,
    test_gen_ai_classifiers_display_infos: list[GenAIClassifierDisplayInfo],
    add_gen_ai_classifiers,
):
    url = f"{V1_API_PREFIX}/groups/{uuid.uuid4().hex}/gen-ai-classifiers"

    response = client.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND
