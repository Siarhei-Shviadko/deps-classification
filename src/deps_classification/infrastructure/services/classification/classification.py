import logging
from collections import Counter

from deps_classification.domain.model import GenAIClassifier
from deps_classification.infrastructure.unit_of_work import AbstractUnitOfWork

from .classification_results import ClassificationResult
from .i_prompted_classifier import IPromptedClassifier
from .request import ClassificationRequestFactory
from .types import T_UNKNOWN, UNKNOWN, DocumentTypeCode

__all__ = ["ClassificationService"]


class ClassificationService:
    _grouping_factor: int = 1
    _classification_temperature: int = 0
    _classification_instructions: str = """
        You are an expert document classifier.

        Goal:
        - Analyze the provided document content and choose exactly one category from the list supplied in the prompt.
        - Use only the CategoryId values provided. Do not invent new categories.

        Output requirements:
        - Respond using structured JSON matching the provided response schema.
        - Return exactly the keys: category_id, confidence, reasoning. No extra fields.
        - "confidence" must be a number from 0 to 100 (higher means stronger match).
        - "reasoning" must be concise and factual; avoid speculation and do not include policy text.

        Decision policy:
        - If an "Other" category is present and nothing matches, choose "Other" with an appropriate low confidence and short justification.
        - If no "Other" category is present and no category clearly applies, set category_id to null and confidence to 0
        - Prefer precise matches over broad ones. If multiple categories seem plausible, pick the closest match and explain briefly why.
        - Use the category descriptions as the source of truth. Avoid relying on generic assumptions.
    """

    def __init__(
        self,
        unit_of_work: AbstractUnitOfWork,
        prompted_classifier: IPromptedClassifier,
    ) -> None:
        self._prompted_classifier = prompted_classifier
        self._uow = unit_of_work

        self._logger = logging.getLogger(self.__class__.__name__)

    def classify(
        self,
        document_id: str,
        tenant_id: str,
        document_type_group_id: str,
    ) -> DocumentTypeCode | T_UNKNOWN:
        self._logger.info(f"Classifying document `{document_id}` on group `{document_type_group_id}`...")

        with self._uow:
            classifiers = self._uow.gen_ai_classifiers.gen_ai_classifiers_of_group(
                group_id=document_type_group_id,
                tenant_id=tenant_id,
            )

            self._uow.commit()

        if not classifiers:
            self._logger.warning(
                "Group `%s` has no classifiers. Therefore Group classification skipped.",
                document_type_group_id,
            )
            return UNKNOWN

        return self._perform_gen_ai_classification(document_id=document_id, gen_ai_classifiers=classifiers)

    def _perform_gen_ai_classification(
        self,
        document_id: str,
        gen_ai_classifiers: list[GenAIClassifier],
    ) -> DocumentTypeCode | T_UNKNOWN:
        """
        We going to use a single LLM for all classifiers, by choosing the most popular LLM Type.
        Then we perform a single AI Fusion request utilizing the structured output
            to make model respond with estimations for each document type.
        """
        try:
            counted_llms = Counter([classifier.llm_type for classifier in gen_ai_classifiers])
            most_common_llm: str = counted_llms.most_common(1)[0][0]

            response = self._prompted_classifier.classify_document(
                document_id=document_id,
                llm_reference=most_common_llm,
                dt_classification_request=(
                    ClassificationRequestFactory.from_classifiers(gen_ai_classifiers).compose_request()
                ),
                custom_instructions=self._classification_instructions.strip(),
                temperature=self._classification_temperature,
                grouping_factor=self._grouping_factor,
            )

            return ClassificationResult.handling_response(gen_ai_classifiers, response).identify_document_type()
        except Exception as ex:
            self._logger.error(
                f"{type(ex).__name__} occurred during '{document_id}' classification: `{ex}`. Document will be classified as 'Unknown'.",
                exc_info=True,
            )

        return UNKNOWN
