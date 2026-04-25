from typing import Any, Mapping

from deps_classification.domain.model import GenAIClassifierDisplayInfo

__all__ = ["GenAIClassifierInfoMapper", "GenAIClassifiersInfoMapper"]

Row = Mapping[str, Any]


class GenAIClassifiersInfoMapper:
    @staticmethod
    def from_gen_ai_classifier_rows(rows: list[Row]) -> list[GenAIClassifierDisplayInfo]:
        return [GenAIClassifierInfoMapper.from_gen_ai_classifier_row(row) for row in rows]


class GenAIClassifierInfoMapper:
    @staticmethod
    def from_gen_ai_classifier_row(row: Row) -> GenAIClassifierDisplayInfo:
        return GenAIClassifierDisplayInfo(
            gen_ai_classifier_id=row["gen_ai_classifier_id"],
            document_type_id=row["document_type_id"],
            prompt=row["prompt"],
            llm_type=row["llm_type"],
            name=row["name"],
        )
