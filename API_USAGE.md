# Mock Data API Usage Guide

## Overview
This API generates mock data using Faker providers and custom field types. It supports both single record generation and bulk data generation with S3 storage.

## Endpoints

### Single Record Generation
- **URL**: `/single`
- **Method**: `GET`
- **Query Parameter**: `fields` - comma-separated list of field definitions

### Bulk Data Generation
- **URL**: `/bulk`
- **Method**: `GET` or `POST`
- **Parameters**: Query parameters (GET) or JSON body (POST)

## Field Types

### Standard Faker Providers
Use any Faker provider name directly:
- `name` - Full name
- `email` - Email address
- `company` - Company name
- `address` - Street address
- `phone_number` - Phone number
- `ean13` - EAN-13 barcode

### Faker Providers with Arguments
Use parentheses to pass arguments to Faker providers:
- `date_of_birth(minimum_age=30,maximum_age=50)` - Date of birth with age constraints
- `random_int(min=1,max=100)` - Random integer in range
- `date_between(start_date='-30y',end_date='today')` - Date in range

### Custom Fields
Use square brackets to define custom field options:
- `machine_type[sewing,printer]` - Random choice from list
- `status[active,inactive,pending]` - Status field with options
- `department[sales,marketing,engineering,hr]` - Department selection

### Prefix Fields
Use square brackets with ID prefix, length, and type:
- `customer_id[ID,6,int]` - Generates "ID123456" (6-digit integer)
- `order_id[ORD,8,int]` - Generates "ORD12345678" (8-digit integer)
- `product_code[PRD,4,str]` - Generates "PRDabcd" (4-character string)

## API Examples

### Single Record Request
```bash
GET /single?fields=name,email,machine_type[sewing,printer],status[active,inactive],customer_id[ID,6,int],date_of_birth(minimum_age=30,maximum_age=50),ean13
```

### Single Record Response
```json
{
  "name": "John Smith",
  "email": "john.smith@example.com",
  "machine_type": "sewing",
  "status": "active",
  "customer_id": "ID123456",
  "date_of_birth": "1985-03-15",
  "ean13": "1234567890123"
}
```

### Bulk Data Request (POST)
```bash
POST /bulk
Content-Type: application/json

{
  "size": 100,
  "bucket": "my-data-bucket",
  "dataset_id": "customer_data_2024",
  "fields": [
    "name",
    "email",
    "company",
    "machine_type[sewing,printer,cutting]",
    "status[active,inactive,pending]",
    "customer_id[ID,6,int]",
    "order_id[ORD,8,int]",
    "date_of_birth(minimum_age=25,maximum_age=65)",
    "phone_number",
    "address",
    "department[sales,marketing,engineering,hr]",
    "ean13"
  ]
}
```

### Bulk Data Request (GET)
```bash
GET /bulk?size=100&bucket=my-data-bucket&dataset_id=customer_data_2024&fields=name,email,company,machine_type[sewing,printer],status[active,inactive],customer_id[ID,6,int]
```

### Bulk Data Response
```json
{
  "message": "Bulk data generated successfully",
  "records_generated": 100,
  "s3_location": "s3://my-data-bucket/customer_data_2024.json",
  "dataset_id": "customer_data_2024"
}
```

### Sample Bulk Data Output
The generated JSON file contains an array of records:
```json
[
  {
    "name": "Alice Johnson",
    "email": "alice.johnson@company.com",
    "company": "Tech Solutions Inc",
    "machine_type": "printer",
    "status": "active",
    "customer_id": "ID789012",
    "order_id": "ORD34567890",
    "date_of_birth": "1982-07-22",
    "phone_number": "+1-555-123-4567",
    "address": "123 Main St, Anytown, ST 12345",
    "department": "engineering",
    "ean13": "9876543210987"
  },
  {
    "name": "Bob Wilson",
    "email": "bob.wilson@example.org",
    "company": "Manufacturing Corp",
    "machine_type": "cutting",
    "status": "pending",
    "customer_id": "ID345678",
    "order_id": "ORD90123456",
    "date_of_birth": "1975-11-08",
    "phone_number": "+1-555-987-6543",
    "address": "456 Oak Ave, Another City, ST 67890",
    "department": "sales",
    "ean13": "5432109876543"
  }
]
```

## Error Responses

### Invalid Field Format
```json
{
  "error": "Invalid field format: invalid_field_name"
}
```

### Missing Required Parameters
```json
{
  "error": "Missing required parameter: size"
}
```

### S3 Upload Error
```json
{
  "error": "Failed to upload to S3: Access denied"
}
```