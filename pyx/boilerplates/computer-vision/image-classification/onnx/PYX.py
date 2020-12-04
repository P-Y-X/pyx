from pyx import PYXModelInterface, DataPreprocessor, PredictionPostprocessor

from preprocessor import DefaultImageNetPreprocessor
from postprocessor import DefaultImageNetPostprocessor

import onnxruntime as rt


class PYXImplementedModel(PYXModelInterface):
    def __init__(self, device='cuda'):
        super().__init__()
        self.model = None
        self.device = device

    def initialize(self, weights_path) -> None:
        """
        Initialize model testing interface.
        Please, construct your model here.
        """
        self.model = rt.InferenceSession(weights_path)

    def get_input_shapes(self) -> dict:
        """
        Depends on the task you have, please consider providing proper model shape (skipping batch-dimension).
        Further information: [docs url]
        """
        return {
            "input_image": [224, 224, 3],
        }

    def get_input_types(self) -> dict:
        """
        Depends on the task you have, please consider providing proper model types.
        Further information: [docs url]
        """
        return {
            "input_image": 'image',
        }

    def get_preprocessor(self) -> DataPreprocessor:
        """
        Depends on the task you have, please consider providing proper model preprocessor.
        Further information: [docs url]
        """
        return DefaultImageNetPreprocessor()

    def get_postprocessor(self) -> PredictionPostprocessor:
        """
        Depends on the task you have, please consider providing proper prediction postprocessor.
        Further information: [docs url]
        """
        return DefaultImageNetPostprocessor()

    def get_weights_path(self) -> str:
        """
        ONNX model path.
        Further information: [docs url]
        """
        return 'model.onnx'

    def predict(self, sample: dict) -> dict:
        """
        Using your model, perform inference.
        Further information: [docs url]
        """
        y = self.model.run(["output_name"], sample)

        return {
            "raw_output": y,
        }


if __name__ == '__main__':
    print('Everything is ready!')
