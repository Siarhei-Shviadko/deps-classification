from http import HTTPStatus
from uuid import uuid4

from deps_classification.constants import V1_API_PREFIX


def test_create_gen_ai_classifier__classifier_created(client, group_1, group_1_document_types, add_groups):
    response = client.post(
        f"{V1_API_PREFIX}/gen-ai-classifiers",
        json={
            "group_id": group_1.id(),
            "document_type_id": group_1_document_types[0],
            "prompt": uuid4().hex,
            "llm_type": uuid4().hex,
            "name": uuid4().hex,
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()["id"] is not None


def test_update_classifier__updated(client, gen_ai_classifier_1, add_gen_ai_classifiers):
    new_prompt = uuid4().hex
    new_llm_type = uuid4().hex
    new_name = uuid4().hex

    response = client.patch(
        f"{V1_API_PREFIX}/gen-ai-classifiers/{gen_ai_classifier_1.id()}",
        json={
            "prompt": new_prompt,
            "llm_type": new_llm_type,
            "name": new_name,
        },
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


def test_update_classifier__updated__with_same_name(client, gen_ai_classifier_1, add_gen_ai_classifiers):
    new_prompt = uuid4().hex
    new_llm_type = uuid4().hex

    response = client.patch(
        f"{V1_API_PREFIX}/gen-ai-classifiers/{gen_ai_classifier_1.id()}",
        json={
            "prompt": new_prompt,
            "llm_type": new_llm_type,
            "name": gen_ai_classifier_1.name,
        },
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_classifiers__classifiers_deleted(client, gen_ai_classifier_1, add_gen_ai_classifiers):
    classifier_ids = [gen_ai_classifier_1.id()]

    response = client.delete(
        f"{V1_API_PREFIX}/gen-ai-classifiers",
        params={"id": classifier_ids},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
