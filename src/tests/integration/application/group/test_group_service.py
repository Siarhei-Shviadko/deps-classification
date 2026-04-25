import pytest

from deps_classification.domain.exceptions import GroupNotFound
from deps_classification.domain.model import GroupInfo


def test_save_all(group_service, group_1, group_1_document_types):
    groups_info = [GroupInfo(id=group_1.id(), tenant_id=group_1.tenant_id(), document_type_ids=group_1_document_types)]
    groups = group_service.save_all(groups_info)
    assert len(groups) == 1
    assert groups[0].id == group_1.id


def test_create(group_service, tenant_id):
    group_id = "new_group_id"
    document_types = ["doc1", "doc2"]
    group = group_service.create(group_id, tenant_id, document_types)

    assert group.id() == group_id
    assert group.tenant_id() == tenant_id
    assert [dt() for dt in group.document_types] == document_types


def test_delete(group_service, group_1, add_groups):
    group = group_service.delete(group_1.id(), group_1.tenant_id())

    assert group.id() == group_1.id()


def test_delete_nonexistent_group(group_service, tenant_id):
    with pytest.raises(GroupNotFound):
        group_service.delete("nonexistent_group_id", tenant_id)


def test_add_document_types(group_service, group_1, add_groups):
    new_document_types = ["doc4", "doc5"]

    group = group_service.add_document_types(group_1.id(), group_1.tenant_id(), new_document_types)

    assert sorted([dt() for dt in group.document_types]) == sorted(
        [dt() for dt in group_1.document_types] + new_document_types
    )


def test_add_document_types_nonexistent_group(group_service, tenant_id):
    with pytest.raises(GroupNotFound):
        group_service.add_document_types("nonexistent_group_id", tenant_id, ["doc4", "doc5"])


def test_remove_document_types(group_service, group_1, add_groups):
    document_types_to_remove = [dt() for dt in group_1.document_types[:2]]
    group = group_service.remove_document_types(group_1.id(), group_1.tenant_id(), document_types_to_remove)
    assert group.document_types == group_1.document_types[2:]


def test_remove_document_types_nonexistent_group(group_service, tenant_id):
    with pytest.raises(GroupNotFound):
        group_service.remove_document_types("nonexistent_group_id", tenant_id, ["doc1", "doc2"])
