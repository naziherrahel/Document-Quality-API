import cv2
import torch
import numpy as np 

# DEVICE 
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# PREPROCESSING FUNCTION

def preprocess_image(image: np.ndarray, target_size: int = 640):
    """
    Resize + pad image while keeping track of scaling and padding,
    so we can map predictions back to original image coordinates.
    """
    h, w = image.shape[:2]
    scale = target_size / max(h, w)
    new_w, new_h = int(w * scale), int(h * scale)

    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    pad_vert = target_size - new_h
    pad_horiz = target_size - new_w
    top, bottom = pad_vert // 2, pad_vert - pad_vert // 2
    left, right = pad_horiz // 2, pad_horiz - pad_horiz // 2

    padded = cv2.copyMakeBorder(resized, top, bottom, left, right,
                                borderType=cv2.BORDER_CONSTANT, value=(114, 114, 114))

    tensor = torch.from_numpy(padded).permute(2, 0, 1).float().div(255.0).unsqueeze(0)
    return tensor.to(device), scale, left, top