from typing import Any

from deps_asb import ASBSettings
from deps_kafka import KafkaSettings
from deps_message_flow import MessagingDriverEnum
from deps_rabbitmq import RabbitMQTLSSettings
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from deps_classification.extras import DatabaseSettings, ServiceInfoSettings


class AIFusionProxySettings(BaseSettings):
    url: str
    timeout: int = 60

    model_config = SettingsConfigDict(env_prefix="AI_FUSION_")


class GenAIClassificationSettings(BaseSettings):
    grouping_factor: int = Field(1, validation_alias="GEN_AI_GROUPING_FACTOR")


class Settings(BaseSettings):
    env: str = "development"
    version: str = "1.0"

    logger_level: str = Field("INFO", validation_alias="LOG_LEVEL")

    info: ServiceInfoSettings = ServiceInfoSettings()
    database: DatabaseSettings = DatabaseSettings()

    messaging_driver: MessagingDriverEnum = Field(MessagingDriverEnum.RABBITMQ, validation_alias="MESSAGING_DRIVER")
    messaging_driver_settings: Any = Field(None, validation_alias="MESSAGING_DRIVER_SETTINGS")
    message_broker_connection_string: str

    ai_fusion: AIFusionProxySettings = AIFusionProxySettings()
    gen_ai: GenAIClassificationSettings = GenAIClassificationSettings()

    documentation_enabled: bool = True
    instrumentation_enabled: bool = False

    model_config = SettingsConfigDict(use_enum_values=True)

    @classmethod
    @field_validator("messaging_driver_settings")
    def validate_messaging_driver_settings(cls, v, values):  # noqa: N805
        messaging_driver = values.get("messaging_driver")
        if not messaging_driver:
            raise ValueError("Invalid messaging driver")

        driver = MessagingDriverEnum(messaging_driver)
        if driver == MessagingDriverEnum.ASB:
            return ASBSettings()
        elif driver == MessagingDriverEnum.KAFKA:
            return KafkaSettings()
        elif driver == MessagingDriverEnum.RABBITMQ:
            return RabbitMQTLSSettings().dict()  # TODO: use BaseSettings

        raise ValueError(f"Driver {driver} is not implemented")
