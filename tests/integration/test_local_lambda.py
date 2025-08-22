#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from moto import mock_aws
import boto3
from lambda_function.lambda_function import lambda_handler

# Set environment variable for S3 bucket (optional)
os.environ['S3_BUCKET'] = 'test-bucket'

def test_single_endpoint():
    """Test /single endpoint"""
    event = {
        'httpMethod': 'GET',
        'path': '/single',
        'queryStringParameters': {
            'fields': 'name,machine_type[sewing,printer],status[active,inactive],user_id[ID,3,int]'
        }
    }
    
    response = lambda_handler(event, {})
    print("=== Single Row Test ===")
    print(f"Status: {response['statusCode']}")
    print(f"Body: {response['body']}")
    print()

@mock_aws
def test_bulk_endpoint():
    """Test /bulk endpoint with mock S3"""
    # Create mock S3 bucket
    s3 = boto3.client('s3', region_name='us-east-1')
    s3.create_bucket(Bucket='test-bucket')
    
    event = {
        'httpMethod': 'POST',
        'path': '/bulk',
        'body': json.dumps({
            'size': 5,
            'bucket': 'test-bucket',
            'dataset_id': 'test_dataset',
            'fields': ['name', 'email', 'company']
        })
    }
    
    response = lambda_handler(event, {})
    print("=== Bulk Data Test (with mock S3) ===")
    print(f"Status: {response['statusCode']}")
    print(f"Body: {response['body']}")
    print()

if __name__ == "__main__":
    test_single_endpoint()
    test_bulk_endpoint()