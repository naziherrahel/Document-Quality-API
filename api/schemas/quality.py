from pydantic import BaseModel
from typing import List, Optional

class DocumentQualityResponse(BaseModel):
    doc_type: str
    quality_category: str
    cropped_roi: str

class MultiDocumentQualityResponse(BaseModel):
    documents: List[DocumentQualityResponse]

class BatchQualityResponse(BaseModel):
    filename: str
    result: Optional[List[DocumentQualityResponse]] = None
    error: Optional[str] = None