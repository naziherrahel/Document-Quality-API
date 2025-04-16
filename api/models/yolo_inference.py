import os
import cv2
from api.models.utils import get_yolo_model  
from typing import Dict

def detect_and_crop_document(image_path: str, debug: bool = False) -> Dict:
    model = get_yolo_model()  # Singleton access

    results = model(image_path)[0]

    if not results.boxes:
        raise ValueError("No document detected.")

    # Get the first bounding box
    box = results.boxes[0]
    cls_id = int(box.cls[0])
    doc_type = model.names[cls_id]
    confidence = float(box.conf[0])

    # Extract bounding box coordinates
    x1, y1, x2, y2 = map(int, box.xyxy[0])

    # Read the image and crop the region
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Failed to load image at: {image_path}")

    cropped = img[y1:y2, x1:x2]

    # Save the cropped image
    cropped_path = image_path.replace(".jpg", "_cropped.jpg").replace(".png", "_cropped.png")
    cv2.imwrite(cropped_path, cropped)

    if debug:
        debug_img = img.copy()
        cv2.rectangle(debug_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(debug_img, f"{doc_type} {confidence:.2f}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        debug_image_path = image_path.replace(".jpg", "_debug.jpg").replace(".png", "_debug.png")
        cv2.imwrite(debug_image_path, debug_img)
        print(f"[DEBUG] Debug image saved to: {debug_image_path}")

    return {
        "cropped_path": cropped_path,
        "doc_type": doc_type,
        "confidence": confidence
    }
