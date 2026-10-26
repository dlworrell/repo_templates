"""Contracts for the Catylist ADR-0013 shared CI and release workflows."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / "shared/github/workflows"


class BranchWorkflowTests(unittest.TestCase):
    def test_ci_runs_on_all_three_branches(self):
        text = (WORKFLOWS / "ci.yml").read_text()
        for event in ("pull_request", "push"):
            self.assertRegex(text, rf"{event}:\n    branches: \[dev-daily, fitment, main\]")
        self.assertIn("persist-credentials: false", text)

    def test_release_parks_at_the_owner_gate_before_tagging(self):
        text = (WORKFLOWS / "release.yml").read_text()
        verify, publish = text.split("\n  publish:\n", 1)
        self.assertIn("permissions:\n  contents: read\n", verify)
        self.assertNotIn("gh release create", verify)
        self.assertIn("refs/heads/main", verify)
        self.assertIn("already exists; release tags are immutable", verify)
        self.assertIn("needs: verify", publish)
        self.assertIn("environment: release", publish)
        self.assertIn("contents: write", publish)
        self.assertIn('--target "$SHA"', publish)

    def test_inputs_reach_shell_only_through_the_environment(self):
        for name in ("ci.yml", "release.yml"):
            for line in (WORKFLOWS / name).read_text().splitlines():
                if "${{" in line and "inputs." in line:
                    self.assertRegex(line, r"^\s+[A-Z_]+: \$\{\{ inputs\.[a-z_]+ \}\}$", f"{name}: {line}")

    def test_actions_are_pinned_to_full_shas(self):
        for name in ("ci.yml", "release.yml"):
            for ref in re.findall(r"uses: ([^\s]+)", (WORKFLOWS / name).read_text()):
                self.assertRegex(ref, r"@[0-9a-f]{40}$", f"{name}: {ref}")


if __name__ == "__main__":
    unittest.main()
