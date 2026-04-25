import uuid
from http import HTTPStatus

from starlette.testclient import TestClient

from deps_classification.constants import V1_API_PREFIX
from deps_classification.domain.model import GenAIClassifier, Group


def test_get_gen_ai_classifiers_of_document_type__ok(
    client: TestClient,
    group_1: Group,
    gen_ai_classifier_1: GenAIClassifier,
    add_groups,
    add_gen_ai_classifiers,
):
    url = f"{V1_API_PREFIX}/document-types/{group_1.document_types[0]()}/gen-ai-classifiers"

    response = client.get(url)

    assert response.status_code == HTTPStatus.OK

    display_info = response.json()["genAiClassifiers"][0]

    assert display_info["genAiClassifierId"] == gen_ai_classifier_1.id()
    assert display_info["documentTypeId"] == gen_ai_classifier_1.document_type_id()
    assert display_info["prompt"] == gen_ai_classifier_1.prompt
    assert display_info["llmType"] == gen_ai_classifier_1.llm_type
    assert display_info["name"] == gen_ai_classifier_1.name
