import json
import os
from generator.faker_generator import generate_row, generate_chunk
from generator.s3_uploader import upload_chunk_to_s3

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
            # Split by comma but preserve bracket content
            import re
            fields = re.findall(r'[^,\[]*(?:\[[^\]]*\])?[^,]*', fields)
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
        'body': json.dumps(row)
    }

def handle_bulk_data(fields, query_params, body):
    """Generate bulk data and save to S3"""
    # Get parameters
    size = int(query_params.get('size') or body.get('size', 100))
    bucket_name = query_params.get('bucket') or body.get('bucket') or os.environ.get('S3_BUCKET')
    dataset_id = query_params.get('dataset_id') or body.get('dataset_id', 'mock_dataset')
    
    if not bucket_name:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'S3 bucket name required'})
        }
    
    # Generate data
    data = generate_chunk(fields, size)
    
    # Upload to S3
    s3_key = upload_chunk_to_s3(data, bucket_name, dataset_id, 'bulk')
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'message': f'Generated {size} rows',
            's3_location': f's3://{bucket_name}/{s3_key}',
            'records_count': len(data)
        })
    }