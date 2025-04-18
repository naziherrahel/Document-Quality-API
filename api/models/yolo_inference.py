import os
import cv2
from api.models.utils import get_yolo_model  
from typing import Dict

import cv2
import numpy as np 

def detect_and_crop_document(image: np.ndarray, debug: bool = False) -> Dict:
    model = get_yolo_model()  # Singleton access

    # YOLO expects an image array, so use it directly for detection
    results = model(image, imgsz= 640)[0]

    if not results.boxes:
        raise ValueError("No document detected.")

    # Get the first bounding box
    box = results.boxes[0]
    cls_id = int(box.cls[0])
    doc_type = model.names[cls_id]
    confidence = float(box.conf[0])

    # Extract bounding box coordinates
    x1, y1, x2, y2 = map(int, box.xyxy[0])

    # Crop the image based on the bounding box
    cropped = image[y1:y2, x1:x2]

    # Save the cropped image if needed
    cropped_path = "cropped_image.jpg"  # Temporary path; adjust based on actual usage
    cv2.imwrite(cropped_path, cropped)

    if debug:
        debug_img = image.copy()
        cv2.rectangle(debug_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(debug_img, f"{doc_type} {confidence:.2f}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        debug_image_path = "debug_image.jpg"  # Temporary path
        cv2.imwrite(debug_image_path, debug_img)
        print(f"[DEBUG] Debug image saved to: {debug_image_path}")

    return {
        "cropped_path": cropped_path,
        "doc_type": doc_type,
        "confidence": confidence
    }
