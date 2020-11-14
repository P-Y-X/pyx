from torchvision.models import resnet18


def get_model():
    return resnet18(pretrained=True)

Model = get_model
