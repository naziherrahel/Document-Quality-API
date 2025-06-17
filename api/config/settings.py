# Application setting 


import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


# Directories for file storage
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
NORMALISED_DIR = os.path.join(BASE_DIR, "normalised")

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(NORMALISED_DIR, exist_ok=True)

