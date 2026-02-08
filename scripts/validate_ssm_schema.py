#!/usr/bin/env python3
import sys
import json
import yaml
from pathlib import Path
from jsonschema import Draft7Validator

SCHEMA_PATH = Path(__file__).parent / "ssm_schema.json"


def load_schema():
    with open(SCHEMA_PATH, "r") as f:
        return json.load(f)


def validate_file(validator, path: Path):
    with path.open("r") as f:
        data = yaml.safe_load(f)
    # Only validate likely SSM Automation docs
    if not isinstance(data, dict):
        return []
    if not any(k in data for k in ("schemaVersion", "assumeRole", "mainSteps")):
        return []
    errors = []
    for err in sorted(validator.iter_errors(data), key=lambda e: e.path):
        loc = "/".join([str(p) for p in err.absolute_path])
        errors.append(f"{path}: {loc} -> {err.message}")
    return errors


def main(argv):
    files = [Path(a) for a in argv[1:]]
    if not files:
        print("Usage: validate_ssm_schema.py <files...>")
        return 2
    schema = load_schema()
    validator = Draft7Validator(schema)
    all_errors = []
    for p in files:
        if p.suffix in (".yaml", ".yml") and len(p.parts) == 1:
            all_errors.extend(validate_file(validator, p))
    if all_errors:
        print("\n".join(all_errors))
        return 1
    print("Schema validation passed for:")
    for p in files:
        if p.suffix in (".yaml", ".yml") and len(p.parts) == 1:
            print(f"- {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
