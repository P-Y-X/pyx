from pyx import PYXModelInterface, DataPreprocessor, PredictionPostprocessor

from model import Model
from preprocessor import DefaultImageNetPreprocessor
from postprocessor import DefaultImageNetPostprocessor

import torch


class PYXImplementedModel(PYXModelInterface):
    def __init__(self):
        self.model = None

    def initialize(self) -> None:
        """
        Initialize model testing interface.
        Please, construct your model here.
        """
        self.model = Model()
        self.model.eval()

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

    def set_weights(self) -> None:
        """
        Depends on the task you have, please consider setting proper model preprocessor.
        Further information: [docs url]
        """
        # self.model.load_state_dict(torch.load('./weights.pth'))
        pass

    def predict(self, sample: dict) -> dict:
        """
        Using your model, perform inference.
        Further information: [docs url]
        """
        with torch.no_grad():
            x = torch.FloatTensor(sample['normalized_image']).unsqueeze(0)
            y = self.model.forward(x).squeeze(0).cpu().detach().numpy()

        return {
            "raw_output": y,
        }


if __name__ == '__main__':
    print('Everything is ready!')
