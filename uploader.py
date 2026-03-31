import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

logger = logging.getLogger("uploader")

# Initialize Supabase client
supabase: Client = None
if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def get_mime_type(file_path: str) -> str:
    """Returns the MIME type based on file extension."""
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return "application/pdf"
    elif ext in [".jpg", ".jpeg"]:
        return "image/jpeg"
    elif ext == ".png":
        return "image/png"
    return "application/octet-stream"

def upload_to_summa(file_path: str, course: str = "UNSORTED") -> bool:
    """
    Uploads a file to Supabase storage and inserts a record into the resources table.
    
    Args:
        file_path: Local path to the file.
        course: Course code classification.
        
    Returns:
        True if successful, False otherwise.
    """
    if not supabase:
        logger.error("Supabase client not initialized. Check .env")
        return False

    path_obj = Path(file_path)
    filename = path_obj.name
    storage_path = f"{course}/{filename}"
    mime_type = get_mime_type(file_path)

    try:
        # 1. Upload to storage bucket
        with open(file_path, "rb") as f:
            logger.info(f"Uploading {filename} to {storage_path}...")
            supabase.storage.from_("resources").upload(
                path=storage_path,
                file=f,
                file_options={"contentType": mime_type, "upsert": "true"}
            )
        
        # 2. Insert record into database
        db_data = {
            "course_code": course,
            "filename": filename,
            "storage_path": storage_path,
            "mime_type": mime_type,
            "status": "uploaded"
        }
        supabase.table("resources").insert(db_data).execute()
        
        logger.info(f"Successfully uploaded: {filename}")
        return True
    except Exception as e:
        logger.error(f"Failed to process {filename}: {str(e)}")
        return False

# Assumptions:
# - Supabase bucket 'resources' already exists.
# - SUPABASE_SERVICE_KEY has sufficient permissions.
