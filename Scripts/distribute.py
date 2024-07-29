import os
import shutil
import random

def distribute_files(source_folder, labels_folder, dest_folder, ratios):
    """
    Distribute images and corresponding labels into train, test, and valid directories.

    Parameters:
    - source_folder (str): Path to the source folder containing images.
    - labels_folder (str): Path to the folder containing YOLOv5 labels.
    - dest_folder (str): Path to the destination folder where train, test, and valid folders will be created.
    - ratios (tuple): Ratios for train, test, and valid datasets, e.g., (0.7, 0.2, 0.1).
    """
    assert sum(ratios) == 1, "Ratios must sum to 1"

    # Create destination folders
    for split in ['train', 'test', 'valid']:
        os.makedirs(os.path.join(dest_folder, split, 'images'), exist_ok=True)
        os.makedirs(os.path.join(dest_folder, split, 'labels'), exist_ok=True)

    # Get list of all image files
    all_images = [f for f in os.listdir(source_folder) if f.endswith(('.jpg', '.png'))]
    all_images.sort()

    # Shuffle and split files
    random.shuffle(all_images)
    total_images = len(all_images)
    train_end = int(total_images * ratios[0])
    test_end = train_end + int(total_images * ratios[1])

    train_images = all_images[:train_end]
    test_images = all_images[train_end:test_end]
    valid_images = all_images[test_end:]

    def copy_files(file_list, split_folder):
        images_folder = os.path.join(dest_folder, split_folder, 'images')
        labels_folder_dest = os.path.join(dest_folder, split_folder, 'labels')

        for file_name in file_list:
            # Copy image file
            img_src = os.path.join(source_folder, file_name)
            img_dst = os.path.join(images_folder, file_name)
            shutil.copy(img_src, img_dst)
            print(f"Copied image: {img_src} to {img_dst}")

            # Copy corresponding label file
            label_file = file_name.rsplit('.', 1)[0] + '.txt'
            label_src = os.path.join(labels_folder, label_file)
            label_dst = os.path.join(labels_folder_dest, label_file)
            if os.path.exists(label_src):
                shutil.copy(label_src, label_dst)
                print(f"Copied label: {label_src} to {label_dst}")
            else:
                print(f"Label file not found: {label_src}")

    # Copy files to respective folders
    copy_files(train_images, 'train')
    copy_files(test_images, 'test')
    copy_files(valid_images, 'valid')

# Define your parameters
source_folder = r'C:\Users\Incri\projects\BCD\BloodCell-Detector-Yolo\Dataset_YOLO\Blood_Cell_Type_Dataset\images'
labels_folder = r'C:\Users\Incri\projects\BCD\BloodCell-Detector-Yolo\Dataset_YOLO\Blood_Cell_Type_Dataset\labels'
dest_folder = r'C:\Users\Incri\projects\BCD\BloodCell-Detector-Yolo\Dataset_YOLO\Blood_Cell_Type_Dataset'
ratios = (0.7, 0.2, 0.1)  # 70% train, 20% test, 10% valid

distribute_files(source_folder, labels_folder, dest_folder, ratios)
