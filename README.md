# AWS SSM Automation Scripts

[![Validate SSM Documents](https://github.com/thomasvincent/aws-ssm-automation-scripts/actions/workflows/validate.yml/badge.svg)](https://github.com/thomasvincent/aws-ssm-automation-scripts/actions/workflows/validate.yml)
[![Security Scan](https://github.com/thomasvincent/aws-ssm-automation-scripts/actions/workflows/security-scan.yml/badge.svg)](https://github.com/thomasvincent/aws-ssm-automation-scripts/actions/workflows/security-scan.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This repository contains a collection of AWS Systems Manager (SSM) Automation documents that help automate various AWS management and operational tasks. These scripts follow AWS best practices and can be used to streamline common operational tasks.

## Scripts

### CDN Management

- **`cloudfront_distribution_management.yaml`**: Manages AWS CloudFront distributions, including creation, update, invalidation and security configuration
  - Parameters:
    - `Operation`: (Required) The operation to perform.
    - `DistributionId`: (Optional) The ID of an existing CloudFront distribution. Required for all operations except Create.
    - `OriginDomainName`: (Optional) The origin domain name for the distribution. Required for Create operation.
    - `OriginPath`: (Optional) The origin path for the distribution.
    - `OriginId`: (Optional) The ID for the origin. If not provided, one will be generated automatically.
    - `Comment`: (Optional) A comment about the distribution.
    - `Enabled`: (Optional) Whether the distribution is enabled to accept end user requests.
    - `PriceClass`: (Optional) The price class for the distribution.
    - `DefaultRootObject`: (Optional) The default root object for the distribution.
    - `DefaultCacheBehavior`: (Optional) The default cache behavior configuration as a JSON string. If not provided, default settings will be used. Example:
  {"ViewerProtocolPolicy":"redirect-to-https",
   "AllowedMethods":["GET","HEAD"],
   "CachedMethods":["GET","HEAD"],
   "DefaultTTL":86400}
    - `CacheBehaviors`: (Optional) A map of path patterns to cache behaviors as a JSON string.
    - `ViewerCertificateConfig`: (Optional) Viewer certificate configuration as a JSON string.
    - `LoggingConfig`: (Optional) Logging configuration as a JSON string. Example:
  {"Bucket":"logs-bucket.s3.amazonaws.com",
   "Prefix":"distribution-logs/",
   "IncludeCookies":false}
    - `PathsToInvalidate`: (Optional) A list of paths to invalidate. Required for Invalidate operation.
    - `UseSSL`: (Optional) Whether to use HTTPS for communication with the origin.
    - `SecurityPolicyConfig`: (Optional) Security policy configuration as a JSON string. Required for UpdateSecurityConfig operation. Example: {"MinimumProtocolVersion":"TLSv1.2_2019","SecurityPolicy":"TLSv1.2_2019"}
    - `AlternateDomainNames`: (Optional) A list of CNAME aliases to associate with the distribution.
    - `CustomHeaders`: (Optional) Custom headers to add to origin requests as a JSON string.
    - `GeoRestriction`: (Optional) Geo-restriction configuration as a JSON string. Example: {"RestrictionType":"whitelist","Locations":["US","CA","GB"]}
    - `Tags`: (Optional) Tags for the CloudFront distribution as a JSON string.
    - `AutomationAssumeRole`: (Optional) The ARN of the role that allows Automation to perform the actions on your behalf.

### EC2 Management

- **`ec2_instance_patching.yaml`**: Patches EC2 instances with security updates
  - Parameters:
    - `InstanceIds`: (Required) List of EC2 instance IDs to patch.
    - `RebootOption`: (Optional) Whether to reboot instances after patching.
    - `PatchSeverity`: (Optional) The severity level of patches to apply.
    - `AutomationAssumeRole`: (Optional) The ARN of the role that allows Automation to perform the actions on your behalf.

### IAM Management

- **`attach_policies_to_role.yaml`**: Attach policies to an IAM role
  - Parameters:
    - `RoleName`: (Required) The name of the IAM role to attach policies to.
    - `AWSManagedPolicies`: (Optional) A list of AWS managed policies to attach to the role.
    - `CustomerManagedPolicies`: (Optional) A list of customer managed policies to attach to the role.
    - `AutomationAssumeRole`: (Optional) The ARN of the role that allows Automation to perform the actions on your behalf.

### Lambda Management

- **`lambda_function_management.yaml`**: Creates, updates, and manages AWS Lambda functions
  - Parameters:
    - `Operation`: (Required) The operation to perform.
    - `FunctionName`: (Required) The name of the Lambda function.
    - `S3Bucket`: (Optional) S3 bucket containing the Lambda deployment package. Required for Create and Update operations.
    - `S3Key`: (Optional) S3 key for the Lambda deployment package. Required for Create and Update operations.
    - `Handler`: (Optional) The function within your code that Lambda calls to begin execution.
    - `Runtime`: (Optional) The runtime environment for the Lambda function.
    - `MemorySize`: (Optional) The amount of memory available to the function at runtime.
    - `Timeout`: (Optional) The amount of time that Lambda allows a function to run before stopping it.
    - `Role`: (Required for Create) The ARN of the IAM role that Lambda assumes when it executes your function.
    - `Environment`: (Optional) Environment variables for the Lambda function, provided as a JSON string.
    - `Tags`: (Optional) Tags for the Lambda function, provided as a JSON string.
    - `ReservedConcurrentExecutions`: (Optional) The number of reserved concurrent executions for this function.
    - `AliasName`: (Optional) Name of the Lambda alias to create or update. Required for AddAlias operation.
    - `AliasVersion`: (Optional) Function version that the alias invokes. Required for AddAlias operation.
    - `AutomationAssumeRole`: (Optional) The ARN of the role that allows Automation to perform the actions on your behalf.

### Maintenance Windows

- **`maintenance_window_setup.yaml`**: Creates an SSM maintenance window with tasks
  - Parameters:
    - `WindowName`: (Required) The name of the maintenance window.
    - `WindowDescription`: (Optional) The description of the maintenance window.
    - `Schedule`: (Required) The schedule of the maintenance window in cron or rate expression.
    - `Duration`: (Required) The duration of the maintenance window in hours.
    - `Cutoff`: (Required) The number of hours before the end of the maintenance window that the system stops scheduling new tasks.
    - `TargetType`: (Required) The type of targets to register with the maintenance window.
    - `TargetKey`: (Required) The key for the target. For INSTANCE type, provide comma-separated instance IDs.
For TAG type, provide the tag key.

    - `TargetValue`: (Required for TAG type) The value for the target key. For TAG type, provide the tag values.
    - `TaskType`: (Required) The type of task to register with the maintenance window.
    - `TaskDocumentName`: (Required) The name of the task document to run.
    - `TaskParameters`: (Optional) The parameters for the task.
    - `ServiceRoleArn`: (Required) The service role ARN for the maintenance window tasks.
    - `AutomationAssumeRole`: (Optional) The ARN of the role that allows Automation to perform the actions on your behalf.

### Other Utilities

- **`cost_optimization_recommendations.yaml`**: Identifies cost optimization opportunities across AWS resources
  - Parameters:
    - `ResourceTypes`: (Optional) Types of resources to check (EC2, EBS, S3, RDS, etc.)
    - `Region`: (Optional) AWS region to check. If not specified, the current region will be used.
    - `IdleDaysThreshold`: (Optional) Number of days of inactivity to consider a resource idle.
    - `LowUtilizationThreshold`: (Optional) CPU utilization percentage below which to consider an instance underutilized.
    - `NotificationTopicArn`: (Optional) SNS topic ARN to send notifications.
    - `GenerateReport`: (Optional) Whether to generate an HTML report of findings.
    - `ReportS3Bucket`: (Optional) S3 bucket to store the HTML report.
    - `ReportS3Prefix`: (Optional) S3 key prefix for the HTML report.
    - `AutomationAssumeRole`: (Optional) The ARN of the role that allows Automation to perform the actions on your behalf.

### Resource Management

- **`create_and_tag_resources.yaml`**: Creates AWS resources and applies consistent tagging
  - Parameters:
    - `ResourceType`: (Required) Type of AWS resource to create (e.g., EC2, S3, RDS).
    - `ResourceName`: (Required) Name to give the created resource.
    - `ResourceParameters`: (Required) JSON object containing parameters specific to the resource type.
    - `Environment`: (Required) Environment this resource belongs to.
    - `Department`: (Required) Department this resource belongs to.
    - `Project`: (Required) Project this resource belongs to.
    - `Owner`: (Required) Owner of this resource (typically an email address).
    - `CostCenter`: (Required) Cost center for billing this resource.
    - `AdditionalTags`: (Optional) Additional tags to apply to the resource.
    - `AutomationAssumeRole`: (Optional) The ARN of the role that allows Automation to perform the actions on your behalf.

- **`cross_account_resource_management.yaml`**: Manages resources across multiple AWS accounts
  - Parameters:
    - `Operation`: (Required) The operation to perform across accounts.
    - `TargetAccounts`: (Required) List of AWS account IDs to perform the operation against.
    - `TargetRegions`: (Optional) AWS regions to target. If not specified, only the current region will be used.
    - `CrossAccountRoleName`: (Required) The name of the IAM role to assume in target accounts. Must be the same name across all accounts.
    - `ResourceType`: (Optional) Type of resource to operate on. Required for CreateResources, TagResources, UpdateSecurityGroups.
    - `ResourceParameters`: (Optional) Parameters specific to the resource type and operation.
    - `TagKey`: (Optional) Tag key when performing TagResources operation.
    - `TagValue`: (Optional) Tag value when performing TagResources operation.
    - `MaxConcurrentAccounts`: (Optional) Maximum number of accounts to process concurrently.
    - `NotificationTopicArn`: (Optional) SNS Topic ARN to send operation notifications to.
    - `AutomationAssumeRole`: (Optional) The ARN of the role that allows Automation to perform the actions on your behalf.

### S3 Management

- **`s3_encryption.yaml`**: Enables server-side encryption on an S3 bucket using a KMS key
  - Parameters:
    - `BucketName`: (Required) The name of the S3 Bucket to enable encryption on.
    - `KMSMasterKey`: (Required) The ARN of the KMS customer master key (CMK) to use for the default encryption.
    - `AutomationAssumeRole`: (Optional) The ARN of the role that allows Automation to perform the actions on your behalf.

### Security Management

- **`security_group_audit.yaml`**: Audits and remediates security groups for public access and best practices
  - Parameters:
    - `SecurityGroupIds`: (Optional) List of security group IDs to audit. If not provided, all security groups in the account will be audited.
    - `VpcIds`: (Optional) List of VPC IDs to audit security groups in. If not provided, security groups in all VPCs will be audited.
    - `RemediationMode`: (Optional) The remediation mode to use. Audit will only report issues, Remediate will fix them.
    - `RemediateOpenPorts`: (Optional) List of ports to remediate if open to 0.0.0.0/0. Default is common high-risk ports.
    - `ExcludedSecurityGroups`: (Optional) List of security group IDs to exclude from remediation.
    - `AutomationAssumeRole`: (Optional) The ARN of the role that allows Automation to perform the actions on your behalf.

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

## Releases and Versioning

This repository uses semantic versioning (SemVer) for releases and is published to GitHub Packages.

### Installing from GitHub Packages

You can install these automation scripts from GitHub Packages:

```bash
# Configure npm to use GitHub Packages (first time only)
echo "@thomasvincent:registry=https://npm.pkg.github.com" >> .npmrc

# Install the package
npm install @thomasvincent/aws-ssm-automation-scripts
```

### Release Process

Releases are created automatically using GitHub Actions when a new version is created:

1. A version bump is triggered using the workflow dispatch event
2. The version is incremented in package.json (major, minor, or patch)
3. A new tag and release is created with the new version number
4. A zip file containing all the SSM documents is attached to the release
5. The package is published to GitHub Packages

### Using the Release Assets

The release assets (zip file) include all SSM documents and shared modules, ready to be deployed to AWS Systems Manager.

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
9. **Versioning**: Proper versioning and release management

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