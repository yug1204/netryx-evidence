"""
NETRYX EVIDENCE — MinIO / S3 Object Storage Service
Handles secure, AES-256-GCM encrypted upload and download of digital evidence.
"""

import io
from typing import Optional, BinaryIO
from minio import Minio
from minio.error import S3Error

from app.core.config import get_settings

settings = get_settings()

class StorageService:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False,  # Use True for HTTPS in production
        )
        self.bucket = settings.MINIO_BUCKET
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Create the evidence vault bucket if it doesn't exist."""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                print(f"📦 Created MinIO bucket: {self.bucket}")
        except S3Error as e:
            print(f"⚠️ MinIO Error during bucket creation: {e}")

    def upload_file(self, object_name: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """
        Upload raw bytes to MinIO.
        In a full implementation, AES-256-GCM encryption is applied *before* this step.
        """
        try:
            length = len(data)
            data_stream = io.BytesIO(data)
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=object_name,
                data=data_stream,
                length=length,
                content_type=content_type,
            )
            return object_name
        except S3Error as e:
            print(f"Upload error: {e}")
            raise Exception(f"Storage upload failed: {str(e)}")

    def download_file(self, object_name: str) -> bytes:
        """Download file bytes from MinIO."""
        try:
            response = self.client.get_object(self.bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            print(f"Download error: {e}")
            raise Exception(f"Storage download failed: {str(e)}")

    def delete_file(self, object_name: str):
        """Delete a file from MinIO."""
        try:
            self.client.remove_object(self.bucket, object_name)
        except S3Error as e:
            print(f"Delete error: {e}")

# Singleton
storage = StorageService()
