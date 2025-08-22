import json
import os
import sys
import logging
from pathlib import Path
from datetime import date, datetime

# Add current directory to path for generator imports
sys.path.insert(0, str(Path(__file__).parent))

logger = logging.getLogger()
logger.setLevel(logging.INFO)

from generator.faker_generator import generate_row, generate_chunk
from generator.s3_uploader import create_unique_bucket_and_upload

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return str(obj)

def lambda_handler(event, context):
    try:
        # Parse the HTTP method and path
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        
        # Parse query parameters and body
        query_params = event.get('queryStringParameters') or {}
        body = event.get('body')
        if body:
            try:
                body = json.loads(body)
            except:
                body = {}
        else:
            body = {}
        
        # Get fields from query params or body
        fields = query_params.get('fields') or body.get('fields')
        if isinstance(fields, str):
            # Split by comma but preserve bracket and parentheses content
            import re
            fields = re.split(r',(?![^\[\(]*[\]\)])', fields)
            fields = [f.strip() for f in fields if f.strip()]
        
        if not fields:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No fields specified'})
            }
        
        # Route to appropriate endpoint
        if path == '/single' or path.endswith('/single'):
            return handle_single_row(fields)
        elif path == '/bulk' or path.endswith('/bulk'):
            return handle_bulk_data(fields, query_params, body)
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Endpoint not found'})
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def handle_single_row(fields):
    """Return a single row of mock data"""
    row = generate_row(fields)
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(row, cls=CustomJSONEncoder)
    }

def handle_bulk_data(fields, query_params, body):
    """Generate bulk data and save to S3"""
    # Get parameters
    size = int(query_params.get('size') or body.get('size', 100))
    dataset_id = query_params.get('dataset_id') or body.get('dataset_id', 'mock_dataset')
    
    logger.info(f"Bulk request: size={size}, dataset_id={dataset_id}")
    
    try:
        # Generate data
        logger.info(f"Generating {size} rows with {len(fields)} fields")
        data = generate_chunk(fields, size)
        
        # Create unique bucket and upload to S3
        bucket_name, s3_key = create_unique_bucket_and_upload(data, dataset_id, 'bulk')
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'message': f'Generated {size} rows',
                's3_location': f's3://{bucket_name}/{s3_key}',
                'bucket_name': bucket_name,
                'records_count': len(data)
            })
        }
    except Exception as e:
        logger.error(f"Error in bulk data generation: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }