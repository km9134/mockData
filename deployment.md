# CDK Deployment Guide

## Prerequisites
- AWS CLI configured with credentials
- Node.js installed
- CDK CLI installed: `npm install -g aws-cdk`
- Colima (lightweight Docker alternative): `brew install colima`

## Setup (First Time)
```bash
cd cdk
npm install
pip3 install -r requirements.txt
cdk bootstrap
```

## Deployment Workflow

### 1. Start Colima (lightweight Docker)
```bash
colima start --disk 8
```

### 2. Generate CloudFormation Template
```bash
cdk synth
```

### 3. Check Changes (Always review before deploying)
```bash
cdk diff --verbose
```

### 4. Deploy
```bash
cdk deploy
```

### 5. Stop Colima (save resources)
```bash
colima stop
```

**Note:** Colima uses ~100MB RAM vs Docker Desktop's ~2GB. PythonFunction automatically bundles dependencies (faker, boto3, etc.) using the Docker API.

## Cleanup
```bash
cdk destroy
```

## Endpoints After Deployment
- `GET /data` - Returns mock data directly (≤200 data points)
- `POST /bulk` - Returns S3 location for large datasets

## Example Usage
```bash
# Get 10 rows of data
curl "https://your-api-url/data?fields=name,email&rows=10"

# Generate bulk data to S3
curl -X POST "https://your-api-url/bulk" \
  -H "Content-Type: application/json" \
  -d '{"fields":["name","email"],"size":1000}'
```