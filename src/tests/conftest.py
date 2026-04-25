from uuid import uuid4

import pytest
from starlette.testclient import TestClient

from deps_classification import api
from deps_classification.domain.model import (
    GenAIClassifierDisplayInfo,
    GenAIClassifierFactory,
    GroupFactory,
)
from deps_classification.entrypoint import create_fastapi
from deps_classification.infrastructure.access_management import user
from tests.fakes import (
    FakeAIFusionProxy,
    FakeDomainEventPublisher,
    FakeObjectStorageProxy,
)


@pytest.fixture(scope="session")
def app():
    fastapi_app = create_fastapi()
    yield fastapi_app


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def session_containers(app):
    return app.containers


@pytest.fixture
def containers(session_containers):
    with session_containers.reset_singletons():
        yield session_containers


@pytest.fixture(autouse=True)
def fake_domain_event_publisher(containers):
    with containers.domain_event_publisher.override(FakeDomainEventPublisher()) as dep:
        yield dep()
        del dep().last_published


@pytest.fixture(autouse=True)
def fake_ai_fusion_proxy(containers):
    with containers.proxies.ai_fusion.override(FakeAIFusionProxy()) as proxy:
        yield proxy()


@pytest.fixture(autouse=True)
def fake_object_storage(containers):
    with containers.proxies.object_storage.override(FakeObjectStorageProxy()) as proxy:
        yield proxy()


@pytest.fixture
def repositories(containers):
    return containers.repositories


@pytest.fixture
def document_type_service(containers):
    return containers.document_type_service()


@pytest.fixture
def group_service(containers):
    return containers.group_service()


@pytest.fixture
def command_gen_ai_classifier_service(containers):
    return containers.command_gen_ai_classifier_service()


@pytest.fixture
def classification_service(containers):
    return containers.infra_services.classification()


@pytest.fixture
def query_gen_ai_classifier_service(containers):
    return containers.query_gen_ai_classifier_service()


@pytest.fixture
def tenant_id():
    return uuid4().hex


@pytest.fixture
def test_llm_type():
    return "openai@gpt-4o"


@pytest.fixture
def document_type_id():
    return uuid4().hex


@pytest.fixture
def group_id():
    return uuid4().hex


@pytest.fixture
def group_1(tenant_id, document_type_id, group_id):
    return GroupFactory.create(
        id_=group_id,
        tenant_id=tenant_id,
        document_types=[document_type_id, *(uuid4().hex for _ in range(3))],
    )


@pytest.fixture
def group_1_document_types(group_1):
    return [doc_type() for doc_type in group_1.document_types]


@pytest.fixture
def gen_ai_classifier_1(tenant_id, group_1, test_llm_type):
    classifier = GenAIClassifierFactory.create(
        tenant_id=tenant_id,
        group_id=group_1.id(),
        document_type_id=group_1.document_types[0](),
        prompt=uuid4().hex,
        llm_type=test_llm_type,
        name=uuid4().hex,
    )

    classifier.events.clear()

    return classifier


@pytest.fixture
def gen_ai_classifier_2(tenant_id, group_1, test_llm_type):
    classifier = GenAIClassifierFactory.create(
        tenant_id=tenant_id,
        group_id=group_1.id(),
        document_type_id=group_1.document_types[1](),
        prompt=uuid4().hex,
        llm_type=test_llm_type,
        name=uuid4().hex,
    )

    classifier.events.clear()

    return classifier


@pytest.fixture
def test_groups(group_1):
    return [
        group_1,
    ]


@pytest.fixture
def test_gen_ai_classifiers(gen_ai_classifier_1, gen_ai_classifier_2):
    return [
        gen_ai_classifier_1,
        gen_ai_classifier_2,
    ]


@pytest.fixture
def test_gen_ai_classifiers_display_infos(test_gen_ai_classifiers):
    return [
        GenAIClassifierDisplayInfo(
            gen_ai_classifier_id=classifier.id(),
            document_type_id=classifier.document_type_id(),
            prompt=classifier.prompt,
            llm_type=classifier.llm_type,
            name=classifier.name,
        )
        for classifier in test_gen_ai_classifiers
    ]


@pytest.fixture
def this_user(tenant_id):
    return dict(
        subject="Test",
        groups=[tenant_id],
        token="token",
        roles=[],
        organisation=tenant_id,
    )


@pytest.fixture(autouse=True)
def set_this_user(this_user):
    user.set(this_user)


@pytest.fixture(autouse=True)
def mocked_middleware(monkeypatch, mocker):
    monkeypatch.setattr(api.auth, "set_user_from_token", mocker.Mock({}))
