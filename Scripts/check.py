from PIL import Image, ImageDraw, ImageFont

def draw_yolov5_labels(image_path, yolov5_labels_path, output_path, font_size=20):
    # Open the image
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    
    # Get image dimensions
    image_width, image_height = image.size
    
    # Load labels from the file
    with open(yolov5_labels_path, 'r') as file:
        labels = file.readlines()
    
    # Load a font
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()
    
    # Draw each label
    for label in labels:
        cls, x_center, y_center, width, height = map(float, label.strip().split())
        
        # Convert normalized coordinates to pixel values
        x_center = x_center * image_width
        y_center = y_center * image_height
        width = width * image_width
        height = height * image_height
        
        # Calculate bounding box coordinates
        left = x_center - width / 2
        top = y_center - height / 2
        right = x_center + width / 2
        bottom = y_center + height / 2
        
        # Draw the bounding box
        draw.rectangle([left, top, right, bottom], outline="red", width=2)
        
        # Draw the class label
        text = str(int(cls))
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
        text_x = x_center - text_width / 2
        text_y = top - text_height - 5  # Adjust text position above the bounding box
        draw.text((text_x, text_y), text, fill="red", font=font)
    
    # Save the annotated image
    image.save(output_path)
    print(f"Annotated image saved to {output_path}")

# Example usage
image_path = r'RBC-9-Dataset/1Elliptocyte1211/ADB_B2_0004 objek#56.png'
yolov5_labels_path = r'RBC-9-Dataset/labels/ADB_B2_0004 objek#56.txt'
output_path = 'annotated_image.jpg'

draw_yolov5_labels(image_path, yolov5_labels_path, output_path)
