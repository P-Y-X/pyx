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
    def initialize(self, weights_path) -> None:
        """
        Load model weights.
        Please, load model / model weights here.
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
    def get_weights_path(self) -> str:
        """
        Path to weights relative to framework folder.
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
