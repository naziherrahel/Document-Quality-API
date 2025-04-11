# api/models/inference.py
import cv2
import numpy as np
from api.config.settings import MODEL_PATH, THRESHOLD
from api.models.yolo_model import YOLOv8Classifier

# Instantiate the classifier once so it can be reused across requests.
classifier = YOLOv8Classifier(MODEL_PATH)

def classify_image(image_bytes: bytes) -> dict:
    """
    Classify the document image quality using YOLOv8.

    Args:
        image_bytes: The raw bytes of the uploaded image.

    Returns:
        A dictionary with keys:
          - quality: "good" or "bad"
          - confidence: the model's confidence score for the top prediction.
    """
    # Convert the raw image bytes into a NumPy array and decode it using OpenCV.
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Invalid image provided.")

    # Run inference using the YOLOv8 classifier.
    results = classifier.classify(image)

    # For demonstration purposes, assume the first result contains the predictions.
    pred = results[0]  # assuming a single result

    # Extract the confidence score for the top-1 prediction using the Probs object's attribute.
    if hasattr(pred, 'probs'):
        # Access the top1 confidence from the probs attribute.
        try:
            confidence_tensor = pred.probs.top1conf
            # If it's a torch.Tensor, convert it to a Python float.
            if hasattr(confidence_tensor, 'cpu'):
                confidence = confidence_tensor.cpu().item()
            else:
                confidence = float(confidence_tensor)
        except Exception as e:
            # Log error if needed and set default confidence.
            confidence = 0.0
    else:
        confidence = 0.0

    quality = "good" if confidence >= THRESHOLD else "bad"

    return {"quality": quality, "confidence": confidence}
