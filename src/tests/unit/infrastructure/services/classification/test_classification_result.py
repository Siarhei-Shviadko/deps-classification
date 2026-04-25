import json

from deps_classification.infrastructure.services import (
    ClassificationResult,
    RawClassificationResponse,
)


class _DummyClassifier:
    def __init__(self, code: str) -> None:
        self._code = code

    def document_type_id(self) -> str:
        return self._code


def test_identify_document_type__valid():
    classifiers = [_DummyClassifier("type1"), _DummyClassifier("type2")]
    response = RawClassificationResponse(
        elements={
            "insight-code": {
                "content": json.dumps(
                    {
                        "category_id": "type1",
                        "confidence": 87.0,
                        "reasoning": "matches",
                    },
                ),
            },
        }
    )

    result = ClassificationResult.handling_response(classifiers, response).identify_document_type()

    assert result == "type1"


def test_identify_document_type__unknown_when_none():
    classifiers = [_DummyClassifier("type1"), _DummyClassifier("type2")]
    response = RawClassificationResponse(
        elements={
            "insight-code": {
                "content": json.dumps(
                    {
                        "category_id": None,
                        "confidence": 0.0,
                        "reasoning": "no match",
                    },
                ),
            },
        }
    )

    result = ClassificationResult.handling_response(classifiers, response).identify_document_type()

    from deps_classification.infrastructure.services import UNKNOWN

    assert result == UNKNOWN


def test_identify_document_type__unknown_when_not_in_available():
    classifiers = [_DummyClassifier("type1"), _DummyClassifier("type2")]
    response = RawClassificationResponse(
        elements={
            "insight-code": {
                "content": json.dumps(
                    {
                        "category_id": "type3",
                        "confidence": 70.0,
                        "reasoning": "out of set",
                    },
                ),
            },
        }
    )

    result = ClassificationResult.handling_response(classifiers, response).identify_document_type()

    from deps_classification.infrastructure.services import UNKNOWN

    assert result == UNKNOWN
