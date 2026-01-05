import cv2
import numpy as np
import math

# Global variables
corner_points = []
dragging_point = None
shot_detections = []  # Store shot coordinates from detection

# Callback function for mouse events
def click_event(event, x, y, flags, param):
    global corner_points, dragging_point
    
    if event == cv2.EVENT_LBUTTONDOWN:
        min_dist = float('inf')
        closest_point = None
        for i, point in enumerate(corner_points):
            dist = np.linalg.norm(np.array([x, y]) - np.array(point))
            if dist < min_dist:
                min_dist = dist
                closest_point = i
        
        if closest_point is not None and min_dist < 15:
            dragging_point = closest_point
    
    elif event == cv2.EVENT_MOUSEMOVE:
        if dragging_point is not None:
            corner_points[dragging_point] = [x, y]
    
    elif event == cv2.EVENT_LBUTTONUP:
        dragging_point = None


def calculate_circle_points(center_x, center_y, radius, num_points=8):
    """
    Generate points evenly distributed on a circle.
    Starting from top (0 degrees) and going clockwise.
    """
    points = []
    for i in range(num_points):
        angle = (i * 2 * math.pi / num_points) - (math.pi / 2)  # Start from top
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        points.append([int(x), int(y)])
    return points


# def calculate_shot_score(x, y, center_x, center_y, max_radius):
#     """
#     Calculate shooting score based on distance from center.
#     Assumes standard shooting target with 10 rings.
#     """
#     distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
    
#     # Normalize distance (0 = center, 1 = edge)
#     normalized_distance = distance / max_radius
    
#     # Calculate score (10 at center, 0 at edge)
#     if normalized_distance >= 1.0:
#         return 0  # Outside target
    
#     # 10 rings, each ring is 10% of radius
#     score = 10 - int(normalized_distance * 10)
#     score = max(0, min(10, score))  # Clamp between 0-10
    
#     return score


def transform_shot_coordinates(shots, homography_matrix):
    """
    Transform shot coordinates from warped space to original space.
    """
    if len(shots) == 0:
        return []
    
    # Convert to homogeneous coordinates
    shots_array = np.array(shots, dtype=np.float32).reshape(-1, 1, 2)
    
    # Apply inverse homography
    transformed = cv2.perspectiveTransform(shots_array, np.linalg.inv(homography_matrix))
    
    return transformed.reshape(-1, 2).tolist()


def detect_shots_from_image(image, sensitivity=30):
    """
    Detect green shot markers from the image.
    This is a placeholder - replace with your actual detection logic.
    """
    # Convert to HSV for green detection
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Green color range
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([80, 255, 255])
    
    # Create mask
    mask = cv2.inRange(hsv, lower_green, upper_green)
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    shots = []
    for contour in contours:
        # Get center of contour
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            shots.append([cx, cy])
    
    return shots


def main():
    global corner_points, shot_detections
    
    # Load image
    img = cv2.imread('E:/AI-Vision/backend/outputs/result_scene00741.png')
    if img is None:
        print("Error: Could not load image")
        return
    
    # Resize image
    target_width, target_height = 1920, 1080
    h, w = img.shape[:2]
    ratio = min(target_width / w, target_height / h)
    new_w = int(w * ratio)
    new_h = int(h * ratio)
    resized_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    # Create canvas with padding
    canvas = np.zeros((target_height, target_width, 3), dtype=np.uint8)
    x_offset = (target_width - new_w) // 2
    y_offset = (target_height - new_h) // 2
    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized_img
    resized_img = canvas
    
    img_copy = resized_img.copy()
    
    # Create window
    cv2.namedWindow('Input Image', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Input Image', 1280, 720)
    cv2.setMouseCallback('Input Image', click_event)
    
    # Initialize 8 corner points around the distorted target
    # ADJUST THESE to match your target's actual position
    center_x, center_y = target_width // 2, target_height // 2
    initial_radius = 400  # Adjust based on your target size
    corner_points = calculate_circle_points(center_x, center_y, initial_radius, num_points=8)
    
    connection_order = list(range(8)) + [0]
    
    # Output image settings (perfect circle)
    output_size = 1000  # Square output
    output_center = output_size // 2
    output_radius = 450  # Radius of perfect circle in output
    
    # print("\n=== CONTROLS ===")
    # print("Drag the 8 points to match the target's edge")
    # print("Press 'q' to quit")
    # print("Press 's' to save warped image")
    # print("Press 'c' to calculate scores for all shots")
    
    while True:
        img_copy = resized_img.copy()
        
        # Draw control points and lines
        for i in range(len(corner_points)):
            cv2.circle(img_copy, tuple(corner_points[i]), 8, (0, 0, 255), -1)
            cv2.circle(img_copy, tuple(corner_points[i]), 20, (42, 255, 255), 2)
            cv2.putText(img_copy, str(i), (corner_points[i][0]+15, corner_points[i][1]-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        for i in range(len(connection_order) - 1):
            pt1 = corner_points[connection_order[i]]
            pt2 = corner_points[connection_order[i+1]]
            cv2.line(img_copy, tuple(pt1), tuple(pt2), (0, 255, 0), 2)
        
        # Create CIRCULAR destination points
        src_points = np.float32(corner_points)
        dst_points = np.float32(calculate_circle_points(output_center, output_center, 
                                                        output_radius, num_points=8))
        
        # Compute homography
        matrix, _ = cv2.findHomography(src_points, dst_points, method=0)
        
        if matrix is not None:
            # Warp the image
            warped_img = cv2.warpPerspective(resized_img, matrix, (output_size, output_size),
                                            borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
            
            # # Detect shots in the original image
            # shot_detections = detect_shots_from_image(resized_img)
            
            # # Transform shot coordinates to warped space
            # if len(shot_detections) > 0:
            #     warped_shots = cv2.perspectiveTransform(
            #         np.array(shot_detections, dtype=np.float32).reshape(-1, 1, 2),
            #         matrix
            #     ).reshape(-1, 2)
                
            #     # Draw shots on warped image and calculate scores
            #     total_score = 0
            #     for i, (wx, wy) in enumerate(warped_shots):
            #         score = calculate_shot_score(wx, wy, output_center, output_center, output_radius)
            #         total_score += score
                    
            #         # Draw shot marker
            #         color = (0, 255, 0) if score >= 7 else (0, 165, 255) if score >= 4 else (0, 0, 255)
            #         cv2.circle(warped_img, (int(wx), int(wy)), 5, color, -1)
            #         cv2.circle(warped_img, (int(wx), int(wy)), 15, color, 2)
                    
            #         # Draw score
            #         cv2.putText(warped_img, f"{score}", (int(wx)+20, int(wy)-10),
            #                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                
            #     # Draw total score
            #     cv2.putText(warped_img, f"Total: {total_score}", (20, 40),
            #                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
            #     cv2.putText(warped_img, f"Shots: {len(warped_shots)}", (20, 80),
            #                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
            
            # # Draw concentric circles (target rings) on warped image
            # for ring in range(1, 11):
            #     ring_radius = int(output_radius * ring / 10)
            #     color = (100, 100, 100)
            #     cv2.circle(warped_img, (output_center, output_center), ring_radius, color, 1)
            
            # # Draw center crosshair
            # cv2.line(warped_img, (output_center-20, output_center), 
            #         (output_center+20, output_center), (0, 255, 255), 2)
            # cv2.line(warped_img, (output_center, output_center-20), 
            #         (output_center, output_center+20), (0, 255, 255), 2)
            
            # Show warped image
            cv2.namedWindow('Warped Image (Perfect Circle)', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Warped Image (Perfect Circle)', 800, 800)
            cv2.imshow('Warped Image (Perfect Circle)', warped_img)
        
        cv2.imshow('Input Image', img_copy)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord("p"):
            print("\n=== 8 CORNER POINTS (INPUT IMAGE) ===")
            for i, (x, y) in enumerate(corner_points):
                print(f"Point {i}: x = {x}, y = {y}")
    
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
