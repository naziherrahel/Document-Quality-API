# well this code does gave me as an output text regions after binarization 
# and when the image is with bad quality, its kinda creates a big black region 
# where the text is also black the white background and the noise is also black


import io
import logging
import os

import cv2
import numpy as np
import pytesseract
import torch
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
from huggingface_hub import hf_hub_download

# Import the DocLayout-YOLO model.
from doclayout_yolo import YOLOv10

# Configure logging at DEBUG level.
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("DocLayout-YOLO-API")

# Initialize FastAPI app with CORS.
app = FastAPI()
origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory to save debug images.
DEBUG_IMAGE_DIR = "debug_images"
os.makedirs(DEBUG_IMAGE_DIR, exist_ok=True)

# Minimum dimension (in pixels) for OCR processing.
MIN_WIDTH = 50
MIN_HEIGHT = 50
# Upscale factor for small regions.
UPSCALE_FACTOR = 2.0

def load_model() -> YOLOv10:
    """
    Load the DocLayout-YOLO model.
    First try loading using from_pretrained. If that fails,
    download the checkpoint from Hugging Face Hub.
    """
    try:
        logger.info("Attempting to load model using from_pretrained...")
        model = YOLOv10.from_pretrained("juliozhao/DocLayout-YOLO-DocStructBench")
        logger.info("Model loaded successfully from from_pretrained.")
    except Exception as e:
        logger.error(f"from_pretrained failed: {e}. Trying manual download...")
        try:
            checkpoint_path = hf_hub_download(
                repo_id="juliozhao/DocLayout-YOLO-DocStructBench",
                filename="doclayout_yolo_docstructbench_imgsz1024.pt"
            )
            logger.info(f"Checkpoint downloaded to {checkpoint_path}")
            model = YOLOv10(checkpoint_path)
        except Exception as download_e:
            logger.error(f"Failed to load model after download: {download_e}")
            raise RuntimeError("Error loading DocLayout-YOLO model") from download_e
    return model

# Load the model on startup.
try:
    model = load_model()
except RuntimeError as load_error:
    logger.critical("Failed to load DocLayout-YOLO model. Exiting.", exc_info=load_error)
    raise load_error

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Accepts an image file, performs layout detection with DocLayout-YOLO,
    and processes each detected region for OCR (using Russian language).
    
    To improve OCR:
      - We run OCR on every detected region (whether it is labeled plain text, title, or figure).
      - If the detected crop is very small (width or height below MIN_WIDTH or MIN_HEIGHT),
        we upscale it before performing OCR.
      
    Debug images for each crop are saved.
    Returns a JSON with bounding boxes and the extracted text.
    """
    try:
        contents = await file.read()
        image_pil = Image.open(io.BytesIO(contents)).convert("RGB")
        image = np.array(image_pil)
        logger.debug("Image successfully read. Image shape: %s", image.shape)
    except Exception as e:
        logger.error("Failed to process uploaded image.", exc_info=e)
        raise HTTPException(status_code=400, detail="Invalid image file") from e

    try:
        det_results = model.predict(image, imgsz=1024, conf=0.2, device="cpu")
        prediction = det_results[0]
        logger.info("Layout detection completed. Found %d bounding boxes.", len(prediction.boxes))
    except Exception as e:
        logger.error("Layout detection failed.", exc_info=e)
        raise HTTPException(status_code=500, detail="Error during layout detection") from e

    detections = []

    # Loop over every detected bounding box.
    for idx, box in enumerate(prediction.boxes):
        logger.debug("Processing bounding box #%d", idx)
        try:
            coords_array = box.xyxy.cpu().numpy()
            logger.debug("Bounding box tensor shape: %s, value: %s", coords_array.shape, coords_array)
            coords = coords_array.flatten()
            logger.debug("Flattened coordinates: %s", coords)
        except Exception as conv_e:
            logger.exception("Failed to convert bounding box tensor: %s", conv_e)
            continue

        if len(coords) != 4:
            logger.error("Invalid bounding box format (expected 4 values, got %s): %s", len(coords), coords)
            continue

        try:
            x1, y1, x2, y2 = map(int, coords)
            logger.debug("Converted bounding box coordinates: x1=%d, y1=%d, x2=%d, y2=%d", x1, y1, x2, y2)
        except Exception as conv_int_e:
            logger.exception("Error converting coordinates to integers: %s", conv_int_e)
            continue

        # Clamp coordinates to the image boundaries.
        x1, y1 = max(x1, 0), max(y1, 0)
        x2, y2 = min(x2, image.shape[1]), min(y2, image.shape[0])
        logger.debug("Clamped coordinates: x1=%d, y1=%d, x2=%d, y2=%d", x1, y1, x2, y2)

        if x2 <= x1 or y2 <= y1:
            logger.error("Invalid crop region: x1=%d, y1=%d, x2=%d, y2=%d", x1, y1, x2, y2)
            detections.append({"box": [x1, y1, x2, y2], "text": ""})
            continue

        cropped = image[y1:y2, x1:x2]
        logger.debug("Initial cropped region shape for box #%d: %s", idx, cropped.shape)
        
        # If the region is very small, upscale it.
        crop_h, crop_w = cropped.shape[:2]
        if crop_w < MIN_WIDTH or crop_h < MIN_HEIGHT:
            new_w = int(crop_w * UPSCALE_FACTOR)
            new_h = int(crop_h * UPSCALE_FACTOR)
            logger.debug("Upscaling small region from (%d, %d) to (%d, %d)",
                         crop_w, crop_h, new_w, new_h)
            cropped = cv2.resize(cropped, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
            logger.debug("Upscaled cropped region shape: %s", cropped.shape)
        
        # Preprocess the cropped region for OCR.
        try:
            gray = cv2.cvtColor(cropped, cv2.COLOR_RGB2GRAY)
            logger.debug("Converted to grayscale. Mean: %.2f, Std: %.2f", gray.mean(), gray.std())
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            logger.debug("Applied OTSU thresholding.")
        except Exception as prep_e:
            logger.exception("Error during image pre-processing: %s", prep_e)
            continue

        # Save the pre-processed image for debugging.
        debug_path = os.path.join(DEBUG_IMAGE_DIR, f"debug_bbox_{idx}.png")
        cv2.imwrite(debug_path, thresh)
        logger.debug("Saved debug image to %s", debug_path)

        try:
            # Perform OCR with Tesseract using the Russian language.
            ocr_text = pytesseract.image_to_string(thresh, lang="rus")
            logger.debug("OCR result for box #%d (length %d): %s", idx, len(ocr_text), ocr_text.strip())
        except Exception as ocr_e:
            logger.exception("Error during OCR on cropped region: %s", ocr_e)
            ocr_text = ""
        
        detections.append({
            "box": [x1, y1, x2, y2],
            "text": ocr_text.strip()
        })

    return JSONResponse(content={"detections": detections})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
