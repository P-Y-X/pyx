from abc import ABC, abstractmethod


class DataPreprocessor(ABC):
    @abstractmethod
    def __init__(self) -> None:
        """
        Initialize data preprocessor interface.
        Please, initialize normalization / etc params here.
        """
        pass

    @abstractmethod
    def preprocess(self, x: dict) -> dict:
        """
        Preprocess data
        Further information: [docs url]
        """
        pass
