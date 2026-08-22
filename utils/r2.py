import os
import boto3
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()

CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME", "pmkdaniel-media")
R2_PUBLIC_DOMAIN = os.getenv("R2_PUBLIC_DOMAIN", "https://pub-pmkdaniel.r2.dev").rstrip("/")

def get_r2_client():
    """Return boto3 client configured for Cloudflare R2."""
    if not CLOUDFLARE_ACCOUNT_ID or not R2_ACCESS_KEY_ID or not R2_SECRET_ACCESS_KEY:
        return None

    endpoint_url = f"https://{CLOUDFLARE_ACCOUNT_ID}.r2.cloudflarestorage.com"
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4"),
        region_name="auto"
    )

def upload_to_r2(file_bytes: bytes, filename: str, content_type: str) -> str:
    """
    Upload file bytes to Cloudflare R2 bucket.
    If R2 credentials are not set, saves to local ./uploads directory.
    """
    client = get_r2_client()
    if client:
        client.put_object(
            Bucket=R2_BUCKET_NAME,
            Key=filename,
            Body=file_bytes,
            ContentType=content_type
        )
        return f"{R2_PUBLIC_DOMAIN}/{filename}"
    else:
        # Local file storage fallback
        os.makedirs("./uploads", exist_ok=True)
        file_path = os.path.join("./uploads", filename)
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        return f"/uploads/{filename}"

def delete_from_r2(filename: str) -> bool:
    """Delete file from Cloudflare R2 bucket."""
    client = get_r2_client()
    if client:
        try:
            client.delete_object(Bucket=R2_BUCKET_NAME, Key=filename)
            return True
        except Exception:
            return False
    else:
        file_path = os.path.join("./uploads", filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    return False
