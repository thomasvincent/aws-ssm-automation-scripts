# Copyright (c) 2024 Thomas Vincent
# SPDX-License-Identifier: MIT

"""
Security helpers for SSM automation documents.
"""

import ipaddress
import logging

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger("aws_ssm_automation")


def is_public_cidr(cidr):
    """
    Check if a CIDR range represents a public IP range.

    Args:
        cidr (str): CIDR range to check

    Returns:
        bool: True if the CIDR represents a public IP range
    """
    if not cidr:
        return False

    # Check if it's 0.0.0.0/0 or similar public range
    if cidr == "0.0.0.0/0" or cidr == "::/0":
        return True

    try:
        network = ipaddress.ip_network(cidr)

        # Check if it's not a private/reserved range
        if not network.is_private and not network.is_reserved:
            return True
    except ValueError:
        pass

    return False


def check_security_group_rules(security_group_id, high_risk_ports=None):
    """
    Check security group rules for potential security issues.

    Args:
        security_group_id (str): Security group ID to check
        high_risk_ports (list): List of high-risk ports to check for
            public access

    Returns:
        dict: Security group analysis results
    """
    if not high_risk_ports:
        high_risk_ports = [22, 3389, 5432, 3306, 1433, 27017, 6379, 9200, 8080, 8443]

    ec2 = boto3.client("ec2")
    try:
        response = ec2.describe_security_groups(GroupIds=[security_group_id])

        if (
            not response
            or "SecurityGroups" not in response
            or not response["SecurityGroups"]
        ):
            logger.warning(f"No security groups found with ID {security_group_id}")
            return {
                "SecurityGroupId": security_group_id,
                "Status": "Error",
                "Error": "Security group not found",
            }

        sg = response["SecurityGroups"][0]
        sg_name = sg.get("GroupName", "Unknown")
        vpc_id = sg.get("VpcId", "default")

        issues = []

        # Check ingress rules
        for rule in sg.get("IpPermissions", []):
            from_port = rule.get("FromPort", 0)
            to_port = rule.get("ToPort", 65535)
            ip_protocol = rule.get("IpProtocol", "-1")

            # Check IP ranges for public access
            for ip_range in rule.get("IpRanges", []):
                cidr = ip_range.get("CidrIp", "")

                # Check if this is a public CIDR
                if is_public_cidr(cidr):
                    # Check if specific high-risk ports are open
                    is_high_risk = False
                    affected_ports = []

                    if ip_protocol == "-1":  # All protocols
                        is_high_risk = True
                        affected_ports = high_risk_ports
                    else:
                        for port in high_risk_ports:
                            if from_port <= port <= to_port:
                                is_high_risk = True
                                affected_ports.append(port)

                    protocol_str = ip_protocol.upper() if ip_protocol != "-1" else "ALL"
                    port_str = (
                        str(from_port)
                        if from_port == to_port
                        else f"{from_port}-{to_port}"
                    )
                    issue = {
                        "Type": "PublicAccess",
                        "Severity": "HIGH" if is_high_risk else "MEDIUM",
                        "FromPort": from_port,
                        "ToPort": to_port,
                        "IpProtocol": ip_protocol,
                        "Cidr": cidr,
                        "AffectedPorts": affected_ports,
                        "Description": (
                            f"Public access ({cidr}) allowed to "
                            f"{protocol_str} port(s) {port_str}"
                        ),
                    }
                    issues.append(issue)

        return {
            "SecurityGroupId": security_group_id,
            "SecurityGroupName": sg_name,
            "VpcId": vpc_id,
            "Status": "HasIssues" if issues else "Clean",
            "Issues": issues,
            "TotalIssues": len(issues),
            "HighRiskIssues": len([i for i in issues if i.get("Severity") == "HIGH"]),
        }

    except ClientError as e:
        logger.error(f"Error checking security group {security_group_id}: {e}")
        return {
            "SecurityGroupId": security_group_id,
            "Status": "Error",
            "Error": str(e),
        }


def remediate_security_group_issues(security_group_id, issues):
    """
    Remediate security group issues by revoking problematic rules.

    Args:
        security_group_id (str): Security group ID to remediate
        issues (list): List of issues to remediate

    Returns:
        dict: Remediation results
    """
    if not issues:
        return {
            "SecurityGroupId": security_group_id,
            "Status": "NoIssues",
            "Message": "No issues to remediate",
        }

    ec2 = boto3.client("ec2")
    remediated_issues = []
    failed_remediations = []

    for issue in issues:
        try:
            if issue.get("Type") == "PublicAccess":
                ip_protocol = issue.get("IpProtocol", "-1")
                from_port = issue.get("FromPort", 0)
                to_port = issue.get("ToPort", 65535)
                cidr = issue.get("Cidr", "")

                if not cidr:
                    failed_remediations.append(
                        {"Issue": issue, "Error": "Missing CIDR information"}
                    )
                    continue

                # Revoke the rule
                ec2.revoke_security_group_ingress(
                    GroupId=security_group_id,
                    IpPermissions=[
                        {
                            "IpProtocol": ip_protocol,
                            "FromPort": from_port,
                            "ToPort": to_port,
                            "IpRanges": [{"CidrIp": cidr}],
                        }
                    ],
                )

                remediated_issues.append(issue)

        except ClientError as e:
            failed_remediations.append({"Issue": issue, "Error": str(e)})

    return {
        "SecurityGroupId": security_group_id,
        "Status": (
            "Remediated"
            if remediated_issues and not failed_remediations
            else "PartiallyRemediated" if remediated_issues else "Failed"
        ),
        "RemediatedIssues": len(remediated_issues),
        "FailedRemediations": len(failed_remediations),
        "Details": {
            "Remediated": remediated_issues,
            "Failed": failed_remediations,
        },
    }


def check_s3_bucket_encryption(bucket_name):
    """
    Check if S3 bucket has encryption enabled.

    Args:
        bucket_name (str): S3 bucket name

    Returns:
        dict: Encryption status
    """
    s3 = boto3.client("s3")
    try:
        response = s3.get_bucket_encryption(Bucket=bucket_name)

        rules = response.get("ServerSideEncryptionConfiguration", {}).get("Rules", [])

        if not rules:
            return {
                "BucketName": bucket_name,
                "Status": "Unencrypted",
                "Message": "No encryption rules found",
            }

        # Check encryption settings
        has_sse = False
        has_kms = False

        for rule in rules:
            default = rule.get("ApplyServerSideEncryptionByDefault", {})
            sse_algorithm = default.get("SSEAlgorithm", "")

            if sse_algorithm:
                has_sse = True

            if sse_algorithm == "aws:kms":
                has_kms = True

        return {
            "BucketName": bucket_name,
            "Status": "Encrypted",
            "HasSSE": has_sse,
            "HasKMS": has_kms,
            "EncryptionRules": rules,
        }

    except ClientError as e:
        if "ServerSideEncryptionConfigurationNotFoundError" in str(e):
            return {
                "BucketName": bucket_name,
                "Status": "Unencrypted",
                "Message": "No encryption configuration found",
            }
        else:
            logger.error(f"Error checking S3 bucket encryption {bucket_name}: {e}")
            return {
                "BucketName": bucket_name,
                "Status": "Error",
                "Error": str(e),
            }


def check_ebs_volume_encryption(volume_id):
    """
    Check if an EBS volume is encrypted.

    Args:
        volume_id (str): EBS volume ID

    Returns:
        dict: Encryption status
    """
    ec2 = boto3.client("ec2")
    try:
        response = ec2.describe_volumes(VolumeIds=[volume_id])

        if not response or "Volumes" not in response or not response["Volumes"]:
            logger.warning(f"No volume found with ID {volume_id}")
            return {
                "VolumeId": volume_id,
                "Status": "Error",
                "Error": "Volume not found",
            }

        volume = response["Volumes"][0]
        is_encrypted = volume.get("Encrypted", False)
        kms_key_id = volume.get("KmsKeyId", None)

        return {
            "VolumeId": volume_id,
            "Status": "Encrypted" if is_encrypted else "Unencrypted",
            "Encrypted": is_encrypted,
            "KmsKeyId": kms_key_id,
            "Size": volume.get("Size", 0),
            "State": volume.get("State", "unknown"),
        }

    except ClientError as e:
        logger.error(f"Error checking EBS volume encryption {volume_id}: {e}")
        return {"VolumeId": volume_id, "Status": "Error", "Error": str(e)}


def enable_s3_bucket_encryption(bucket_name, kms_key_id=None):
    """
    Enable encryption on an S3 bucket.

    Args:
        bucket_name (str): S3 bucket name
        kms_key_id (str): Optional KMS key ID to use for encryption

    Returns:
        dict: Result of enabling encryption
    """
    s3 = boto3.client("s3")
    try:
        encryption_config = {
            "Rules": [
                {
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "aws:kms" if kms_key_id else "AES256"
                    }
                }
            ]
        }

        # Add KMS key if provided
        if kms_key_id:
            encryption_config["Rules"][0]["ApplyServerSideEncryptionByDefault"][
                "KMSMasterKeyID"
            ] = kms_key_id

        s3.put_bucket_encryption(
            Bucket=bucket_name,
            ServerSideEncryptionConfiguration=encryption_config,
        )

        return {
            "BucketName": bucket_name,
            "Status": "Enabled",
            "EncryptionType": "KMS" if kms_key_id else "AES256",
            "KmsKeyId": kms_key_id,
        }

    except ClientError as e:
        logger.error(f"Error enabling S3 bucket encryption for {bucket_name}: {e}")
        return {
            "BucketName": bucket_name,
            "Status": "Error",
            "Error": str(e),
        }


def check_iam_password_policy():
    """
    Check the IAM password policy for security best practices.

    Returns:
        dict: Password policy analysis
    """
    iam = boto3.client("iam")
    try:
        response = iam.get_account_password_policy()

        policy = response.get("PasswordPolicy", {})

        # Define best practices
        best_practices = {
            "MinimumPasswordLength": 14,
            "RequireSymbols": True,
            "RequireNumbers": True,
            "RequireUppercaseCharacters": True,
            "RequireLowercaseCharacters": True,
            "PasswordReusePrevention": 24,
            "MaxPasswordAge": 90,
        }

        # Check compliance with best practices
        compliance = {}
        for key, recommended_value in best_practices.items():
            current_value = policy.get(key)

            if key == "MinimumPasswordLength":
                compliance[key] = {
                    "Status": (
                        "Compliant"
                        if current_value and current_value >= recommended_value
                        else "NonCompliant"
                    ),
                    "CurrentValue": current_value,
                    "RecommendedValue": recommended_value,
                }
            elif key in [
                "RequireSymbols",
                "RequireNumbers",
                "RequireUppercaseCharacters",
                "RequireLowercaseCharacters",
            ]:
                compliance[key] = {
                    "Status": "Compliant" if current_value else "NonCompliant",
                    "CurrentValue": current_value,
                    "RecommendedValue": recommended_value,
                }
            elif key == "PasswordReusePrevention":
                compliance[key] = {
                    "Status": (
                        "Compliant"
                        if current_value and current_value >= recommended_value
                        else "NonCompliant"
                    ),
                    "CurrentValue": current_value,
                    "RecommendedValue": recommended_value,
                }
            elif key == "MaxPasswordAge":
                compliance[key] = {
                    "Status": (
                        "Compliant"
                        if current_value and current_value <= recommended_value
                        else "NonCompliant"
                    ),
                    "CurrentValue": current_value,
                    "RecommendedValue": recommended_value,
                }

        # Calculate overall compliance
        compliant_count = sum(
            1 for item in compliance.values() if item["Status"] == "Compliant"
        )
        total_checks = len(compliance)
        compliance_percentage = (
            (compliant_count / total_checks) * 100 if total_checks > 0 else 0
        )

        return {
            "Status": (
                "Compliant"
                if compliance_percentage == 100
                else (
                    "PartiallyCompliant"
                    if compliance_percentage > 0
                    else "NonCompliant"
                )
            ),
            "CompliancePercentage": compliance_percentage,
            "ComplianceDetails": compliance,
            "CurrentPolicy": policy,
        }

    except ClientError as e:
        if "NoSuchEntity" in str(e):
            return {
                "Status": "NonCompliant",
                "CompliancePercentage": 0,
                "Error": "No password policy is set",
                "ComplianceDetails": {},
                "CurrentPolicy": {},
            }
        else:
            logger.error(f"Error checking IAM password policy: {e}")
            return {"Status": "Error", "Error": str(e)}


def generate_least_privilege_policy(service, actions):
    """
    Generate a least privilege IAM policy for specific service actions.

    Args:
        service (str): AWS service (e.g., 's3', 'ec2')
        actions (list): List of service actions

    Returns:
        dict: IAM policy document
    """
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [f"{service}:{action}" for action in actions],
                "Resource": "*",
            }
        ],
    }

    return policy


def check_cloudtrail_status():
    """
    Check CloudTrail status and configuration.

    Returns:
        dict: CloudTrail analysis
    """
    cloudtrail = boto3.client("cloudtrail")
    try:
        response = cloudtrail.describe_trails()

        trails = response.get("trailList", [])

        if not trails:
            return {
                "Status": "NotConfigured",
                "Message": "No CloudTrail trails found",
            }

        trail_details = []

        for trail in trails:
            trail_name = trail.get("Name", "Unknown")
            is_multi_region = trail.get("IsMultiRegionTrail", False)
            is_logging = False

            # Check if the trail is logging
            try:
                status = cloudtrail.get_trail_status(Name=trail_name)
                is_logging = status.get("IsLogging", False)
            except ClientError:
                pass

            # Check for key settings
            log_file_validation = trail.get("LogFileValidationEnabled", False)
            is_organization_trail = trail.get("IsOrganizationTrail", False)
            has_kms = "KmsKeyId" in trail

            trail_details.append(
                {
                    "TrailName": trail_name,
                    "IsMultiRegion": is_multi_region,
                    "IsLogging": is_logging,
                    "LogFileValidation": log_file_validation,
                    "IsOrganizationTrail": is_organization_trail,
                    "KmsEncryption": has_kms,
                    "Status": (
                        "Healthy"
                        if (is_logging and is_multi_region and log_file_validation)
                        else "Suboptimal"
                    ),
                }
            )

        # Calculate overall status
        healthy_trails = [t for t in trail_details if t["Status"] == "Healthy"]
        multi_region_trails = [t for t in trail_details if t["IsMultiRegion"]]

        return {
            "Status": (
                "Healthy"
                if healthy_trails
                else "Suboptimal" if trails else "NotConfigured"
            ),
            "TrailCount": len(trails),
            "HealthyTrailCount": len(healthy_trails),
            "MultiRegionTrailCount": len(multi_region_trails),
            "Trails": trail_details,
        }

    except ClientError as e:
        logger.error(f"Error checking CloudTrail status: {e}")
        return {"Status": "Error", "Error": str(e)}


def check_root_account_mfa():
    """
    Check if the root account has MFA enabled.

    Returns:
        dict: Root account MFA status
    """
    iam = boto3.client("iam")
    try:
        response = iam.get_account_summary()

        # Check if root account MFA is enabled
        account_mfa_enabled = bool(
            response.get("SummaryMap", {}).get("AccountMFAEnabled", 0)
        )

        return {
            "Status": "Enabled" if account_mfa_enabled else "Disabled",
            "MFAEnabled": account_mfa_enabled,
        }

    except ClientError as e:
        logger.error(f"Error checking root account MFA: {e}")
        return {"Status": "Error", "Error": str(e)}
