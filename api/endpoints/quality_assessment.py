import os
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from api.config.settings import UPLOAD_DIR
from api.models.utils import generate_unique_filename, save_upload_file
from api.quality.ocr_quality import preprocess_image, assess_binarization_quality, calculate_ocr_quality
from api.quality.scoring import calculate_global_score
from api.schemas.quality import DocumentQualityResponse
from api.models.yolo_inference import detect_and_crop_document  # ✅ NEW

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/quality-assessment/", response_model=DocumentQualityResponse)
async def quality_assessment(image: UploadFile = File(...)):
    logger.info(f"Received image of type: {type(image)}")
    try:
        # Save uploaded file
        unique_filename = generate_unique_filename(image.filename)
        upload_path = os.path.join(str(UPLOAD_DIR), unique_filename)
        file_path = await save_upload_file(image, upload_path)
        logger.info(f"Saved uploaded file to: {file_path}")

        # Detect document and crop
        try:
            detection_result = detect_and_crop_document(file_path)
            cropped_path = detection_result["cropped_path"]
            doc_type = detection_result["doc_type"]
            confidence = detection_result["confidence"]
            logger.info(f"YOLO detected doc_type={doc_type} with confidence={confidence}")
            logger.info(f"Cropped image saved to: {cropped_path}")
        except Exception as e:
            logger.error("Document detection failed", exc_info=True)
            raise HTTPException(status_code=422, detail=f"Document detection failed: {str(e)}")

        # Preprocess the cropped image
        processed_path, binary_img = preprocess_image(cropped_path)
        logger.info(f"Preprocessed image path: {processed_path}")

        # Evaluate binarization quality
        global_black_ratio, large_black_ratio = assess_binarization_quality(binary_img)
        binarization_quality = (
            f"High large-black region ratio ({large_black_ratio:.2f}%), potential quality issues."
            if large_black_ratio > 20 else
            f"Low large-black region ratio ({large_black_ratio:.2f}%), image quality acceptable."
        )

        # OCR quality evaluation
        text, average_conf, ocr_quality = calculate_ocr_quality(processed_path, lang="rus")
        logger.info(f"OCR average confidence: {average_conf:.2f}")

        # Calculate global score
        global_score, quality_category = calculate_global_score(
            ocr_conf=average_conf,
            global_black_ratio=global_black_ratio,
            large_black_ratio=large_black_ratio
        )

        return DocumentQualityResponse(
            doc_type=doc_type,
            confidence=confidence,
            text=text,
            average_confidence=average_conf,
            ocr_quality_assessment=ocr_quality,
            global_black_ratio=f"{global_black_ratio:.2f}%",
            large_black_region_ratio=f"{large_black_ratio:.2f}%",
            binarization_quality=binarization_quality,
            global_score=global_score,
            quality_category=quality_category
        )

    except Exception as e:
        logger.error("Unhandled error in quality assessment", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
