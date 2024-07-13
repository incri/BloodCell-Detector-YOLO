import sys
import os
from typing import List, Dict
import numpy as np
import cv2
import torch

# Add yolov5 to path
YOLOV5_PATH = os.path.join(os.path.dirname(__file__), '../../yolov5')
sys.path.append(YOLOV5_PATH)

from yolov5.models.common import DetectMultiBackend
from yolov5.utils.torch_utils import select_device
from yolov5.utils.general import non_max_suppression

def process_images(images: List[bytes]) -> Dict[str, List]:
    # Load the YOLO model
    weights = 'yolov5/runs/train/exp5/weights/best.pt'
    device = select_device('')
    model = DetectMultiBackend(weights, device=device, dnn=False)

    counts = {'RBC': 0, 'WBC': 0, 'Platelets': 0}
    labeled_images = []

    for image_bytes in images:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Pre-process image (e.g., resize if needed)
        img_resized = cv2.resize(img, (640, 640))

        # Prepare image for model input
        img_tensor = torch.from_numpy(img_resized).float().permute(2, 0, 1) / 255.0
        img_tensor = img_tensor.unsqueeze(0).to(device)

        # Perform inference
        with torch.no_grad():
            results = model(img_tensor)

        # Apply non-max suppression
        results = non_max_suppression(results, conf_thres=0.25, iou_thres=0.45)

        # Extract results
        for result in results[0]:
            if len(result) < 6:
                print(f"Unexpected result format: {result}")
                continue
            x1, y1, x2, y2, conf, class_id = result[:6]
            class_id = int(class_id)
            if class_id == 0:
                counts['Platelets'] += 1
            elif class_id == 1:
                counts['RBC'] += 1
            elif class_id == 2:
                counts['WBC'] += 1

    return {"counts": counts, "labeled_images": labeled_images}
