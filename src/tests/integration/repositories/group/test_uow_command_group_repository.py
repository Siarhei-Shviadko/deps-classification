from uuid import uuid4

from deps_classification.domain.model import GroupFactory


def test_group_of_id__success(unit_of_work, group_1, add_groups):
    assert unit_of_work.groups.group_of_id(group_1.id(), group_1.tenant_id()) == group_1


def test_group_of_id__not_found(unit_of_work, tenant_id):
    assert unit_of_work.groups.group_of_id(uuid4().hex, tenant_id) is None


def test_save_all__success(unit_of_work, group_1):
    new_group = GroupFactory.create(
        id_=uuid4().hex,
        tenant_id=group_1.tenant_id(),
        document_types=[uuid4().hex for _ in range(3)],
    )

    unit_of_work.groups.save_all([group_1, new_group])

    assert unit_of_work.groups.group_of_id(group_1.id(), group_1.tenant_id()) == group_1
    assert unit_of_work.groups.group_of_id(new_group.id(), new_group.tenant_id()) == new_group


def test_save_all__empty_list(unit_of_work):
    unit_of_work.groups.save_all([])


def test_save_all__update_existing_group(unit_of_work, group_1, add_groups):
    updated_group = GroupFactory.create(
        id_=group_1.id(),
        tenant_id=group_1.tenant_id(),
        document_types=[uuid4().hex for _ in range(3)],
    )

    unit_of_work.groups.save_all([updated_group])

    assert unit_of_work.groups.group_of_id(group_1.id(), group_1.tenant_id()) == updated_group


def test_save__success(unit_of_work, group_1):
    unit_of_work.groups.save(group_1)

    assert unit_of_work.groups.group_of_id(group_1.id(), group_1.tenant_id()) == group_1


def test_save__update_existing_group(unit_of_work, group_1, add_groups):
    updated_group = GroupFactory.create(
        id_=group_1.id(),
        tenant_id=group_1.tenant_id(),
        document_types=[uuid4().hex for _ in range(3)],
    )

    unit_of_work.groups.save(updated_group)

    assert unit_of_work.groups.group_of_id(group_1.id(), group_1.tenant_id()) == updated_group


def test_delete__success(unit_of_work, group_1, add_groups):
    group_1.delete()

    unit_of_work.groups.delete(group_1)

    assert unit_of_work.groups.group_of_id(group_1.id(), group_1.tenant_id()) is None


def test_has_group_with_document_type__success(unit_of_work, group_1, add_groups):
    document_type_id = group_1.document_types[0]()
    assert unit_of_work.groups.has_group_with_document_type(group_1.id(), document_type_id) is True


def test_has_group_with_document_type__not_found(unit_of_work, group_1, add_groups):
    non_existent_document_type_id = uuid4().hex
    assert unit_of_work.groups.has_group_with_document_type(group_1.id(), non_existent_document_type_id) is False


def test_has_group_with_document_type__unknown_group(unit_of_work, tenant_id):
    unknown_group_id = uuid4().hex
    document_type_id = uuid4().hex
    assert unit_of_work.groups.has_group_with_document_type(unknown_group_id, document_type_id) is False
