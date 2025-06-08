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
        return JSONResponse(
            content={"message": "Apple image saved successfully", "filename": filename},
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

# Run the FastAPI app with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
