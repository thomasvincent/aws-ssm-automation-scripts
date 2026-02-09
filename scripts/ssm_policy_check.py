#!/usr/bin/env python3
import sys
from pathlib import Path

import yaml

errors = []


# Add CloudFormation intrinsic function support
class CFNLoader(yaml.SafeLoader):
    pass


# Handle CloudFormation intrinsic functions by returning None
CFNLoader.add_multi_constructor("!", lambda loader, suffix, node: None)


def check_file(path: Path):
    try:
        with path.open("r") as f:
            doc = yaml.load(f, Loader=CFNLoader)  # nosec B506
    except Exception as e:
        errors.append(f"{path}: YAML load error: {e}")
        return
    if not isinstance(doc, dict):
        # not an SSM doc
        return
    # Only enforce if it looks like an SSM Automation doc
    if (
        "schemaVersion" not in doc
        and "assumeRole" not in doc
        and "mainSteps" not in doc
    ):
        return
    sv = str(doc.get("schemaVersion", "")).strip()
    ar = doc.get("assumeRole")
    if sv != "0.3":
        errors.append(f"{path}: schemaVersion must be '0.3' (found '{sv}')")
    if not ar:
        errors.append(f"{path}: 'assumeRole' is required at top level")


def main(argv):
    targets = [Path(a) for a in argv[1:]]
    for p in targets:
        if p.suffix in (".yaml", ".yml") and len(p.parts) == 1:
            check_file(p)
    if errors:
        print("\n".join(errors))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
