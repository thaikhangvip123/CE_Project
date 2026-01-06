import numpy as np

# 8 điểm ảnh gốc
src_pts = np.array([
    [252, 109],
    [772, 108],
    [821, 157],
    [813, 672],
    [765, 720],
    [257, 717],
    [209, 672],
    [205, 156]
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

def warp_point(x, y, H):
    """
    Chuyển 1 điểm (x, y) từ ảnh gốc sang ảnh chuẩn
    """
    pt = np.array([x, y, 1.0])
    warped = H @ pt

    X = warped[0] / warped[2]
    Y = warped[1] / warped[2]

    return X, Y

def warp_two_points(x1, y1, x2, y2, H):
    p1 = warp_point(x1, y1, H)
    p2 = warp_point(x2, y2, H)
    return p1, p2

x1, y1 = 333, 389
x2, y2 = 361, 417

(p1x, p1y), (p2x, p2y) = warp_two_points(x1, y1, x2, y2, H)

print(f"Điểm 1 sau warp: ({p1x:.2f}, {p1y:.2f})")
print(f"Điểm 2 sau warp: ({p2x:.2f}, {p2y:.2f})")
