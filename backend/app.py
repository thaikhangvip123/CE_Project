# backend/app.py

import os
import time
from typing import List

import numpy as np
from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, Response, StreamingResponse
from ultralytics import YOLO
import torch
import cv2
import base64
import json

from services.detection import DetectionService
from utils.utils import read_image_bytes
from services.dot_detection import detect_keypoints
from services.score import find_bullseye_center, score_boxes

# -----------------------------
# Config
# -----------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join("best.pt")
CONF_THRESH = 0.25  # confidence threshold for returned detections

# -----------------------------
# App + CORS
# -----------------------------
app = FastAPI(title="YOLOv8 Realtime Detection")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, restrict this to your domain(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Load model once at startup
# -----------------------------
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Put your best.pt there.")

model = YOLO(MODEL_PATH)
# Select device automatically (0 for first CUDA GPU if available)
DEVICE = 0 if torch.cuda.is_available() else "cpu"

# -----------------------------
# Health check
# -----------------------------
@app.get("/health")
def health():
    return {"status": "ok", "device": "cuda" if DEVICE == 0 else "cpu"}

# -----------------------------
# Realtime detect (WebSocket)
# Client sends binary JPEG frames; server replies JSON per frame
# -----------------------------

model = YOLO("best.pt")  # put your path here
os.makedirs("outputs", exist_ok=True)
@app.post("/api/predict-image")
async def predict_image(file: UploadFile = File(...)):
    # Read image
    contents = await file.read()
    boxes = DetectionService.detect_image(contents)
    return {"boxes": boxes}

# -----------------------------

# DOT_MODEL_PATH = "target.pt"

# if not os.path.exists(DOT_MODEL_PATH):
#     raise FileNotFoundError("target.pt not found")

# dot_service = DotDetection(DOT_MODEL_PATH)

@app.post("/detect_pose")
async def detect_pose(file: UploadFile = File(...)):
    """
    Endpoint nhận ảnh upload, detect 8 keypoints, trả về JSON + ảnh PNG đã đánh dấu
    """
    contents = await file.read()
    keypoints, img_bytes = detect_keypoints(contents)

    if keypoints is None:
        return JSONResponse(content={"error": "Không thể đọc ảnh hoặc không tìm thấy keypoints"}, status_code=400)

    # Trả về ảnh + tọa độ keypoints
    return StreamingResponse(img_bytes, media_type="image/png")


dst_points = np.float32([
    [50, 0],
    [550, 0],
    [600, 50],
    [600, 550],
    [550, 600],
    [50, 600],
    [0, 550],
    [0, 50]
])

@app.post("/homography")
async def homography(
    image: UploadFile = File(...),
    points: str = Form(...)
):
    img_bytes = await image.read()
    npimg = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    src_points = np.array(json.loads(points), dtype=np.float32)

    H, _ = cv2.findHomography(src_points, dst_points, cv2.RANSAC, 5.0)
    warped = cv2.warpPerspective(img, H, (600, 600))

    _, buffer = cv2.imencode(".png", warped)
    img_base64 = base64.b64encode(buffer).decode("utf-8")

    return {
        "image": img_base64,
        "H": H.tolist()
    }
    # return Response(buffer.tobytes(), media_type="image/png")


@app.post("/api/score")
async def score_endpoint(
    image_base64: str = Form(...),
    boxes: str = Form(...)
):
    if "," in image_base64:
        image_base64 = image_base64.split(",")[1]
    # Decode image
    img_bytes = base64.b64decode(image_base64)
    npimg = np.frombuffer(img_bytes, np.uint8)
    warped_img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    if warped_img is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid warped image"}
        )

    # Parse boxes
    try:
        boxes = json.loads(boxes)
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid boxes format"}
        )

    # Find center
    center = find_bullseye_center(warped_img)

    # Score
    total_score, shot_results = score_boxes(boxes, center)

    return {
        "center": {
            "x": center[0],
            "y": center[1]
        },
        "total_score": total_score,
        "shots": shot_results
    }