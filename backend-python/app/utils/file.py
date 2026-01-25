import os
import uuid
from typing import Optional
from fastapi import UploadFile
from pathlib import Path


async def save_upload_file(
    upload_file: UploadFile,
    upload_dir: str,
    filename: Optional[str] = None
) -> str:
    """Save uploaded file to disk"""
    if not filename:
        # Generate unique filename
        file_extension = os.path.splitext(upload_file.filename)[1]
        filename = f"{uuid.uuid4()}{file_extension}"

    # Create upload directory if it doesn't exist
    Path(upload_dir).mkdir(parents=True, exist_ok=True)

    # Save file
    file_path = os.path.join(upload_dir, filename)
    with open(file_path, "wb") as f:
        content = await upload_file.read()
        f.write(content)

    return file_path


def get_file_url(filename: str, base_url: str) -> str:
    """Get file URL from filename"""
    return f"{base_url}/{filename}"


def delete_file(file_path: str) -> bool:
    """Delete file from disk"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False
