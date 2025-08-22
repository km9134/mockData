import boto3
import io
import csv
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def upload_chunk_to_s3(chunk_data, bucket_name, dataset_id, chunk_id):
    s3 = boto3.client("s3")
    key = f"{dataset_id}/chunk_{chunk_id}.csv"
    
    logger.info(f"Attempting to upload to bucket: {bucket_name}, key: {key}")

    try:
        # Convert chunk data to CSV in memory
        csv_buffer = io.StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=chunk_data[0].keys())
        writer.writeheader()
        writer.writerows(chunk_data)

        s3.put_object(Bucket=bucket_name, Key=key, Body=csv_buffer.getvalue())
        logger.info(f"Successfully uploaded to s3://{bucket_name}/{key}")
        return key
    except Exception as e:
        logger.error(f"Failed to upload to S3: {str(e)}")
        raise
