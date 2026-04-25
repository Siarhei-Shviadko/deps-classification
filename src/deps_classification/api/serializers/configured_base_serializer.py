from pydantic import BaseModel, ConfigDict

__all__ = ["ConfiguredResponseSerializer", "ConfiguredRequestSerializer"]


class ConfiguredRequestSerializer(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
        use_enum_values=True,
    )


class ConfiguredResponseSerializer(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
    )
