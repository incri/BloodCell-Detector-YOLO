from PIL import Image, ImageDraw

def draw_labels_on_image(image_path, label_path, output_path, bbox_size=(50, 50)):
    """
    Draws bounding boxes on the image based on the label file and saves the image.
    
    Args:
        image_path (str): Path to the input image.
        label_path (str): Path to the label file containing coordinates.
        output_path (str): Path to save the output image.
        bbox_size (tuple): Size of the bounding box to draw (width, height).
    """
    # Load the image
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    
    # Load the labels
    with open(label_path, 'r') as file:
        labels = file.readlines()

    # Extract bounding box size
    bbox_width, bbox_height = bbox_size

    # Iterate through labels and draw bounding boxes
    for label in labels:
        # Parse the coordinates
        try:
            x_center, y_center = map(int, label.strip().split())
        except ValueError:
            print(f"Skipping invalid label: {label.strip()}")
            continue

        # Convert center coordinates to bounding box coordinates
        img_width, img_height = image.size
        x1 = int(x_center - bbox_width / 2)
        y1 = int(y_center - bbox_height / 2)
        x2 = int(x_center + bbox_width / 2)
        y2 = int(y_center + bbox_height / 2)

        # Draw the rectangle
        draw.rectangle([x1, y1, x2, y2], outline='red', width=3)

    # Save the output image
    image.save(output_path)
    print(f"Image saved to {output_path}")

# Example usage
if __name__ == "__main__":
    # Replace these paths with your own
    image_path = r'RBC-12-Dataset\Dataset\1.jpg'
    label_path = r'RBC-12-Dataset\Label\1.txt'
    output_path = r'output_image.jpg'
    
    # You can adjust bbox_size to your needs
    draw_labels_on_image(image_path, label_path, output_path, bbox_size=(50, 50))
