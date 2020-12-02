from pyx import DataPreprocessor
import numpy as np


class DefaultImageNetPreprocessor(DataPreprocessor):

    def __init__(self) -> None:
        super().__init__()

    def preprocess(self, x: dict) -> dict:
        """
        x contains ["rgba_image"] in 0...1 range, CHW
        """

        mean = np.array([0.485, 0.456, 0.406])[:, np.newaxis, np.newaxis]
        std = np.array([0.229, 0.224, 0.225])[:, np.newaxis, np.newaxis]

        x_preprocessed = (x["input_image"][:3] - mean) / std

        return {
            "input_image": x_preprocessed
        }
