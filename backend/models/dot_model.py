from ultralytics import YOLO


class DotYOLOModel:
    def __init__(self, weights_path: str):
        self.model = YOLO(weights_path)

    def predict(self, image, conf=0.25):
        return self.model(image, conf=conf)

    @property
    def names(self):
        return self.model.names
