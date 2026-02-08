# Copyright (c) 2024 Thomas Vincent
# SPDX-License-Identifier: MIT

"""Shared AWS helper functions for SSM automation documents."""

import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import logging

logger = logging.getLogger("aws_ssm_automation")


def setup_logging(log_level=logging.INFO):
    """Configure logging for automation scripts."""
    logger.setLevel(log_level)
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(handler)
    return logger


def get_aws_account_id():
    """Get the current AWS account ID."""
    return boto3.client("sts").get_caller_identity().get("Account")


def get_aws_region():
    """Get the current AWS region."""
    return boto3.session.Session().region_name


def wait_for_resource_state(
    service_name, waiter_name, resource_id, resource_type, max_attempts=40, delay=15
):
    """Wait for an AWS resource to reach a specific state."""
    client = boto3.client(service_name)
    try:
        waiter = client.get_waiter(waiter_name)
        logger.info(f"Waiting for {resource_type} {resource_id}: {waiter_name}")

        config = {"Delay": delay, "MaxAttempts": max_attempts}

        if service_name == "ec2":
            if "instance" in waiter_name:
                waiter.wait(InstanceIds=[resource_id], WaiterConfig=config)
            elif "volume" in waiter_name:
                waiter.wait(VolumeIds=[resource_id], WaiterConfig=config)
        elif service_name == "s3":
            waiter.wait(Bucket=resource_id, WaiterConfig=config)
        elif service_name == "rds":
            waiter.wait(DBInstanceIdentifier=resource_id, WaiterConfig=config)
        else:
            waiter.wait(**{resource_type: resource_id}, WaiterConfig=config)

        logger.info(f"{resource_type} {resource_id} reached state: {waiter_name}")
        return True
    except ClientError as e:
        logger.error(f"Error waiting for {resource_type} {resource_id}: {e}")
        return False


def create_standard_tags(resource_name, environment, owner, additional_tags=None):
    """Create standard tags for AWS resources."""
    tags = [
        {"Key": "Name", "Value": resource_name},
        {"Key": "Environment", "Value": environment},
        {"Key": "Owner", "Value": owner},
        {"Key": "CreatedBy", "Value": "SSM-Automation"},
        {"Key": "CreatedDate", "Value": datetime.now().strftime("%Y-%m-%d")},
    ]
    if additional_tags:
        tags.extend({"Key": k, "Value": v} for k, v in additional_tags.items())
    return tags


def convert_tags_to_dict(tags):
    """Convert tag list to dictionary."""
    return {t["Key"]: t["Value"] for t in tags if "Key" in t and "Value" in t}


def validate_parameters(parameters, required_params):
    """Validate required parameters are present. Returns (is_valid, missing_params)."""
    missing = [p for p in required_params if not parameters.get(p)]
    return len(missing) == 0, missing


def send_notification(topic_arn, subject, message):
    """Send SNS notification."""
    try:
        boto3.client("sns").publish(
            TopicArn=topic_arn, Subject=subject, Message=message
        )
        logger.info(f"Notification sent to {topic_arn}")
        return True
    except ClientError as e:
        logger.error(f"Error sending notification: {e}")
        return False


def assume_role(role_arn, session_name="SSMAutomationSession"):
    """Assume IAM role and return credentials dict."""
    sts = boto3.client("sts")
    creds = sts.assume_role(RoleArn=role_arn, RoleSessionName=session_name)[
        "Credentials"
    ]
    return {
        "aws_access_key_id": creds["AccessKeyId"],
        "aws_secret_access_key": creds["SecretAccessKey"],
        "aws_session_token": creds["SessionToken"],
    }


def get_client_for_account(service, role_arn=None, region=None):
    """Get boto3 client, optionally assuming a role."""
    if role_arn:
        return boto3.client(service, region_name=region, **assume_role(role_arn))
    return (
        boto3.client(service, region_name=region) if region else boto3.client(service)
    )


def format_results_as_html(title, results):
    """Format results dict as HTML report."""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #0066cc; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .success {{ color: green; }}
        .error {{ color: red; }}
        .warning {{ color: orange; }}
        .summary {{ background-color: #f0f0f0; padding: 15px; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="summary">
        <p><strong>Date:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
"""

    if "summary" in results:
        for k, v in results["summary"].items():
            html += f"<p><strong>{k}:</strong> {v}</p>\n"
    html += "</div>\n"

    for section, data in results.items():
        if section == "summary":
            continue
        html += f"<h2>{section}</h2>\n"

        if isinstance(data, list) and data and isinstance(data[0], dict):
            html += (
                "<table>\n<tr>" + "".join(f"<th>{k}</th>" for k in data[0]) + "</tr>\n"
            )
            for item in data:
                html += "<tr>"
                for k, v in item.items():
                    css = ""
                    if k.lower() in ["status", "state"]:
                        vl = str(v).lower()
                        if vl in [
                            "success",
                            "succeeded",
                            "passed",
                            "ok",
                            "healthy",
                            "active",
                            "clean",
                        ]:
                            css = ' class="success"'
                        elif vl in ["error", "failed", "fail", "failure", "unhealthy"]:
                            css = ' class="error"'
                        elif vl in ["warning", "pending", "progress", "in progress"]:
                            css = ' class="warning"'
                    html += f"<td{css}>{v}</td>"
                html += "</tr>\n"
            html += "</table>\n"
        elif isinstance(data, dict):
            html += (
                "<table>\n"
                + "".join(
                    f"<tr><th>{k}</th><td>{v}</td></tr>\n" for k, v in data.items()
                )
                + "</table>\n"
            )
        else:
            html += f"<p>{data}</p>\n"

    return html + "</body></html>"
