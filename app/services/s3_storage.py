import logging
from typing import BinaryIO
from uuid import uuid4

from botocore.exceptions import ClientError
from types_aiobotocore_s3.client import S3Client

logger = logging.getLogger(__name__)

DEFAULT_URL_TTL_SECONDS = 60 * 15  # 15 min


class S3StorageService:
    def __init__(self, client: S3Client, bucket: str):
        self._client = client
        self._bucket = bucket

    async def ensure_bucket(self) -> None:
        """Удобно для dev/MinIO. В production bucket обычно создают заранее."""
        try:
            await self._client.head_bucket(Bucket=self._bucket)
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code")
            if code in ("404", "NoSuchBucket", "NotFound"):
                await self._client.create_bucket(Bucket=self._bucket)
                logger.info("Created bucket %s", self._bucket)
            else:
                raise
        except Exception:
            logger.error(
                "The bucket don't exists when starting app and was not able to create %s",
                self._bucket,
            )
            pass

    async def upload(
        self, key: str, data: bytes, content_type: str, public_read: bool = False
    ):
        try:
            extra_args = {}
            if public_read:
                extra_args["ACL"] = "public-read"

            await self._client.put_object(
                Bucket=self._bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
                **extra_args,
            )
        except Exception:
            raise StorageError()

    async def upload_obj(
        self, key: str, obj: BinaryIO, content_type: str, public_read: bool = False
    ):
        try:
            extra_args = {}
            if public_read:
                extra_args["ACL"] = "public-read"

            self._client.upload_fileobj(
                Fileobj=obj,
                Bucket=self._bucket,
                Key=key,
                ContentType=content_type,
                **extra_args,
            )
        except Exception:
            raise StorageError()

    async def delete(self, key: str) -> None:
        await self._client.delete_object(Bucket=self._bucket, Key=key)

    async def exists(self, key: str) -> bool:
        try:
            await self._client.head_object(Bucket=self._bucket, Key=key)
            return True
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code")
            if code in ("404", "NoSuchKey", "NotFound"):
                return False
            raise StorageError(str(exc)) from exc

    async def presigned_get_url(self, key: str, expires: int | None = None) -> str:
        try:
            expire_seconds = expires or DEFAULT_URL_TTL_SECONDS
            return await self._client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": self._bucket, "Key": key},
                ExpiresIn=expire_seconds,
            )
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code")
            if code in ("404", "NoSuchKey", "NotFound"):
                raise ObjectNotFoundError(key)
            raise StorageError(str(exc)) from exc

    @staticmethod
    def build_key(prefix: str, owner_id: int, filename: str) -> str:
        """
        Пример: users/avatars/42/a1b2c3d4.jpg
        UUID нужен, чтобы не перезаписывать файлы при повторной загрузке.
        """
        ext = ""
        if "." in filename:
            ext = filename.rsplit(".", 1)[-1].lower()
        suffix = f".{ext}" if ext else ""
        return f"{prefix}/{owner_id}/{uuid4().hex}{suffix}"


class StorageError(Exception):
    """Базовая ошибка при использоании S3-хранилища"""


class ObjectNotFoundError(StorageError):
    """Ошибка, когда запрашиваемого файла нет"""

    def __init__(self, object_name: str):
        self._object_name = object_name

    def __str__(self):
        return f"Файла с именем {self._object_name} не существует"

    def __repr__(self):
        return f"Файла с именем {self._object_name} не существует"
