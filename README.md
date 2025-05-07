# AWS SSM Automation Scripts

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

## Best Practices

These scripts follow these AWS best practices:

1. **Least Privilege**: Use IAM roles with minimal permissions needed for the task
2. **Structured Parameters**: Clear parameter definitions with descriptions and constraints
3. **Error Handling**: Proper error handling and recovery mechanisms
4. **Idempotency**: Safe to run multiple times without unexpected side effects
5. **Documentation**: Comprehensive documentation in the code and README
6. **Consistent Structure**: Standardized document structure for easier understanding

## Development

To create new automation documents:

1. Use the existing scripts as templates
2. Follow the same parameter structure and naming conventions
3. Include proper error handling and validation
4. Add comprehensive documentation in the script and README
5. Test thoroughly before using in production

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.