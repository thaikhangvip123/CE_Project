# from fastapi import APIRouter, UploadFile, File, Form
# from fastapi.responses import Response
# import cv2
# import numpy as np

# router = APIRouter()

# # === dst_points GIỮ NGUYÊN ===
# dst_points = np.float32([
#     [50, 0],
#     [550, 0],
#     [600, 50],
#     [600, 550],
#     [550, 600],
#     [50, 600],
#     [0, 550],
#     [0, 50]
# ])

# @router.post("/homography")
# async def homography(
#     image: UploadFile = File(...),
#     points: str = Form(...)
# ):
#     # Decode image
#     img_bytes = await image.read()
#     npimg = np.frombuffer(img_bytes, np.uint8)
#     img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

#     # Parse points
#     src_points = np.array(eval(points), dtype=np.float32)

#     H, _ = cv2.findHomography(src_points, dst_points, cv2.RANSAC, 5.0)

#     warped = cv2.warpPerspective(img, H, (600, 600))

#     _, buffer = cv2.imencode(".png", warped)
#     return Response(buffer.tobytes(), media_type="image/png")
