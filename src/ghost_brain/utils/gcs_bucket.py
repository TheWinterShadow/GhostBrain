import logging

from google.api_core.exceptions import GoogleAPIError
from google.cloud.exceptions import NotFound
from google.cloud.storage import Client


class GCSBucket:
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.client = Client()
        self.bucket = self._get_bucket()

    def _get_bucket(self):
        try:
            bucket = self.client.get_bucket(self.bucket_name)
            logging.info(f"Successfully accessed bucket: {self.bucket_name}")
            return bucket
        except NotFound:
            logging.error(f"Bucket {self.bucket_name} not found.")
            raise
        except GoogleAPIError as e:
            logging.error(f"Google API error while accessing bucket: {e}")
            raise

    def download_blob_as_string(self, blob_name: str) -> str:
        try:
            blob = self.bucket.blob(blob_name)
            content = blob.download_as_text()
            logging.info(f"Successfully downloaded blob: {blob_name}")
            return content
        except NotFound:
            logging.error(f"Blob {blob_name} not found in bucket {self.bucket_name}.")
            raise
        except GoogleAPIError as e:
            logging.error(f"Google API error while downloading blob: {e}")
            raise

    def upload_string_to_blob(self, blob_name: str, content: str) -> None:
        try:
            blob = self.bucket.blob(blob_name)
            blob.upload_from_string(content)
            logging.info(f"Successfully uploaded string to blob: {blob_name}")
        except GoogleAPIError as e:
            logging.error(f"Google API error while uploading to blob: {e}")
            raise
