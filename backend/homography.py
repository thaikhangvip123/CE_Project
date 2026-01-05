import cv2
import numpy as np

# 1. BỘ TỌA ĐỘ ĐÍCH CHUẨN (Lấy từ ảnh chính diện đẹp nhất đã cân chỉnh)
# Các điểm này tạo thành hình bát giác cân đối lấp đầy khung hình 600x600
# Bộ tọa độ đích mới giúp bia lấp đầy khung hình 600x600
dst_points = np.float32([
    [50, 0],     # 1. Cạnh trên bên trái (sát mép trên)
    [550, 0],    # 2. Cạnh trên bên phải
    [600, 50],   # 3. Góc vát trên bên phải (sát mép phải)
    [600, 550],  # 4. Góc vát dưới bên phải
    [550, 600],  # 5. Cạnh dưới bên phải (sát mép dưới)
    [50, 600],   # 6. Cạnh dưới bên trái
    [0, 550],    # 7. Góc vát dưới bên trái (sát mép trái)
    [0, 50]      # 8. Góc vát trên bên trái
])

# Biến toàn cục để lưu 8 điểm bạn chấm trên ảnh nghiêng
src_points = []

def pick_points(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        src_points.append([x, y])
        # Vẽ điểm đã chấm
        cv2.circle(img_display, (x, y), 5, (0, 0, 255), -1)
        cv2.putText(img_display, str(len(src_points)), (x+10, y+10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.imshow("Buoc 1: Cham 8 diem theo thu tu", img_display)
        
        if len(src_points) == 8:
            print("Đã đủ 8 điểm. Đang thực hiện nắn ảnh...")
            run_homography()

def run_homography():
    # Chuyển list sang numpy array
    pts_src = np.array(src_points, dtype=np.float32)
    pts_dst = dst_points # Đã khai báo ở trên
    
    # Tính ma trận Homography dùng thuật toán RANSAC để khử sai số [cite: 370, 553]
    H, status = cv2.findHomography(pts_src, pts_dst, cv2.RANSAC, 5.0)
    
    if H is not None:
        # Thực hiện biến đổi phối cảnh (Perspective Warp) [cite: 342, 555]
        # Kích thước đầu ra cố định 600x600 để khớp với bộ dst_points
        warped_img = cv2.warpPerspective(img_original, H, (600, 600))
        
        # Hiển thị kết quả nắn thẳng
        cv2.imshow("Buoc 2: Ket qua sau khi nan (Warped)", warped_img)
        print("Nắn ảnh thành công! Kiểm tra độ phẳng của bia ở cửa sổ mới.")
    else:
        print("Lỗi: Không tính được ma trận H.")

# --- CHƯƠNG TRÌNH CHÍNH ---
# Thay 'scene00006.png' bằng đường dẫn ảnh nghiêng của bạn
IMAGE_PATH = 'test_images/scene00006.png' 
img_original = cv2.imread(IMAGE_PATH)

if img_original is None:
    print("Không tìm thấy ảnh tại đường dẫn đã cung cấp!")
else:
    img_display = img_original.copy()
    cv2.namedWindow("Buoc 1: Cham 8 diem theo thu tu")
    cv2.setMouseCallback("Buoc 1: Cham 8 diem theo thu tu", pick_points)
    
    print("HƯỚNG DẪN:")
    print("1. Chấm 8 điểm lên các góc vát của bia trên ảnh nghiêng.")
    print("2. Thứ tự: Bắt đầu từ đỉnh TRÊN-TRÁI, đi theo CHIỀU KIM ĐỒNG HỒ.")
    print("3. Nhấn 'r' để reset nếu chấm sai, 'q' để thoát.")

    while True:
        cv2.imshow("Buoc 1: Cham 8 diem theo thu tu", img_display)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if key == ord('r'): # Reset điểm
            src_points = []
            img_display = img_original.copy()
            print("Đã reset điểm chấm.")

    cv2.destroyAllWindows()