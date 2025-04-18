from typing import Tuple

def calculate_global_score(ocr_conf: float, global_black_ratio: float, large_black_ratio: float,
                           alpha: float = 1.0, beta: float = 0.5, gamma: float = 1.0) -> Tuple[float, str]:
    """
    Calculate a global quality score by combining OCR confidence and 
    binarization quality metrics.
    
    The formula used is:
    
        Global Score = (alpha * OCR_confidence) - (beta * global_black_ratio) - (gamma * large_black_ratio)
    
    Returns:
        A tuple of (global_score, quality_category)
        with quality_category based on defined thresholds.
    """
    score = alpha * ocr_conf - beta * global_black_ratio - gamma * large_black_ratio

    if score >= 64:
        quality_category = "Excellent"
    elif score >= 50:
        quality_category = "Moderate"
    else:
        quality_category = "Poor"
    
    return score, quality_category
