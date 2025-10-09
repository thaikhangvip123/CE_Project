import os
import cv2
import torch

from models.yolo_model import YOLO
from utils.utils import read_image_bytes, draw_boxes


MODEL_PATH = os.path.join("best.pt")
model = YOLO(MODEL_PATH)

class DetectionService:
    @staticmethod
    def detect_image(file_bytes: bytes) -> str:
        img = read_image_bytes(file_bytes)
        results = model.predict(img, conf=0.25, verbose=False)[0]
        img = draw_boxes(img, results, model)

        # Save output
        os.makedirs("outputs", exist_ok=True)
        output_path = os.path.join("outputs", "labeled_result.jpg")
        cv2.imwrite(output_path, img)
        return output_path
