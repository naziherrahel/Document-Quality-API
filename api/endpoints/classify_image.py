import asyncio
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from api.models.inference import classify_image
import logging

router = APIRouter()

@router.post("/classify", summary="Classify document image quality")
async def classify_document(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    timestamp: str = Form(...)
):
    try:
        contents = await file.read()
        logging.info(f"Received image with size: {len(contents)} bytes")
        
        # Run the blocking classification in a separate thread
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, classify_image, contents)

        result.update({
            "user_id": user_id,
            "timestamp": timestamp
        })
        return result

    except Exception as e:
        logging.error(f"Error during image classification: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image classification failed: {str(e)}")
