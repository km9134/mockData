import json
import csv
from io import StringIO

def format_as_json(data, indent=2):
    """Format data as pretty JSON"""
    return json.dumps(data, indent=indent)

def format_as_compact_json(data):
    """Format data as compact JSON"""
    return json.dumps(data, separators=(',', ':'))

def format_as_csv(data):
    """Format data as CSV"""
    if not data:
        return ""
    
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()

def format_as_sql(data, table_name="mock_data"):
    """Format data as SQL INSERT statements"""
    if not data:
        return ""
    
    columns = list(data[0].keys())
    column_names = ", ".join(columns)
    
    sql_lines = [f"INSERT INTO {table_name} ({column_names}) VALUES"]
    
    for i, row in enumerate(data):
        values = []
        for col in columns:
            value = row[col]
            if isinstance(value, str):
                # Escape single quotes in strings
                escaped_value = value.replace("'", "''")
                values.append(f"'{escaped_value}'")
            else:
                values.append(str(value))
        
        value_str = f"({', '.join(values)})"
        if i < len(data) - 1:
            value_str += ","
        else:
            value_str += ";"
        
        sql_lines.append(f"  {value_str}")
    
    return "\n".join(sql_lines)