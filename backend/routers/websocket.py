from fastapi import APIRouter, WebSocket
from services.detection import DetectionService

router = APIRouter()
detection_service = DetectionService()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ Client connected")

    try:
        while True:
            data = await websocket.receive_bytes()
            jpeg = detection_service.process_frame(data)
            await websocket.send_bytes(jpeg)

    except Exception as e:
        print("❌ WebSocket error:", e)
    finally:
        await websocket.close()
