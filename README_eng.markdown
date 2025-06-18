# Document Quality API - README

## Overview
The Document Quality API is a standalone FastAPI-based service designed to classify document types and assess text quality from uploaded images or PDFs. Leveraging YOLO for document detection and PaddleOCR for text extraction, the API is optimized for Russian-language documents and runs in a Docker container with NVIDIA GPU support. This version, updated as of June 18, 2025, focuses on simplicity and efficiency for integration with systems like 1C.

### Key Features
- Classifies documents into types such as passports, INN, SNILS, etc.
- Assesses text quality, categorizing it as "Bad" or "Excellent."
- Returns cropped regions of interest (ROIs) as downloadable URLs.
- Supports batch processing of up to 10 files per request.
- Handles multiple documents within a single image or PDF page.

### Supported Document Types
- Passport (Russian Federation)
- INN
- SNILS
- Registration Certificate
- Children's Documents
- Migration Cards

---

## System Workflow
1. **Upload**: Send images or PDFs via a POST request to the API.
2. **Processing**: The API detects documents, assesses quality, crops ROIs, and saves them to a static directory.
3. **Response**: Returns a JSON response with `doc_type`, `quality_category`, and `cropped_roi` URLs for each detected document.

---

## Prerequisites

### Hardware
| Component    | Minimum              | Recommended            |
|--------------|----------------------|------------------------|
| **GPU**      | NVIDIA RTX 3060 (12 GB VRAM) | NVIDIA RTX 3090 (24 GB VRAM) |
| **CPU**      | Intel i7-12700K      | AMD Ryzen 9 7950X      |
| **RAM**      | 32 GB DDR4           | 64 GB DDR5             |
| **Storage**  | 512 GB SSD           | 1 TB NVMe SSD          |

### Software
- **Docker**: Installed with NVIDIA Container Toolkit for GPU acceleration.
- **Operating System**: Windows or Linux.

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Document-Quality-API
```

### 2. Build and Run the Docker Container
- **Configure Storage**: Edit `docker/docker-compose.yml` to map a local directory to `/app/api/static` (e.g., `/path/to/host/storage:/app/api/static`) for storing cropped images.
- **Run**:
  ```bash
  docker-compose -f docker/docker-compose.yml up -d
  ```
- The API will be available at `http://localhost:8000`.

### 3. Verify Deployment
- Access `http://localhost:8000/` to confirm the service is running (returns `{"message": "Model loaded successfully!"}`).

---

## API Usage

### Endpoint: `/batch-quality-assessment/`
#### Request
- **Method**: POST
- **URL**: `http://<api-host>:8000/batch-quality-assessment/`
- **Content-Type**: `multipart/form-data`
- **Body**: Up to 10 files (images or PDFs).
- **Example**:
  ```bash
  curl -X POST http://localhost:8000/batch-quality-assessment/ \
    -F "files=@document1.jpg" \
    -F "files=@document2.pdf"
  ```

#### Response
- **Format**: JSON array of objects.
- **Fields**:
  - `filename`: Name of the uploaded file.
  - `result`: List of detected documents, each with:
    - `doc_type`: Document type (e.g., "passport").
    - `quality_category`: Quality assessment ("Bad" or "Excellent").
    - `cropped_roi`: URL to download the cropped image.
  - `error`: Error message (if applicable).
- **Example Response**:
  ```json
  [
    {
      "filename": "document1.jpg",
      "result": [
        {
          "doc_type": "passport",
          "quality_category": "Excellent",
          "cropped_roi": "http://localhost:8000/static/cropped_docs/abc123.jpg"
        },
        {
          "doc_type": "inn",
          "quality_category": "Bad",
          "cropped_roi": "http://localhost:8000/static/cropped_docs/def456.jpg"
        }
      ],
      "error": null
    },
    {
      "filename": "document2.pdf",
      "result": [
        {
          "doc_type": "snils",
          "quality_category": "Excellent",
          "cropped_roi": "http://localhost:8000/static/cropped_docs/ghi789.jpg"
        }
      ],
      "error": null
    }
  ]
  ```
- **Notes**:
  - A single file may contain multiple documents, each returned as a separate object in `result`.
  - PDFs are processed page by page, with each page treated as a separate file (e.g., "document.pdf_page1.jpg").

---

## For the 1C Department

### How to Interact
1. **Send Request**: Use a POST request to `/batch-quality-assessment/` with document files.
2. **Parse Response**: Expect a JSON array where each file may have multiple `result` entries.
3. **Utilize Results**:
   - `doc_type`: Identify the document type.
   - `quality_category`: Determine if the document is usable ("Excellent" or "Bad").
   - `cropped_roi`: Access the cropped image via the provided URL for further processing or storage.

### Integration Notes
- Handle multiple documents per file by iterating over the `result` list.
- Check for `error` fields to manage failed processing (e.g., invalid files).
- Store the `cropped_roi` images locally if needed by downloading from the URL.

---

## Guidance for Repository Users
If you clone this repo to test the API:

### Setup
1. Install Docker and NVIDIA Container Toolkit.
2. Clone the repo and navigate to the directory:
   ```bash
   git clone <repository-url>
   cd Document-Quality-API
   ```
3. Update `docker/docker-compose.yml` with a valid host path for the `/app/api/static` volume (e.g., `/home/user/storage:/app/api/static`).
4. Start the container:
   ```bash
   docker-compose -f docker/docker-compose.yml up -d
   ```

### Test the API
- Send a test request:
  ```bash
  curl -X POST http://localhost:8000/batch-quality-assessment/ \
    -F "files=@test_image.jpg"
  ```
- Verify the response includes `doc_type`, `quality_category`, and a valid `cropped_roi` URL.
- Access a `cropped_roi` URL (e.g., `http://localhost:8000/static/cropped_docs/abc123.jpg`) in a browser to download the image.

### Troubleshooting
- **GPU Issues**: Ensure NVIDIA drivers and Container Toolkit are installed. Check logs with `docker logs <container-name>`.
- **Storage**: Confirm the volume path is accessible and writable.
- **Errors**: Review `app.log` in the container for detailed error messages.

---

## Performance Considerations
- Tested on NVIDIA RTX 3070 (8 GB VRAM), 2 × Xeon E5-2696 v3 (36 threads), 64 GB RAM.
- Handles up to 10 concurrent files efficiently; latency averages 427 ms per request.

---

## Future Improvements
- Enhance support for additional document types (e.g., foreign passports).
- Refine quality assessment with more labeled data.

---

## Contact
For support or inquiries, contact:
- **Name**: Назих Эррахел (Nazih Errahel)
- **Email**: [Insert email address]