from fastapi import FastAPI
from routers import websocket

app = FastAPI(title="AI Vision Detection API")

# Register routers
app.include_router(websocket.router)
