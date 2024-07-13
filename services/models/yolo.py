# models/yolo.py
from pydantic import BaseModel
from typing import List

class YoloRequest(BaseModel):
    bloodtest_id: str
    auth_token: str
    images: List[bytes]  

class YoloResponse(BaseModel):
    labeled_images: List[str]
    counts: dict
