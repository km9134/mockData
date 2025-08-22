import unittest
import json
import csv
import io
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lambda_function.generator.formatters import format_as_json, format_as_compact_json, format_as_csv, format_as_sql


class TestFormatters(unittest.TestCase):

    def test_format_as_json(self):
        data = [{"name": "John", "status": "active"}]
        result = format_as_json(data)
        
        with open("/Users/kylemoffett/Documents/Development/mockDataLambda/tests/testOutputs/formatter_json.json", "w") as f:
            f.write(result)
        
        # Validate by reading file
        with open("/Users/kylemoffett/Documents/Development/mockDataLambda/tests/testOutputs/formatter_json.json", "r") as f:
            loaded = json.load(f)
        
        self.assertEqual(loaded[0]["name"], "John")
        self.assertIn('\n', result)  # pretty formatted

    def test_format_as_compact_json(self):
        data = [{"name": "Jane", "status": "inactive"}]
        result = format_as_compact_json(data)
        
        with open("/Users/kylemoffett/Documents/Development/mockDataLambda/tests/testOutputs/formatter_compact.json", "w") as f:
            f.write(result)
        
        # Validate by reading file
        with open("/Users/kylemoffett/Documents/Development/mockDataLambda/tests/testOutputs/formatter_compact.json", "r") as f:
            loaded = json.load(f)
        
        self.assertEqual(loaded[0]["name"], "Jane")
        self.assertNotIn(': ', result)  # compact format

    def test_format_as_csv(self):
        data = [{"name": "Bob", "age": 30}, {"name": "Alice", "age": 25}]
        result = format_as_csv(data)
        
        with open("/Users/kylemoffett/Documents/Development/mockDataLambda/tests/testOutputs/formatter_output.csv", "w") as f:
            f.write(result)
        
        # Validate by reading file
        with open("/Users/kylemoffett/Documents/Development/mockDataLambda/tests/testOutputs/formatter_output.csv", "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["name"], "Bob")
        self.assertEqual(rows[1]["age"], "25")

    def test_format_as_csv_empty(self):
        result = format_as_csv([])
        self.assertEqual(result, "")

    def test_format_as_sql(self):
        data = [{"name": "Charlie", "status": "active"}, {"name": "Diana", "status": "inactive"}]
        result = format_as_sql(data, "test_users")
        
        with open("/Users/kylemoffett/Documents/Development/mockDataLambda/tests/testOutputs/formatter_output.sql", "w") as f:
            f.write(result)
        
        # Validate by reading file
        with open("/Users/kylemoffett/Documents/Development/mockDataLambda/tests/testOutputs/formatter_output.sql", "r") as f:
            content = f.read()
        
        self.assertIn("INSERT INTO test_users", content)
        self.assertIn("'Charlie'", content)
        self.assertIn("VALUES", content)
        self.assertTrue(content.endswith(";"))

    def test_format_as_sql_empty(self):
        result = format_as_sql([])
        self.assertEqual(result, "")

    def test_format_as_sql_with_quotes(self):
        data = [{"name": "O'Connor", "note": "It's great"}]
        result = format_as_sql(data, "quotes_test")
        
        with open("/Users/kylemoffett/Documents/Development/mockDataLambda/tests/testOutputs/formatter_quotes.sql", "w") as f:
            f.write(result)
        
        # Validate by reading file
        with open("/Users/kylemoffett/Documents/Development/mockDataLambda/tests/testOutputs/formatter_quotes.sql", "r") as f:
            content = f.read()
        
        self.assertIn("'O''Connor'", content)  # escaped quotes
        self.assertIn("'It''s great'", content)

    def test_format_as_json_with_indent(self):
        data = [{"test": "value"}]
        result = format_as_json(data, indent=4)
        self.assertIn('    "test"', result)  # 4-space indent


if __name__ == '__main__':
    unittest.main()