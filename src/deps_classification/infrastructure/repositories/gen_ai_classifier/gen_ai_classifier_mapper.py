from typing import Any

from deps_classification.domain.model import GenAIClassifier

__all__ = ["GenAIClassifierMapper"]


class GenAIClassifierMapper:
    @staticmethod
    def to_dict(gen_ai_classifier: GenAIClassifier) -> dict[str, Any]:
        return {
            "gen_ai_classifier_id": gen_ai_classifier.id(),
            "tenant_id": gen_ai_classifier.tenant_id(),
            "group_id": gen_ai_classifier.group_id(),
            "document_type_id": gen_ai_classifier.document_type_id(),
            "prompt": gen_ai_classifier.prompt,
            "llm_type": gen_ai_classifier.llm_type,
            "created_at": gen_ai_classifier.created_at,
            "updated_at": gen_ai_classifier.updated_at,
            "name": gen_ai_classifier.name,
        }

    @staticmethod
    def from_dict(gen_ai_classifier: dict[str, Any]) -> GenAIClassifier:
        return GenAIClassifier(
            id_=gen_ai_classifier["gen_ai_classifier_id"],
            tenant_id=gen_ai_classifier["tenant_id"],
            group_id=gen_ai_classifier["group_id"],
            document_type_id=gen_ai_classifier["document_type_id"],
            prompt=gen_ai_classifier["prompt"],
            llm_type=gen_ai_classifier["llm_type"],
            created_at=gen_ai_classifier["created_at"],
            updated_at=gen_ai_classifier["updated_at"],
            name=gen_ai_classifier["name"],
        )
