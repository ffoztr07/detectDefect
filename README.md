# Apple Detection and Classification System

This project implements a web-based system for detecting and classifying apples using YOLOv8. The system can detect apples in images and classify them as either healthy or defective.

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
git clone <repository-url>
cd apple-detection
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Download the required YOLO models:
- YOLOv8x model for detection (`yolov8x.pt`)
- Custom trained model for classification (`best.pt`)

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
2. Custom trained model (`best.pt`) for apple classification

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Add your license information here]

## Contact

[Add your contact information here] 