# Copyright (c) 2024 Thomas Vincent
# SPDX-License-Identifier: MIT

"""
Configuration management for SSM automation documents.
"""

import boto3
import json
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger('aws_ssm_automation')

class ConfigManager:
    """
    Manages configuration for SSM automation documents.
    Supports loading configuration from SSM Parameter Store or S3.
    """
    
    def __init__(self, config_source='parameter_store', region=None):
        """
        Initialize the configuration manager.
        
        Args:
            config_source (str): Source of configuration ('parameter_store' or 's3')
            region (str): AWS region
        """
        self.config_source = config_source
        self.region = region
        self.clients = {}
        
    def _get_client(self, service_name):
        """Get a boto3 client for the specified service."""
        if service_name not in self.clients:
            if self.region:
                self.clients[service_name] = boto3.client(service_name, region_name=self.region)
            else:
                self.clients[service_name] = boto3.client(service_name)
        return self.clients[service_name]
    
    def get_parameter_store_config(self, parameter_path):
        """
        Get configuration from SSM Parameter Store.
        
        Args:
            parameter_path (str): Path to the parameter
            
        Returns:
            dict: Configuration dictionary
        """
        try:
            ssm = self._get_client('ssm')
            response = ssm.get_parameter(
                Name=parameter_path,
                WithDecryption=True
            )
            
            parameter_value = response['Parameter']['Value']
            
            # Check if it's JSON and parse it
            try:
                return json.loads(parameter_value)
            except json.JSONDecodeError:
                # If it's not JSON, return as is
                return parameter_value
                
        except ClientError as e:
            logger.error(f"Error retrieving parameter {parameter_path}: {e}")
            raise
    
    def get_s3_config(self, bucket, key):
        """
        Get configuration from S3.
        
        Args:
            bucket (str): S3 bucket name
            key (str): S3 object key
            
        Returns:
            dict: Configuration dictionary
        """
        try:
            s3 = self._get_client('s3')
            response = s3.get_object(
                Bucket=bucket,
                Key=key
            )
            
            content = response['Body'].read().decode('utf-8')
            
            # Check if it's JSON and parse it
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # If it's not JSON, return as is
                return content
                
        except ClientError as e:
            logger.error(f"Error retrieving S3 object {bucket}/{key}: {e}")
            raise
    
    def get_config(self, identifier, is_json=True):
        """
        Get configuration from the configured source.
        
        Args:
            identifier (str or dict): Parameter path or S3 location details
            is_json (bool): Whether to parse the value as JSON
            
        Returns:
            dict or str: Configuration value
        """
        if self.config_source == 'parameter_store':
            if isinstance(identifier, str):
                return self.get_parameter_store_config(identifier)
            else:
                raise ValueError("For parameter_store source, identifier must be a string")
        elif self.config_source == 's3':
            if isinstance(identifier, dict) and 'bucket' in identifier and 'key' in identifier:
                return self.get_s3_config(identifier['bucket'], identifier['key'])
            else:
                raise ValueError("For s3 source, identifier must be a dict with 'bucket' and 'key'")
        else:
            raise ValueError(f"Unsupported config source: {self.config_source}")
    
    def put_parameter_store_config(self, parameter_path, config_value, parameter_type='String', description=None):
        """
        Store configuration in SSM Parameter Store.
        
        Args:
            parameter_path (str): Path to the parameter
            config_value (dict or str): Configuration value
            parameter_type (str): Parameter type ('String', 'StringList', or 'SecureString')
            description (str): Optional description
            
        Returns:
            bool: True if successful
        """
        try:
            ssm = self._get_client('ssm')
            
            # Convert dict to JSON string if needed
            if isinstance(config_value, dict):
                value = json.dumps(config_value)
            else:
                value = config_value
                
            params = {
                'Name': parameter_path,
                'Value': value,
                'Type': parameter_type,
                'Overwrite': True
            }
            
            if description:
                params['Description'] = description
                
            ssm.put_parameter(**params)
            logger.info(f"Successfully stored configuration at {parameter_path}")
            return True
            
        except ClientError as e:
            logger.error(f"Error storing parameter {parameter_path}: {e}")
            return False
    
    def put_s3_config(self, bucket, key, config_value):
        """
        Store configuration in S3.
        
        Args:
            bucket (str): S3 bucket name
            key (str): S3 object key
            config_value (dict or str): Configuration value
            
        Returns:
            bool: True if successful
        """
        try:
            s3 = self._get_client('s3')
            
            # Convert dict to JSON string if needed
            if isinstance(config_value, dict):
                content = json.dumps(config_value)
            else:
                content = config_value
                
            s3.put_object(
                Bucket=bucket,
                Key=key,
                Body=content.encode('utf-8'),
                ContentType='application/json' if isinstance(config_value, dict) else 'text/plain'
            )
            
            logger.info(f"Successfully stored configuration at s3://{bucket}/{key}")
            return True
            
        except ClientError as e:
            logger.error(f"Error storing S3 object {bucket}/{key}: {e}")
            return False
    
    def put_config(self, identifier, config_value, **kwargs):
        """
        Store configuration in the configured source.
        
        Args:
            identifier (str or dict): Parameter path or S3 location details
            config_value (dict or str): Configuration value
            **kwargs: Additional arguments for the specific storage method
            
        Returns:
            bool: True if successful
        """
        if self.config_source == 'parameter_store':
            if isinstance(identifier, str):
                return self.put_parameter_store_config(identifier, config_value, **kwargs)
            else:
                raise ValueError("For parameter_store source, identifier must be a string")
        elif self.config_source == 's3':
            if isinstance(identifier, dict) and 'bucket' in identifier and 'key' in identifier:
                return self.put_s3_config(identifier['bucket'], identifier['key'], config_value)
            else:
                raise ValueError("For s3 source, identifier must be a dict with 'bucket' and 'key'")
        else:
            raise ValueError(f"Unsupported config source: {self.config_source}")