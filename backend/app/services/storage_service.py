import os
import shutil
import hashlib
from typing import Optional
from abc import ABC, abstractmethod

class StorageService(ABC):
    @abstractmethod
    async def save(self, file_content: bytes, destination_name: str, content_type: str = "application/octet-stream") -> str:
        """Saves file content to storage and returns the storage path."""
        pass

    @abstractmethod
    async def get(self, storage_path: str) -> Optional[bytes]:
        """Returns the content of the file."""
        pass

    @abstractmethod
    async def delete(self, storage_path: str) -> bool:
        """Deletes a file from storage."""
        pass

class LocalDiskStorageService(StorageService):
    def __init__(self, base_dir: str = "storage"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    async def save(self, file_content: bytes, destination_name: str, content_type: str = "application/octet-stream") -> str:
        dest_path = os.path.join(self.base_dir, destination_name)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, "wb") as f:
            f.write(file_content)
        return dest_path

    async def get(self, storage_path: str) -> Optional[bytes]:
        if os.path.exists(storage_path):
            with open(storage_path, "rb") as f:
                return f.read()
        return None

    async def delete(self, storage_path: str) -> bool:
        if os.path.exists(storage_path):
            os.remove(storage_path)
            return True
        return False

from app.core.config import settings

# Export a default instance using the configured storage path
storage_service = LocalDiskStorageService(base_dir=settings.STORAGE_PATH)
