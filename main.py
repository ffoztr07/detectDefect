from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
from ultralytics import YOLO
import os
from datetime import datetime
import logging
import tensorflow as tf


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Create directory for saving apple images if it doesn't exist
SAVE_DIR = "saved_apples"
os.makedirs(SAVE_DIR, exist_ok=True)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount templates directory
templates = Jinja2Templates(directory="templates")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load a pre-trained YOLOv8 model
model = YOLO('yolov8x.pt')

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return templates.TemplateResponse("index.html", {"request": {}})

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    # Read the uploaded image
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Run inference
    results = model(img)
    
    # Process results
    detections = []
    for result in results:
        for box in result.boxes:
            if box.cls[0] == 47:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append({
                "class": "Apple",
                "confidence": conf,
                "box": [x1, y1, x2, y2]
                })
    
    return JSONResponse(content={"detections": detections})

@app.post("/save_apple")
async def save_apple(cropped_apple: UploadFile = File(...)):
    try:
        # Validate file type
        if not cropped_apple.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image"
            )
        
        # Read the uploaded cropped apple image
        contents = await cropped_apple.read()
        
        # Validate image can be decoded
        try:
            nparr = np.frombuffer(contents, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid image format"
                )
        except Exception as e:
            logger.error(f"Error decoding image: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail="Failed to process image"
            )
        
        # Generate unique filename using timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"apple_{timestamp}.png"
        filepath = os.path.join(SAVE_DIR, filename)
        
        # Save the image
        with open(filepath, "wb") as f:
            f.write(contents)
        
        logger.info(f"Successfully saved apple image: {filename}")
        label, confidence = predict_apple(filepath)
        
        print(label, confidence)
        return JSONResponse(
            content={"message": f"Prediction: {label}, Confidence: {confidence}"},
            status_code=200
        )
    except HTTPException as he:
        logger.error(f"HTTP error: {str(he)}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JSONResponse(
            content={"error": "An unexpected error occurred while saving the image"},
            status_code=500
        )


def predict_apple(image_path, model_path='model9148.h5'):
    """
    Predict whether an apple is healthy or defective using the trained model.
    
    Args:
        image_path (str): Path to the image file of the apple
        model_path (str): Path to the trained model file
        
    Returns:
        tuple: (prediction, confidence)
            - prediction (str): 'Healthy' or 'Defective'
            - confidence (float): Confidence score between 0 and 1
    """
    # Load the model
    model = tf.keras.models.load_model(model_path)
    
    # Load and preprocess the image
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
    img = cv2.resize(img, (224, 224))  # Resize to match model input size
    img = img / 255.0  # Normalize pixel values
    
    # Add batch dimension
    img = np.expand_dims(img, axis=0)
    
    # Make prediction
    prediction = model.predict(img)[0][0]
    
    # Convert prediction to label and confidence
    label = 'Healthy' if prediction > 0.5 else 'Defective'
    confidence = prediction if prediction > 0.5 else 1 - prediction
    
    return label, confidence

# Run the FastAPI app with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
