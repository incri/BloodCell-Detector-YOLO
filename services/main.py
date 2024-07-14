from fastapi import FastAPI
from services.routers import yolo  # Import your router from the routers module

app = FastAPI()

# Include your YOLO router
app.include_router(yolo.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7000)
