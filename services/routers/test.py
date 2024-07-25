from fastapi import APIRouter, HTTPException, Form
import subprocess
import requests
import os
import tempfile
import re
import uuid
import shutil
import cv2

router = APIRouter()

# Define directories
results_dir = "C:\\Users\\Incri\\projects\\BCD\\BloodCell-Detector-Backend\\media\\lab\\result-images"
cropped_rbc_dir = "C:\\Users\\Incri\\projects\\BCD\\BloodCell-Detector-Backend\\media\\lab\\cropped_rbc_images"

# Ensure the directory for saving cropped RBC images exists
os.makedirs(cropped_rbc_dir, exist_ok=True)

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
            "--weights", "yolov5/runs/train/blood_cell_count_model/weights/best.pt",
            "--img", "640",
            "--conf", "0.25",
            "--source", temp_dir,  # Pass local file paths as the source
            "--project", temp_dir,  # Use a temp directory for initial results
            "--name", "results",  # Use a fixed name for results subdirectory
            "--exist-ok",
            "--save-txt" # Allow existing project/name
        ]

        # Log the YOLOv5 command for debugging
        print("Running YOLOv5 command:", ' '.join(yolo_command))

        # Start subprocess to execute YOLOv5 detection
        process = subprocess.Popen(yolo_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait for YOLOv5 process to finish and get outputs
        stdout, stderr = process.communicate()

        # Check for errors
        if process.returncode != 0:
            error_message = stderr.decode("utf-8").strip()
            raise Exception(f"YOLOv5 process error: {error_message}")

        # Log stdout and stderr for debugging
        stdout_output = stdout.decode("utf-8").strip()
        stderr_output = stderr.decode("utf-8").strip()
        print("YOLOv5 stdout:", stdout_output)
        print("YOLOv5 stderr:", stderr_output)

        # Initialize counters
        total_rbcs = 0
        total_wbcs = 0
        total_platelets = 0

        # Regular expression patterns to extract counts
        pattern_rbc = r"(\d+) RBC"
        pattern_wbc = r"(\d+) WBC"
        pattern_platelets = r"(\d+) Platelets" 

        # Search for matches in the output text
        matches_rbc = re.findall(pattern_rbc, stderr_output)
        matches_wbc = re.findall(pattern_wbc, stderr_output)
        matches_platelets = re.findall(pattern_platelets, stderr_output)

        # Sum up the counts
        total_rbcs += sum(int(count) for count in matches_rbc)
        total_wbcs += sum(int(count) for count in matches_wbc)
        total_platelets += sum(int(count) for count in matches_platelets)

        print(f"{total_rbcs} {total_wbcs}  {total_platelets}")

        # Locate the correct results directory
        results_subdir = os.path.join(temp_dir, "results")
        labels_subdir = os.path.join(results_subdir, "labels")
        images_subdir = results_subdir

        # List all files in results_subdir for debugging
        print("Files in results_subdir after YOLOv5 processing:", os.listdir(results_subdir))

        # Collect processed image paths and rename them with UUIDs
        processed_image_paths = []
        for file_name in os.listdir(images_subdir):
            if file_name.endswith(".jpg") or file_name.endswith(".png"):
                new_file_name = f"{uuid.uuid4().hex}{os.path.splitext(file_name)[1]}"
                new_file_path = os.path.join(results_dir, new_file_name)
                shutil.move(os.path.join(images_subdir, file_name), new_file_path)
                processed_image_paths.append(f"http://127.0.0.1:8000/media/lab/result-images/{new_file_name}")

        # Extract and save cropped RBC images
        for img_path in local_image_paths:
            # Load the image
            img = cv2.imread(img_path)

            # Get the base name of the image file
            img_name = os.path.basename(img_path).split('.')[0]

            # Path to the YOLOv5 results file
            results_file = os.path.join(labels_subdir, f"{img_name}.txt")

            # Debugging: Check if the results file exists
            if os.path.exists(results_file):
                print(f"Results file found: {results_file}")

                with open(results_file, 'r') as f:
                    for i, line in enumerate(f.readlines()):
                        class_id, x_center, y_center, width, height = map(float, line.strip().split())

                        if int(class_id) == 1:  # Assuming class 0 is RBC
                            x_min = int((x_center - width / 2) * img.shape[1])
                            y_min = int((y_center - height / 2) * img.shape[0])
                            x_max = int((x_center + width / 2) * img.shape[1])
                            y_max = int((y_center + height / 2) * img.shape[0])

                            print(f"Cropping coordinates for {img_name} RBC {i}: x_min={x_min}, y_min={y_min}, x_max={x_max}, y_max={y_max}")

                            # Ensure coordinates are within the image boundaries
                            x_min = max(0, x_min)
                            y_min = max(0, y_min)
                            x_max = min(img.shape[1], x_max)
                            y_max = min(img.shape[0], y_max)

                            # Crop the detected RBC from the image
                            cropped_rbc = img[y_min:y_max, x_min:x_max]

                            # Convert the cropped RBC to grayscale
                            gray_rbc = cv2.cvtColor(cropped_rbc, cv2.COLOR_BGR2GRAY)

                            # Save the cropped RBC image
                            cropped_rbc_path = os.path.join(cropped_rbc_dir, f'{img_name}_rbc_{i}.png')
                            cv2.imwrite(cropped_rbc_path, gray_rbc)

                            print(f"Saved cropped RBC: {cropped_rbc_path}")
            else:
                print(f"Results file not found: {results_file}")

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
