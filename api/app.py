from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.endpoints import quality_assessment
from api.models.utils import preload_yolo_model, get_yolo_model

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Initialize FastAPI with a lifespan context for YOLO model
app = FastAPI(
    title="Document Quality API",
    version="1.0",
    lifespan=preload_yolo_model
)

# Mount the static directory for serving cropped images
app.mount("/static", StaticFiles(directory="api/static"), name="static")

# Root endpoint for verification
@app.get("/")
async def read_root():
    # Use the preloaded model for inference or other tasks
    model = get_yolo_model()
    return {"message": "Model loaded successfully!"}

# Include the router
app.include_router(quality_assessment.router)