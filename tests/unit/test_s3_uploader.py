import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lambda_function.generator.s3_uploader import upload_chunk_to_s3


class TestS3Uploader(unittest.TestCase):
    """Test cases for S3 uploader functionality"""

    @patch('lambda_function.generator.s3_uploader.boto3.client')  # Mock boto3 to avoid real AWS calls
    def test_upload_chunk_to_s3(self, mock_boto3_client):
        # Setup mock S3 client
        mock_s3 = MagicMock()
        mock_boto3_client.return_value = mock_s3
        
        # Test data - sample chunk with 2 records
        chunk_data = [
            {"name": "John", "age": 30},
            {"name": "Jane", "age": 25}
        ]
        bucket_name = "test-bucket"
        dataset_id = "test-dataset"
        chunk_id = 1
        
        # Call the function under test
        result = upload_chunk_to_s3(chunk_data, bucket_name, dataset_id, chunk_id)
        
        # Verify boto3.client was called correctly
        mock_boto3_client.assert_called_once_with("s3")
        mock_s3.put_object.assert_called_once()
        
        # Check S3 upload parameters
        call_args = mock_s3.put_object.call_args
        self.assertEqual(call_args[1]['Bucket'], bucket_name)  # Correct bucket
        self.assertEqual(call_args[1]['Key'], f"{dataset_id}/chunk_{chunk_id}.csv")  # Proper key format
        self.assertIn("name,age", call_args[1]['Body'])  # CSV header present
        self.assertIn("John,30", call_args[1]['Body'])  # First record
        self.assertIn("Jane,25", call_args[1]['Body'])  # Second record
        
        # Verify function returns expected S3 key
        self.assertEqual(result, f"{dataset_id}/chunk_{chunk_id}.csv")


if __name__ == '__main__':
    unittest.main()