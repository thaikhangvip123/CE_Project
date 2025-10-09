from fastapi import FastAPI
from routers import ws

app = FastAPI()

# Register routers
app.include_router(ws.router)
