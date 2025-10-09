import cv2
import numpy as np

def jpeg_bytes_to_bgr(img_bytes: bytes) -> np.ndarray:
    """Decode JPEG bytes to BGR numpy image."""
    np_img = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Failed to decode image bytes.")
    return img

def scale_boxes_to_canvas(boxes_xyxy, src_w, src_h, dst_w, dst_h):
    """Scale boxes from model image size to canvas size (if needed)."""
    # If you send frames at the same width/height as the canvas,
    # you usually don't need any scaling. This function is here if you do.
    sx = dst_w / float(src_w)
    sy = dst_h / float(src_h)
    scaled = []
    for x1, y1, x2, y2 in boxes_xyxy:
        scaled.append([x1 * sx, y1 * sy, x2 * sx, y2 * sy])
    return scaled
