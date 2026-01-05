# backend/services/detection.py

import os
import cv2
import torch

from models.yolo_model import YOLO
from utils.utils import read_image_bytes


MODEL_PATH = os.path.join("best.pt")
model = YOLO(MODEL_PATH)

class DetectionService:
    @staticmethod
    def detect_image(file_bytes: bytes):
        img = read_image_bytes(file_bytes)
        results = model.predict(img)[0]

        boxes = []
        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf)
            cls = int(box.cls)

            boxes.append({
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "confidence": conf,
                "class": cls,
                "label": model.names[cls]  
            })

        return boxes