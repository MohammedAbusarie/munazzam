# app/core/supabase_service.py

import uuid
import os
import io # Required for in-memory file handling
from PIL import Image # Import from Pillow
from .config import get_supabase_client

# --- Configuration for Image Compression ---
MAX_IMAGE_SIZE = (1280, 1280) # Max width/height
JPEG_QUALITY = 85 # From 0 to 100

def upload_image(local_file_path: str, bucket_name: str) -> dict:
    """
    Compresses, resizes, and uploads an image to a specified Supabase bucket.
    """
    try:
        supabase = get_supabase_client()
        file_ext = os.path.splitext(local_file_path)[1].lower()
        remote_path_on_bucket = f"{uuid.uuid4()}{file_ext}"

        # --- Image Compression Logic ---
        image = Image.open(local_file_path)
        
        # Convert RGBA (like in PNGs) to RGB for saving as JPEG
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
            
        # Resize the image if it's larger than the max dimensions
        image.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
        
        # Save the compressed image to an in-memory buffer
        in_mem_file = io.BytesIO()
        image.save(in_mem_file, format='JPEG', quality=JPEG_QUALITY, optimize=True)
        in_mem_file.seek(0) # Go to the beginning of the buffer

        # --- Upload the compressed image data ---
        supabase.storage.from_(bucket_name).upload(
            remote_path_on_bucket,
            in_mem_file.read(), # Read the bytes from the buffer
            {"content-type": "image/jpeg"} # Upload as JPEG
        )

        public_url = supabase.storage.from_(bucket_name).get_public_url(remote_path_on_bucket)
        
        return {"success": True, "url": public_url, "path": remote_path_on_bucket}
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_image(remote_path_on_bucket: str, bucket_name: str) -> dict:
    """
    Deletes an image from a specified Supabase storage bucket.
    """
    try:
        supabase = get_supabase_client()
        supabase.storage.from_(bucket_name).remove([remote_path_on_bucket])
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_path_from_url(url: str) -> str:
    """
    Helper function to extract the storage path from a public URL.
    """
    try:
        return url.rsplit('/', 1)[-1]
    except (IndexError, AttributeError):
        return ""