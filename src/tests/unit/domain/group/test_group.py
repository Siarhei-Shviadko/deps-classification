from uuid import uuid4

from deps_classification.domain.model import EntityId, Group, TenantId


def test_group_initialization(group_1):
    assert isinstance(group_1.tenant_id, TenantId)
    assert all(isinstance(doc_type, EntityId) for doc_type in group_1.document_types)
    assert len(group_1.events) == 0


def test_group_equality(group_1):
    group2 = Group(id_=group_1.id.value, tenant_id=uuid4().hex, document_types=[uuid4().hex])
    assert group_1 == group2


def test_group_inequality(group_1):
    group2 = Group(id_=uuid4().hex, tenant_id=group_1.tenant_id.value, document_types=[uuid4().hex for _ in range(3)])
    assert group_1 != group2


def test_add_document_type(group_1):
    document_type_id = uuid4().hex
    group_1.add_document_types([document_type_id])

    assert EntityId(document_type_id) in group_1.document_types


def test_add_existing_document_type(group_1, group_1_document_types):
    existing_document_type_id = group_1_document_types[0]
    group_1.add_document_types([existing_document_type_id])

    assert group_1.document_types.count(EntityId(existing_document_type_id)) == 1


def test_remove_document_type(group_1, group_1_document_types):
    document_type_id = group_1_document_types[0]
    group_1.add_document_types([document_type_id])

    group_1.remove_document_types([document_type_id])

    assert EntityId(document_type_id) not in group_1.document_types


def test_remove_nonexistent_document_type(group_1):
    initial_length = len(group_1.document_types)
    group_1.remove_document_types([uuid4().hex])
    assert len(group_1.document_types) == initial_length
