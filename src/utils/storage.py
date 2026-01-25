"""Cloudflare R2 storage management"""
import boto3
import os
import logging
from botocore.exceptions import ClientError
from botocore.config import Config

# Use singleton pattern for S3 client
_s3_client = None

def _get_s3_client():
    """Get or create S3 client with optimized config"""
    global _s3_client
    if _s3_client is None:
        account_id = os.getenv('R2_ACCOUNT_ID')
        access_key = os.getenv('R2_ACCESS_KEY')
        secret_key = os.getenv('R2_SECRET_KEY')
        
        # Optimize client config for memory and performance
        config = Config(
            max_pool_connections=1,  # Reduce connection pool
            tcp_keepalive=True,
            retries={'max_attempts': 2, 'mode': 'adaptive'}
        )
        
        _s3_client = boto3.client(
            's3',
            endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name='auto',
            config=config
        )
    return _s3_client

def upload_to_r2(local_file_path, filename):
    """Upload file to Cloudflare R2 with streaming for memory efficiency"""
    try:
        client = _get_s3_client()
        bucket_name = os.getenv('R2_BUCKET')
        account_id = os.getenv('R2_ACCOUNT_ID')
        
        logging.info(f"Uploading {filename} to R2")
        
        # Stream upload instead of loading entire file
        with open(local_file_path, 'rb') as f:
            client.upload_fileobj(
                f,
                bucket_name,
                filename,
                ExtraArgs={'ContentType': 'video/mp4'}
            )
        
        # Generate public URL from environment variable
        public_url = os.getenv('R2_BUCKET_PUBLIC_DEV_URL')
        if not public_url:
            raise ValueError("R2_BUCKET_PUBLIC_DEV_URL environment variable is not set")
        url = f"{public_url}/{filename}"
        logging.info(f"Successfully uploaded: {filename}")
        return url
        
    except ClientError as e:
        logging.error(f"R2 upload failed: {e}")
        return None
    except Exception as e:
        logging.error(f"Upload error: {e}")
        return None
