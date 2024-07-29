import os
from PIL import Image

def convert_labels_to_yolov5(labels_folder, images_folder, bbox_size=(40, 40)):
    # Process each label file in the labels folder
    for filename in os.listdir(labels_folder):
        if filename.endswith('.txt'):
            labels_path = os.path.join(labels_folder, filename)
            image_path = os.path.join(images_folder, filename.replace('.txt', '.jpg'))  # Adjust the image extension if needed

            # Open the image to get its dimensions
            try:
                with Image.open(image_path) as img:
                    image_width, image_height = img.size
            except FileNotFoundError:
                print(f"Image file {image_path} does not exist. Skipping...")
                continue

            with open(labels_path, 'r') as file:
                labels = file.readlines()

            yolov5_labels = []

            for label in labels:
                x, y, cls = map(int, label.strip().split())

                # Normalize coordinates
                x_center = x / image_width
                y_center = y / image_height
                norm_width = bbox_size[0] / image_width
                norm_height = bbox_size[1] / image_height

                yolov5_label = f"{cls} {x_center:.6f} {y_center:.6f} {norm_width:.6f} {norm_height:.6f}\n"
                yolov5_labels.append(yolov5_label)

            # Overwrite the label file with YOLOv5 format
            with open(labels_path, 'w') as file:
                file.writelines(yolov5_labels)
            print(f"Converted labels in {labels_path} to YOLOv5 format")

# Example usage
labels_folder = r'C:\Users\Incri\projects\BCD\BloodCell-Detector-Yolo\Dataset_YOLO\Chula-RBC-12-Dataset\Label'
images_folder = r'C:\Users\Incri\projects\BCD\BloodCell-Detector-Yolo\Dataset_YOLO\Chula-RBC-12-Dataset\Dataset'
bbox_size = (40, 40)  # Fixed bounding box size

convert_labels_to_yolov5(labels_folder, images_folder, bbox_size)
