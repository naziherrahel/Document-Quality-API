from fastapi import FastAPI
from api.endpoints import image_upload, classify_image, quality_assessment
from api.models.utils import preload_yolo_model, get_yolo_model
from contextlib import asynccontextmanager

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)


app = FastAPI(title="Document Quality API", version="1.0")



# Initialize FastAPI with a lifespan context
app = FastAPI(lifespan=preload_yolo_model)

@app.get("/")
async def read_root():
    # Use the preloaded model for inference or other tasks
    model = get_yolo_model()
    # You can now call model detection methods or whatever is needed.
    return {"message": "Model loaded successfully!"}
# app.include_router(image_upload.router)
# app.include_router(classify_image.router)
app.include_router(quality_assessment.router)
