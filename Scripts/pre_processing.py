import cv2
import numpy as np
import os

def preprocess_image(image_path):
    # Read the image
    image = cv2.imread(image_path)
    
    # Resize the image to a smaller size if feasible
    resized_image = cv2.resize(image, (400, 300))  # Example smaller size
    
    # Extract the green channel
    green_channel = resized_image[:, :, 1]
    
    # Apply median filtering
    median_filtered = cv2.medianBlur(green_channel, 5)
    
    # Apply Canny edge detection
    edges = cv2.Canny(median_filtered, 10, 50)
    
    # Dilate the edges with a smaller kernel
    kernel = np.ones((2, 2), np.uint8)  # Smaller kernel
    dilated = cv2.dilate(edges, kernel, iterations=1)
    
    # Watershed transform to separate overlapping cells
    dist_transform = cv2.distanceTransform(dilated, cv2.DIST_L2, 5)
    _, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(dilated, sure_fg)
    _, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0
    markers = cv2.watershed(cv2.merge([green_channel, green_channel, green_channel]), markers)
    dilated[markers == -1] = 0
    
    # Erosion with a smaller kernel
    eroded = cv2.erode(dilated, kernel, iterations=1)
    
    # Apply the mask to the original grayscale image
    masked_image = cv2.bitwise_and(green_channel, green_channel, mask=eroded)
    
    return masked_image

def process_folder(input_folder, output_folder):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Process each image in the input folder
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):  # Process only image files
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            
            # Preprocess the image
            processed_image = preprocess_image(input_path)
            
            # Save the processed image
            cv2.imwrite(output_path, processed_image)
            print(f"Processed and saved: {output_path}")

# Example usage
input_folder = r'C:\Users\Incri\projects\BCD\BloodCell-Detector-Yolo\Dataset_YOLO\Chula-RBC-12-Dataset\Dataset'
output_folder = r'C:\Users\Incri\projects\BCD\BloodCell-Detector-Yolo\Dataset_YOLO\Chula-RBC-12-Dataset\preprocessed'
process_folder(input_folder, output_folder)
