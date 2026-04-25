from pydantic import Field

from .configured_base_serializer import ConfiguredResponseSerializer

__all__ = ["BuildInfoSerializer"]


class BuildInfoSerializer(ConfiguredResponseSerializer):
    build_tag: str = Field(default="", alias="buildTag")
    build_date: str = Field(default="", alias="buildDate")
    commit_hash: str = Field(default="", alias="commitHash")
