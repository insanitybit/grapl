from typing import Optional, TYPE_CHECKING
import time
import logging
import sys
import os

from grapl_common.grapl_logger import get_module_grapl_logger

if TYPE_CHECKING:
    from mypy_boto3_s3.service_resource import Bucket

LOGGER = get_module_grapl_logger()

IS_LOCAL = bool(os.environ.get("IS_LOCAL", False))

class LazyUxBucket:
    def __init__(self) -> None:
        self.ux_bucket: Optional[Bucket] = None

    def get(self) -> Bucket:
        if self.ux_bucket is None:
            self.ux_bucket = self._retrieve_bucket()
        return self.ux_bucket

    def get_resource(self, resource_name: str) -> Optional[bytes]:
        bucket = self.get()
        start = int(time.time())
        try:
            obj = bucket.Object(resource_name)
            end = int(time.time())
            LOGGER.debug(f"retrieved object {resource_name} after {end - start}")
        except Exception as e:
            # TODO: We should only return None in cases where the object doesn't exist
            end = int(time.time())
            LOGGER.warning(f"Failed to retrieve object: {e} after {end - start}")
            return None

        # todo: We could just compress right here instead of allocating this intermediary
        # Or we could compress the files in s3?
        return obj.get()["Body"].read()

    def _retrieve_bucket(self) -> Bucket:
        if IS_LOCAL:
            return self._retrieve_bucket_local()
        else:
            s3 = boto3.resource("s3")
            return s3.Bucket(UX_BUCKET_NAME)

    def _retrieve_bucket_local(self) -> Bucket:
        timeout_secs = 30
        bucket: Optional[Bucket] = None

        for _ in range(timeout_secs):
            try:
                s3 = S3ResourceFactory(boto3).from_env()
                bucket = s3.Bucket(UX_BUCKET_NAME)
                break
            except Exception as e:
                LOGGER.debug(e)
                time.sleep(1)
        if not bucket:
            raise TimeoutError(
                f"Expected s3 ux bucket to be available within {timeout_secs} seconds"
            )
        return bucket