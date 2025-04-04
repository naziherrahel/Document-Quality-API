from fastapi import FastAPI
from api.endpoints import classify_image

app = FastAPI(title="Document Quality Classification API", version="1.0")

# Include the classify image router under the '/api' prefix
app.include_router(classify_image.router, prefix="/api")

# Optional: Root endpoint to check API health
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Document Quality Classification API"}
