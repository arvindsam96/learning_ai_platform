import boto3
from botocore.exceptions import ClientError
from app.core.config import settings

class S3Client:
    def __init__(self):
        if settings.S3_ACCESS_KEY_ID and settings.S3_SECRET_ACCESS_KEY:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.S3_ACCESS_KEY_ID,
                aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
        else:
            # Use IAM roles or instance profile in AWS environment
            self.s3_client = boto3.client('s3', region_name=settings.AWS_REGION)

    async def upload_file(self, file_content: bytes, key: str, content_type: str = None) -> str:
        """Upload file to S3 and return the S3 URL"""
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type

            self.s3_client.put_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=key,
                Body=file_content,
                **extra_args
            )
            return f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
        except ClientError as e:
            raise Exception(f"Failed to upload file to S3: {str(e)}")

    async def download_file(self, key: str) -> bytes:
        """Download file from S3"""
        try:
            response = self.s3_client.get_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
            return response['Body'].read()
        except ClientError as e:
            raise Exception(f"Failed to download file from S3: {str(e)}")

    async def delete_file(self, key: str) -> None:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
        except ClientError as e:
            raise Exception(f"Failed to delete file from S3: {str(e)}")

    def is_available(self) -> bool:
        """Check if S3 is available and configured"""
        return bool(settings.S3_BUCKET_NAME)
