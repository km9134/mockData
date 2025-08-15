import unittest
import json
import csv
import io
import time
from generator.faker_generator import generate_row, generate_chunk, generate_data


class TestFakerGenerator(unittest.TestCase):

    def test_generate_row_with_faker_field(self):
        result = generate_row(["name"])
        self.assertIn("name", result)
        self.assertIsInstance(result["name"], str)

    def test_generate_row_with_custom_field_descriptor(self):
        result = generate_row(["machine_type[sewing,printer]"])
        
        self.assertIn("machine_type", result)
        self.assertIn(result["machine_type"], ["sewing", "printer"])

    def test_generate_row_fallback_to_word(self):
        result = generate_row(["nonexistent_field"])
        self.assertIn("nonexistent_field", result)
        self.assertIsInstance(result["nonexistent_field"], str)

    def test_generate_chunk(self):
        fields = [
        "name",
        "username[HS,4,int]",
        "status[active,inactive,pending]", 
        "barcode[Tx,8,str]"
        ]
        result = generate_chunk(fields, 100)
        
        with open("/Users/kylemoffett/Documents/Development/mockDataLambda/test_output.json", "w") as f:
            json.dump(result, f, indent=2)
        
        self.assertEqual(len(result), 100)
        for row in result:
            self.assertEqual(len(row), 4)
            self.assertIn("name", row)

            self.assertIn("username", row)
            self.assertTrue(row["username"].startswith("HS"))
            self.assertTrue(row["username"][2:].isdigit())
            self.assertEqual(len(row["username"]), 6)

            self.assertIn("barcode", row)
            self.assertTrue(row["barcode"].startswith("Tx"))
            self.assertTrue(row["barcode"][2:].isalpha())
            self.assertEqual(len(row["barcode"]), 10)

            self.assertIn("status", row)
            self.assertIn(row["status"], ["active", "inactive", "pending"])

    def test_json_format(self):
        result = generate_data(["name", "status[active,inactive]"], 5, "json")
        with open("/Users/kylemoffett/Documents/Development/mockDataLambda/tests/testOutputs/output.json", "w") as f:
            f.write(result)
        
        # Validate JSON syntax
        json.loads(result)
        self.assertIsInstance(result, str)
        self.assertIn('"name":', result)
        self.assertIn('"status":', result)

    def test_compact_json_format(self):
        result = generate_data(["name", "email"], 5, "compact_json")
        with open("/Users/kylemoffett/Documents/Development/mockDataLambda/tests/testOutputs/output_compact.json", "w") as f:
            f.write(result)
        
        # Validate JSON syntax
        json.loads(result)
        self.assertIsInstance(result, str)
        self.assertNotIn('\n', result)
        self.assertNotIn(': ', result)  # no space after colons

    def test_csv_format(self):
        result = generate_data(["name", "email", "username[USR,4,int]"], 5, "csv")
        with open("/Users/kylemoffett/Documents/Development/mockDataLambda/tests/testOutputs/output.csv", "w") as f:
            f.write(result)
        
        # Validate CSV syntax
        csv.reader(io.StringIO(result))
        rows = list(csv.reader(io.StringIO(result)))
        self.assertEqual(len(rows), 6)  # header + 5 rows
        self.assertIsInstance(result, str)
        self.assertIn("name,email", result)

    def test_sql_format(self):
        result = generate_data(["name", "status[active,inactive]", "user_id[ID,3,int]"], 5, "sql", "users")
        with open("/Users/kylemoffett/Documents/Development/mockDataLambda/tests/testOutputs/output.sql", "w") as f:
            f.write(result)
        
        # Basic SQL syntax validation
        self.assertIn("INSERT INTO users", result)
        self.assertIn("VALUES", result)
        self.assertIn(";", result)
        self.assertTrue(result.count("(") == result.count(")"))  # balanced parentheses

    def test_performance_10000_rows(self):
        fields = [
            "name",
            "email", 
            "address",
            "phone_number",
            "company",
            "job",
            "priority[critical,high,medium,low,none]",
            "product_code[PROD,10,str]"
        ]
        
        start_time = time.time()
        result = generate_chunk(fields, 10000)
        chunk_time = time.time() - start_time
        
        # Test SQL generation time
        start_time = time.time()
        sql_result = generate_data(fields, 10000, "sql", "performance_test")
        sql_time = time.time() - start_time
        
        with open("/Users/kylemoffett/Documents/Development/mockDataLambda/tests/testOutputs/performance_10000.sql", "w") as f:
            f.write(sql_result)
        
        total_time = chunk_time + sql_time
        
        # Save timing info to file for inspection
        with open("/Users/kylemoffett/Documents/Development/mockDataLambda/tests/testOutputs/performance.txt", "w") as f:
            f.write(f"Generated 10000 rows with 8 columns in {chunk_time:.4f} seconds\n")
            f.write(f"SQL formatting took {sql_time:.4f} seconds\n")
            f.write(f"Total time: {total_time:.4f} seconds\n")
            f.write(f"Average time per row: {total_time/100:.6f} seconds\n")
        
        self.assertEqual(len(result), 10000)
        self.assertLess(total_time, 20.0)  # Should complete within 5 seconds
        for row in result:
            self.assertEqual(len(row), 8)
            self.assertIn(row["priority"], ["critical", "high", "medium", "low", "none"])
            self.assertTrue(row["product_code"].startswith("PROD"))
            self.assertEqual(len(row["product_code"]), 14)  # PROD + 10 chars


if __name__ == '__main__':
    unittest.main()