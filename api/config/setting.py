# Application setting ( model path, 1C integration)


import os

# Path to the YOLOv8 classification model weights
MODEL_PATH = os.getenv("MODEL_PATH", "model/weights/yolov8m-cls.pt")

# Confidence threshold for classifying an image as "good"
THRESHOLD = float(os.getenv("THRESHOLD", 0.8))

# 1C integration settings (example)
ONE_C_API_URL = os.getenv("ONE_C_API_URL", "http://localhost:8001/1c")
