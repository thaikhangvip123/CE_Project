import math
import numpy as np

def circle_points(cx, cy, r, n=8):
    pts = []
    for i in range(n):
        angle = 2 * math.pi * i / n - math.pi/2
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        pts.append([x, y])
    return np.array(pts, dtype=np.float32)
dst_points = circle_points(500, 500, 450)
src_points = np.array([
    [544, 45],
    [1134, 204],
    [1180, 262],
    [1206, 854],
    [1158, 918],
    [489, 978],
    [410, 897],
    [470, 88]
], dtype=np.float32)
import cv2

H, _ = cv2.findHomography(src_points, dst_points)
shots = np.array([
    [700, 520],
    [820, 610],
    [640, 450],
    [780, 480]
], dtype=np.float32).reshape(-1,1,2)
shots_warped = cv2.perspectiveTransform(shots, H)
center = (500, 500)
R = 450
ring_step = R / 10

def score_shot(x, y):
    d = math.hypot(x-500, y-500)
    if d > R:
        return 0
    return 10 - int(d / ring_step)
for i, p in enumerate(shots_warped):
    x, y = p[0]
    print(f"Shot {i+1}: score = {score_shot(x, y)}")
