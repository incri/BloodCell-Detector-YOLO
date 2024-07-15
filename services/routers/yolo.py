from fastapi import APIRouter, HTTPException, Form, Request
import subprocess
import requests
import os
import tempfile
import re
import uuid
import shutil

router = APIRouter()

# Define the directory to save YOLOv5 detection results
results_dir = "C:\\Users\\Incri\\projects\\BCD\\BloodCell-Detector-Backend\\media\\lab\\result-images"

@router.post("/process-images/")
async def process_images_endpoint(
    image_urls: str = Form(...)
):
    try:
        # Convert image_urls from comma-separated string to list
        image_urls = image_urls.split(',')

        # Create a temporary directory to save images
        temp_dir = tempfile.mkdtemp()

        # Save images locally
        local_image_paths = []
        for idx, url in enumerate(image_urls):
            response = requests.get(url)
            response.raise_for_status()
            # Use a unique identifier for each image
            image_path = os.path.join(temp_dir, f"image_{uuid.uuid4().hex}.jpg")
            with open(image_path, 'wb') as f:
                f.write(response.content)
            local_image_paths.append(image_path)

        # Path to the Python executable in your environment
        python_executable = "C:\\Users\\Incri\\projects\\env\\BCD_YOLO_env\\Scripts\\python.exe"

        # Prepare the command to call YOLOv5 detection script
        yolo_command = [
            python_executable, "yolov5/detect.py",
            "--weights", "yolov5/runs/train/exp5/weights/best.pt",
            "--img", "640",
            "--conf", "0.25",
            "--source", temp_dir,  # Pass local file paths as the source
            "--project", temp_dir,  # Use a temp directory for initial results
            "--name", ".",  # Specify name to save directly in the temp_dir
            "--exist-ok"  # Allow existing project/name
        ]

        # Start subprocess to execute YOLOv5 detection
        process = subprocess.Popen(yolo_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait for YOLOv5 process to finish and get outputs
        stdout, stderr = process.communicate()

        # Check for errors
        if process.returncode != 0:
            error_message = stderr.decode("utf-8").strip()
            print(f"Error: {error_message}")
            raise Exception(f"YOLOv5 process error: {error_message}")

        # Log stdout and stderr for debugging (optional)
        stdout_output = stdout.decode("utf-8").strip()
        stderr_output = stderr.decode("utf-8").strip()
        print(f"STDOUT: {stdout_output}")
        print(f"STDERR: {stderr_output}")

        # Define regex pattern to extract counts of RBCs, WBCs, and Platelets
        pattern = r"(\d+) Plateletss?, (\d+) RBCs?, (\d+) WBCs?"

        # Initialize counters
        total_platelets = 0
        total_rbcs = 0
        total_wbcs = 0

        # Use re.findall to find all occurrences of the pattern in the stderr output
        matches = re.findall(pattern, stderr_output)

        # Process each match and accumulate counts
        for match in matches:
            platelets_count = int(match[0])
            rbc_count = int(match[1])
            wbc_count = int(match[2])

            total_platelets += platelets_count
            total_rbcs += rbc_count
            total_wbcs += wbc_count

        # Get the base URL of the request to dynamically determine the port

        # Collect processed image paths and rename them with UUIDs
        processed_image_paths = []
        for file_name in os.listdir(temp_dir):
            if file_name.endswith(".jpg") or file_name.endswith(".png"):
                new_file_name = f"{uuid.uuid4().hex}{os.path.splitext(file_name)[1]}"
                new_file_path = os.path.join(results_dir, new_file_name)
                shutil.move(os.path.join(temp_dir, file_name), new_file_path)
                processed_image_paths.append(f"http://127.0.0.1:8000/media/lab/result-images/{new_file_name}")

        return {
            "message": "Processing complete",
            "platelets_count": total_platelets,
            "rbc_count": total_rbcs,
            "wbc_count": total_wbcs,
            "processed_images": processed_image_paths,
        }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching images: {e}")
        raise HTTPException(status_code=400, detail=f"Error fetching images: {e}")
    except Exception as e:
        print(f"Error processing images: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing images: {e}")
    finally:
        # Clean up temporary files
        for image_path in local_image_paths:
            if os.path.exists(image_path):
                os.remove(image_path)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
