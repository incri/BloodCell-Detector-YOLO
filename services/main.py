# main.py
from fastapi import FastAPI

from routers import yolo
app = FastAPI()

# Include routers
app.include_router(yolo.router, prefix="/yolo", tags=["yolo"])
