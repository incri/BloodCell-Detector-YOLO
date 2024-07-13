# routers/yolo.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List

from models.yolo import YoloRequest, YoloResponse

router = APIRouter()

@router.post("/process-images/")
async def process_images(yolo_request: YoloRequest):
    # Validate auth_token (you might want to implement authentication logic here)

    # Access bloodtest_id and images
    bloodtest_id = yolo_request.bloodtest_id
    images = yolo_request.images

    # Process the images (for demonstration, we will print the details)
    print(f"Processing images for bloodtest_id: {bloodtest_id}")
    for image in images:
        print(f"Received image of size {len(image)} bytes")

    # Simulate YOLO processing and prepare response
    labeled_images = ["image1_labeled.jpg", "image2_labeled.jpg"]  # Example of labeled images
    counts = {"RBC": 7, "WBC": 1, "Platelets": 2}  # Example counts

    return YoloResponse(labeled_images=labeled_images, counts=counts)
