from torchvision.models import resnet18


class Model:
    def __init__(self) -> None:
        super(Model, self).__init__()
        self.model = resnet18()

    def load_state_dict(self, x):
        self.model.load_state_dict(x)

    def forward(self, x):
        return self.model.forward(x)
