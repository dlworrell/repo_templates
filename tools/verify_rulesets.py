#!/usr/bin/env python3
"""Verify the shared repository ruleset definitions in rulesets/.

Checks that each ruleset parses as JSON, carries the expected name and
target, defines no bypass actors, and contains none of the rule types that
would block merges in repositories where they cannot be satisfied.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

EXPECTED = {
    "rulesets/protect-default-branch.json": {
        "name": "protect-default-branch",
        "target": "branch",
    },
    "rulesets/protect-release-tags.json": {
        "name": "protect-release-tags",
        "target": "tag",
    },
    "rulesets/protect-integration-branches.json": {
        "name": "protect-integration-branches",
        "target": "branch",
    },
}

FORBIDDEN_RULE_TYPES = frozenset(
    {
        "required_linear_history",
        "required_status_checks",
        "code_scanning",
    }
)


def check_ruleset(data: Any, name: str, target: str) -> list[str]:
    """Return a list of problems with one parsed ruleset."""
    if not isinstance(data, dict):
        return ["top-level value is not a JSON object"]
    errors: list[str] = []
    if data.get("name") != name:
        errors.append(f"name is {data.get('name')!r}, expected {name!r}")
    if data.get("target") != target:
        errors.append(f"target is {data.get('target')!r}, expected {target!r}")
    if data.get("enforcement") != "active":
        errors.append(f"enforcement is {data.get('enforcement')!r}, expected 'active'")
    if data.get("bypass_actors", []) != []:
        errors.append("bypass_actors must be empty")
    rules = data.get("rules")
    if not isinstance(rules, list) or not rules:
        errors.append("rules must be a non-empty list")
        return errors
    for rule in rules:
        rule_type = rule.get("type") if isinstance(rule, dict) else None
        if rule_type is None:
            errors.append(f"rule without a type: {rule!r}")
        elif rule_type in FORBIDDEN_RULE_TYPES:
            errors.append(f"forbidden rule type: {rule_type}")
    return errors


def verify(root: Path) -> list[str]:
    """Verify every expected ruleset under root; return all problems."""
    errors: list[str] = []
    for relative, expected in EXPECTED.items():
        path = root / relative
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            errors.append(f"{relative}: file is missing")
            continue
        except json.JSONDecodeError as exc:
            errors.append(f"{relative}: invalid JSON: {exc}")
            continue
        errors.extend(
            f"{relative}: {problem}"
            for problem in check_ruleset(data, expected["name"], expected["target"])
        )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="repository root (default: parent of tools/)",
    )
    args = parser.parse_args()
    errors = verify(args.root)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"Verified {len(EXPECTED)} rulesets.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
