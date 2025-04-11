import cv2
import numpy as np
import os
from typing import Tuple
from api.config import NORMALISED_DIR

def preprocess_image(img_path: str) -> Tuple[str, np.ndarray]:
    """
    Preprocess the image and save a binary version.
    The processing includes conversion to grayscale, resizing, denoising,
    morphological filtering, Gaussian blur and Otsu binarization.
    
    Returns:
      - The path to the processed image.
      - The binary image (as a numpy array).
    """
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError("Unable to read image. Please check the file format and path.")
    file_name = os.path.splitext(os.path.basename(img_path))[0]
    
    # Convert to grayscale
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Resize to enhance text details
    img_gray = cv2.resize(img_gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    # Denoise the image
    img_gray = cv2.fastNlMeansDenoising(img_gray, None, 10, 7, 21)
    # Morphological operations: dilation then erosion
    kernel = np.ones((1, 1), np.uint8)
    img_gray = cv2.dilate(img_gray, kernel, iterations=1)
    img_gray = cv2.erode(img_gray, kernel, iterations=1)
    # Apply Gaussian blur and Otsu binarization
    img_blur = cv2.GaussianBlur(img_gray, (3, 3), 0)
    _, binary_img = cv2.threshold(img_blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Save the processed binary image
    save_path = os.path.join(NORMALISED_DIR, f"{file_name}_processed.jpg")
    cv2.imwrite(save_path, binary_img)
    return save_path, binary_img

def assess_binarization_quality(binary_img: np.ndarray) -> Tuple[float, float]:
    """
    Assess the quality of the binarization process using:
      - Global black ratio: the percentage of black pixels.
      - The ratio of large black regions relative to the total image area.
    
    Returns:
      - Global black ratio (percentage).
      - Large black region ratio (percentage).
    """
    total_pixels = binary_img.size
    black_pixels = total_pixels - cv2.countNonZero(binary_img)
    global_black_ratio = (black_pixels / total_pixels) * 100
    
    # Invert image for connected component analysis
    inverted = cv2.bitwise_not(binary_img)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(inverted, connectivity=8)
    
    # Consider regions covering more than 1% of total area as significant
    area_threshold = total_pixels * 0.01
    large_component_area = sum(stats[i, cv2.CC_STAT_AREA]
                               for i in range(1, num_labels)
                               if stats[i, cv2.CC_STAT_AREA] > area_threshold)
    
    large_black_ratio = (large_component_area / total_pixels) * 100
    return global_black_ratio, large_black_ratio
