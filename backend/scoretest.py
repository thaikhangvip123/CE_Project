import cv2
import numpy as np
import math

# --- 1. CẤU HÌNH DỮ LIỆU ĐÃ CHỐT ---
SIZE = 600

# Bộ bán kính chuẩn bạn đã tinh chỉnh
RADII_SCORES = [
    (25, 10),   # Vòng 10
    (47, 9),    # Vòng 9
    (69, 8),    # Vòng 8
    (90, 7),    # Vòng 7
    (113, 6),   # Vòng 6
    (135, 5),   # Vòng 5
    (157, 4),   # Vòng 4
    (179, 3),   # Vòng 3
    (201, 2),   # Vòng 2
    (223, 1),   # Vòng 1
    (257, 0)    # Vòng hụt
]

dst_points = np.float32([
    [50, 0], [550, 0], [600, 50], [600, 550],
    [550, 600], [50, 600], [0, 550], [0, 50]
])

# Biến toàn cục
src_points = []
img_original = None
img_display = None
warped_global = None     # Ảnh đã nắn
real_center_global = (300, 300) # Tâm thực tế

# --- 2. HÀM TÍNH ĐIỂM CỐT LÕI (CORE LOGIC) ---
def get_score_from_distance(distance):
    """
    So sánh khoảng cách với danh sách bán kính để trả về điểm số.
    Quy tắc: So từ vòng nhỏ nhất (10đ) ra ngoài.
    Nếu khoảng cách < bán kính vòng 10 -> 10 điểm.
    Nếu không, check tiếp vòng 9...
    """
    for radius, score in RADII_SCORES:
        if distance <= radius:
            return score
    return -1 # Ra ngoài bia hoàn toàn

# --- 3. HÀM TÌM TÂM (AUTO-CENTER) ---
def find_bullseye_center(warped_img):
    gray = cv2.cvtColor(warped_img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    best_center = (300, 300)
    max_area = 0
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 500:
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                if np.sqrt((cx - 300)**2 + (cy - 300)**2) < 50:
                    if area > max_area:
                        max_area = area
                        best_center = (cx, cy)
    return best_center

# --- 4. HÀM XỬ LÝ CLICK CHUỘT ĐỂ GIẢ LẬP BẮN ---
def on_mouse_click_shooting(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        if warped_global is None: return
        
        # 1. Tính khoảng cách từ điểm click (x,y) tới tâm (real_center_global)
        cx, cy = real_center_global
        distance = math.sqrt((x - cx)**2 + (y - cy)**2)
        
        # 2. Lấy điểm số
        score = get_score_from_distance(distance)
        
        # 3. Vẽ phản hồi lên ảnh
        display_img = warped_global.copy()
        
        # Vẽ lại overlay cơ bản
        cv2.drawMarker(display_img, (cx, cy), (0, 0, 255), cv2.MARKER_CROSS, 20, 2)
        for r, s in RADII_SCORES:
            cv2.circle(display_img, (cx, cy), r, (0, 255, 0), 1)

        # Vẽ vết đạn giả lập (Màu đỏ)
        cv2.circle(display_img, (x, y), 5, (0, 0, 255), -1)
        
        # Vẽ đường nối từ tâm đến vết đạn
        cv2.line(display_img, (cx, cy), (x, y), (255, 255, 0), 1)
        
        # Hiển thị thông số
        txt_score = f"DIEM: {score}" if score >= 0 else "TRUOT"
        txt_dist = f"Dist: {distance:.1f}px"
        
        cv2.putText(display_img, txt_score, (10, 550), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
        cv2.putText(display_img, txt_dist, (10, 590), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        cv2.imshow("SIMULATION (Click to Shoot)", display_img)
        print(f"Bắn tại ({x}, {y}) - Khoảng cách: {distance:.2f} - Điểm: {score}")

# --- 5. MAIN PROCESS ---
def run_simulation():
    global warped_global, real_center_global
    
    pts_src = np.array(src_points, dtype=np.float32)
    H, _ = cv2.findHomography(pts_src, dst_points, cv2.RANSAC, 5.0)
    
    if H is not None:
        warped_global = cv2.warpPerspective(img_original, H, (SIZE, SIZE))
        real_center_global = find_bullseye_center(warped_global)
        
        # Hiển thị cửa sổ mô phỏng
        cv2.namedWindow("SIMULATION (Click to Shoot)")
        cv2.setMouseCallback("SIMULATION (Click to Shoot)", on_mouse_click_shooting)
        
        # Vẽ trạng thái ban đầu
        initial_view = warped_global.copy()
        cv2.drawMarker(initial_view, real_center_global, (0, 0, 255), cv2.MARKER_CROSS, 20, 2)
        for r, s in RADII_SCORES:
            cv2.circle(initial_view, real_center_global, r, (0, 255, 0), 1)
            
        cv2.imshow("SIMULATION (Click to Shoot)", initial_view)
        print("\n--- CHẾ ĐỘ GIẢ LẬP BẮN SÚNG ---")
        print("Click chuột lên bia để kiểm tra logic tính điểm.")
        print("Nhấn 'q' để thoát.")
        
        while True:
            if cv2.waitKey(1) & 0xFF == ord('q'): break
        cv2.destroyAllWindows()

def pick_points(event, x, y, flags, param):
    global img_display
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(src_points) < 8:
            src_points.append([x, y])
            cv2.circle(img_display, (x, y), 5, (0, 0, 255), -1)
            if len(src_points) > 1:
                cv2.line(img_display, tuple(src_points[-2]), tuple(src_points[-1]), (255, 0, 0), 1)
            if len(src_points) == 8:
                cv2.line(img_display, tuple(src_points[-1]), tuple(src_points[0]), (255, 0, 0), 1)
            cv2.imshow("Input", img_display)
            
            if len(src_points) == 8:
                cv2.destroyWindow("Input")
                run_simulation()

if __name__ == "__main__":
    IMAGE_PATH = 'E:/DAKTMT/Test image/Screenshot 2026-01-04 235843.png' 
    img_original = cv2.imread(IMAGE_PATH)
    
    if img_original is None:
        print("Lỗi ảnh!")
    else:
        src_points = []
        img_display = img_original.copy()
        cv2.namedWindow("Input")
        cv2.setMouseCallback("Input", pick_points)
        print("Chấm 8 điểm để bắt đầu...")
        cv2.imshow("Input", img_display)
        cv2.waitKey(0)