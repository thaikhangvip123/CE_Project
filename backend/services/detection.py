from models.yolo_model import YOLOModel
from utils.utils import decode_image, draw_detections, encode_jpeg

class DetectionService:
    def __init__(self):
        self.yolo = YOLOModel("best.pt")

    def process_frame(self, data: bytes):
        frame = decode_image(data)
        results = self.yolo.predict(frame)
        frame = draw_detections(frame, results, self.yolo.labels)
        return encode_jpeg(frame)
