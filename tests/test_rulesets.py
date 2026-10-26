"""Tests for tools/verify_rulesets.py and the shared ruleset definitions.

Run with: python3 -m unittest discover -s tests
"""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import verify_rulesets  # noqa: E402


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class RepositoryRulesetsTest(unittest.TestCase):
    def test_repository_rulesets_verify_clean(self) -> None:
        self.assertEqual(verify_rulesets.verify(ROOT), [])

    def test_default_branch_rules(self) -> None:
        data = load("rulesets/protect-default-branch.json")
        types = [rule["type"] for rule in data["rules"]]
        self.assertEqual(
            types,
            ["deletion", "non_fast_forward", "required_signatures", "pull_request"],
        )
        self.assertEqual(data["conditions"]["ref_name"]["include"], ["~DEFAULT_BRANCH"])
        params = data["rules"][3]["parameters"]
        self.assertEqual(params["allowed_merge_methods"], ["merge"])
        self.assertEqual(params["required_approving_review_count"], 0)

    def test_release_tag_rules(self) -> None:
        data = load("rulesets/protect-release-tags.json")
        types = [rule["type"] for rule in data["rules"]]
        self.assertEqual(types, ["deletion", "non_fast_forward", "update"])
        self.assertEqual(data["conditions"]["ref_name"]["include"], ["refs/tags/v*"])


    def test_integration_branch_rules_match_the_default_branch(self) -> None:
        # Catylist ADR-0013: dev-daily and fitment get the ADR-0006 rules.
        data = load("rulesets/protect-integration-branches.json")
        default = load("rulesets/protect-default-branch.json")
        self.assertEqual(data["rules"], default["rules"])
        self.assertEqual(data["bypass_actors"], [])
        self.assertEqual(
            data["conditions"]["ref_name"]["include"],
            ["refs/heads/dev-daily", "refs/heads/fitment"],
        )


class CheckRulesetTest(unittest.TestCase):
    def setUp(self) -> None:
        self.base = load("rulesets/protect-default-branch.json")

    def check(self, data: object) -> list[str]:
        return verify_rulesets.check_ruleset(data, "protect-default-branch", "branch")

    def test_rejects_forbidden_rule_types(self) -> None:
        for rule_type in sorted(verify_rulesets.FORBIDDEN_RULE_TYPES):
            with self.subTest(rule_type=rule_type):
                data = copy.deepcopy(self.base)
                data["rules"].append({"type": rule_type})
                self.assertIn(f"forbidden rule type: {rule_type}", self.check(data))

    def test_rejects_bypass_actors(self) -> None:
        data = copy.deepcopy(self.base)
        data["bypass_actors"] = [
            {"actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always"}
        ]
        self.assertIn("bypass_actors must be empty", self.check(data))

    def test_rejects_wrong_name_and_target(self) -> None:
        data = copy.deepcopy(self.base)
        data["name"] = "other"
        data["target"] = "tag"
        errors = self.check(data)
        self.assertEqual(len(errors), 2)

    def test_rejects_non_object(self) -> None:
        self.assertEqual(self.check([]), ["top-level value is not a JSON object"])


class VerifyTreeTest(unittest.TestCase):
    def test_reports_missing_and_invalid_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "rulesets").mkdir()
            (root / "rulesets" / "protect-default-branch.json").write_text("{not json")
            errors = verify_rulesets.verify(root)
        # One invalid file, and every other expected file is missing.
        self.assertEqual(len(errors), len(verify_rulesets.EXPECTED))
        self.assertTrue(any("invalid JSON" in error for error in errors))
        self.assertTrue(any("file is missing" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
