from ultralytics import YOLO

class YOLOModel:
    def __init__(self, weights_path="best.pt"):
        self.model = YOLO(weights_path)

    def predict(self, frame, conf=0.25):
        return self.model(frame, conf=conf)

    @property
    def labels(self):
        return self.model.names
