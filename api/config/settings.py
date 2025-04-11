# Application setting ( model path, 1C integration)


import os
from pathlib import Path

# Use environment variables for production flexibility
TESSERACT_CMD = os.getenv("TESSERACT_CMD", r"C:/Program Files/Tesseract-OCR/tesseract.exe")
BASE_DIR = Path(__file__).resolve().parent.parent
# Path to the YOLOv8 classification model weights
MODEL_PATH = os.getenv("MODEL_PATH", "model/weights/yolov8m.pt")

# Directories for file storage
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
NORMALISED_DIR = os.path.join(BASE_DIR, "normalised")

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(NORMALISED_DIR, exist_ok=True)
# 1C integration settings (example)
ONE_C_API_URL = os.getenv("ONE_C_API_URL", "http://localhost:8001/1c")
