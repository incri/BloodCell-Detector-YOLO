from fastapi import APIRouter, HTTPException, Form
from typing import List
import requests
from services.models.yolo import process_images

router = APIRouter()

@router.post("/process-images/")
async def process_images_endpoint(
    bloodtest_id: str = Form(...), 
    auth_token: str = Form(...), 
    image_urls: str = Form(...)
):
    try:
        # Convert image_urls from comma-separated string to list
        image_urls = image_urls.split(',')

        # Fetch images from URLs
        images = []
        for url in image_urls:
            response = requests.get(url)
            response.raise_for_status()
            images.append(response.content)

        # Process images using YOLO
        result = process_images(images)

        return {"message": "Processing complete", "counts": result['counts']}
    except requests.exceptions.RequestException as e:
        print(f"Error fetching images: {e}")
        raise HTTPException(status_code=400, detail=f"Error fetching images: {e}")
    except Exception as e:
        print(f"Error processing images: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing images: {e}")