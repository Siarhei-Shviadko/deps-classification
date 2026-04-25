from sqlalchemy import Column, DateTime, ForeignKey, String, Table, UniqueConstraint

from deps_classification.extras import metadata

__all__ = ["gen_ai_classifier_table"]


gen_ai_classifier_table = Table(
    "gen_ai_classifier",
    metadata,
    Column("gen_ai_classifier_id", String, primary_key=True),
    Column("tenant_id", String, nullable=False),
    Column("group_id", String, nullable=False),
    Column(
        "document_type_id",
        String,
        ForeignKey("group_document_types.document_type_id", ondelete="cascade", name="document_type_id_fk"),
        nullable=False,
    ),
    Column("prompt", String, nullable=False),
    Column("llm_type", String, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    Column("name", String, nullable=False),
    UniqueConstraint("name", "group_id", name="gen_ai_classifier_unique_name_group_id"),
)
