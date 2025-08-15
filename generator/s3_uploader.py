import boto3
import io
import csv

def upload_chunk_to_s3(chunk_data, bucket_name, dataset_id, chunk_id):
    s3 = boto3.client("s3")
    key = f"{dataset_id}/chunk_{chunk_id}.csv"

    # Convert chunk data to CSV in memory
    csv_buffer = io.StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=chunk_data[0].keys())
    writer.writeheader()
    writer.writerows(chunk_data)

    s3.put_object(Bucket=bucket_name, Key=key, Body=csv_buffer.getvalue())
    return key
