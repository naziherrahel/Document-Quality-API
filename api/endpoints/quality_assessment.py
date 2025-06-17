import logging
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from api.config.settings import UPLOAD_DIR
from api.models.utils import save_upload_file
from api.quality.ocr_quality import preprocess_image, assess_binarization_quality, async_calculate_ocr_quality
from api.quality.scoring import calculate_global_score
from api.schemas.quality import DocumentQualityResponse, MultiDocumentQualityResponse, BatchQualityResponse
from api.models.yolo_inference import detect_and_crop_document 
import numpy as np 
import cv2
import time
from pdf2image import convert_from_bytes
from PIL import Image
import io
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

async def process_image(img: np.ndarray, filename: str) -> MultiDocumentQualityResponse:
    """Process a single image for document detection and quality assessment."""
    start_time = time.time()
    logger.info(f"Processing image: {filename}")

    if img is None:
        logger.error(f"Failed to load image: {filename}")
        return MultiDocumentQualityResponse(documents=[
            DocumentQualityResponse(
                doc_type="unknown",
                confidence=0.0,
                text="",
                average_confidence=0.0,
                ocr_quality_assessment="Failed: Image could not be loaded.",
                global_black_ratio="0.00%",
                large_black_region_ratio="0.00%",
                binarization_quality="Failed: Image could not be loaded.",
                global_score=0.0,
                quality_category="Failed"
            )
        ])

    # YOLO detection and cropping
    try:
        detection_results = detect_and_crop_document(img)
        if not detection_results:
            logger.info(f"No documents detected in {filename}")
            return MultiDocumentQualityResponse(documents=[
                DocumentQualityResponse(
                    doc_type="unknown",
                    confidence=0.0,
                    text="",
                    average_confidence=0.0,
                    ocr_quality_assessment="Failed: No documents detected.",
                    global_black_ratio="0.00%",
                    large_black_region_ratio="0.00%",
                    binarization_quality="Failed: No documents detected.",
                    global_score=0.0,
                    quality_category="Failed"
                )
            ])
        logger.info(f"YOLO detected {len(detection_results)} documents in {filename}")
    except Exception as e:
        logger.error(f"Document detection failed for {filename}: {str(e)}")
        return MultiDocumentQualityResponse(documents=[
            DocumentQualityResponse(
                doc_type="unknown",
                confidence=0.0,
                text="",
                average_confidence=0.0,
                ocr_quality_assessment=f"Failed: {str(e)}",
                global_black_ratio="0.00%",
                large_black_region_ratio="0.00%",
                binarization_quality="Failed: Document could not be detected.",
                global_score=0.0,
                quality_category="Failed"
            )
        ])

    # Process each detected document
    documents = []
    for detection in detection_results:
        cropped_path = detection["cropped_path"]
        doc_type = detection["doc_type"]
        confidence = detection["confidence"]
        logger.info(f"Processing document: {doc_type} with confidence={confidence} in {filename}")

        # Preprocess image
        processed_path, binary_img = preprocess_image(cropped_path)

        # Binarization quality
        global_black_ratio, large_black_ratio = assess_binarization_quality(binary_img)
        binarization_quality = (
            f"High large-black region ratio ({large_black_ratio:.2f}%), potential quality issues."
            if large_black_ratio > 20 else
            f"Low large-black region ratio ({large_black_ratio:.2f}%), image quality acceptable."
        )

        # OCR quality
        try:
            text, average_conf, ocr_quality = await async_calculate_ocr_quality(processed_path, lang="ru")
        except Exception as e:
            logger.error(f"OCR processing failed for {doc_type} in {filename}: {str(e)}")
            documents.append(DocumentQualityResponse(
                doc_type=doc_type,
                confidence=confidence,
                text="",
                average_confidence=0.0,
                ocr_quality_assessment=f"Failed: OCR processing error - {str(e)}",
                global_black_ratio="0.00%",
                large_black_region_ratio="0.00%",
                binarization_quality="Failed: OCR processing error.",
                global_score=0.0,
                quality_category="Failed"
            ))
            continue
        logger.info(f"OCR average confidence for {doc_type}: {average_conf:.2f}")

        # Global score
        global_score, quality_category = calculate_global_score(
            ocr_conf=average_conf,
            global_black_ratio=global_black_ratio,
            large_black_ratio=large_black_ratio
        )

        documents.append(DocumentQualityResponse(
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
        ))

    logger.info(f"Processing time for {filename}: {time.time() - start_time:.2f} seconds")
    return MultiDocumentQualityResponse(documents=documents)

@router.post("/batch-quality-assessment/", response_model=List[BatchQualityResponse])
async def batch_quality_assessment(files: List[UploadFile] = File(...)):
    """Process a batch of files (images or PDFs) for quality assessment."""
    start_time = time.time()
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed per request.")
    
    results = []
    for file in files:
        try:
            # Save and load file
            file_like_object = await save_upload_file(file)
            file_like_object.seek(0)
            file_bytes = file_like_object.read()

            # Handle PDF files
            if file.content_type == "application/pdf":
                logger.info(f"Processing PDF: {file.filename}")
                try:
                    pages = convert_from_bytes(file_bytes, dpi=200)
                    base_filename = file.filename.rsplit('.', 1)[0]
                    for page_num, page in enumerate(pages, 1):
                        # Convert PIL image to OpenCV format
                        img_byte_arr = io.BytesIO()
                        page.save(img_byte_arr, format='JPEG')
                        img_bytes = img_byte_arr.getvalue()
                        img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
                        page_filename = f"{base_filename}_page{page_num}.jpg"
                        result = await process_image(img, page_filename)
                        results.append(BatchQualityResponse(
                            filename=page_filename,
                            result=result.documents
                        ))
                        logger.info(f"Processed PDF page: {page_filename}")
                except Exception as e:
                    logger.error(f"Failed to process PDF {file.filename}: {str(e)}")
                    results.append(BatchQualityResponse(
                        filename=file.filename,
                        error=f"PDF processing error: {str(e)}"
                    ))
                    continue
            else:
                # Handle images
                img = cv2.imdecode(np.frombuffer(file_bytes, np.uint8), cv2.IMREAD_COLOR)
                result = await process_image(img, file.filename)
                results.append(BatchQualityResponse(
                    filename=file.filename,
                    result=result.documents
                ))

        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {str(e)}")
            results.append(BatchQualityResponse(
                filename=file.filename,
                error=str(e)
            ))

    logger.info(f"Batch processing time for {len(files)} files: {time.time() - start_time:.2f} seconds")
    return results
