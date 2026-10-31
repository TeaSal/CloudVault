import os
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=os.getenv("S3_ENDPOINT", "http://localhost:9000"),
        aws_access_key_id=os.getenv("S3_ACCESS_KEY", "cloudvault"),
        aws_secret_access_key=os.getenv("S3_SECRET_KEY", "cloudvault-local-secret"),
        region_name=os.getenv("S3_REGION", "us-east-1"),
        config=Config(signature_version="s3v4"),
    )

def ensure_bucket(client, bucket):
    try:
        client.head_bucket(Bucket=bucket)
    except ClientError:
        client.create_bucket(Bucket=bucket)

def list_objects(client, bucket):
    response = client.list_objects_v2(Bucket=bucket)
    result = []
    for obj in response.get("Contents", []):
        result.append({
            "key": obj["Key"],
            "name": obj["Key"].split("_", 1)[-1],
            "size_bytes": obj["Size"],
            "size": format_size(obj["Size"]),
            "modified": obj["LastModified"].strftime("%d %b %Y, %H:%M"),
        })
    return sorted(result, key=lambda x: x["modified"], reverse=True)

def upload_object(client, bucket, key, file_storage):
    client.upload_fileobj(
        file_storage,
        bucket,
        key,
        ExtraArgs={"ContentType": file_storage.mimetype or "application/octet-stream"},
    )

def download_object(client, bucket, key):
    response = client.get_object(Bucket=bucket, Key=key)
    data = response["Body"].read()
    filename = key.split("_", 1)[-1]
    return data, response.get("ContentType", "application/octet-stream"), filename

def delete_object(client, bucket, key):
    client.delete_object(Bucket=bucket, Key=key)

def format_size(size):
    if size < 1024:
        return f"{size} B"
    if size < 1024**2:
        return f"{size / 1024:.1f} KB"
    if size < 1024**3:
        return f"{size / (1024**2):.1f} MB"
    return f"{size / (1024**3):.2f} GB"
