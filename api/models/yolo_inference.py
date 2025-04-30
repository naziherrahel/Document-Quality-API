import os
from uuid import uuid4

import cv2
import numpy as np
import torch
import torchvision.ops as ops
from ultralytics import YOLO
from yolo_inference import preprocess_image

# DEVICE & MODEL LOADING
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = YOLO("./model/weights/yolov8.pt").to(device)
model.fuse()  # (optional) for faster inference if supported

# PATCH torchvision.ops.nms FOR CUDA → CPU FALLBACK

_original_nms = ops.nms
def nms_with_fallback(boxes: torch.Tensor, scores: torch.Tensor, iou_threshold: float):
    try:
        return _original_nms(boxes, scores, iou_threshold)
    except NotImplementedError:
        return _original_nms(boxes.cpu(), scores.cpu(), iou_threshold).to(boxes.device)

ops.nms = nms_with_fallback



# MAIN DETECTION & CROP FUNCTION

SAVE_DIR = "api/static/cropped_docs"
os.makedirs(SAVE_DIR, exist_ok=True)

def detect_and_crop_document(image: np.ndarray, debug: bool = False) -> dict:
    """
    Run YOLO inference, correct bounding box, crop, save, and return metadata.
    """
    tensor_image, scale, pad_left, pad_top = preprocess_image(image)
    if debug:
        print(f"[DEBUG] Input tensor shape: {tensor_image.shape}, device: {tensor_image.device}")

    # Inference
    results = model(tensor_image)[0]

    # No detections?
    if results.boxes is None or len(results.boxes) == 0:
        raise ValueError("No document detected.")

    # Highest-confidence box
    best = results.boxes[0]
    x1, y1, x2, y2 = best.xyxy[0].cpu().numpy()
    conf = float(best.conf[0].cpu().item())
    cls_id = int(best.cls[0].cpu().item())
    doc_type = model.names.get(cls_id, str(cls_id))

    # Adjust box coordinates back to original image space
    x1 = (x1 - pad_left) / scale
    y1 = (y1 - pad_top) / scale
    x2 = (x2 - pad_left) / scale
    y2 = (y2 - pad_top) / scale

    h, w = image.shape[:2]
    x1, y1 = max(0, int(round(x1))), max(0, int(round(y1)))
    x2, y2 = min(w, int(round(x2))), min(h, int(round(y2)))

    if debug:
        print(f"[DEBUG] Detected '{doc_type}' with confidence {conf:.2f}")
        print(f"[DEBUG] Box on original image: ({x1}, {y1}), ({x2}, {y2})")

    # Crop original image
    cropped = image[y1:y2, x1:x2]

    # Save crop
    filename = f"{uuid4().hex}.jpg"
    save_path = os.path.join(SAVE_DIR, filename)
    cv2.imwrite(save_path, cropped)

    if debug:
        print(f"[DEBUG] Cropped image saved at: {save_path}")

    return {
        "doc_type": doc_type,
        "confidence": conf,
        "cropped_path": save_path
    }