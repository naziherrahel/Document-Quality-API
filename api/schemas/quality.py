from pydantic import BaseModel
from typing import List, Optional

class DocumentQualityResponse(BaseModel):
    doc_type: str
    confidence: float
    text: str
    average_confidence: float
    ocr_quality_assessment: str
    global_black_ratio: str
    large_black_region_ratio: str
    binarization_quality: str
    global_score: float
    quality_category: str

class MultiDocumentQualityResponse(BaseModel):
    documents: List[DocumentQualityResponse]

class BatchQualityResponse(BaseModel):
    filename: str
    result: Optional[List[DocumentQualityResponse]] = None
    error: Optional[str] = None