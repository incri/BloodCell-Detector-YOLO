import os
import cv2

def create_labels(image_folder, label_folder):
    # Create the label folder if it doesn't exist
    if not os.path.exists(label_folder):
        os.makedirs(label_folder)

    # Loop through all files in the image folder
    for image_name in os.listdir(image_folder):
        if image_name.endswith('.png'):
            image_path = os.path.join(image_folder, image_name)
            print(f"Processing image: {image_path}")
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                h, w = img.shape

                # Assuming the entire image is the bounding box
                x_center = 0.5
                y_center = 0.5
                width = 1.0
                height = 1.0

                # Create the label content
                label_content = f"8 {x_center} {y_center} {width} {height}\n"

                # Save the label to a file with the same name as the image
                label_path = os.path.join(label_folder, image_name.replace('.png', '.txt'))
                with open(label_path, 'w') as f:
                    f.write(label_content)
                print(f"Label created for {image_name} at {label_path}")
            else:
                print(f"Failed to read image: {image_path}")

# Define the paths
image_folder = r'C:\Users\Incri\projects\BCD\BloodCell-Detector-Yolo\Dataset_YOLO\rfdz6wfzn4-1\9_acantocyte_354'
label_folder = os.path.join(image_folder, 'labels')

# Create labels
create_labels(image_folder, label_folder)
