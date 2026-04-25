import pytest

from deps_classification.domain.model import (
    GenAIClassifierDisplayInfo,
    Group,
    IQueryGroupRepository,
)


def test_exists_group_of_id__exists(
    query_group_repository: IQueryGroupRepository,
    group_1: Group,
    add_groups,
):
    group_exists = query_group_repository.exists_group_of_id(group_id=group_1.id(), tenant_id=group_1.tenant_id())

    assert group_exists


def test_exists_group_of_id__doesnt_exist(query_group_repository: IQueryGroupRepository, group_1: Group):
    group_exists = query_group_repository.exists_group_of_id(group_id=group_1.id(), tenant_id=group_1.tenant_id())

    assert not group_exists
