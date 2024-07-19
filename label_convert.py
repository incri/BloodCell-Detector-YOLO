import os
from PIL import Image, ImageDraw, ImageFont

def draw_labels_and_convert_to_yolov5(image_folder, labels_folder, output_folder, yolov5_labels_folder, bbox_size=50, font_size=20):
    # Create the output folders if they don't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    if not os.path.exists(yolov5_labels_folder):
        os.makedirs(yolov5_labels_folder)

    # Process each label file in the labels folder
    for filename in os.listdir(labels_folder):
        if filename.endswith('.txt'):
            image_path = os.path.join(image_folder, filename.replace('.txt', '.jpg'))
            labels_path = os.path.join(labels_folder, filename)
            output_image_path = os.path.join(output_folder, filename.replace('.txt', '.jpg'))
            yolov5_labels_path = os.path.join(yolov5_labels_folder, filename)
            
            # Open the image to get its dimensions
            image = Image.open(image_path)
            image_width, image_height = image.size
            draw = ImageDraw.Draw(image)
            
            # Load labels from the file
            with open(labels_path, 'r') as file:
                labels = file.readlines()
            
            # Load a font
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()
            
            new_labels = []
            yolov5_labels = []
            
            # Draw each label
            for label in labels:
                x, y, cls = map(int, label.strip().split())
                
                # Calculate bounding box coordinates
                left = x - bbox_size // 2
                top = y - bbox_size // 2
                right = x + bbox_size // 2
                bottom = y + bbox_size // 2
                
                # Calculate width and height of the bounding box
                width = right - left
                height = bottom - top
                
                # Save the new label in the format x y cls width height
                new_labels.append(f"{x} {y} {cls} {width} {height}\n")
                
                # Draw the bounding box
                draw.rectangle([left, top, right, bottom], outline="red", width=2)
                
                # Draw the class label
                text = str(cls)
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
                text_x = x - text_width // 2
                text_y = y - bbox_size // 2 - text_height
                draw.text((text_x, text_y), text, fill="red", font=font)
                
                # Convert to YOLOv5 format
                x_center = (x + width / 2) / image_width
                y_center = (y + height / 2) / image_height
                norm_width = width / image_width
                norm_height = height / image_height
                
                yolov5_label = f"{cls} {x_center:.6f} {y_center:.6f} {norm_width:.6f} {norm_height:.6f}\n"
                yolov5_labels.append(yolov5_label)
            
            # Save the annotated image
            image.save(output_image_path)
            print(f"Annotated image saved to {output_image_path}")
            
            # Write the new labels to the file
            with open(os.path.join(output_folder, filename), 'w') as file:
                file.writelines(new_labels)
            print(f"New labels saved to {os.path.join(output_folder, filename)}")
            
            # Write the YOLOv5 labels to the file
            with open(yolov5_labels_path, 'w') as file:
                file.writelines(yolov5_labels)
            print(f"YOLOv5 labels saved to {yolov5_labels_path}")

# Example usage
image_folder = r'RBC-12-Dataset/Dataset'
labels_folder = r'RBC-12-Dataset/Label'
output_folder = r'RBC-12-Dataset/Annotated'
yolov5_labels_folder = r'RBC-12-Dataset/yolov5_labels'

draw_labels_and_convert_to_yolov5(image_folder, labels_folder, output_folder, yolov5_labels_folder)
