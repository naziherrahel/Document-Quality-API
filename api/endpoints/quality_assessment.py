import os
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from api.config.settings import UPLOAD_DIR
from api.models.utils import generate_unique_filename, save_upload_file
from api.quality.ocr_quality import preprocess_image, assess_binarization_quality, calculate_ocr_quality
from api.quality.scoring import calculate_global_score
from api.schemas.quality import DocumentQualityResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/quality-assessment/", response_model=DocumentQualityResponse)
async def quality_assessment(image: UploadFile = File(...)):
    """
    Endpoint to assess document quality by:
      - Saving the uploaded image.
      - Preprocessing and binarizing it.
      - Assessing image quality metrics.
      - Running OCR to extract text and confidence.
      - Computing a global quality score.
    
    Returns:
        A structured JSON response containing all quality metrics.
    """
    try:
        unique_filename = generate_unique_filename(image.filename)
        upload_path = os.path.join(str(UPLOAD_DIR), unique_filename)
        
        # Save the file
        file_path = await save_upload_file(image, upload_path)
        
        # Preprocess image and generate binary image
        processed_path, binary_img = preprocess_image(file_path)
        
        # Evaluate binarization metrics
        global_black_ratio, large_black_ratio = assess_binarization_quality(binary_img)
        if large_black_ratio > 20:
            binarization_quality = f"High large-black region ratio ({large_black_ratio:.2f}%), potential quality issues."
        else:
            binarization_quality = f"Low large-black region ratio ({large_black_ratio:.2f}%), image quality acceptable."
        
        # Run OCR quality assessment
        text, average_conf, ocr_quality = calculate_ocr_quality(processed_path, lang="rus")
        
        # Compute global score and quality category
        global_score, quality_category = calculate_global_score(
            ocr_conf=average_conf,
            global_black_ratio=global_black_ratio,
            large_black_ratio=large_black_ratio
        )
        
        response = DocumentQualityResponse(
            text=text,
            average_confidence=average_conf,
            ocr_quality_assessment=ocr_quality,
            global_black_ratio=f"{global_black_ratio:.2f}%",
            large_black_region_ratio=f"{large_black_ratio:.2f}%",
            binarization_quality=binarization_quality,
            global_score=global_score,
            quality_category=quality_category
        )
        return response
    except Exception as e:
        logger.error("Error in quality assessment endpoint", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
