from pyx import PYXModelInterface, DataPreprocessor, PredictionPostprocessor

from model import Model
from preprocessor import DefaultImageNetPreprocessor
from postprocessor import DefaultImageNetPostprocessor

import torch


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
        self.model = Model()
        # self.model.load_state_dict(torch.load(weights_path))
        self.model.eval()
        self.model.to(self.device)

    def get_input_shapes(self) -> dict:
        """
        Depends on the task you have, please consider providing proper model shape (skipping batch-dimension).
        Further information: [docs url]
        """
        return {
            "input_image": [3, 224, 224],
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
        Pytorch model path.
        """
        return 'model.pth'

    def predict(self, sample: dict) -> dict:
        """
        Using your model, perform inference.
        Further information: [docs url]
        """
        with torch.no_grad():
            x = torch.FloatTensor(sample['input_image']).unsqueeze(0).to(self.device)
            y = self.model.forward(x).squeeze(0).cpu().detach().numpy()

        return {
            "raw_output": y,
        }


if __name__ == '__main__':
    print('Everything is ready!')
