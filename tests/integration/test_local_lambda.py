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
    """Test /data endpoint with multiple rows"""
    event = {
        'httpMethod': 'GET',
        'path': '/data',
        'queryStringParameters': {
            'fields': 'name,machine_type[sewing,printer],status[active,inactive],user_id[ID,3,int]',
            'rows': '3'
        }
    }
    
    response = lambda_handler(event, {})
    print(f"Debug - Status: {response['statusCode']}, Body: {response.get('body', 'No body')}")
    assert response['statusCode'] == 200
    data = json.loads(response['body'])
    assert len(data) == 3
    assert all('name' in row for row in data)
    assert all(row['machine_type'] in ['sewing', 'printer'] for row in data)
    assert all(row['status'] in ['active', 'inactive'] for row in data)
    assert all(row['user_id'].startswith('ID') for row in data)
    print(f"✓ Generated {len(data)} rows with correct structure")

@mock_aws
def test_bulk_endpoint():
    """Test /bulk endpoint with mock S3"""
    event = {
        'httpMethod': 'POST',
        'path': '/bulk',
        'body': json.dumps({
            'size': 5,
            'dataset_id': 'test_dataset',
            'fields': ['name', 'email', 'company']
        })
    }
    
    response = lambda_handler(event, {})
    assert response['statusCode'] == 200
    data = json.loads(response['body'])
    assert 'message' in data
    assert 's3_location' in data
    assert data['records_count'] == 5
    print("✓ Bulk endpoint created S3 file with correct record count")

def test_single_endpoint_200_limit():
    """Test /data endpoint 200 data point limit"""
    event = {
        'httpMethod': 'GET',
        'path': '/data',
        'queryStringParameters': {
            'fields': 'name,email',
            'rows': '101'  # 2 * 101 = 202 > 200
        }
    }
    
    response = lambda_handler(event, {})
    assert response['statusCode'] == 400
    error_data = json.loads(response['body'])
    assert 'error' in error_data
    assert 'exceeds limit of 200' in error_data['error']
    print("✓ 200 data point limit enforced correctly")

def test_single_endpoint_max_data():
    """Test /data endpoint at 200 data point limit"""
    event = {
        'httpMethod': 'GET',
        'path': '/data',
        'queryStringParameters': {
            'fields': 'name,email,phone,age',
            'rows': '50'  # 4 * 50 = 200
        }
    }
    
    response = lambda_handler(event, {})
    assert response['statusCode'] == 200
    data = json.loads(response['body'])
    assert len(data) == 50
    assert len(data[0]) == 4  # 4 fields
    assert len(data) * len(data[0]) == 200
    print(f"✓ Generated exactly 200 data points ({len(data)} × {len(data[0])})")

def test_single_endpoint_no_rows():
    """Test /data endpoint without rows parameter (default behavior)"""
    event = {
        'httpMethod': 'GET',
        'path': '/data',
        'queryStringParameters': {
            'fields': 'name,email'
        }
    }
    
    response = lambda_handler(event, {})
    assert response['statusCode'] == 200
    data = json.loads(response['body'])
    assert isinstance(data, dict)  # Single object, not array
    assert 'name' in data
    assert 'email' in data
    print("✓ Default behavior returns single object")

def test_missing_fields():
    """Test error handling for missing fields"""
    event = {
        'httpMethod': 'GET',
        'path': '/data',
        'queryStringParameters': {}
    }
    
    response = lambda_handler(event, {})
    assert response['statusCode'] == 400
    error_data = json.loads(response['body'])
    assert 'error' in error_data
    assert 'No fields specified' in error_data['error']
    print("✓ Missing fields error handled correctly")

def test_invalid_endpoint():
    """Test 404 for invalid endpoint"""
    event = {
        'httpMethod': 'GET',
        'path': '/invalid',
        'queryStringParameters': {'fields': 'name'}
    }
    
    response = lambda_handler(event, {})
    assert response['statusCode'] == 404
    error_data = json.loads(response['body'])
    assert 'error' in error_data
    assert 'Endpoint not found' in error_data['error']
    print("✓ Invalid endpoint returns 404")

if __name__ == "__main__":
    print("Starting tests...")
    test_single_endpoint()
    test_single_endpoint_200_limit()
    test_single_endpoint_max_data()
    test_single_endpoint_no_rows()
    test_missing_fields()
    test_invalid_endpoint()
    test_bulk_endpoint()
    print("Tests completed.")