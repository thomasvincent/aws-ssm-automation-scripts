# SSM Automation

This project contains a collection of scripts for automating various tasks using AWS Systems Manager (SSM).

## Scripts

- `attach_policies_to_role.yaml`: This script attaches IAM policies to a specific role. It takes in three parameters: `ResourceId`, `AWSManagedPolicies`, and `CustomerManagedPolicies`. `ResourceId` is the role you want to attach policies to, `AWSManagedPolicies` is a list of AWS managed policy names that you want to attach to the role and `CustomerManagedPolicies` is a list of customer managed policy arns that you want to attach to the role.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
