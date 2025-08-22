import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lambda_function.generator.s3_uploader import create_unique_bucket_and_upload


class TestS3Uploader(unittest.TestCase):
    """Test cases for S3 uploader functionality"""

    @patch('lambda_function.generator.s3_uploader.boto3.client')
    @patch('lambda_function.generator.s3_uploader.uuid.uuid4')
    def test_create_unique_bucket_and_upload(self, mock_uuid, mock_boto3_client):
        # Setup mocks
        mock_s3 = MagicMock()
        mock_boto3_client.return_value = mock_s3
        mock_uuid.return_value = MagicMock()
        mock_uuid.return_value.__str__ = MagicMock(return_value='12345678-1234-1234-1234-123456789012')
        
        # Test data
        chunk_data = [
            {"name": "John", "age": 30},
            {"name": "Jane", "age": 25}
        ]
        dataset_id = "test-dataset"
        chunk_id = "bulk"
        
        # Call the function
        bucket_name, s3_key = create_unique_bucket_and_upload(chunk_data, dataset_id, chunk_id)
        
        # Verify bucket creation
        mock_s3.create_bucket.assert_called_once()
        create_call_args = mock_s3.create_bucket.call_args
        self.assertTrue(create_call_args[1]['Bucket'].startswith('mock-data-'))
        
        # Verify upload
        mock_s3.put_object.assert_called_once()
        upload_call_args = mock_s3.put_object.call_args
        self.assertEqual(upload_call_args[1]['Key'], f"{dataset_id}.json")
        
        # Verify return values
        self.assertTrue(bucket_name.startswith('mock-data-'))
        self.assertEqual(s3_key, f"{dataset_id}.json")
    
    @patch('lambda_function.generator.s3_uploader.boto3.client')
    def test_create_unique_bucket_and_upload_error(self, mock_boto3_client):
        # Setup mock to raise exception
        mock_s3 = MagicMock()
        mock_s3.create_bucket.side_effect = Exception("S3 Error")
        mock_boto3_client.return_value = mock_s3
        
        chunk_data = [{"name": "John"}]
        
        with self.assertRaises(Exception):
            create_unique_bucket_and_upload(chunk_data, "test", "bulk")


if __name__ == '__main__':
    unittest.main()