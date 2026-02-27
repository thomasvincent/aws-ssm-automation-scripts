# Shared Modules for AWS SSM Automation

This directory contains shared modules that can be used across SSM automation documents.

## Python Modules

The `python` directory contains shared Python modules that provide common functionality:

### aws_helpers.py

General AWS helper functions for SSM automation documents:

- `setup_logging()`: Configure logging for automation scripts
- `get_aws_account_id()`: Get the current AWS account ID
- `get_aws_region()`: Get the current AWS region
- `wait_for_resource_state()`: Generic function to wait for a resource to reach a specific state
- `create_standard_tags()`: Create a standard set of tags for AWS resources
- `convert_tags_to_dict()`: Convert a list of tag dictionaries to a simple dictionary
- `validate_parameters()`: Validate that all required parameters are present
- `send_notification()`: Send a notification using SNS
- `assume_role()`: Assume a role and return credentials
- `get_client_for_account()`: Get a boto3 client for a service in a specific account and region
- `format_results_as_html()`: Format results as HTML

### config_manager.py

Configuration management for SSM automation documents:

- `ConfigManager`: Class to manage configuration from SSM Parameter Store or S3
  - `get_parameter_store_config()`: Get configuration from SSM Parameter Store
  - `get_s3_config()`: Get configuration from S3
  - `get_config()`: Get configuration from the configured source
  - `put_parameter_store_config()`: Store configuration in SSM Parameter Store
  - `put_s3_config()`: Store configuration in S3
  - `put_config()`: Store configuration in the configured source

### security_helpers.py

Security-related helper functions for SSM automation documents:

- `is_public_cidr()`: Check if a CIDR range represents a public IP range
- `check_security_group_rules()`: Check security group rules for potential security issues
- `remediate_security_group_issues()`: Remediate security group issues by revoking problematic rules
- `check_s3_bucket_encryption()`: Check if S3 bucket has encryption enabled
- `check_ebs_volume_encryption()`: Check if an EBS volume is encrypted
- `enable_s3_bucket_encryption()`: Enable encryption on an S3 bucket
- `check_iam_password_policy()`: Check the IAM password policy for security best practices
- `generate_least_privilege_policy()`: Generate a least privilege IAM policy for specific service actions
- `check_cloudtrail_status()`: Check CloudTrail status and configuration
- `check_root_account_mfa()`: Check if the root account has MFA enabled

## Requirements

- Python 3.10 or later
- AWS SDK for Python (boto3)
- SSM Automation Document Schema Version 0.3

## Using Shared Modules in SSM Documents

To use these shared modules in your SSM automation documents, you have several options:

### Option 1: Upload to S3 and Import

1. Upload the Python modules to an S3 bucket
2. In your SSM document's Python script, add the S3 bucket to the Python path and import the modules

```python
import sys
import os
import boto3

# Import shared modules from S3
s3 = boto3.resource('s3')
bucket_name = 'your-bucket-name'
prefix = 'shared/python'

# Create a temporary directory to store the modules
temp_dir = '/tmp/shared'
os.makedirs(temp_dir, exist_ok=True)

# Download the modules
for obj in s3.Bucket(bucket_name).objects.filter(Prefix=prefix):
    if obj.key.endswith('.py'):
        local_file = f"{temp_dir}/{os.path.basename(obj.key)}"
        s3.meta.client.download_file(bucket_name, obj.key, local_file)

# Add to Python path
sys.path.append(temp_dir)

# Now you can import the modules
from aws_helpers import setup_logging, create_standard_tags
from config_manager import ConfigManager
from security_helpers import check_security_group_rules
```

### Option 2: Package as Lambda Layer

1. Create a Lambda layer containing the shared modules
2. Reference the layer in your Lambda functions used in SSM automation documents

### Option 3: Include in SSM Document

For small utility functions, you can include them directly in your SSM document's Python script.
