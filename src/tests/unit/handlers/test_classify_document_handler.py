from uuid import uuid4

from deps_message_flow.commands.consumer import CommandMessage

from deps_classification.application import DocumentProcessingService
from deps_classification.messaging import ClassifyDocument
from deps_classification.messaging.handlers import classify_document_handler


def test_classify_document_handler(mocker):
    document_id = uuid4().hex
    tenant_id = uuid4().hex
    group_id = uuid4().hex
    files = [uuid4().hex]
    engine = uuid4().hex
    language = uuid4().hex
    parsing_features = [uuid4().hex, uuid4().hex]

    process_document = mocker.patch.object(DocumentProcessingService, "process_document", return_value=None)
    command_message = mocker.Mock(CommandMessage)
    command_message.command = ClassifyDocument(
        document_id=document_id,
        tenant_id=tenant_id,
        group_id=group_id,
        files=files,
        engine=engine,
        language=language,
        parsing_features=parsing_features,
    )

    classify_document_handler(command_message=command_message)

    process_document.assert_called_with(
        document_id=document_id,
        tenant_id=tenant_id,
        group_id=group_id,
        files=files,
        engine=engine,
        language=language,
        parsing_features=parsing_features,
    )
