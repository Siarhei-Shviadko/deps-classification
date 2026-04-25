from typing import Any, Dict, Optional, Type, Union

from dependency_injector import containers, providers, resources
from deps_asb import ASBClient, ASBConsumer, ASBProducer
from deps_kafka import KafkaClient, KafkaConsumer, KafkaProducer
from deps_message_flow import MessagingDriverEnum
from deps_message_flow.commands.producer import CommandProducer
from deps_message_flow.events.publisher import DomainEventPublisher
from deps_message_flow.messaging.consumer import IMessageConsumer
from deps_message_flow.messaging.producer import IMessageProducer
from deps_message_flow.sagas.orchestration import (
    SagaCommandProducer,
    SagaDataMapping,
    SagaInstanceFactory,
    SagaManagerFactory,
)
from deps_object_storage import ObjectStorage, make_object_storage
from deps_rabbitmq import RabbitMQClient, RabbitMQConsumer, RabbitMQProducer

from deps_classification.application import (
    CommandGenAIClassifierService,
    DocumentProcessingService,
    DocumentTypeService,
    GroupService,
    QueryGenAIClassifierService,
)
from deps_classification.constants import PROJECT_NAME
from deps_classification.domain.model import (
    IQueryGenAIClassifierRepository,
    IQueryGroupRepository,
)
from deps_classification.extras import DatabaseSession
from deps_classification.infrastructure.access_management import user
from deps_classification.infrastructure.proxies import AIFusionProxy
from deps_classification.infrastructure.repositories import (
    QueryGenAIClassifierRepository,
    QueryGroupRepository,
    SagaInstanceRepository,
)
from deps_classification.infrastructure.services import ClassificationService
from deps_classification.infrastructure.unit_of_work import (
    AbstractUnitOfWork,
    SqlAlchemyUnitOfWork,
)
from deps_classification.messaging.dispatcher import make_message_dispatcher
from deps_classification.messaging.orchestration import (
    BatchFileClassificationSaga,
    BatchFileClassificationSagaSteps,
    ClassificationSaga,
    ClassificationSagaSteps,
    FileClassificationSaga,
    FileClassificationSagaSteps,
    make_saga_data_mapping,
)

MessagingClient = Union[ASBClient, KafkaClient, RabbitMQClient]


class MessageBrokerResource(resources.Resource):
    def init(
        self,
        driver_type: str,
        expected_driver: str,
        client: Type[MessagingClient],
        message_connection_string: str,
        **kwargs: Dict[str, Any],
    ) -> Optional[MessagingClient]:
        return client(message_connection_string, **kwargs) if driver_type == expected_driver else None

    def shutdown(self, resource: Optional[MessagingClient]) -> None:
        if resource:
            resource.close()


class MessageBrokers(containers.DeclarativeContainer):
    config = providers.Configuration()
    messaging_driver_settings = providers.Dependency(instance_of=object)

    broker_client: providers.Provider[MessagingClient] = providers.Selector(
        config.messaging_driver,
        asb=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.ASB.value,
            expected_driver=config.messaging_driver,
            client=ASBClient,
            message_connection_string=config.message_broker_connection_string,
            asb_settings=messaging_driver_settings,
        ),
        kafka=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.KAFKA.value,
            expected_driver=config.messaging_driver,
            client=KafkaClient,
            message_connection_string=config.message_broker_connection_string,
            settings=messaging_driver_settings,
        ),
        rabbitmq=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.RABBITMQ.value,
            expected_driver=config.messaging_driver,
            client=RabbitMQClient,
            message_connection_string=config.message_broker_connection_string,
            settings=messaging_driver_settings,
        ),
    )


class Messaging(containers.DeclarativeContainer):
    config = providers.Configuration()
    message_brokers = providers.DependenciesContainer()

    producer: providers.Provider[IMessageProducer] = providers.Selector(
        config.messaging_driver,
        asb=providers.Singleton(
            ASBProducer,
            client=message_brokers.broker_client,
            topic_name=config.messaging_driver_settings.topic_name,
        ),
        kafka=providers.Singleton(
            KafkaProducer,
            client=message_brokers.broker_client,
        ),
        rabbitmq=providers.Singleton(
            RabbitMQProducer,
            client=message_brokers.broker_client,
        ),
    )
    consumer: providers.Provider[IMessageConsumer] = providers.Selector(
        config.messaging_driver,
        asb=providers.Singleton(
            ASBConsumer,
            client=message_brokers.broker_client,
            topic_name=config.messaging_driver_settings.topic_name,
            custom_subscription_name=PROJECT_NAME,
        ),
        kafka=providers.Singleton(
            KafkaConsumer,
            client=message_brokers.broker_client,
        ),
        rabbitmq=providers.Singleton(
            RabbitMQConsumer,
            client=message_brokers.broker_client,
        ),
    )


class Core(containers.DeclarativeContainer):
    config = providers.Configuration()
    build_info: providers.Provider[Dict] = providers.Dict(
        {
            "build_tag": config.info.tag,
            "build_date": config.info.date,
            "commit_hash": config.info.hash,
        },
    )


class Datasources(containers.DeclarativeContainer):
    config = providers.Configuration()

    postgres_session: providers.Provider[DatabaseSession] = providers.Singleton(
        DatabaseSession,
        config.user,
        config.password,
        config.host,
        config.port,
        config.db,
        config.dialect,
        config.driver,
        config.require_secure_transport,
        pool_size=config.pool_size,
    )


class Repositories(containers.DeclarativeContainer):
    config = providers.Configuration()
    datasources = providers.DependenciesContainer()

    saga_instance: providers.Provider[SagaInstanceRepository] = providers.Singleton(
        SagaInstanceRepository,
        datasources.postgres_session,
    )
    query_gen_ai_classifier: providers.Singleton[IQueryGenAIClassifierRepository] = providers.Singleton(
        QueryGenAIClassifierRepository,
        database=datasources.postgres_session,
    )
    query_group: providers.Singleton[IQueryGroupRepository] = providers.Singleton(
        QueryGroupRepository,
        database=datasources.postgres_session,
    )


class Proxies(containers.DeclarativeContainer):
    config = providers.Configuration()

    ai_fusion: providers.Provider[AIFusionProxy] = providers.Singleton(
        AIFusionProxy,
        base_url=config.ai_fusion.url,
        timeout=config.ai_fusion.timeout,
    )

    object_storage: providers.Provider[ObjectStorage] = providers.Singleton(make_object_storage)


class InfraServices(containers.DeclarativeContainer):
    config = providers.Configuration()
    proxies = providers.DependenciesContainer()
    unit_of_work: providers.ExternalDependency[AbstractUnitOfWork] = providers.ExternalDependency()

    classification: providers.Provider[ClassificationService] = providers.Singleton(
        ClassificationService,
        unit_of_work=unit_of_work,
        prompted_classifier=proxies.ai_fusion,
    )


class SagaSteps(containers.DeclarativeContainer):
    infra_services = providers.DependenciesContainer()
    proxies = providers.DependenciesContainer()

    classification: providers.Singleton[ClassificationSagaSteps] = providers.Singleton(
        ClassificationSagaSteps,
        classification_service=infra_services.classification,
    )

    file_classification: providers.Singleton[FileClassificationSagaSteps] = providers.Singleton(
        FileClassificationSagaSteps,
        classification_service=infra_services.classification,
        storage=proxies.object_storage,
    )

    batch_file_classification: providers.Singleton[BatchFileClassificationSagaSteps] = providers.Singleton(
        BatchFileClassificationSagaSteps,
        classification_service=infra_services.classification,
    )


class Containers(containers.DeclarativeContainer):
    config = providers.Configuration()
    current_user_tenant = providers.Callable(lambda: user.get()["organisation"])
    messaging_driver_settings = providers.Dependency(instance_of=object)

    datasources: providers.Container[Datasources] = providers.Container(
        Datasources,
        config=config.database,
    )

    repositories: providers.Container[Repositories] = providers.Container(
        Repositories,
        config=config,
        datasources=datasources,
    )

    unit_of_work: providers.Singleton[AbstractUnitOfWork] = providers.Singleton(
        SqlAlchemyUnitOfWork,
        database_session=datasources.postgres_session,
    )

    core: providers.Container[Core] = providers.Container(Core, config=config)
    message_brokers: providers.Container[MessageBrokers] = providers.Container(
        MessageBrokers,
        config=config,
        messaging_driver_settings=messaging_driver_settings,
    )

    messaging: providers.Container[Messaging] = providers.Container(
        Messaging,
        config=config,
        message_brokers=message_brokers,
    )

    proxies: providers.Container[Proxies] = providers.Container(
        Proxies,
        config=config,
    )

    command_producer: providers.Singleton[CommandProducer] = providers.Singleton(
        CommandProducer,
        messaging.producer,
    )

    domain_event_publisher: providers.Singleton[DomainEventPublisher] = providers.Singleton(
        DomainEventPublisher,
        messaging.producer,
    )

    message_dispatcher: providers.Singleton[IMessageConsumer] = providers.Singleton(
        make_message_dispatcher,
        messaging.consumer,
        messaging.producer,
    )

    infra_services: providers.Container[InfraServices] = providers.Container(
        InfraServices,
        config=config,
        proxies=proxies,
        unit_of_work=unit_of_work,
    )

    saga_command_producer: providers.Singleton[SagaCommandProducer] = providers.Singleton(
        SagaCommandProducer,
        command_producer,
    )

    saga_data_mapping: providers.Singleton[SagaDataMapping] = providers.Singleton(
        make_saga_data_mapping,
    )

    saga_manager_factory: providers.Singleton[SagaManagerFactory] = providers.Singleton(
        SagaManagerFactory,
        repositories.saga_instance,
        command_producer,
        messaging.consumer,
        saga_command_producer,
        saga_data_mapping,
    )

    saga_steps: providers.Container[SagaSteps] = providers.Container(
        SagaSteps,
        infra_services=infra_services,
        proxies=proxies,
    )

    sagas = providers.List(
        providers.Singleton(
            ClassificationSaga,
            domain_event_publisher=domain_event_publisher,
            steps=saga_steps.classification,
        ),
        providers.Singleton(
            FileClassificationSaga,
            steps=saga_steps.file_classification,
            message_producer=messaging.producer,
        ),
        providers.Singleton(
            BatchFileClassificationSaga,
            steps=saga_steps.batch_file_classification,
            message_producer=messaging.producer,
        ),
    )

    saga_instance_factory: providers.Singleton[SagaManagerFactory] = providers.Singleton(
        SagaInstanceFactory,
        saga_manager_factory,
        sagas,
    )

    document_processing_service: providers.Singleton[DocumentProcessingService] = providers.Singleton(
        DocumentProcessingService,
        saga_instance_factory=saga_instance_factory,
        sagas=sagas,
    )

    group_service: providers.Singleton[GroupService] = providers.Singleton(
        GroupService,
        unit_of_work=unit_of_work,
        command_producer=command_producer,
        domain_event_publisher=domain_event_publisher,
    )

    document_type_service: providers.Singleton[DocumentTypeService] = providers.Singleton(
        DocumentTypeService,
        unit_of_work=unit_of_work,
        domain_event_publisher=domain_event_publisher,
    )

    command_gen_ai_classifier_service: providers.Singleton[CommandGenAIClassifierService] = providers.Singleton(
        CommandGenAIClassifierService,
        unit_of_work=unit_of_work,
        domain_event_publisher=domain_event_publisher,
    )

    query_gen_ai_classifier_service: providers.Singleton[QueryGenAIClassifierService] = providers.Singleton(
        QueryGenAIClassifierService,
        query_gen_ai_classifier_repository=repositories.query_gen_ai_classifier,
        query_group_repository=repositories.query_group,
    )
