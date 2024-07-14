import subprocess
import os

def run_yolo_detection(image_path: str, output_dir: str, weights: str, img_size: int = 640):
    yolo_dir = "yolov5"  # Update this to your YOLOv5 directory
    detect_script = os.path.join(yolo_dir, "detect.py")

    python_executable = "C:\\Users\\Incri\\projects\\env\\BCD_YOLO_env\\Scripts\\python.exe"

    command = [
         python_executable,
        "python", detect_script,
        "--source", image_path,
        "--weights", weights,
        "--img-size", str(img_size),
        "--save-txt",
        "--save-conf",
        "--project", output_dir,
        "--exist-ok"
    ]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running YOLOv5 detect.py: {e}")
        return None
