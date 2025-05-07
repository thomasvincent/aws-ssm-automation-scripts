#!/usr/bin/env python3
"""
Script to automatically update the README.md file with script documentation.
"""

import os
import re
import yaml
from glob import glob
from collections import defaultdict

# Script categories mapping
CATEGORIES = {
    'attach_policies_to_role.yaml': 'IAM Management',
    's3_encryption.yaml': 'S3 Management',
    'ec2_instance_patching.yaml': 'EC2 Management',
    'create_and_tag_resources.yaml': 'Resource Management',
    'security_group_audit.yaml': 'Security Management',
    'maintenance_window_setup.yaml': 'Maintenance Windows',
    'lambda_function_management.yaml': 'Lambda Management',
    'cloudfront_distribution_management.yaml': 'CDN Management',
}

def get_script_category(filename):
    """Determine the category for a script based on its filename."""
    base_filename = os.path.basename(filename)
    if base_filename in CATEGORIES:
        return CATEGORIES[base_filename]
    
    # Try to determine category from filename
    if 'ec2' in base_filename or 'instance' in base_filename:
        return 'EC2 Management'
    elif 's3' in base_filename or 'bucket' in base_filename:
        return 'S3 Management'
    elif 'iam' in base_filename or 'role' in base_filename or 'polic' in base_filename:
        return 'IAM Management'
    elif 'secur' in base_filename or 'audit' in base_filename:
        return 'Security Management'
    elif 'resource' in base_filename or 'tag' in base_filename:
        return 'Resource Management'
    elif 'maintenance' in base_filename or 'window' in base_filename:
        return 'Maintenance Windows'
    elif 'lambda' in base_filename or 'function' in base_filename:
        return 'Lambda Management'
    elif 'cloudfront' in base_filename or 'distribution' in base_filename or 'cdn' in base_filename:
        return 'CDN Management'
    else:
        return 'Other Utilities'

def parse_yaml_file(file_path):
    """Parse YAML file and extract documentation."""
    with open(file_path, 'r') as file:
        # Skip comment lines at the beginning
        content = file.read()
        content_without_comments = re.sub(r'^#.*$', '', content, flags=re.MULTILINE)
        
        try:
            data = yaml.safe_load(content_without_comments)
            return {
                'description': data.get('description', 'No description available'),
                'parameters': data.get('parameters', {})
            }
        except yaml.YAMLError:
            return {
                'description': 'Error parsing script',
                'parameters': {}
            }

def generate_script_section(file_path):
    """Generate markdown documentation for a script."""
    base_name = os.path.basename(file_path)
    script_data = parse_yaml_file(file_path)
    
    # Start with script name and description
    md = f"- **`{base_name}`**: {script_data['description']}\n"
    
    # Add parameters if they exist
    if script_data['parameters']:
        md += "  - Parameters:\n"
        for param_name, param_details in script_data['parameters'].items():
            description = param_details.get('description', 'No description')
            is_optional = '(Optional)' in description
            param_text = f"{param_name}: {description}"
            
            if not is_optional and '(Required)' not in description:
                param_text = param_text.replace(param_name, f"{param_name} (Required)")
                
            md += f"    - `{param_name}`: {description}\n"
    
    return md

def update_readme():
    """Update the README.md file with script documentation."""
    # Get all YAML files (except those in .github)
    yaml_files = glob('*.yaml') + glob('*.yml')
    yaml_files = [f for f in yaml_files if not f.startswith('.github')]
    
    # Group scripts by category
    categorized_scripts = defaultdict(list)
    for file_path in yaml_files:
        category = get_script_category(file_path)
        categorized_scripts[category].append(file_path)
    
    # Read existing README
    with open('README.md', 'r') as file:
        readme_content = file.read()
    
    # Extract the part before and after the scripts section
    scripts_section_start = readme_content.find('## Scripts')
    if scripts_section_start == -1:
        scripts_section_start = readme_content.find('# Scripts')
        
    if scripts_section_start == -1:
        print("Could not find Scripts section in README.md")
        return
    
    usage_section_start = readme_content.find('## Usage')
    if usage_section_start == -1:
        usage_section_start = len(readme_content)
    
    header = readme_content[:scripts_section_start]
    footer = readme_content[usage_section_start:]
    
    # Generate new scripts section
    new_scripts_section = "## Scripts\n\n"
    
    for category, scripts in sorted(categorized_scripts.items()):
        new_scripts_section += f"### {category}\n\n"
        for script in sorted(scripts):
            new_scripts_section += generate_script_section(script) + "\n"
    
    # Combine sections
    updated_readme = header + new_scripts_section + footer
    
    # Write updated README
    with open('README.md', 'w') as file:
        file.write(updated_readme)
    
    print("README.md updated successfully")

if __name__ == "__main__":
    update_readme()