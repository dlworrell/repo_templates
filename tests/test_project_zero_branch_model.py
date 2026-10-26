"""Project Zero checks for Catylist ADR-0013 daily, fitment and release branches."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import project_zero as p0  # noqa: E402

MODEL = {"adr": "Catylist ADR-0013", "branches": ["dev-daily", "fitment"], "release_environment": "release",
         "severity": "medium"}
GATED_RELEASE = "on:\n  workflow_dispatch:\njobs:\n  publish:\n    environment: release\n"


class TriggerTests(unittest.TestCase):
    def test_push_without_branch_filter_covers_every_branch(self):
        for text in ("on:\n  push:\n  pull_request:\n", "on: push\n", "on: [push, pull_request]\n",
                     "on:\n  push:\n    paths: ['src/**']\n"):
            with self.subTest(text=text):
                self.assertTrue(p0.runs_on_branches(text, ["dev-daily", "fitment"]))

    def test_branch_filter_must_name_every_branch(self):
        self.assertTrue(p0.runs_on_branches(
            "on:\n  push:\n    branches: [dev-daily, fitment, main]\n", ["dev-daily", "fitment"]))
        self.assertTrue(p0.runs_on_branches(
            "on:\n  push:\n    branches:\n      - main\n      - dev-daily\n      - fitment\n", ["dev-daily", "fitment"]))
        self.assertFalse(p0.runs_on_branches("on:\n  push:\n    branches: [main]\n", ["dev-daily", "fitment"]))
        self.assertFalse(p0.runs_on_branches(
            "on:\n  push:\n    branches: [dev-daily-old, fitment]\n", ["dev-daily", "fitment"]))

    def test_no_push_trigger_does_not_count(self):
        self.assertFalse(p0.runs_on_branches("on:\n  workflow_dispatch:\n", ["dev-daily"]))
        self.assertFalse(p0.runs_on_branches("on:\n  pull_request:\n    branches: [dev-daily]\n", ["dev-daily"]))


class AssessTests(unittest.TestCase):
    def repo(self, branches=(), workflows=None) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        run = lambda *a: subprocess.run(["git", "-C", str(root), *a], check=True, capture_output=True)
        run("init", "-q", "-b", "main")
        run("-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q", "--allow-empty",
            "--no-gpg-sign", "-m", "init")
        for branch in branches:
            run("branch", branch)
        (root / ".github/workflows").mkdir(parents=True)
        for name, text in (workflows or {}).items():
            (root / ".github/workflows" / name).write_text(text)
        return root

    def titles(self, root):
        return [f["title"] for f in p0.assess_branch_model(root, MODEL)]

    def test_unadopted_repository_reports_each_gap(self):
        titles = self.titles(self.repo(workflows={"ci.yml": "on:\n  push:\n    branches: [main]\n"}))
        self.assertIn("Long-lived branch is missing: dev-daily", titles)
        self.assertIn("Long-lived branch is missing: fitment", titles)
        self.assertTrue(any(t.startswith("No workflow runs on pushes") for t in titles))
        self.assertTrue(any("release" in t for t in titles))

    def test_adopted_repository_is_clean(self):
        root = self.repo(("dev-daily", "fitment"), {"ci.yml": "on:\n  push:\n  pull_request:\n",
                                                    "release.yml": GATED_RELEASE})
        self.assertEqual(self.titles(root), [])

    def test_release_without_the_gate_is_reported(self):
        root = self.repo(("dev-daily", "fitment"), {"ci.yml": "on: push\n",
                                                    "release.yml": "on:\n  workflow_dispatch:\njobs:\n  x:\n"})
        self.assertEqual(len(self.titles(root)), 1)

    def test_findings_are_report_only_with_the_profile_severity(self):
        for finding in p0.assess_branch_model(self.repo(), MODEL):
            self.assertEqual((finding["severity"], finding["domain"]), ("medium", "branch-model"))
            self.assertIn("Catylist ADR-0013", finding["remediation"])

    def test_default_profile_is_unchanged_and_adr0013_profile_blocks(self):
        import json
        default = json.loads((ROOT / ".aems/project-zero/profiles/default/profile.json").read_text())
        adopted = json.loads((ROOT / ".aems/project-zero/profiles/adr-0013/profile.json").read_text())
        self.assertNotIn("branch_model", default)
        self.assertEqual(adopted["branch_model"]["severity"], "high")
        self.assertEqual({k: v for k, v in adopted.items() if k not in ("branch_model", "profile_id", "title")},
                         {k: v for k, v in default.items() if k not in ("profile_id", "title")})
        level, result = p0.readiness(p0.assess(self.repo(), adopted))
        self.assertEqual(result, "REMEDIATION REQUIRED")

    def test_profile_without_branch_model_adds_nothing(self):
        root = self.repo()
        self.assertFalse([f for f in p0.assess(root, {}) if f["domain"] == "branch-model"])


if __name__ == "__main__":
    unittest.main()
