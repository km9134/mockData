import boto3
import io
import csv
import logging
import uuid
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def create_unique_bucket_and_upload(chunk_data, dataset_id, chunk_id):
    s3 = boto3.client("s3")
    
    # Create unique bucket name
    unique_id = str(uuid.uuid4())[:8]
    bucket_name = f"mock-data-{unique_id}"
    key = f"{dataset_id}.json"
    
    logger.info(f"Creating bucket: {bucket_name}")
    
    try:
        # Create bucket
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': 'eu-central-1'}
        )
        logger.info(f"Successfully created bucket: {bucket_name}")
        
        # Convert chunk data to JSON
        json_data = json.dumps(chunk_data, indent=2, default=str)
        
        # Upload to S3
        s3.put_object(Bucket=bucket_name, Key=key, Body=json_data)
        logger.info(f"Successfully uploaded to s3://{bucket_name}/{key}")
        
        return bucket_name, key
    except Exception as e:
        logger.error(f"Failed to create bucket or upload: {str(e)}")
        raise
