import cv2
import numpy as np
import os
import logging
from typing import Tuple
from paddleocr import PaddleOCR
import asyncio
from fastapi import HTTPException
from api.config.settings import NORMALISED_DIR

logger = logging.getLogger(__name__)

# Initialize PaddleOCR once with GPU enabled and Russian language
ocr = PaddleOCR(use_angle_cls=True, lang='ru', use_gpu=True)

def preprocess_image(img_input) -> Tuple[str, np.ndarray]:
    """
    Preprocess the image using GPU-accelerated OpenCV (if built with CUDA).
    Handles both file paths and in-memory images (numpy.ndarray).
    
    Returns:
        - Path to saved binary image
        - Binary image (np.ndarray)
    """
    if isinstance(img_input, np.ndarray):
        img = img_input
    elif isinstance(img_input, str):
        img = cv2.imread(img_input)
        if img is None:
            raise ValueError(f"Failed to read image from path: {img_input}")
    else:
        raise TypeError("Input should be either a numpy.ndarray or a file path (str).")

    file_name = "processed_image"

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Resize image if necessary
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # Upload to GPU if available
    try:
        gpu_mat = cv2.cuda_GpuMat()
        gpu_mat.upload(gray)

        # Denoising using Gaussian blur (CUDA)
        gpu_blur = cv2.cuda.createGaussianFilter(cv2.CV_8UC1, -1, (3, 3), 0)
        gpu_blurred = gpu_blur.apply(gpu_mat)

        blurred = gpu_blurred.download()
    except Exception as e:
        logger.warning("CUDA not available for OpenCV im_prepro, falling back to CPU preprocessing.")
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    _, binary_img = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    save_path = os.path.join(str(NORMALISED_DIR), f"{file_name}_processed.jpg")
    cv2.imwrite(save_path, binary_img)

    return save_path, binary_img

def assess_binarization_quality(binary_img: np.ndarray) -> Tuple[float, float]:
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

import time
import numpy as np
from typing import Tuple
import logging


def calculate_ocr_quality(image_path: str, lang: str = "ru", max_retries: int = 3) -> Tuple[str, float, str]:
    """
    Perform OCR using PaddleOCR with GPU support.
    Retries up to 'max_retries' times if OCR result is out of range (incomplete or mismatch).

    Args:
        - image_path: Path to the image for OCR processing
        - lang: Language for OCR (default is Russian "ru")
        - max_retries: Maximum number of retries in case of result mismatch or incomplete result

    Returns:
        - Extracted text
        - Average confidence
        - Quality label
    """
    retries = 0
    while retries < max_retries:
        try:
            # Run OCR on the image
            result = ocr.ocr(image_path, cls=True)

            # Check if the result has the expected structure
            if len(result) < 2:
                logger.error(f"OCR result is incomplete for image {image_path}. Expected 2 elements, found {len(result)}.")
                logger.error(f"OCR result: {result}")
                retries += 1
                logger.warning(f"Retrying OCR for image {image_path}... Attempt {retries}/{max_retries}")
                time.sleep(1)  # Small delay before retrying
                continue  # Retry OCR if result is incomplete

            # Extract dt_boxes (detected boxes) and rec_res (recognition results)
            dt_boxes = result[0]  # Detected boxes
            rec_res = result[1]  # Recognition results

            # Ensure that the number of detected boxes and OCR results match
            if len(dt_boxes) != len(rec_res):
                logger.error(f"Mismatch in the number of detected boxes ({len(dt_boxes)}) vs OCR results ({len(rec_res)})")
                logger.error(f"Detected Boxes: {dt_boxes}")
                logger.error(f"Recognition Results: {rec_res}")
                retries += 1
                logger.warning(f"Retrying OCR for image {image_path}... Attempt {retries}/{max_retries}")
                time.sleep(1)  # Small delay before retrying
                continue  # Retry OCR if there is a mismatch

            # Extract text and confidence from OCR results
            text_lines = []
            confidences = []

            for i in range(len(dt_boxes)):
                text, conf = rec_res[i]
                text_lines.append(text)
                confidences.append(conf)

            # Join the text lines into a single string
            text = "\n".join(text_lines)

            # Calculate the average confidence from all recognized text
            average_conf = np.mean(confidences) * 100 if confidences else 0.0

            # Determine readability quality based on average confidence
            if average_conf >= 80:
                quality = "Excellent readability"
            elif average_conf >= 60:
                quality = "Moderate readability"
            else:
                quality = "Poor readability"

            # Log the results for debugging and monitoring
            logger.info(f"OCR processing completed for {image_path} with average confidence: {average_conf:.2f}%")
            logger.info(f"Text extracted: {text[:100]}...")  # Log the first 100 characters of the text as preview

            return text, average_conf, quality

        except Exception as e:
            # If the error is not related to out-of-range result, break the loop and raise the error
            if retries >= max_retries:
                logger.error(f"Max retries reached. OCR failed for image {image_path}.")
                raise e  # Raise the exception if maximum retries are reached
            else:
                # If the exception is something else, log the error and break the loop
                logger.error(f"PaddleOCR failed on image {image_path}: {e}", exc_info=True)
                raise e

    # If all retries failed, return failure
    return "", 0.0, "OCR failed after multiple retries"


async def safe_ocr_call(image_path: str, lang: str = 'ru', max_retries=3, timeout=120) -> Tuple[str, float, str]:
    retries = 0
    while retries < max_retries:
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(calculate_ocr_quality, image_path, lang), timeout
            )
            return result
        except asyncio.TimeoutError:
            logger.warning(f"OCR processing timed out (attempt {retries + 1})")
        except Exception as e:
            logger.error(f"OCR failed with error: {e}")
            raise e

        retries += 1
        await asyncio.sleep(2)

    raise HTTPException(status_code=500, detail="OCR processing failed after multiple attempts.")