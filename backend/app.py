import os
import time
from typing import List

import numpy as np
from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from ultralytics import YOLO
import torch
import cv2
import base64

from utils.utils import read_image_bytes, draw_boxes

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
# Single image detect (HTTP)
# -----------------------------
# @app.post("/detect")
# async def detect(file: UploadFile = File(...)):
#     try:
#         # Read and decode image
#         contents = await file.read()
#         np_img = np.frombuffer(contents, np.uint8)
#         img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

#         if img is None:
#             return JSONResponse(content={"error": "Invalid image"}, status_code=400)

#         # Run YOLO prediction
#         results = model.predict(img, conf=0.5)

#         # Draw results (annotated image)
#         annotated = results[0].plot()

#         # Encode to base64 string
#         _, buffer = cv2.imencode('.jpg', annotated)
#         img_base64 = base64.b64encode(buffer).decode("utf-8")

#         # Return base64 image as JSON
#         return {"image": f"data:image/jpeg;base64,{img_base64}"}

#     except Exception as e:
#         return JSONResponse(content={"error": str(e)}, status_code=500)

    # img_bytes = await file.read()
    # img = jpeg_bytes_to_bgr(img_bytes)

    # # Inference
    # results = model.predict(img, conf=CONF_THRESH, device=DEVICE, verbose=False)[0]

    # # Parse detections
    # detections = []
    # if results.boxes is not None and len(results.boxes) > 0:
    #     xyxy = results.boxes.xyxy.cpu().numpy()   # (N,4)
    #     conf = results.boxes.conf.cpu().numpy()   # (N,)
    #     cls  = results.boxes.cls.cpu().numpy()    # (N,)
    #     names = results.names  # dict of class idx->name

    #     for (x1, y1, x2, y2), c, k in zip(xyxy, conf, cls):
    #         detections.append({
    #             "bbox": [float(x1), float(y1), float(x2), float(y2)],
    #             "confidence": float(c),
    #             "class_id": int(k),
    #             "class_name": names[int(k)]
    #         })

    # return JSONResponse({"detections": detections, "width": img.shape[1], "height": img.shape[0]})

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
    np_img = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    # Run YOLO inference
    results = model(img)[0]

    # Draw bounding boxes
    for box in results.boxes:
        cls = int(box.cls)
        label = model.names[cls]
        conf = float(box.conf)
        x1, y1, x2, y2 = box.xyxy[0].tolist()

        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.putText(img, f"{label} {conf:.2f}", (int(x1), int(y1) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Save output image
    output_path = f"outputs/result_{file.filename}"
    cv2.imwrite(output_path, img)

    # Return the processed image file directly
    return FileResponse(output_path, media_type="image/jpeg")


@app.websocket("/ws")
async def ws_detect(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()

            # Convert bytes → numpy image
            nparr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Run YOLO detection
            results = model(frame)

            # Draw bounding boxes
            for r in results:
                for box in r.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    cls = int(box.cls)
                    label = model.names[cls]
                    conf = float(box.conf)

                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    cv2.putText(frame, f"{label} {conf:.2f}",
                                (int(x1), int(y1) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.9, (0, 255, 0), 2)

            # Encode frame as JPEG
            _, jpeg = cv2.imencode(".jpg", frame)
            await websocket.send_bytes(jpeg.tobytes())


            # # Binary frame expected (JPEG)
            # frame_bytes = await websocket.receive_bytes()
            # start = time.time()

            # # Decode
            # try:
            #     img = jpeg_bytes_to_bgr(frame_bytes)
            # except Exception as e:
            #     await websocket.send_json({"type": "error", "message": str(e)})
            #     continue

            # # Inference
            # results = model.predict(img, conf=CONF_THRESH, device=DEVICE, verbose=False)[0]

            # detections = []
            # if results.boxes is not None and len(results.boxes) > 0:
            #     xyxy = results.boxes.xyxy.cpu().numpy()
            #     conf = results.boxes.conf.cpu().numpy()
            #     cls  = results.boxes.cls.cpu().numpy()
            #     names = results.names

            #     for (x1, y1, x2, y2), c, k in zip(xyxy, conf, cls):
            #         detections.append({
            #             "bbox": [float(x1), float(y1), float(x2), float(y2)],
            #             "confidence": float(c),
            #             "class_id": int(k),
            #             "class_name": names[int(k)]
            #         })

            # dt = time.time() - start
            # await websocket.send_json({
            #     "type": "detections",
            #     "fps": (1.0 / dt) if dt > 0 else None,
            #     "width": img.shape[1],
            #     "height": img.shape[0],
            #     "detections": detections
            # })
    except Exception as e:
        print("❌ WebSocket error:", e)
    finally:
        await websocket.close()
        print("🔌 WebSocket closed")
    # except WebSocketDisconnect:
    #     # Client disconnected
    #     return
    # except Exception as e:
    #     # Send error to client then close
    #     try:
    #         await websocket.send_json({"type": "error", "message": str(e)})
    #     finally:
    #         await websocket.close()
