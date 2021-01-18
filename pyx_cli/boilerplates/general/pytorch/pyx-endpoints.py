from typing import Dict


def get_weight_paths() -> Dict[str, str]:
    """
    Return model weights relative to the project directory
    """
    return {}


def predict(input_directory: str, output_directory: str, weight_paths: Dict[str, str], device: str) -> bool:
    """
    Perform inference.
    Further information: https://github.com/P-Y-X/pyx#publish-your-own-model
    """
    return True

