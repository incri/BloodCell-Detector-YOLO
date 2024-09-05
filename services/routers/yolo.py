from fastapi import APIRouter, HTTPException, Form
import subprocess
import requests
import os
import tempfile
import re
import uuid
import shutil

router = APIRouter()

# Define the directory to save YOLOv5 detection results



@router.post("/process-images/")
async def process_images_endpoint(
    image_urls: str = Form(...)
    
):
    try:
        # Convert image_urls from comma-separated string to list
        image_urls = image_urls.split(',')
        result_dir = os.getenv("RESULT_DIR")
        env_activate = os.getenv("ENV_ACTIVATE")
        processed_image_base_url = os.getenv("PROCESSED_IMAGE_PATH")


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
        python_executable = env_activate

        # Prepare the command to call YOLOv5 detection script
        yolo_command = [
            python_executable, "yolov5/detect.py",
            "--weights", "yolov5/runs/train/blood_cell_count_model/weights/best.pt",
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
            raise Exception(f"YOLOv5 process error: {error_message}")

        # Log stdout and stderr for debugging (optional)
        stdout_output = stdout.decode("utf-8").strip()
        stderr_output = stderr.decode("utf-8").strip()


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


        # Collect processed image paths and rename them with UUIDs
        processed_image_paths = []
        for file_name in os.listdir(temp_dir):
            if file_name.endswith(".jpg") or file_name.endswith(".png"):
                new_file_name = f"{uuid.uuid4().hex}{os.path.splitext(file_name)[1]}"
                new_file_path = os.path.join(result_dir, new_file_name)
                shutil.move(os.path.join(temp_dir, file_name), new_file_path)
                processed_image_paths.append(f"{processed_image_base_url}{new_file_name}")

        return {
            "message": "Processing complete",
            "detected":{

            "platelets_count": total_platelets,
            "rbc_count": total_rbcs,
            "wbc_count": total_wbcs,

            },
            
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


@router.post("/process-blood-types-images/")
async def process_images_endpoint(
    image_urls: str = Form(...)
):
    try:
        # Convert image_urls from comma-separated string to list
        image_urls = image_urls.split(',')
        result_dir = os.getenv("RESULT_DIR")
        env_activate = os.getenv("ENV_ACTIVATE")
        processed_image_base_url = os.getenv("PROCESSED_IMAGE_PATH")


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
        python_executable = env_activate

        # Prepare the command to call YOLOv5 detection script
        yolo_command = [
            python_executable, "yolov5/detect.py",
            "--weights", "yolov5/runs/train/blood_cell_types_model/weights/best.pt",
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
            raise Exception(f"YOLOv5 process error: {error_message}")

        # Log stdout and stderr for debugging (optional)
        stdout_output = stdout.decode("utf-8").strip()
        stderr_output = stderr.decode("utf-8").strip()


        # Initialize counters
        total_normal_cell = 0
        total_macrocyte = 0
        total_microcyte = 0
        total_spherocyte = 0
        total_target_cell = 0
        total_stomatocyte = 0
        total_ovalocyte = 0
        total_teardrop = 0
        total_burr_cell = 0
        total_schistocyte = 0
        total_uncategorised = 0
        total_hypochromia = 0
        total_elliptocyte = 0
        total_pencil = 0
        total_spero_bulat = 0
        total_acantocyte = 0

        # Regular expression patterns to extract counts
        pattern_normal_cell = r"(\d+) Normal cell"
        pattern_macrocyte = r"(\d+) Macrocyte"
        pattern_microcyte = r"(\d+) Microcyte"
        pattern_spherocyte = r"(\d+) Spherocyte"
        pattern_target_cell = r"(\d+) Target cell"
        pattern_stomatocyte = r"(\d+) Stomatocyte"
        pattern_ovalocyte = r"(\d+) Ovalocyte"
        pattern_teardrop = r"(\d+) Teardrop"
        pattern_burr_cell = r"(\d+) Burr cell"
        pattern_schistocyte = r"(\d+) Schistocyte"
        pattern_uncategorised = r"(\d+) Uncategorised"
        pattern_hypochromia = r"(\d+) Hypochromia"
        pattern_elliptocyte = r"(\d+) Elliptocyte"
        pattern_pencil = r"(\d+) pencil"
        pattern_spero_bulat = r"(\d+) SPERO bulat"
        pattern_acantocyte = r"(\d+) acantocyte"


        # Search for matches in the output text
        matches_normal_cell = re.findall(pattern_normal_cell, stderr_output)
        matches_macrocyte = re.findall(pattern_macrocyte, stderr_output)
        matches_microcyte = re.findall(pattern_microcyte, stderr_output)
        matches_spherocyte = re.findall(pattern_spherocyte, stderr_output)
        matches_target_cell = re.findall(pattern_target_cell, stderr_output)
        matches_stomatocyte = re.findall(pattern_stomatocyte, stderr_output)
        matches_ovalocyte = re.findall(pattern_ovalocyte, stderr_output)
        matches_teardrop = re.findall(pattern_teardrop, stderr_output)
        matches_burr_cell = re.findall(pattern_burr_cell, stderr_output)
        matches_schistocyte = re.findall(pattern_schistocyte, stderr_output)
        matches_uncategorised = re.findall(pattern_uncategorised, stderr_output)
        matches_hypochromia = re.findall(pattern_hypochromia, stderr_output)
        matches_elliptocyte = re.findall(pattern_elliptocyte, stderr_output)
        matches_pencil = re.findall(pattern_pencil, stderr_output)
        matches_spero_bulat = re.findall(pattern_spero_bulat, stderr_output)
        matches_acantocyte = re.findall(pattern_acantocyte, stderr_output)


        # Sum up the counts
        total_normal_cell += sum(int(count) for count in matches_normal_cell)
        total_macrocyte += sum(int(count) for count in matches_macrocyte)
        total_microcyte += sum(int(count) for count in matches_microcyte)
        total_spherocyte += sum(int(count) for count in matches_spherocyte)
        total_target_cell += sum(int(count) for count in matches_target_cell)
        total_stomatocyte += sum(int(count) for count in matches_stomatocyte)
        total_ovalocyte += sum(int(count) for count in matches_ovalocyte)
        total_teardrop += sum(int(count) for count in matches_teardrop)
        total_burr_cell += sum(int(count) for count in matches_burr_cell)
        total_schistocyte += sum(int(count) for count in matches_schistocyte)
        total_uncategorised += sum(int(count) for count in matches_uncategorised)
        total_hypochromia += sum(int(count) for count in matches_hypochromia)
        total_elliptocyte += sum(int(count) for count in matches_elliptocyte)
        total_pencil += sum(int(count) for count in matches_pencil)
        total_spero_bulat += sum(int(count) for count in matches_spero_bulat)
        total_acantocyte += sum(int(count) for count in matches_acantocyte)



        # Collect processed image paths and rename them with UUIDs
        processed_image_paths = []
        for file_name in os.listdir(temp_dir):
            if file_name.endswith(".jpg") or file_name.endswith(".png"):
                new_file_name = f"{uuid.uuid4().hex}{os.path.splitext(file_name)[1]}"
                new_file_path = os.path.join(result_dir, new_file_name)
                shutil.move(os.path.join(temp_dir, file_name), new_file_path)
                processed_image_paths.append(f"{processed_image_base_url}{new_file_name}")

        return {
            "message": "Processing complete",
            "detected" : {

            "normal_cell_count": total_normal_cell,
            "macrocyte_count": total_macrocyte,
            "microcyte_count": total_microcyte,
            "spherocyte_count": total_spherocyte,
            "target_cell_count": total_target_cell,
            "stomatocyte_count": total_stomatocyte,
            "ovalocyte_count": total_ovalocyte,
            "teardrop_count": total_teardrop,
            "burr_cell_count": total_burr_cell,
            "schistocyte_count": total_schistocyte,
            "uncategorised_count": total_uncategorised,
            "hypochromia_count": total_hypochromia,
            "elliptocyte_count": total_elliptocyte,
            "pencil_count": total_pencil,
            "spero_bulat_count": total_spero_bulat,
            "acantocyte_count": total_acantocyte,

            },
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
