from fastapi import APIRouter, HTTPException, Form
import subprocess
import requests
import os
import tempfile
import re

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

        # Create a temporary directory to save images
        temp_dir = tempfile.mkdtemp()

        # Save images locally
        local_image_paths = []
        for idx, url in enumerate(image_urls):
            response = requests.get(url)
            response.raise_for_status()
            image_path = os.path.join(temp_dir, f"image_{idx}.jpg")
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
            "--source", *local_image_paths,  # Pass local file paths as the source
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

        # Print actual outputs from detect.py
        print(f"Actual stdout output from detect.py: {stdout_output}")
        print(f"Actual stderr output from detect.py: {stderr_output}")


        # Define regex pattern to extract counts of RBCs, WBCs, and Platelets
        pattern = r"(\d+) Plateletss?, (\d+) RBCs?, (\d+) WBCs?"

# Use re.search to find the pattern in the text
        match = re.search(pattern, stderr_output)

        if match:
            platelets_count = int(match.group(1))
            rbc_count = int(match.group(2))
            wbc_count = int(match.group(3))

            return {
            "message": "Processing complete",
            "platelets_count" : platelets_count,
            "rbc_count" : rbc_count,
            "wbc_count" : wbc_count
     
        }

        else:
            return("Counts not found in the text.")

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
            os.rmdir(temp_dir)
