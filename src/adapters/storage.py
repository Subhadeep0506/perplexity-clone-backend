"""Storage adapter protocol."""

from typing import Protocol
from fastapi import UploadFile


class StorageAdapter(Protocol):
    """Protocol for storage adapters."""

    async def upload_file(
        self, file: UploadFile, user_id: int, folder: str = "avatar"
    ) -> str:
        """Upload a file to storage.

        Args:
            file: The file to upload
            user_id: User ID for organizing files
            folder: Folder name within user's space

        Returns:
            Storage key/path for the uploaded file
        """
        ...

    def get_file_url(self, file_key: str) -> str:
        """Get public URL for a stored file.

        Args:
            file_key: Storage key returned from upload_file

        Returns:
            Public URL to access the file
        """
        ...

    async def delete_file(self, file_key: str) -> bool:
        """Delete a file from storage.

        Args:
            file_key: Storage key to delete

        Returns:
            True if successful, False otherwise
        """
        ...
