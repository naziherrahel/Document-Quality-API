import os
import uuid
import logging
from fastapi import UploadFile

logger = logging.getLogger(__name__)

def generate_unique_filename(original_filename: str) -> str:
    """
    Generate a unique filename using UUID and the original basename.
    """
    safe_filename = os.path.basename(original_filename)
    return f"{uuid.uuid4().hex}_{safe_filename}"

async def save_upload_file(file: UploadFile, destination: str) -> str:
    """
    Save an uploaded file to the destination path.
    """
    with open(destination, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    return destination
