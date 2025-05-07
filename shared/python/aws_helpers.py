# Copyright (c) 2024 Thomas Vincent
# SPDX-License-Identifier: MIT

"""
Shared AWS helper functions for SSM automation documents.
"""

import json
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import time
import logging

# Setup logging
logger = logging.getLogger('aws_ssm_automation')

def setup_logging(log_level=logging.INFO):
    """Configure logging for automation scripts."""
    logger.setLevel(log_level)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def get_aws_account_id():
    """Get the current AWS account ID."""
    try:
        return boto3.client('sts').get_caller_identity().get('Account')
    except ClientError as e:
        logger.error(f"Error getting AWS account ID: {e}")
        raise

def get_aws_region():
    """Get the current AWS region."""
    return boto3.session.Session().region_name

def wait_for_resource_state(service_name, waiter_name, resource_id, resource_type, max_attempts=40, delay=15):
    """
    Generic function to wait for a resource to reach a specific state.
    
    Args:
        service_name (str): AWS service name (e.g., 'ec2', 's3')
        waiter_name (str): Waiter name (e.g., 'instance_running')
        resource_id (str): Resource identifier
        resource_type (str): Type of resource for logging
        max_attempts (int): Maximum number of attempts
        delay (int): Delay between attempts in seconds
        
    Returns:
        bool: True if resource reached desired state, False otherwise
    """
    client = boto3.client(service_name)
    try:
        waiter = client.get_waiter(waiter_name)
        
        logger.info(f"Waiting for {resource_type} {resource_id} to reach state: {waiter_name}")
        
        # Configure the waiter
        waiter_config = {
            'Delay': delay,
            'MaxAttempts': max_attempts
        }
        
        # Determine the correct parameter based on service and resource type
        if service_name == 'ec2':
            if 'instance' in waiter_name:
                waiter.wait(InstanceIds=[resource_id], WaiterConfig=waiter_config)
            elif 'volume' in waiter_name:
                waiter.wait(VolumeIds=[resource_id], WaiterConfig=waiter_config)
        elif service_name == 's3':
            waiter.wait(Bucket=resource_id, WaiterConfig=waiter_config)
        elif service_name == 'rds':
            waiter.wait(DBInstanceIdentifier=resource_id, WaiterConfig=waiter_config)
        else:
            # Generic approach for other services
            waiter.wait(**{resource_type: resource_id}, WaiterConfig=waiter_config)
            
        logger.info(f"{resource_type} {resource_id} reached state: {waiter_name}")
        return True
        
    except ClientError as e:
        logger.error(f"Error waiting for {resource_type} {resource_id}: {e}")
        return False

def create_standard_tags(resource_name, environment, owner, additional_tags=None):
    """
    Create a standard set of tags for AWS resources.
    
    Args:
        resource_name (str): Name of the resource
        environment (str): Environment (e.g., Production, Development)
        owner (str): Owner of the resource
        additional_tags (dict): Additional tags to add
        
    Returns:
        list: List of tag dictionaries with Key and Value
    """
    standard_tags = [
        {'Key': 'Name', 'Value': resource_name},
        {'Key': 'Environment', 'Value': environment},
        {'Key': 'Owner', 'Value': owner},
        {'Key': 'CreatedBy', 'Value': 'SSM-Automation'},
        {'Key': 'CreatedDate', 'Value': datetime.now().strftime('%Y-%m-%d')}
    ]
    
    # Add additional tags
    if additional_tags:
        for key, value in additional_tags.items():
            standard_tags.append({'Key': key, 'Value': value})
    
    return standard_tags

def convert_tags_to_dict(tags):
    """Convert a list of tag dictionaries to a simple dictionary."""
    return {tag['Key']: tag['Value'] for tag in tags if 'Key' in tag and 'Value' in tag}

def validate_parameters(parameters, required_params):
    """
    Validate that all required parameters are present.
    
    Args:
        parameters (dict): Parameters to validate
        required_params (list): List of required parameter names
        
    Returns:
        tuple: (is_valid, missing_params)
    """
    missing_params = [param for param in required_params if param not in parameters or not parameters[param]]
    return len(missing_params) == 0, missing_params

def send_notification(topic_arn, subject, message):
    """
    Send a notification using SNS.
    
    Args:
        topic_arn (str): SNS topic ARN
        subject (str): Notification subject
        message (str): Notification message
        
    Returns:
        bool: True if notification was sent successfully
    """
    try:
        sns = boto3.client('sns')
        sns.publish(
            TopicArn=topic_arn,
            Subject=subject,
            Message=message
        )
        logger.info(f"Notification sent to {topic_arn}")
        return True
    except ClientError as e:
        logger.error(f"Error sending notification: {e}")
        return False

def assume_role(role_arn, session_name="SSMAutomationSession"):
    """
    Assume a role and return credentials.
    
    Args:
        role_arn (str): ARN of the role to assume
        session_name (str): Name for the session
        
    Returns:
        dict: Credentials dictionary
    """
    try:
        sts = boto3.client('sts')
        response = sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName=session_name
        )
        
        credentials = response['Credentials']
        logger.info(f"Successfully assumed role: {role_arn}")
        
        return {
            'aws_access_key_id': credentials['AccessKeyId'],
            'aws_secret_access_key': credentials['SecretAccessKey'],
            'aws_session_token': credentials['SessionToken']
        }
    except ClientError as e:
        logger.error(f"Error assuming role {role_arn}: {e}")
        raise

def get_client_for_account(service, role_arn=None, region=None):
    """
    Get a boto3 client for a service in a specific account and region.
    
    Args:
        service (str): AWS service name
        role_arn (str): Optional role ARN to assume
        region (str): Optional AWS region
        
    Returns:
        boto3.client: Boto3 client for the service
    """
    if role_arn:
        credentials = assume_role(role_arn)
        return boto3.client(service, region_name=region, **credentials)
    elif region:
        return boto3.client(service, region_name=region)
    else:
        return boto3.client(service)

def format_results_as_html(title, results):
    """
    Format results as HTML.
    
    Args:
        title (str): Report title
        results (dict): Results to format
        
    Returns:
        str: HTML formatted results
    """
    html = f"""
    <!DOCTYPE html>
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
            <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    """
    
    # Add summary data if available
    if 'summary' in results:
        for key, value in results['summary'].items():
            html += f"<p><strong>{key}:</strong> {value}</p>\n"
    
    html += "</div>\n"
    
    # Add detailed results tables
    for section_name, section_data in results.items():
        if section_name == 'summary':
            continue
            
        html += f"<h2>{section_name}</h2>\n"
        
        if isinstance(section_data, list) and len(section_data) > 0:
            # It's a list of dictionaries, create a table
            if isinstance(section_data[0], dict):
                html += "<table>\n<tr>\n"
                
                # Create headers from the keys of the first item
                for key in section_data[0].keys():
                    html += f"<th>{key}</th>\n"
                
                html += "</tr>\n"
                
                # Add rows for each item
                for item in section_data:
                    html += "<tr>\n"
                    for key, value in item.items():
                        # Determine styling based on value
                        css_class = ""
                        if key.lower() in ['status', 'state']:
                            if str(value).lower() in ['success', 'succeeded', 'passed', 'ok', 'healthy', 'active', 'clean']:
                                css_class = "success"
                            elif str(value).lower() in ['error', 'failed', 'fail', 'failure', 'unhealthy']:
                                css_class = "error"
                            elif str(value).lower() in ['warning', 'pending', 'progress', 'in progress', 'hasissues']:
                                css_class = "warning"
                        
                        if css_class:
                            html += f"<td class=\"{css_class}\">{value}</td>\n"
                        else:
                            html += f"<td>{value}</td>\n"
                            
                    html += "</tr>\n"
                    
                html += "</table>\n"
        elif isinstance(section_data, dict):
            # It's a dictionary of values, create a simple table
            html += "<table>\n"
            for key, value in section_data.items():
                html += f"<tr><th>{key}</th><td>{value}</td></tr>\n"
            html += "</table>\n"
        else:
            # Just display the value
            html += f"<p>{section_data}</p>\n"
    
    html += """
    </body>
    </html>
    """
    
    return html