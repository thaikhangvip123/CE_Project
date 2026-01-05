# backend/utils/utils.py

import cv2
import numpy as np

def read_image_bytes(contents: bytes):
    np_img = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Failed to decode image bytes.")
    return img

# def draw_boxes(img, results, model):
#     for box in results.boxes:
#         cls = int(box.cls)
#         label = model.names[cls]
#         conf = float(box.conf)
#         x1, y1, x2, y2 = map(int, box.xyxy[0])

#         cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
#         cv2.putText(img, f"{label} {conf:.2f}", (x1, y1 - 10),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
#     return img

