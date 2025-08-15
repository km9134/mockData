# Field Descriptors Guide

This guide explains how to specify fields for mock data generation using our field descriptor format.

## Basic Format

Send an array of field descriptors as strings. Each field can be one of three types:

## 1. Faker Provider Fields

Use any Faker provider method directly as a field name:

```json
["name", "email", "address", "phone_number", "company"]
```

**Common Faker providers:**
- `name` - Full name
- `first_name` - First name only
- `last_name` - Last name only
- `email` - Email address
- `phone_number` - Phone number
- `address` - Street address
- `city` - City name
- `country` - Country name
- `company` - Company name
- `job` - Job title
- `date` - Random date
- `ean13` - Barcode number

## 2. Custom Choice Fields

Select randomly from a predefined list of options:

```json
["status[active,inactive,pending]", "priority[high,medium,low]"]
```

**Format:** `fieldname[option1,option2,option3]`

**Examples:**
- `"machine_type[printer,scanner,copier]"`
- `"department[sales,marketing,engineering,hr]"`
- `"color[red,blue,green,yellow]"`

## 3. Custom Random Fields

Generate random strings with prefixes and specified length:

```json
["username[HS,4,int]", "barcode[TX,8,str]"]
```

**Format:** `fieldname[prefix,length,type]`

**Parameters:**
- `prefix` - Text to prepend
- `length` - Number of random characters
- `type` - Either `int` (digits) or `str` (letters)

**Examples:**
- `"username[HS,4,int]"` → `"HS1234"`
- `"product_code[TX,6,str]"` → `"TXabcdef"`
- `"serial[SN,8,int]"` → `"SN12345678"`

## Complete Example

```json
[
  "name",
  "email", 
  "department[sales,marketing,engineering]",
  "employee_id[EMP,5,int]",
  "status[active,inactive]"
]
```

**Sample Output:**
```json
{
  "name": "John Smith",
  "email": "john.smith@example.com",
  "department": "engineering",
  "employee_id": "EMP12345",
  "status": "active"
}
```

## Fallback Behavior

If a field name doesn't match any Faker provider, the system will generate a random word as fallback.