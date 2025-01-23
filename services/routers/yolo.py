from fastapi import APIRouter, HTTPException, Form
import subprocess
import requests
import os
import tempfile
import re
import uuid
import shutil
import logging

# Initialize the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Utility function to download images
def download_images(image_urls, temp_dir):
    local_image_paths = []
    for idx, url in enumerate(image_urls):
        try:
            response = requests.get(url)
            response.raise_for_status()
            image_path = os.path.join(temp_dir, f"image_{uuid.uuid4().hex}.jpg")
            with open(image_path, 'wb') as f:
                f.write(response.content)
            local_image_paths.append(image_path)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching image from {url}: {e}")
            raise HTTPException(status_code=400, detail=f"Error fetching image from {url}: {e}")
    return local_image_paths

# Utility function to run YOLOv5 detection
def run_yolo_detection(env_activate, weights_path, temp_dir):
    yolo_command = [
        env_activate, "yolov5/detect.py",
        "--weights", weights_path,
        "--img", "640",
        "--conf", "0.25",
        "--source", temp_dir,
        "--project", temp_dir,
        "--name", ".",
        "--exist-ok",
        "--hide-labels"
    ]
    process = subprocess.Popen(yolo_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        error_message = stderr.decode("utf-8").strip()
        logger.error(f"YOLOv5 process error: {error_message}")
        raise Exception(f"YOLOv5 process error: {error_message}")
    return stdout.decode("utf-8").strip(), stderr.decode("utf-8").strip()

# Utility function to extract counts from YOLOv5 output
def extract_counts(stderr_output, patterns):
    counts = {key: 0 for key in patterns}
    for key, pattern in patterns.items():
        matches = re.findall(pattern, stderr_output)
        counts[key] += sum(int(count) for count in matches)
    return counts

# Utility function to move processed images
def move_processed_images(temp_dir, result_dir, processed_image_base_url):
    processed_image_paths = []
    for file_name in os.listdir(temp_dir):
        if file_name.endswith(".jpg") or file_name.endswith(".png"):
            new_file_name = f"{uuid.uuid4().hex}{os.path.splitext(file_name)[1]}"
            new_file_path = os.path.join(result_dir, new_file_name)
            shutil.move(os.path.join(temp_dir, file_name), new_file_path)
            processed_image_paths.append(f"{processed_image_base_url}{new_file_name}")
    return processed_image_paths

@router.post("/process-images/")
async def process_images_endpoint(
    image_urls: str = Form(...)
):
    try:
        image_urls = image_urls.split(',')
        result_dir = os.getenv("RESULT_DIR")
        env_activate = os.getenv("ENV_ACTIVATE")
        processed_image_base_url = os.getenv("PROCESSED_IMAGE_PATH")

        temp_dir = tempfile.mkdtemp()
        local_image_paths = download_images(image_urls, temp_dir)

        stdout_output, stderr_output = run_yolo_detection(
            env_activate,
            "yolov5/runs/train/blood_cell_count_model/weights/best.pt",
            temp_dir
        )

        patterns = {
            'rbc': r"(\d+) RBC",
            'wbc': r"(\d+) WBC",
            'platelets': r"(\d+) Platelets"
        }
        counts = extract_counts(stderr_output, patterns)

        processed_image_paths = move_processed_images(temp_dir, result_dir, processed_image_base_url)

        return {
            "message": "Processing complete",
            "detected": counts,
            "processed_images": processed_image_paths,
        }

    except Exception as e:
        logger.error(f"Error processing images: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing images: {e}")
    finally:
        for image_path in local_image_paths:
            if os.path.exists(image_path):
                os.remove(image_path)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

@router.post("/process-blood-types-images/")
async def process_blood_types_images_endpoint(
    image_urls: str = Form(...)
):
    try:
        image_urls = image_urls.split(',')
        result_dir = os.getenv("RESULT_DIR")
        env_activate = os.getenv("ENV_ACTIVATE")
        processed_image_base_url = os.getenv("PROCESSED_IMAGE_PATH")

        temp_dir = tempfile.mkdtemp()
        local_image_paths = download_images(image_urls, temp_dir)

        stdout_output, stderr_output = run_yolo_detection(
            env_activate,
            "yolov5/runs/train/blood_cell_types_model/weights/best.pt",
            temp_dir
        )


        patterns = {
            'basophil': r"(\d+) basophil",
            'eosinophil': r"(\d+) eosinophil",
            'lymphocyte': r"(\d+) lymphocyte",
            'monocyte': r"(\d+) monocyte",
            'neutrophil': r"(\d+) neutrophil",
        }
        counts = extract_counts(stderr_output, patterns)

        processed_image_paths = move_processed_images(temp_dir, result_dir, processed_image_base_url)

        return {
            "message": "Processing complete",
            "detected": counts,
            "processed_images": processed_image_paths,
        }

    except Exception as e:
        logger.error(f"Error processing images: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing images: {e}")
    finally:
        for image_path in local_image_paths:
            if os.path.exists(image_path):
                os.remove(image_path)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
