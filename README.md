# BloodCell-Detector-Yolo

## Overview

BloodCell-Detector-Yolo is a YOLOv5 implementation tailored to detect Red Blood Cells (RBC), White Blood Cells (WBC), and Platelets from microscopic images. This project includes a self-trained model to accurately identify and count these blood cell types. The detected cells are labeled in the images, and their counts are provided as part of the output. The project also features a FastAPI server that serves as a microservice to handle image processing requests.

## Features

- **YOLOv5-based Detection**: Utilizes the YOLOv5 model for detecting RBC, WBC, and Platelets.
- **Self-trained Model**: The model is trained specifically on a custom dataset of microscopic images to ensure accurate detection.
- **Labeling and Counting**: Processes images to label detected cells and provide total counts for each cell type.
- **FastAPI Integration**: A FastAPI server wraps the YOLOv5 detection, providing an API for backend integration.
- **Microservice Architecture**: Designed to work as a microservice, making it easy to integrate with other systems.
