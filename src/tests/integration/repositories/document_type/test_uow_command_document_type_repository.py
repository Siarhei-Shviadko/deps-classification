def test_delete__success(unit_of_work, group_1, group_1_document_types, add_groups):
    unit_of_work.document_types.delete(group_1_document_types[0])

    group = unit_of_work.groups.group_of_id(group_1.id(), group_1.tenant_id())

    assert len(group.document_types) == len(group_1.document_types) - 1
