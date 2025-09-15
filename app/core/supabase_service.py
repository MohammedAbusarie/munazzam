# app/core/supabase_service.py

import uuid
import os
from .config import get_supabase_client

BUCKET_NAME = "car_images"

def upload_image(local_file_path: str) -> dict:
    """
    Uploads an image to the Supabase storage bucket.

    Args:
        local_file_path: The full path to the local file to upload.

    Returns:
        A dictionary with the success status and public URL or error message.
    """
    try:
        supabase = get_supabase_client()
        file_ext = os.path.splitext(local_file_path)[1]
        # Generate a unique path to prevent filename collisions
        remote_path_on_bucket = f"{uuid.uuid4()}{file_ext}"

        with open(local_file_path, 'rb') as f:
            # content_type is important for the browser to render the image
            supabase.storage.from_(BUCKET_NAME).upload(
                remote_path_on_bucket,
                f,
                {"content-type": f"image/{file_ext.strip('.')}"}
            )

        # Get the public URL for the uploaded file
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(remote_path_on_bucket)
        
        return {"success": True, "url": public_url, "path": remote_path_on_bucket}
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_image(remote_path_on_bucket: str) -> dict:
    """
    Deletes an image from the Supabase storage bucket.

    Args:
        remote_path_on_bucket: The path of the file within the bucket.

    Returns:
        A dictionary with the success status or error message.
    """
    try:
        supabase = get_supabase_client()
        supabase.storage.from_(BUCKET_NAME).remove([remote_path_on_bucket])
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_path_from_url(url: str) -> str:
    """Helper function to extract the storage path from a public URL."""
    try:
        # Splits the URL and returns the last part, which is the path
        return url.split(f'{BUCKET_NAME}/')[-1]
    except (IndexError, AttributeError):
        return ""