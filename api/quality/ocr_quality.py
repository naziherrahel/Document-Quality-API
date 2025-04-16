import cv2
import numpy as np
import os
from typing import Tuple
from PIL import Image
import pytesseract
import logging
import pytesseract

# Explicitly define the path to tesseract.exe on Windows
pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

from api.config.settings import NORMALISED_DIR

logger = logging.getLogger(__name__)

def preprocess_image(img_path: str) -> Tuple[str, np.ndarray]:
    """
    Preprocess the image by converting it to grayscale, resizing,
    denoising, applying morphological operations, and then
    binarizing via Gaussian blur and Otsu thresholding.
    
    Returns:
        A tuple containing:
        - The file path to the processed binary image.
        - The binary image (as a numpy array).
    """
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError("Unable to read image. Please check the file format and path.")
    file_name = os.path.splitext(os.path.basename(img_path))[0]
    
    # Convert to grayscale
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Resize (enlarge) to enhance text clarity
    img_gray = cv2.resize(img_gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    # Denoise the image
    img_gray = cv2.fastNlMeansDenoising(img_gray, None, 10, 7, 21)
    # Morphological operations: dilation followed by erosion
    kernel = np.ones((1, 1), np.uint8)
    img_gray = cv2.dilate(img_gray, kernel, iterations=1)
    img_gray = cv2.erode(img_gray, kernel, iterations=1)
    # Apply Gaussian Blur then perform Otsu thresholding
    img_blur = cv2.GaussianBlur(img_gray, (3, 3), 0)
    _, binary_img = cv2.threshold(img_blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Save processed image to NORMALISED_DIR
    save_path = os.path.join(str(NORMALISED_DIR), f"{file_name}_processed.jpg")
    cv2.imwrite(save_path, binary_img)
    return save_path, binary_img

def assess_binarization_quality(binary_img: np.ndarray) -> Tuple[float, float]:
    """
    Assess binarization quality by computing:
      - Global black ratio (percentage of black pixels)
      - Large black region ratio (percentage of area of large connected components)
    
    Returns:
        A tuple of (global_black_ratio, large_black_ratio).
    """
    total_pixels = binary_img.size
    black_pixels = total_pixels - cv2.countNonZero(binary_img)
    global_black_ratio = (black_pixels / total_pixels) * 100
    
    # Invert image for connected components analysis.
    inverted = cv2.bitwise_not(binary_img)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(inverted, connectivity=8)
    
    area_threshold = total_pixels * 0.01
    large_component_area = sum(
        stats[i, cv2.CC_STAT_AREA] for i in range(1, num_labels)
        if stats[i, cv2.CC_STAT_AREA] > area_threshold
    )
    large_black_ratio = (large_component_area / total_pixels) * 100
    return global_black_ratio, large_black_ratio

def calculate_ocr_quality(image_path: str, lang: str = "rus") -> Tuple[str, float, str]:
    """
    Perform OCR using Tesseract and return the extracted text, 
    average confidence, and a qualitative readability assessment.
    
    Returns:
        A tuple of (text, average_confidence, quality assessment).
    """
    try:
        img = Image.open(image_path)
    except Exception as e:
        logger.error("Error opening image for OCR", exc_info=True)
        raise e

    # Extract OCR data including per-word confidence
    data = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DICT)
    conf_list = []
    for conf in data.get("conf", []):
        try:
            conf_val = int(conf)
            if conf_val > 0:
                conf_list.append(conf_val)
        except ValueError:
            continue

    average_conf = sum(conf_list) / len(conf_list) if conf_list else 0.0
    text = pytesseract.image_to_string(img, lang=lang)
    
    if average_conf >= 80:
        quality = "Excellent readability"
    elif average_conf >= 60:
        quality = "Moderate readability"
    else:
        quality = "Poor readability"
    
    return text, average_conf, quality
