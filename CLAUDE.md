# CLAUDE.md

AWS Systems Manager automation documents for infrastructure operations and compliance.

## Stack
- YAML (SSM documents)
- Python 3.x (shared helper modules)

## Validation
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('document.yaml'))"

# Run validation workflow locally
act -j validate
```

## Testing
```bash
# Python helpers
cd shared/python
pytest tests/

# Dry-run automation
aws ssm start-automation-execution \
  --document-name "TestDocument" \
  --parameters '{"DryRun":["true"]}'
```
