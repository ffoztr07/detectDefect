# Apple Detection and Classification System

This project implements a web-based system for detecting and classifying apples using YOLOv8. The system can detect apples in images and classify them as either healthy or defective.

Visit our live demo site to test the apple detection and classification system in real-time. Upload your apple images and get instant results for defect detection and classification.

🌐 **Live Demo**: [http://45.147.47.83:8000/](http://45.147.47.83:8000/)

## Features

- Real-time apple detection using YOLOv8
- Apple classification (Healthy/Defective)
- Web interface for image upload and processing
- Automatic saving of detected apples
- RESTful API endpoints for integration

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/InterFaze0/detectDefect.git
cd apple-detection
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Download the required YOLO models:
- YOLOv8x model for detection (`yolov8x.pt`)
- Custom trained model for classification (`best.pt`)

## Dataset and Model Training

The system uses a custom-trained model that was fine-tuned on a curated dataset of 2,002 apple images selected from multiple sources:

1. Apple Type Dataset (ennur/apple-type)
   - Original dataset contains 1,187 images
   - Classification dataset for fresh and rotten apples
   - Source: [https://universe.roboflow.com/ennur/apple-type](https://universe.roboflow.com/ennur/apple-type)

2. Apple Defect Dataset (apple-defect/appledetectionv1.0)
   - Original dataset contains 1,585 images
   - Object detection dataset for apple defects
   - Source: [https://universe.roboflow.com/apple-defect/appledetectionv1.0-kzzoi](https://universe.roboflow.com/apple-defect/appledetectionv1.0-kzzoi)

3. Apple Detection Dataset (phamhuyhoangs-project/apple-detection)
   - Original dataset contains 2,057 images
   - Comprehensive object detection dataset
   - Source: [https://universe.roboflow.com/phamhuyhoangs-project/apple-detection-8rtsu/dataset/1](https://universe.roboflow.com/phamhuyhoangs-project/apple-detection-8rtsu/dataset/1)

The model was trained by:
1. Selecting and labeling 2,002 apple images from these datasets
2. Fine-tuning YOLOv8n.pt on the combined dataset
3. Generating the final model (`best.pt`)

## Project Structure

```
.
├── main.py              # FastAPI application
├── templates/           # HTML templates
│   └── index.html      # Main web interface
├── static/             # Static files (CSS, JS)
├── saved_apples/       # Directory for saved apple images
└── requirements.txt    # Project dependencies
```

## Usage

1. Start the server:
```bash
python main.py
```

2. Open your web browser and navigate to:
```
http://localhost:8000
```

3. Use the web interface to:
   - Upload images for apple detection
   - View detection results
   - Save detected apples
   - Get classification results

## API Endpoints

- `GET /`: Web interface
- `POST /detect`: Detect apples in an uploaded image
- `POST /save_apple`: Save and classify a cropped apple image

## Model Information

The system uses two YOLO models:
1. YOLOv8x (`yolov8x.pt`) for apple detection
2. Custom-trained model (best.pt) for apple classification, fine-tuned from YOLOv8n on a dataset of 2,002 apple images.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Contact

ffoztrk08@gmail.com 
