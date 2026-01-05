import numpy as np
import cv2
from models.dot_model import DotYOLOModel


DOT_COLORS = [
    (0, 0, 255),     # dot 1 - red
    (255, 0, 0),     # dot 2 - blue
    (0, 255, 0),     # dot 3 - green
    (0, 255, 255),   # dot 4 - yellow
    (255, 0, 255),   # dot 5 - purple
    (255, 255, 0),   # dot 6 - cyan
    (0, 165, 255),   # dot 7 - orange
    (255, 255, 255), # dot 8 - white
]

import cv2
import numpy as np
import base64
from models.dot_model import DotYOLOModel

class DotDetection:
    def __init__(self, model_path: str):
        self.model = DotYOLOModel(model_path)

    def detect(self, image_bytes: bytes):
        np_img = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Invalid image")

        result = self.model.predict(img)[0]

        if result.keypoints is None:
            return [], None

        keypoints = result.keypoints.xy[0]
        confidences = result.keypoints.conf[0]

        detections = []

        for i, (point, conf) in enumerate(zip(keypoints, confidences)):
            x, y = map(int, point.tolist())

            # Draw dot
            cv2.circle(img, (x, y), 6, DOT_COLORS[i], -1)
            cv2.putText(
                img,
                f"{i+1}",
                (x + 8, y - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                DOT_COLORS[i],
                2
            )

            detections.append({
                "id": i + 1,
                "label": f"dot_{i + 1}",
                "x": x,
                "y": y,
                "confidence": round(float(conf), 3)
            })

        # Encode image → base64
        _, buffer = cv2.imencode(".jpg", img)
        image_base64 = base64.b64encode(buffer).decode("utf-8")

        return detections, image_base64
