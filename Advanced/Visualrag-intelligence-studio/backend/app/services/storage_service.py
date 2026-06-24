"""Storage service for local and S3/MinIO file storage."""
import os
import shutil
from typing import Optional
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class StorageService:
    """Handles file storage with local and S3 backends."""

    def __init__(self):
        self.backend = settings.STORAGE_BACKEND
        self._s3_client = None

    def _get_s3_client(self):
        """Lazy-initialize S3 client."""
        if self._s3_client is None:
            import boto3
            self._s3_client = boto3.client(
                "s3",
                endpoint_url=settings.S3_ENDPOINT_URL,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
            )
            # Ensure bucket exists
            try:
                self._s3_client.head_bucket(Bucket=settings.S3_BUCKET)
            except Exception:
                try:
                    self._s3_client.create_bucket(Bucket=settings.S3_BUCKET)
                    logger.info("Created S3 bucket: %s", settings.S3_BUCKET)
                except Exception as e:
                    logger.warning("Could not create S3 bucket: %s", e)
        return self._s3_client

    def save_file(self, file_content: bytes, storage_path: str) -> str:
        """Save file content to storage. Returns the storage path."""
        if self.backend == "s3":
            return self._save_s3(file_content, storage_path)
        return self._save_local(file_content, storage_path)

    def _save_local(self, file_content: bytes, storage_path: str) -> str:
        """Save file to local filesystem."""
        full_path = os.path.join(settings.UPLOAD_DIR, storage_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb") as f:
            f.write(file_content)
        logger.info("Saved file locally: %s", full_path)
        return full_path

    def _save_s3(self, file_content: bytes, storage_path: str) -> str:
        """Save file to S3/MinIO."""
        try:
            client = self._get_s3_client()
            client.put_object(
                Bucket=settings.S3_BUCKET,
                Key=storage_path,
                Body=file_content,
            )
            s3_path = f"s3://{settings.S3_BUCKET}/{storage_path}"
            logger.info("Saved file to S3: %s", s3_path)
            return s3_path
        except Exception as e:
            logger.warning("S3 save failed, falling back to local: %s", e)
            return self._save_local(file_content, storage_path)

    def read_file(self, storage_path: str) -> Optional[bytes]:
        """Read file content from storage."""
        if storage_path.startswith("s3://"):
            return self._read_s3(storage_path)
        return self._read_local(storage_path)

    def _read_local(self, storage_path: str) -> Optional[bytes]:
        """Read from local filesystem."""
        # Try as full path first, then relative to upload dir
        if os.path.exists(storage_path):
            with open(storage_path, "rb") as f:
                return f.read()
        full_path = os.path.join(settings.UPLOAD_DIR, storage_path)
        if os.path.exists(full_path):
            with open(full_path, "rb") as f:
                return f.read()
        return None

    def _read_s3(self, storage_path: str) -> Optional[bytes]:
        """Read from S3/MinIO."""
        try:
            # Parse s3://bucket/key
            path = storage_path.replace("s3://", "")
            parts = path.split("/", 1)
            bucket = parts[0]
            key = parts[1] if len(parts) > 1 else ""
            client = self._get_s3_client()
            response = client.get_object(Bucket=bucket, Key=key)
            return response["Body"].read()
        except Exception as e:
            logger.warning("S3 read failed: %s", e)
            return None

    def delete_file(self, storage_path: str) -> bool:
        """Delete a file from storage."""
        try:
            if storage_path.startswith("s3://"):
                path = storage_path.replace("s3://", "")
                parts = path.split("/", 1)
                client = self._get_s3_client()
                client.delete_object(Bucket=parts[0], Key=parts[1])
            else:
                if os.path.exists(storage_path):
                    os.remove(storage_path)
            return True
        except Exception as e:
            logger.warning("Delete failed: %s", e)
            return False


# Singleton
storage_service = StorageService()
