import numpy as np

# 8 điểm ảnh gốc
src_pts = np.array([
    [382, 74],
    [1264, 76],
    [1316, 164],
    [1152, 826],
    [1086, 876],
    [466, 934],
    [404, 890],
    [308, 170]
], dtype=float)

# 8 điểm ảnh chuẩn
dst_pts = np.array([
    [50, 0],
    [550, 0],
    [600, 50],
    [600, 550],
    [550, 600],
    [50, 600],
    [0, 550],
    [0, 50]
], dtype=float)

# Xây ma trận A và vector b
A = []
b = []

for (x, y), (xp, yp) in zip(src_pts, dst_pts):
    A.append([x, y, 1, 0, 0, 0, -x*xp, -y*xp])
    A.append([0, 0, 0, x, y, 1, -x*yp, -y*yp])
    b.append(xp)
    b.append(yp)

A = np.array(A)
b = np.array(b)

# Giải hệ tuyến tính Ah = b bằng least squares
h = np.linalg.lstsq(A, b, rcond=None)[0]

# Xây ma trận H 3x3
H = np.array([
    [h[0], h[1], h[2]],
    [h[3], h[4], h[5]],
    [h[6], h[7], 1.0]
])

print("Ma trận homography H:\n", H)
