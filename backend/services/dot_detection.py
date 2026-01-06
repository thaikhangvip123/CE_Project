import cv2
import numpy as np
import io

from models.yolo_model import YOLO

# Load model một lần khi server khởi chạy
MODEL_PATH = 'target.pt'
print(f"Loading YOLO model from {MODEL_PATH}...")
model = YOLO(MODEL_PATH)

def detect_keypoints(image_bytes):
    # 1. Đọc ảnh từ bytes
    np_arr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    if frame is None:
        return None, None

    # 2. Chạy inference
    results = model(frame, conf=0.5)[0]

    keypoints_list = []

    debug_img = frame.copy()

    if results.keypoints is not None and len(results.keypoints.xy) > 0:
        keypoints = results.keypoints.xy[0].cpu().numpy()  # Lấy đối tượng đầu tiên
        for i, (x, y) in enumerate(keypoints):
            if x != 0 or y != 0:
                keypoints_list.append({"id": i, "x": float(x), "y": float(y)})
                # Vẽ chấm đỏ và số thứ tự màu vàng
                cv2.circle(debug_img, (int(x), int(y)), 5, (0, 0, 255), -1)
                cv2.putText(debug_img, str(i), (int(x), int(y)-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    # Encode ảnh để trả về client
    _, buffer = cv2.imencode('.png', debug_img)
    img_bytes = io.BytesIO(buffer)

    return keypoints_list, img_bytes