import json
import uuid
import boto3
from concurrent.futures import ThreadPoolExecutor
from generator.s3_uploader import upload_chunk_to_s3
from generator.faker_generator import generate_chunk

CHUNK_SIZE = 5000  # rows per chunk
AWS_REGION = "eu-west-1"  # adjust for your environment

def lambda_handler(event, context):
    s3 = boto3.client("s3", region_name=AWS_REGION)

    # 1. Generate unique bucket name
    bucket_name = f"fake-data-{uuid.uuid4().hex[:8]}"

    # 2. Create bucket
    s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={"LocationConstraint": AWS_REGION}
    )

    fields = event.get("fields", ["name", "email"])
    num_rows = event.get("rows", 10000)
    dataset_id = event.get("dataset_id", "dataset1")

    # 3. Calculate chunks
    num_chunks = (num_rows + CHUNK_SIZE - 1) // CHUNK_SIZE
    uploaded_keys = []

    # 4. Generate + Upload in parallel
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = []
        for chunk_id in range(num_chunks):
            size = min(CHUNK_SIZE, num_rows - chunk_id * CHUNK_SIZE)
            chunk_data = generate_chunk(fields, size)
            futures.append(
                executor.submit(upload_chunk_to_s3, chunk_data, bucket_name, dataset_id, chunk_id)
            )

        for f in futures:
            uploaded_keys.append(f.result())

    # 5. Return bucket and keys
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Dataset generated successfully",
            "bucket": bucket_name,
            "chunks": uploaded_keys
        })
    }
