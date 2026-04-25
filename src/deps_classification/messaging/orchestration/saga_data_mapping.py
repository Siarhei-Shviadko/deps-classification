from deps_message_flow.sagas.orchestration import SagaDataMapping

from .batch_file_classification import BatchFileClassificationSagaData
from .classification import ClassificationSagaData
from .file_classification import FileClassificationSagaData

__all__ = ["make_saga_data_mapping"]


def make_saga_data_mapping() -> SagaDataMapping:
    return SagaDataMapping(
        {
            ClassificationSagaData.__name__: ClassificationSagaData,
            FileClassificationSagaData.__name__: FileClassificationSagaData,
            BatchFileClassificationSagaData.__name__: BatchFileClassificationSagaData,
        },
    )
