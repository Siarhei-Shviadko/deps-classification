from datetime import datetime

import pytest

from deps_classification.domain.exceptions import IllegalArgument
from deps_classification.domain.model import (
    GenAIClassifier,
    GenAIClassifierDeleted,
    GenAIClassifierUpdated,
)


def test_gen_ai_classifier_creation(gen_ai_classifier_1):
    assert isinstance(gen_ai_classifier_1, GenAIClassifier)
    assert gen_ai_classifier_1.prompt is not None
    assert gen_ai_classifier_1.llm_type is not None
    assert gen_ai_classifier_1.name is not None


def test_gen_ai_classifier_update(gen_ai_classifier_1):
    new_prompt = "new_prompt"
    new_llm_type = "new_llm_type"
    new_name = "new_name"
    gen_ai_classifier_1.update(prompt=new_prompt, llm_type=new_llm_type, name=new_name)

    assert gen_ai_classifier_1.prompt == new_prompt
    assert gen_ai_classifier_1.llm_type == new_llm_type
    assert gen_ai_classifier_1.name == new_name
    assert len(gen_ai_classifier_1.events) == 1
    assert isinstance(gen_ai_classifier_1.events[0], GenAIClassifierUpdated)


def test_gen_ai_classifier_delete(gen_ai_classifier_1):
    gen_ai_classifier_1.delete()

    assert len(gen_ai_classifier_1.events) == 1
    assert isinstance(gen_ai_classifier_1.events[0], GenAIClassifierDeleted)


def test_gen_ai_classifier_equality(gen_ai_classifier_1, gen_ai_classifier_2):
    assert gen_ai_classifier_1 != gen_ai_classifier_2
    assert gen_ai_classifier_1 == gen_ai_classifier_1


def test_gen_ai_classifier_repr(gen_ai_classifier_1):
    repr_str = repr(gen_ai_classifier_1)
    assert "GenAIClassifier" in repr_str
    assert gen_ai_classifier_1.id() in repr_str


def test_gen_ai_classifier_edge_cases():
    with pytest.raises(IllegalArgument):
        GenAIClassifier(
            id_="",
            tenant_id="",
            group_id="",
            document_type_id="",
            prompt="",
            llm_type="",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            name="",
        )
