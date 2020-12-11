from model import Model
from typing import Dict


def get_weight_paths() -> Dict[str, str]:
    """
    Return model weights relative to framework directory
    """
    return {}


def predict(input_directory: str, output_directory: str, weight_paths: Dict[str, str], device: str) -> bool:
    """
    Using your model, perform inference.
    Further information: [docs url]
    """
    from glob import glob
    import torch
    import numpy as np
    import os
    import cv2

    model = Model()
    # model.load_state_dict(torch.load(weight_paths['model']))
    model = model.to(device)

    input_files = glob(os.path.join(input_directory, '*'))

    for input_file in input_files:
        img = cv2.imread(input_file, cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224))
        img = img.transpose(2, 0, 1) / 255.0
        mean = np.array([0.485, 0.456, 0.406])[:, np.newaxis, np.newaxis]
        std = np.array([0.229, 0.224, 0.225])[:, np.newaxis, np.newaxis]

        x_preprocessed = torch.FloatTensor((img - mean) / std).unsqueeze(0).to(device)

        with torch.no_grad():
            y_pred = model(x_preprocessed).squeeze(0).cpu().numpy()

        with open(os.path.join(output_directory, os.path.basename(input_file) + '.pred'), 'w') as f:
            y_pred.tofile(f, sep=' ')
            f.close()

    return True


if __name__ == '__main__':
    print('Everything is ready!')
