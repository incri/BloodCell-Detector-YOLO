from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from services.routers import yolo, test  # Import your router from the routers module
from dotenv import load_dotenv
import os

app = FastAPI()

load_dotenv()
# Include your YOLO router
app.include_router(yolo.router)

# CORS settings
origins = [
    "*",  # Replace with your Django frontend URL
    "*",  # Example: If Django runs on port 8000
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Serve the result_images directory
app.mount("/result_images", StaticFiles(directory="C:\\Users\\Incri\\projects\\BCD\\BloodCell-Detector-Backend\\media\\lab\\result-images"), name="result_images")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)
