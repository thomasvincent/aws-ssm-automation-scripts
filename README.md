# AWS SSM Automation Scripts

[![Validate SSM Documents](https://github.com/thomasvincent/aws-ssm-automation-scripts/actions/workflows/validate.yml/badge.svg)](https://github.com/thomasvincent/aws-ssm-automation-scripts/actions/workflows/validate.yml)
[![Security Scan](https://github.com/thomasvincent/aws-ssm-automation-scripts/actions/workflows/security-scan.yml/badge.svg)](https://github.com/thomasvincent/aws-ssm-automation-scripts/actions/workflows/security-scan.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This repository contains a collection of AWS Systems Manager (SSM) Automation documents that help automate various AWS management and operational tasks. These scripts follow AWS best practices and can be used to streamline common operational tasks.

## Scripts

### IAM Management

- **`attach_policies_to_role.yaml`**: Attaches IAM policies to a specific IAM role.
  - Parameters:
    - `RoleName`: The name of the IAM role to attach policies to
    - `AWSManagedPolicies`: A list of AWS managed policy names to attach
    - `CustomerManagedPolicies`: A list of customer managed policy ARNs to attach

### S3 Management

- **`s3_encryption.yaml`**: Enables server-side encryption on an S3 bucket using a KMS key.
  - Parameters:
    - `BucketName`: The name of the S3 bucket to encrypt
    - `KMSMasterKey`: The ARN of the KMS customer master key to use
    - `AutomationAssumeRole`: (Optional) The ARN of the automation role

### EC2 Management

- **`ec2_instance_patching.yaml`**: Patches EC2 instances with security updates.
  - Parameters:
    - `InstanceIds`: List of EC2 instance IDs to patch
    - `RebootOption`: Whether to reboot instances after patching
    - `PatchSeverity`: The severity level of patches to apply
    - `AutomationAssumeRole`: (Optional) The ARN of the automation role

### Resource Management

- **`create_and_tag_resources.yaml`**: Creates AWS resources and applies consistent tagging.
  - Parameters:
    - `ResourceType`: Type of AWS resource to create (S3, EC2, RDS)
    - `ResourceName`: Name to give the created resource
    - `ResourceParameters`: JSON object with resource-specific parameters
    - `Environment`: Environment this resource belongs to
    - `Department`: Department this resource belongs to
    - `Project`: Project this resource belongs to
    - `Owner`: Owner of this resource
    - `CostCenter`: Cost center for billing
    - `AdditionalTags`: (Optional) Additional tags to apply
    - `AutomationAssumeRole`: (Optional) The ARN of the automation role

- **`cross_account_resource_management.yaml`**: Manages resources across multiple AWS accounts.
  - Parameters:
    - `Operation`: The operation to perform across accounts
    - `TargetAccounts`: List of AWS account IDs to perform the operation against
    - `TargetRegions`: (Optional) AWS regions to target
    - `CrossAccountRoleName`: The name of the IAM role to assume in target accounts
    - `ResourceType`: (Optional) Type of resource to operate on
    - `ResourceParameters`: (Optional) Parameters specific to the resource type and operation
    - `MaxConcurrentAccounts`: (Optional) Maximum number of accounts to process concurrently
    - `NotificationTopicArn`: (Optional) SNS Topic ARN to send operation notifications to
    - `AutomationAssumeRole`: (Optional) The ARN of the automation role

### Cost Management

- **`cost_optimization_recommendations.yaml`**: Identifies cost optimization opportunities across AWS resources.
  - Parameters:
    - `ResourceTypes`: (Optional) Types of resources to check (EC2, EBS, S3, RDS, etc.)
    - `Region`: (Optional) AWS region to check
    - `IdleDaysThreshold`: (Optional) Number of days of inactivity to consider a resource idle
    - `LowUtilizationThreshold`: (Optional) CPU utilization percentage below which to consider an instance underutilized
    - `NotificationTopicArn`: (Optional) SNS topic ARN to send notifications
    - `GenerateReport`: (Optional) Whether to generate an HTML report of findings
    - `ReportS3Bucket`: (Optional) S3 bucket to store the HTML report
    - `ReportS3Prefix`: (Optional) S3 key prefix for the HTML report
    - `AutomationAssumeRole`: (Optional) The ARN of the automation role

### Security Management

- **`security_group_audit.yaml`**: Audits and remediates security groups for public access and best practices.
  - Parameters:
    - `SecurityGroupIds`: (Optional) List of security group IDs to audit
    - `VpcIds`: (Optional) List of VPC IDs to audit security groups in
    - `RemediationMode`: The remediation mode to use (Audit/Remediate)
    - `RemediateOpenPorts`: List of ports to remediate if open to 0.0.0.0/0
    - `ExcludedSecurityGroups`: (Optional) Security groups to exclude from remediation
    - `AutomationAssumeRole`: (Optional) The ARN of the automation role

### Maintenance Windows

- **`maintenance_window_setup.yaml`**: Creates an SSM maintenance window with tasks.
  - Parameters:
    - `WindowName`: The name of the maintenance window
    - `WindowDescription`: (Optional) The description of the maintenance window
    - `Schedule`: The schedule of the maintenance window in cron/rate expression
    - `Duration`: The duration of the maintenance window in hours
    - `Cutoff`: Number of hours before the end to stop scheduling new tasks
    - `TargetType`: The type of targets to register (INSTANCE, RESOURCE_GROUP, TAG)
    - `TargetKey`: The key for the target
    - `TargetValue`: (Required for TAG type) The value for the target key
    - `TaskType`: The type of task to register (RUN_COMMAND, AUTOMATION, etc.)
    - `TaskDocumentName`: The name of the task document to run
    - `TaskParameters`: (Optional) The parameters for the task
    - `ServiceRoleArn`: The service role ARN for the maintenance window tasks
    - `AutomationAssumeRole`: (Optional) The ARN of the automation role

## Shared Python Modules

This repository includes shared Python modules in the `shared/python` directory that provide common functionality for the SSM automation documents:

- **`aws_helpers.py`**: General AWS helper functions (logging, tagging, parameter validation, etc.)
- **`config_manager.py`**: Configuration management from SSM Parameter Store or S3
- **`security_helpers.py`**: Security-related helper functions (encryption checks, security group auditing, etc.)

See the [shared README](shared/README.md) for more details.

## Usage

1. Clone this repository or download the specific script you need
2. Upload the script to your S3 bucket
3. Register the document in AWS SSM using the AWS CLI:

```bash
aws ssm create-document \
  --name "MyS3EncryptionDocument" \
  --document-type "Automation" \
  --content file://s3_encryption.yaml
```

4. Run the automation using the AWS CLI or AWS Console:

```bash
aws ssm start-automation-execution \
  --document-name "MyS3EncryptionDocument" \
  --parameters '{"BucketName":["my-bucket"],"KMSMasterKey":["arn:aws:kms:region:account:key/key-id"]}'
```

### Using Shared Python Modules

To use the shared Python modules in your SSM documents:

1. Upload the modules to an S3 bucket:

```bash
aws s3 cp --recursive shared/python s3://your-bucket-name/shared/python/
```

2. In your SSM document's Python script, add code to import the modules from S3:

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
```

## Cross-Account Operations

The `cross_account_resource_management.yaml` document allows you to perform operations across multiple AWS accounts. To use it:

1. Create an IAM role in each target account with the same name (e.g., `SSMCrossAccountRole`)
2. Configure the trust relationship to allow the automation account to assume the role
3. Register the document in the automation account
4. Run the automation with the appropriate parameters

Example trust policy for the cross-account role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::AUTOMATION_ACCOUNT_ID:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {}
    }
  ]
}
```

## CI/CD Pipeline

This repository uses GitHub Actions for continuous integration and continuous deployment:

- **Validation**: All YAML files are automatically linted and validated when pushed
- **Security Scanning**: CodeQL security scanning is performed on all code changes
- **Automated Testing**: Scripts can be tested in a sandbox environment when approved
- **Automatic Releases**: New releases are created automatically when version tags are pushed
- **Dependency Management**: Dependabot keeps dependencies up to date

## Best Practices

These scripts follow these AWS best practices:

1. **Least Privilege**: Use IAM roles with minimal permissions needed for the task
2. **Structured Parameters**: Clear parameter definitions with descriptions and constraints
3. **Error Handling**: Proper error handling and recovery mechanisms
4. **Idempotency**: Safe to run multiple times without unexpected side effects
5. **Documentation**: Comprehensive documentation in the code and README
6. **Consistent Structure**: Standardized document structure for easier understanding
7. **Reusability**: Shared modules for common functionality
8. **Multi-Account Support**: Cross-account resource management capabilities

## Development

To create new automation documents:

1. Use the existing scripts as templates
2. Follow the same parameter structure and naming conventions
3. Include proper error handling and validation
4. Use the shared Python modules for common functionality
5. Add comprehensive documentation in the script and README
6. Test thoroughly before using in production

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.