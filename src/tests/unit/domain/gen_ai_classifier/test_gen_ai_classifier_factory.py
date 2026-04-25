from datetime import datetime

import pytest

from deps_classification.domain.exceptions import IllegalArgument
from deps_classification.domain.model import (
    GenAIClassifierCreated,
    GenAIClassifierFactory,
)


def test_create_gen_ai_classifier(tenant_id, group_1, group_1_document_types):
    document_type_id = group_1_document_types[0]

    prompt = "Test prompt"
    llm_type = "Test LLM"
    name = "Test name"

    classifier = GenAIClassifierFactory.create(
        tenant_id=tenant_id,
        group_id=group_1.id(),
        document_type_id=document_type_id,
        prompt=prompt,
        llm_type=llm_type,
        name=name,
    )

    assert classifier.id is not None
    assert classifier.tenant_id() == tenant_id
    assert classifier.group_id() == group_1.id()
    assert classifier.document_type_id() == document_type_id
    assert classifier.prompt == prompt
    assert classifier.llm_type == llm_type
    assert classifier.name == name
    assert isinstance(classifier.created_at, datetime)
    assert isinstance(classifier.updated_at, datetime)
    assert len(classifier.events) == 1
    assert isinstance(classifier.events[0], GenAIClassifierCreated)
    assert classifier.events[0].id == classifier.id()
    assert classifier.events[0].tenant_id == tenant_id
    assert classifier.events[0].group_id == group_1.id()
    assert classifier.events[0].document_type_id == document_type_id
    assert classifier.events[0].prompt == prompt
    assert classifier.events[0].llm_type == llm_type
    assert classifier.events[0].name == name


def test_create_gen_ai_classifier_invalid_params():
    with pytest.raises(IllegalArgument):
        GenAIClassifierFactory.create(
            tenant_id=None,
            group_id=None,
            document_type_id=None,
            prompt=None,
            llm_type=None,
            name=None,
        )

    with pytest.raises(IllegalArgument):
        GenAIClassifierFactory.create(
            tenant_id="",
            group_id="",
            document_type_id="",
            prompt="",
            llm_type="",
            name="",
        )
