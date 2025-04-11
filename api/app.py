from fastapi import FastAPI
from api.endpoints import image_upload, classify_image, quality_assessment

app = FastAPI(title="Document Quality API", version="1.0")

# app.include_router(image_upload.router)
# app.include_router(classify_image.router)
app.include_router(quality_assessment.router)
