import json

from deps_classification.infrastructure.services import UNKNOWN, ClassificationService
from tests.fakes import FakeAIFusionProxy


def test_classify__valid_classification__same_llm_type(
    group_1,
    gen_ai_classifier_1,
    gen_ai_classifier_2,
    fake_unit_of_work,
    fake_ai_fusion_proxy: FakeAIFusionProxy,
    classification_service: ClassificationService,
) -> None:
    fake_unit_of_work.gen_ai_classifiers.gen_ai_classifiers_of_group.return_value = [
        gen_ai_classifier_1,
        gen_ai_classifier_2,
    ]
    fake_ai_fusion_proxy.saved_response = {
        "elements": {
            "insight-code": {
                "content": json.dumps(
                    {
                        "category_id": gen_ai_classifier_1.document_type_id(),
                        "confidence": 95.0,
                        "reasoning": "matches",
                    },
                ),
            },
        },
    }

    result = classification_service.classify(
        document_id="document_id",
        tenant_id="tenant_id",
        document_type_group_id=group_1.id(),
    )

    assert result == gen_ai_classifier_1.document_type_id()


def test_classify__valid_classification__different_llm_type(
    group_1,
    gen_ai_classifier_1,
    gen_ai_classifier_2,
    fake_unit_of_work,
    fake_ai_fusion_proxy: FakeAIFusionProxy,
    classification_service: ClassificationService,
) -> None:
    gen_ai_classifier_2.llm_type = "openai@another"
    fake_unit_of_work.gen_ai_classifiers.gen_ai_classifiers_of_group.return_value = [
        gen_ai_classifier_1,
        gen_ai_classifier_2,
    ]
    fake_ai_fusion_proxy.saved_response = {
        "elements": {
            "insight-code": {
                "content": json.dumps(
                    {
                        "category_id": gen_ai_classifier_2.document_type_id(),
                        "confidence": 88.0,
                        "reasoning": "matches",
                    },
                ),
            },
        },
    }

    result = classification_service.classify(
        document_id="document_id",
        tenant_id="tenant_id",
        document_type_group_id=group_1.id(),
    )

    assert result == gen_ai_classifier_2.document_type_id()


def test_classify__unknown(
    group_1,
    gen_ai_classifier_1,
    gen_ai_classifier_2,
    fake_unit_of_work,
    fake_ai_fusion_proxy: FakeAIFusionProxy,
    classification_service: ClassificationService,
) -> None:
    fake_unit_of_work.gen_ai_classifiers.gen_ai_classifiers_of_group.return_value = [
        gen_ai_classifier_1,
        gen_ai_classifier_2,
    ]
    fake_ai_fusion_proxy.saved_response = {
        "elements": {
            "insight-code": {
                "content": json.dumps(
                    {
                        "category_id": None,
                        "confidence": 0.0,
                        "reasoning": "no match",
                    },
                ),
            },
        },
    }

    result = classification_service.classify(
        document_id="document_id",
        tenant_id="tenant_id",
        document_type_group_id=group_1.id(),
    )

    assert result == UNKNOWN


def test_classify__no_classifiers__exception(
    group_1,
    gen_ai_classifier_1,
    gen_ai_classifier_2,
    fake_unit_of_work,
    fake_ai_fusion_proxy: FakeAIFusionProxy,
    classification_service: ClassificationService,
) -> None:
    fake_unit_of_work.gen_ai_classifiers.gen_ai_classifiers_of_group.return_value = []

    result = classification_service.classify(
        document_id="document_id",
        tenant_id="tenant_id",
        document_type_group_id=group_1.id(),
    )

    assert result == UNKNOWN
