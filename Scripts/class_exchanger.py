import os
import glob

# Define the updated class remapping dictionary
class_remap = {
    0: 12,  # "Elliptocyte" -> "Elliptocyte"
    1: 13,  # "pencil" -> "pencil"
    2: 7,   # "teardrop" -> "Teardrop"
    3: 0,   # "normal" -> "Normal cell"
    4: 5,   # "stomatocyte" -> "Stomatocyte"
    5: 4,   # "TARGETSEL" -> "Target cell"
    6: 11,  # "hypochromic" -> "Hypochromia"
    7: 14,  # "SPERO bulat" -> "SPERO bulat"
    8: 15,  # "acantocyte" -> "acantocyte"
    # Map other classes as needed
}

def remap_labels(label_file, mapping):
    """
    Remap class indices in a YOLO format label file.
    """
    with open(label_file, 'r') as file:
        lines = file.readlines()

    with open(label_file, 'w') as file:
        for line in lines:
            parts = line.strip().split()
            old_class_index = int(parts[0])
            new_class_index = mapping.get(old_class_index)
            if new_class_index is not None:
                file.write(f"{new_class_index} {' '.join(parts[1:])}\n")
            else:
                print(f"Warning: Class index {old_class_index} not found in remapping dictionary.")

def process_label_files(directory, mapping):
    """
    Process all label files in the specified directory.
    """
    label_files = glob.glob(os.path.join(directory, '*.txt'))
    for label_file in label_files:
        print(f"Processing file: {label_file}")
        remap_labels(label_file, mapping)

def main():
    import argparse

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Remap class indices in YOLO format label files.")
    parser.add_argument('folder', type=str, help='Path to the folder containing label files.')
    args = parser.parse_args()

    # Ensure the folder exists
    if not os.path.isdir(args.folder):
        print(f"Error: The folder {args.folder} does not exist.")
        return

    # Process the label files in the specified folder
    process_label_files(args.folder, class_remap)
    print("Class remapping completed.")

if __name__ == '__main__':
    main()
