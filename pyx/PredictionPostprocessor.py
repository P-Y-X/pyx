from abc import ABC, abstractmethod


class PredictionPostprocessor(ABC):
    @abstractmethod
    def __init__(self) -> None:
        """
        Initialize data postprocessor interface.
        Please, initialize lists/maps with classes and other params here.
        """
        pass

    @abstractmethod
    def postprocess(self, x: dict) -> dict:
        """
        Preprocess data
        Further information: [docs url]
        """
        pass
