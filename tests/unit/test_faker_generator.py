import unittest
import json
import csv
import io
import time
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lambda_function.generator.faker_generator import generate_row, generate_chunk, generate_data, parse_field


class TestFakerGenerator(unittest.TestCase):

    def test_parse_field_with_brackets(self):
        name, options, args = parse_field("status[active,inactive]")
        self.assertEqual(name, "status")
        self.assertEqual(options, ["active", "inactive"])
        self.assertIsNone(args)

    def test_parse_field_with_parentheses(self):
        name, options, args = parse_field("date_between(start_date=-30d,end_date=today)")
        self.assertEqual(name, "date_between")
        self.assertIsNone(options)
        self.assertEqual(args, ["start_date=-30d", "end_date=today"])

    def test_parse_field_simple(self):
        name, options, args = parse_field("name")
        self.assertEqual(name, "name")
        self.assertIsNone(options)
        self.assertIsNone(args)

    def test_generate_row_with_faker_field(self):
        result = generate_row(["name"])
        self.assertIn("name", result)
        self.assertIsInstance(result["name"], str)

    def test_generate_row_with_custom_field_descriptor(self):
        result = generate_row(["machine_type[sewing,printer]"])
        
        self.assertIn("machine_type", result)
        self.assertIn(result["machine_type"], ["sewing", "printer"])

    def test_generate_row_with_prefix_int(self):
        result = generate_row(["user_id[ID,3,int]"])
        self.assertIn("user_id", result)
        self.assertTrue(result["user_id"].startswith("ID"))
        self.assertTrue(result["user_id"][2:].isdigit())
        self.assertEqual(len(result["user_id"]), 5)

    def test_generate_row_with_prefix_str(self):
        result = generate_row(["code[ABC,4,str]"])
        self.assertIn("code", result)
        self.assertTrue(result["code"].startswith("ABC"))
        self.assertTrue(result["code"][3:].isalpha())
        self.assertEqual(len(result["code"]), 7)

    def test_generate_row_with_prefix_mixed(self):
        result = generate_row(["token[TK,5,mixed]"])
        self.assertIn("token", result)
        self.assertTrue(result["token"].startswith("TK"))
        self.assertEqual(len(result["token"]), 7)

    def test_generate_row_with_prefix_unknown_type(self):
        result = generate_row(["test[PRE,3,unknown]"])
        self.assertIn("test", result)
        self.assertTrue(result["test"].startswith("PRE"))
        self.assertTrue(result["test"][3:].isdigit())  # fallback to digits

    def test_generate_row_with_faker_method_args(self):
        result = generate_row(["date_of_birth(minimum_age=30,maximum_age=50)"])
        self.assertIn("date_of_birth", result)
        from datetime import date
        self.assertIsInstance(result["date_of_birth"], date)

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
        
        with open("/Users/kylemoffett/Documents/Development/mockDataLambda/tests/testOutputs/test_output.json", "w") as f:
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


    def test_default_format_is_compact_json(self):
        result = generate_data(["name"], 1)
        self.assertIsInstance(result, str)
        self.assertNotIn(': ', result)  # compact format
        self.assertIn('"name":', result)

    def test_generate_data_csv_format(self):
        result = generate_data(["name", "email"], 2, "csv")
        self.assertIsInstance(result, str)
        self.assertIn("name", result)
        self.assertIn(",", result)  # CSV format

    def test_generate_data_sql_with_non_string_values(self):
        result = generate_data(["name", "random_int(min=1,max=100)"], 2, "sql")
        self.assertIsInstance(result, str)
        self.assertIn("INSERT INTO", result)
        self.assertIn("name", result)
        self.assertIn("random_int", result)

    def test_generate_row_with_positional_args(self):
        result = generate_row(["random_int(1,100)"])
        self.assertIn("random_int", result)
        self.assertIsInstance(result["random_int"], int)
        self.assertGreaterEqual(result["random_int"], 1)
        self.assertLessEqual(result["random_int"], 100)

    def test_unknown_format_fallback(self):
        result = generate_data(["name"], 1, "unknown_format_xyz")
        self.assertIsInstance(result, str)
        import json
        parsed = json.loads(result)
        self.assertIn("name", parsed[0])

    def test_generate_row_with_string_positional_args(self):
        result = generate_row(["passport_owner(M)"])
        self.assertIn("passport_owner", result)
        self.assertIsInstance(result["passport_owner"], tuple)
        self.assertEqual(len(result["passport_owner"]), 2)

    def test_generate_row_with_mixed_args(self):
        result = generate_row(["bothify(##-??,letters)"])
        self.assertIn("bothify", result)
        self.assertIsInstance(result["bothify"], str)

    def test_generate_row_positional_and_keyword_args(self):
        # Tests line 69: faker_method(*kwargs.pop('args'), **kwargs)
        result = generate_row(["date_between(-30d,end_date=today)"])
        self.assertIn("date_between", result)
        from datetime import date
        self.assertIsInstance(result["date_between"], date)

    def test_generate_row_keyword_only_args(self):
        # Tests line 72 (else branch): faker_method(**kwargs)
        result = generate_row(["random_int(min=1,max=100)"])
        self.assertIn("random_int", result)
        self.assertIsInstance(result["random_int"], int)
        self.assertGreaterEqual(result["random_int"], 1)
        self.assertLessEqual(result["random_int"], 100)

if __name__ == '__main__':
    unittest.main()