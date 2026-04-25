import logging

from deps_message_flow.commands.producer import CommandProducer
from deps_message_flow.events.publisher import DomainEventPublisher

from deps_classification.constants import (
    CLASSIFICATION_DESTINATION,
    COMMANDS_CHANNEL,
    COMMANDS_REPLIES_CHANNEL,
)
from deps_classification.domain.exceptions import GroupNotFound
from deps_classification.domain.model import Group, GroupFactory, GroupInfo
from deps_classification.infrastructure.unit_of_work import AbstractUnitOfWork
from deps_classification.messaging import GetGroups

from .retry_transaction import retry_on_transaction_error

__all__ = ["GroupService"]


class GroupService:
    def __init__(
        self,
        unit_of_work: AbstractUnitOfWork,
        command_producer: CommandProducer,
        domain_event_publisher: DomainEventPublisher,
    ) -> None:
        self._uow = unit_of_work
        self._command_producer = command_producer
        self._domain_event_publisher = domain_event_publisher

        self._logger = logging.getLogger(self.__class__.__name__)

    def obtain_all(self) -> None:
        self._command_producer.send(
            COMMANDS_CHANNEL,
            GetGroups(),
            COMMANDS_REPLIES_CHANNEL,
        )

        self._logger.info("Groups are requested.")

    @retry_on_transaction_error()
    def save_all(self, groups_info: list[GroupInfo]) -> list[Group]:
        with self._uow:
            groups = [
                GroupFactory.create(
                    id_=info["id"],
                    tenant_id=info["tenant_id"],
                    document_types=info["document_type_ids"],
                )
                for info in groups_info
            ]

            self._uow.groups.save_all(groups)

            self._uow.commit()

        self._logger.info("Groups are obtained from master source.")

        return groups

    @retry_on_transaction_error()
    def create(self, group_id: str, tenant_id: str, document_type_ids: list[str]) -> Group:
        with self._uow:
            group = GroupFactory.create(
                id_=group_id,
                tenant_id=tenant_id,
                document_types=document_type_ids,
            )

            self._uow.groups.save(group)

            self._uow.commit()

        self._logger.info("Group %s is saved.", group_id)

        return group

    @retry_on_transaction_error()
    def delete(self, group_id: str, tenant_id: str) -> Group:
        with self._uow:
            group = self._find_group(group_id, tenant_id)

            group.delete()

            self._uow.groups.delete(group)
            self._uow.commit()

        self._logger.info("Group %s is deleted.", group_id)

        return group

    @retry_on_transaction_error()
    def add_document_types(self, group_id: str, tenant_id: str, document_type_ids: list[str]) -> Group:
        with self._uow:
            group = self._find_group(group_id, tenant_id)

            group.add_document_types(document_type_ids)

            self._uow.groups.save(group)
            self._uow.commit()

        self._logger.info("Document Types `%s` are added to Group %s.", document_type_ids, group_id)

        return group

    @retry_on_transaction_error()
    def remove_document_types(self, group_id: str, tenant_id: str, document_type_ids: list[str]) -> Group:
        with self._uow:
            group = self._find_group(group_id, tenant_id)

            group.remove_document_types(document_type_ids)

            self._uow.groups.save(group)
            self._uow.commit()

            self._publish_events(group)

        self._logger.info("Document Types `%s` are removed from Group %s.", document_type_ids, group_id)

        return group

    def _find_group(self, id_: str, tenant_id: str) -> Group:
        if (group := self._uow.groups.group_of_id(id_, tenant_id)) is None:
            raise GroupNotFound(group_id=id_)

        return group

    def _publish_events(self, group: Group) -> None:
        self._domain_event_publisher.publish(
            aggregate_type=CLASSIFICATION_DESTINATION,
            aggregate_id=group.id(),
            domain_events=group.events,
        )
