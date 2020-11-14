from .DataPreprocessor import DataPreprocessor
from .PredictionPostprocessor import PredictionPostprocessor
from abc import ABC, abstractmethod


class PYXModelInterface(ABC):
    @abstractmethod
    def __init__(self) -> None:
        """
        Initialize model testing interface.
        Please, construct your model here.
        """
        pass

    @abstractmethod
    def get_input_shapes(self) -> dict:
        """
        Depends on the task you have, please consider providing proper model shape (skipping batch-dimensions).
        Further information: [docs url]
        """
        pass

    @abstractmethod
    def get_input_types(self) -> dict:
        """
        Depends on the task you have, please consider providing proper input types.
        Further information: [docs url]
        """
        pass

    @abstractmethod
    def get_preprocessor(self) -> DataPreprocessor:
        """
        Depends on the task you have, please consider providing proper model preprocessor.
        Further information: [docs url]
        """
        pass

    @abstractmethod
    def get_postprocessor(self) -> PredictionPostprocessor:
        """
        Depends on the task you have, please consider providing proper prediction postprocessor.
        Further information: [docs url]
        """
        pass

    @abstractmethod
    def set_weights(self) -> None:
        """
        Depends on the task you have, please consider setting proper model weights here.
        Further information: [docs url]
        """
        pass

    @abstractmethod
    def predict(self, sample: dict) -> dict:
        """
        Using your model, perform inference.
        Further information: [docs url]
        """
        pass
