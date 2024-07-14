from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from services.routers import yolo  # Import your router from the routers module

app = FastAPI()

# Include your YOLO router
app.include_router(yolo.router)

# Serve the result_images directory
app.mount("/result_images", StaticFiles(directory="result_images"), name="result_images")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)
