# ?? File operations for user ROMs & save files
import os
from aiofiles import open as aio_open

UPLOAD_ROOT = "/home/blankthedeer/gba/uploads"

def get_user_dir(user_id: str) -> str:
    """Return or create user-specific directory."""
    path = os.path.join(UPLOAD_ROOT, user_id)
    os.makedirs(path, exist_ok=True)
    return path

async def save_file(user_id: str, filename: str, file):
    """Save uploaded file asynchronously."""
    user_path = get_user_dir(user_id)
    file_path = os.path.join(user_path, filename)
    async with aio_open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)
    return file_path

async def delete_file(user_id: str, filename: str):
    """Delete specific file."""
    user_path = get_user_dir(user_id)
    file_path = os.path.join(user_path, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

async def list_files(user_id: str):
    """List ROMs and saves in user directory."""
    user_path = get_user_dir(user_id)
    files = []
    for file in os.listdir(user_path):
        full = os.path.join(user_path, file)
        size = os.path.getsize(full)
        files.append({"name": file, "size": size})
    return files
