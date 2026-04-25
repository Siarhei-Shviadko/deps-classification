from datetime import datetime
from uuid import uuid4

from .gen_ai_classifier import GenAIClassifier
from .gen_ai_classifier_created import GenAIClassifierCreated

__all__ = ["GenAIClassifierFactory"]


class GenAIClassifierFactory:
    @classmethod
    def create(
        cls,
        tenant_id: str,
        group_id: str,
        document_type_id: str,
        prompt: str,
        llm_type: str,
        name: str,
    ) -> GenAIClassifier:
        classifier_id = uuid4().hex

        return GenAIClassifier(
            id_=classifier_id,
            tenant_id=tenant_id,
            group_id=group_id,
            document_type_id=document_type_id,
            prompt=prompt,
            llm_type=llm_type,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            name=name,
            events=[
                GenAIClassifierCreated(
                    id=classifier_id,
                    tenant_id=tenant_id,
                    group_id=group_id,
                    document_type_id=document_type_id,
                    prompt=prompt,
                    llm_type=llm_type,
                    name=name,
                ),
            ],
        )
