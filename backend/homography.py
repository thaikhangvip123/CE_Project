import cv2
import numpy as np

# Global variables to store the four corner points
corner_points = []
dragging_point = None  # To keep track of which point is being dragged

# Callback function for mouse events to capture the points
def click_event(event, x, y, flags, param):
    global corner_points, dragging_point
    
    # If left mouse button is clicked, check if it's near a point to start dragging
    if event == cv2.EVENT_LBUTTONDOWN:
        min_dist = float('inf')
        closest_point = None
        for i, point in enumerate(corner_points):
            dist = np.linalg.norm(np.array([x, y]) - np.array(point))
            if dist < min_dist:
                min_dist = dist
                closest_point = i
        
        # Start dragging if a point is close enough to the click
        if closest_point is not None and min_dist < 10:  # 10 pixels threshold
            dragging_point = closest_point
    
    # If the mouse is moving and a point is being dragged
    elif event == cv2.EVENT_MOUSEMOVE:
        if dragging_point is not None:
            corner_points[dragging_point] = [x, y]  # Update the dragged point's coordinates
    
    # If the left mouse button is released, stop dragging
    elif event == cv2.EVENT_LBUTTONUP:
        dragging_point = None  # Stop dragging

# Load the image
img = cv2.imread('E:\Picture\Screenshot 2023-08-27 220719.png')  # Change to your image path
img_copy = img.copy()  # Copy for visualization

# Resize the image to 650x1000 (width: 650, height: 1000)
resized_img = cv2.resize(img, (650, 1000), interpolation=cv2.INTER_AREA)
img_copy = resized_img.copy()

# Create a window to display the image
cv2.namedWindow('Input Image')

# Set mouse callback for interactive point selection
cv2.setMouseCallback('Input Image', click_event)

# Define initial arbitrary corner points for the resized image
corner_points = [[50, 50], [500, 50], [500, 950], [50, 950]]

while True:
    # Show the resized image with the current corner points
    img_copy = resized_img.copy()
    
    # Draw the points and the lines between them
    for i in range(len(corner_points)):
        cv2.circle(img_copy, tuple(corner_points[i]), 5, (0, 0, 255), -1)
        cv2.circle(img_copy, tuple(corner_points[i]), 15, (42, 255, 255), 1)

        if i > 0:
            cv2.line(img_copy, tuple(corner_points[i-1]), tuple(corner_points[i]), (0, 255, 0), 2)
    
    # Close the rectangle if all 4 points are selected
    cv2.line(img_copy, tuple(corner_points[3]), tuple(corner_points[0]), (0, 255, 0), 2)

    # Define the source points for perspective transform (resize coordinates accordingly)
    src_points = np.float32(corner_points)
    
    # Define the destination points (to a square, but this will be adjusted later)
    dst_points = np.float32([[0, 0], [650, 0], [650, 1000], [0, 1000]])

    # Compute the perspective transform matrix
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)

    # Transform the corners of the original image to determine output size
    h, w = resized_img.shape[:2]
    original_corners = np.float32([[0,0], [w,0], [w,h], [0,h]]).reshape(-1,1,2)
    transformed_corners = cv2.perspectiveTransform(original_corners, matrix)

    # Calculate the bounding box of the transformed corners
    x_coords = transformed_corners[:,0,0]
    y_coords = transformed_corners[:,0,1]
    min_x, max_x = np.min(x_coords), np.max(x_coords)
    min_y, max_y = np.min(y_coords), np.max(y_coords)

    # Compute required output size and adjust the matrix to avoid cropping
    output_width = max(w, int(np.ceil(max_x - min_x)))
    output_height = max(h, int(np.ceil(max_y - min_y)))
    adjustment_matrix = np.array([[1, 0, -min_x], [0, 1, -min_y], [0, 0, 1]], dtype=np.float32)
    adjusted_matrix = adjustment_matrix @ matrix

    # Apply the perspective warp with computed output size and padding
    warped_img = cv2.warpPerspective(resized_img, adjusted_matrix, (output_width, output_height), 
                                     borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0))

    # Resize the warped image to 650x1000 (same dimensions as the output)
    warped_img = cv2.resize(warped_img, (650, 1000), interpolation=cv2.INTER_AREA)

    # Show the original image with corner points
    cv2.imshow('Input Image', img_copy)
    # Show the warped image
    cv2.imshow('Warped Image', warped_img)

    # Wait for the 'q' key to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Close all windows
cv2.destroyAllWindows()