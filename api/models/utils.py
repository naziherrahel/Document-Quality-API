import os
import uuid
import logging
from fastapi import UploadFile
from ultralytics import YOLO
from threading import Lock
from contextlib import asynccontextmanager
from fastapi import FastAPI
from io import BytesIO

logger = logging.getLogger(__name__)

# Helper for file handling
def generate_unique_filename(original_filename: str) -> str:
    safe_filename = os.path.basename(original_filename)
    return f"{uuid.uuid4().hex}_{safe_filename}"

async def save_upload_file(file: UploadFile, destination: str) -> str:
    with open(destination, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    return destination

# Singleton YOLO loader
_model = None
_lock = Lock()
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
model_path = os.path.join(base_dir, "model", "weights", "yolov8.pt")

# Lifespan event handler for FastAPI
@asynccontextmanager
async def preload_yolo_model(app: FastAPI):
    global _model
    with _lock:
        if _model is None:
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found at: {model_path}")
            print("Loading YOLO model...")
            _model = YOLO(model_path)  # Load YOLO model here
    try:
        yield
    finally:
        # Cleanup if necessary (for example, unloading the model or other resources)
        pass

def get_yolo_model():
    if _model is None:
        raise RuntimeError("Model not loaded. Make sure to call preload_yolo_model() at startup.")
    return _model


async def save_upload_file(file: UploadFile, destination: str = None) -> BytesIO:
    # Save the uploaded file to a BytesIO object in memory
    content = await file.read()
    file_like_object = BytesIO(content)
    
    # Optionally save it to disk if required or for long-term storage
    if destination:
        with open(destination, "wb") as buffer:
            buffer.write(content)

    return file_like_object  # Returning in-memory object instead of a file path
