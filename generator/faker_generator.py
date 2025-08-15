import random
import re
from faker import Faker
import string

fake = Faker()

def parse_field(field_str):
    """
    Parse a field string into:
    - field name
    - custom options list or special instructions
    - faker method args (if any)
    """
    # Check for custom options in square brackets
    bracket_match = re.match(r"(\w+)\[(.+)\]$", field_str)
    if bracket_match:
        name, options_str = bracket_match.groups()
        options = [opt.strip() for opt in options_str.split(",")]
        return name, options, None
    
    # Check for faker method with args in parentheses
    paren_match = re.match(r"(\w+)\((.*)\)$", field_str)
    if paren_match:
        name, args_str = paren_match.groups()
        args = [arg.strip() for arg in args_str.split(",")] if args_str else []
        return name, None, args
    
    # Otherwise just a normal field
    return field_str, None, None

def generate_row(fields):
    row = {}
    for field_str in fields:
        name, options, args = parse_field(field_str)
        
        if options:
            # If options look like [prefix, length] or [prefix, length, type]
            if len(options) >= 2 and options[1].isdigit():
                prefix = options[0]
                length = int(options[1])
                kind = options[2].lower() if len(options) > 2 else "int"

                if kind == "int":
                    random_part = "".join(str(random.randint(0, 9)) for _ in range(length))
                elif kind == "str":
                    random_part = "".join(random.choice(string.ascii_uppercase) for _ in range(length))
                elif kind == "mixed":
                    random_part = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
                else:
                    random_part = "".join(str(random.randint(0, 9)) for _ in range(length))  # fallback to digits

                row[name] = prefix + random_part
            else:
                # regular random choice from list
                row[name] = random.choice(options)
        else:
            try:
                faker_method = getattr(fake, name)
                if args:
                    row[name] = faker_method(*args)
                else:
                    row[name] = faker_method()
            except AttributeError:
                row[name] = fake.word()
    return row

def generate_chunk(fields, size):
    return [generate_row(fields) for _ in range(size)]

def generate_data(fields, size, output_format="json", table_name="mock_data"):
    """Generate data in specified format"""
    from .formatters import format_as_json, format_as_compact_json, format_as_csv, format_as_sql
    
    data = generate_chunk(fields, size)
    
    if output_format.lower() == "json":
        return format_as_json(data)
    elif output_format.lower() == "compact_json":
        return format_as_compact_json(data)
    elif output_format.lower() == "csv":
        return format_as_csv(data)
    elif output_format.lower() == "sql":
        return format_as_sql(data, table_name)
    else:
        return data  # return raw data if format not recognized
