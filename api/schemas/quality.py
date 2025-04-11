from pydantic import BaseModel, Field

class DocumentQualityResponse(BaseModel):
    text: str = Field(..., description="OCR extracted text from the document.")
    average_confidence: float = Field(..., description="Average OCR confidence score.")
    ocr_quality_assessment: str = Field(..., description="Qualitative assessment of OCR readability.")
    global_black_ratio: str = Field(..., description="Global percentage of black pixels in the image.")
    large_black_region_ratio: str = Field(..., description="Percentage of large black regions in the image.")
    binarization_quality: str = Field(..., description="Overall binarization quality assessment.")
    global_score: float = Field(..., description="Aggregated global quality score.")
    quality_category: str = Field(..., description="Global quality category: Excellent, Moderate, or Poor.")
