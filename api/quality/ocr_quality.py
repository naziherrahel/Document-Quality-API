# api/quality/ocr_quality.py

import cv2
import numpy as np
import os
import logging
from typing import Tuple
from paddleocr import PaddleOCR
import asyncio

from api.config.settings import NORMALISED_DIR

logger = logging.getLogger(__name__)

# Initialize PaddleOCR once with GPU enabled and Russian language
ocr = PaddleOCR(use_angle_cls=True, lang='ru', use_gpu=True)

def preprocess_image(img_path: str) -> Tuple[str, np.ndarray]:
    """
    Preprocess the image using GPU-accelerated OpenCV (if built with CUDA).

    Returns:
        - Path to saved binary image
        - Binary image (np.ndarray)
    """
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError("Failed to read image.")

    file_name = os.path.splitext(os.path.basename(img_path))[0]

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Resize
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # Upload to GPU if available
    try:
        gpu_mat = cv2.cuda_GpuMat()
        gpu_mat.upload(gray)

        # Denoising using Gaussian blur (CUDA)
        gpu_blur = cv2.cuda.createGaussianFilter(cv2.CV_8UC1, -1, (3, 3), 0)
        gpu_blurred = gpu_blur.apply(gpu_mat)

        # Thresholding using adaptive threshold (falling back to CPU if needed)
        blurred = gpu_blurred.download()
    except Exception as e:
        logger.warning("CUDA not available, falling back to CPU preprocessing.")
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    # Thresholding
    _, binary_img = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Save processed image
    save_path = os.path.join(str(NORMALISED_DIR), f"{file_name}_processed.jpg")
    cv2.imwrite(save_path, binary_img)

    return save_path, binary_img

def assess_binarization_quality(binary_img: np.ndarray) -> Tuple[float, float]:
    """
    Evaluate black pixel distribution and large black regions.

    Returns:
        - Global black pixel ratio
        - Large black region ratio
    """
    total_pixels = binary_img.size
    black_pixels = total_pixels - cv2.countNonZero(binary_img)
    global_black_ratio = (black_pixels / total_pixels) * 100

    inverted = cv2.bitwise_not(binary_img)
    num_labels, _, stats, _ = cv2.connectedComponentsWithStats(inverted, connectivity=8)

    area_threshold = total_pixels * 0.01
    large_area = sum(
        stats[i, cv2.CC_STAT_AREA]
        for i in range(1, num_labels)
        if stats[i, cv2.CC_STAT_AREA] > area_threshold
    )
    large_black_ratio = (large_area / total_pixels) * 100

    return global_black_ratio, large_black_ratio

def calculate_ocr_quality(image_path: str, lang: str = "ru") -> Tuple[str, float, str]:
    """
    Perform OCR using PaddleOCR with GPU support.

    Returns:
        - Extracted text
        - Average confidence
        - Quality label
    """
    try:
        result = ocr.ocr(image_path, cls=True)
    except Exception as e:
        logger.error("PaddleOCR failed on image", exc_info=True)
        raise e

    text_lines = []
    confidences = []

    for line in result:
        for box, (text, conf) in line:
            text_lines.append(text)
            confidences.append(conf)

    text = "\n".join(text_lines)
    average_conf = np.mean(confidences) * 100 if confidences else 0.0

    if average_conf >= 80:
        quality = "Excellent readability"
    elif average_conf >= 60:
        quality = "Moderate readability"
    else:
        quality = "Poor readability"

    return text, average_conf, quality

async def async_calculate_ocr_quality(image_path: str, lang: str = "ru") -> Tuple[str, float, str]:
    """
    Asynchronous wrapper for OCR using asyncio to avoid blocking FastAPI.
    """
    return await asyncio.to_thread(calculate_ocr_quality, image_path, lang)
