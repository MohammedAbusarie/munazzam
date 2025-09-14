# app/core/cloudinary_service.py

import cloudinary.uploader
import cloudinary.api
from typing import Dict, Any

def upload_image(file_path: str, public_id: str = None) -> Dict[str, Any]:
    """
    Uploads an image file to Cloudinary.

    Args:
        file_path: The local path to the image file.
        public_id: The desired public_id for the asset. If None, one is generated.

    Returns:
        A dictionary containing the API response from Cloudinary.
    """
    try:
        upload_result = cloudinary.uploader.upload(
            file_path,
            folder="munazzam_cars",  # Organizes assets in a specific folder
            public_id=public_id,
            overwrite=True
        )
        return {"success": True, "data": upload_result}
    except Exception as e:
        print(f"Cloudinary upload failed: {e}")
        return {"success": False, "error": str(e)}

def delete_image(public_id: str) -> Dict[str, Any]:
    """
    Deletes an image from Cloudinary using its public_id.

    Args:
        public_id: The public ID of the resource to delete.

    Returns:
        A dictionary containing the API response.
    """
    try:
        delete_result = cloudinary.api.delete_resources([public_id])
        return {"success": True, "data": delete_result}
    except Exception as e:
        print(f"Cloudinary deletion failed: {e}")
        return {"success": False, "error": str(e)}