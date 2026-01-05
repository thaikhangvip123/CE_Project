import cv2
import math
import numpy as np

SIZE = 600

RADII_SCORES = [
    (25, 10),
    (47, 9),
    (69, 8),
    (90, 7),
    (113, 6),
    (135, 5),
    (157, 4),
    (179, 3),
    (201, 2),
    (223, 1),
    (257, 0),
]


def get_score_from_distance(distance: float) -> int:
    for radius, score in RADII_SCORES:
        if distance <= radius:
            return score
    return -1


def find_bullseye_center(warped_img: np.ndarray):
    gray = cv2.cvtColor(warped_img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    best_center = (SIZE // 2, SIZE // 2)
    max_area = 0

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 500:
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])

                if math.hypot(cx - 300, cy - 300) < 50:
                    if area > max_area:
                        max_area = area
                        best_center = (cx, cy)

    return best_center


def score_boxes(boxes, center):
    cx, cy = center
    results = []
    total_score = 0

    for idx, b in enumerate(boxes):
        bx = (b["x1"] + b["x2"]) / 2
        by = (b["y1"] + b["y2"]) / 2

        distance = math.hypot(bx - cx, by - cy)
        score = get_score_from_distance(distance)

        total_score += max(score, 0)

        results.append({
            "id": idx,
            "center": {"x": bx, "y": by},
            "distance": round(distance, 2),
            "score": score
        })
    print("CENTER:", center)
    for b in boxes:
        bx = (b["x1"] + b["x2"]) / 2
        by = (b["y1"] + b["y2"]) / 2
        print("SHOT:", bx, by)
    return total_score, results
    
