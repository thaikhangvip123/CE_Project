import cv2
import numpy as np

def read_image_bytes(contents: bytes):
    np_img = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Failed to decode image bytes.")
    return img

def draw_boxes(img, results, model):
    for box in results.boxes:
        cls = int(box.cls)
        label = model.names[cls]
        conf = float(box.conf)
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img, f"{label} {conf:.2f}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    return img


############################################

# def decode_image(img_bytes: bytes):
#     """Decode bytes to OpenCV image (BGR)."""
#     np_img = np.frombuffer(img_bytes, np.uint8)
#     img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
#     if img is None:
#         raise ValueError("Failed to decode image bytes.")
#     return img

# def draw_detections(img, boxes, labels=None, scores=None):
#     """Draw bounding boxes with optional labels and scores."""
#     for i, box in enumerate(boxes):
#         x1, y1, x2, y2 = map(int, box)
#         color = (0, 255, 0)
#         cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
#         label = labels[i] if labels else "Object"
#         score = f"{scores[i]:.2f}" if scores is not None else ""
#         text = f"{label} {score}"
#         cv2.putText(img, text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
#     return img

# def encode_jpeg(img):
#     """Encode image to JPEG bytes."""
#     ret, buffer = cv2.imencode('.jpg', img)
#     if not ret:
#         raise ValueError("Failed to encode image to JPEG.")
#     return buffer.tobytes()

# def scale_boxes_to_canvas(boxes_xyxy, src_w, src_h, dst_w, dst_h):
#     sx = dst_w / float(src_w)
#     sy = dst_h / float(src_h)
#     scaled = []
#     for x1, y1, x2, y2 in boxes_xyxy:
#         scaled.append([x1 * sx, y1 * sy, x2 * sx, y2 * sy])
#     return scaled
