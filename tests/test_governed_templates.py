"""Behavioral contracts for the governed-scope and agent-context scaffolds."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCOPE = ROOT / "templates/project_scope"
AGENT = ROOT / "templates/agent_instructions"


class GovernedTemplateTests(unittest.TestCase):
    def test_scope_catalog_has_real_source_files_and_disjoint_destinations(self):
        catalog = json.loads((SCOPE / "template.json").read_text())
        targets = set()
        for item in catalog["files"]:
            self.assertTrue((ROOT / item["source"]).is_file())
            self.assertNotIn(item["target"], targets)
            self.assertFalse(item["target"].startswith("/"))
            self.assertNotIn("..", Path(item["target"]).parts)
            targets.add(item["target"])
        self.assertTrue({"{{SCOPE_PATH}}/README.md", "{{SCOPE_PATH}}/ci/check.sh",
                         "{{SCOPE_PATH}}/docs/engineering/README.md",
                         "{{SCOPE_PATH}}/tests/README.md"} <= targets)

    def test_unconfigured_scope_cannot_report_success(self):
        run = subprocess.run(["bash", str(SCOPE / "skeleton/ci/check.sh")],
                             text=True, capture_output=True)
        self.assertEqual(run.returncode, 2)
        self.assertIn("Configure scope-specific", run.stderr)

    def test_root_caller_is_read_only_and_delegates_to_scope(self):
        text = (SCOPE / "scope-ci.yml.example").read_text()
        self.assertIn("pull_request:", text)
        self.assertNotIn("pull_request_target", text)
        self.assertNotIn("self-hosted", text)
        self.assertNotIn("write", text)
        self.assertIn("contents: read", text)
        self.assertIn("persist-credentials: false", text)
        self.assertEqual(re.findall(r"^\s+run:\s*(.+)$", text, re.M),
                         ["bash '{{SCOPE_PATH}}/ci/check.sh'"])
        self.assertRegex(text, r"actions/checkout@[0-9a-f]{40}")

    def test_applicability_is_unresolved_until_evidence_is_supplied(self):
        text = (SCOPE / "manifest-scope.yaml.example").read_text()
        self.assertIn("{{STANDARD_APPLICABILITY}}", text)
        self.assertIn("{{APPLICABILITY_REASON}}", text)
        self.assertNotIn("applicability: not-applicable", text)
        self.assertIn("does not establish", (ROOT / "README.md").read_text())

    def test_agent_context_routes_to_authority_without_extra_permissions(self):
        text = (AGENT / "root/CLAUDE.md").read_text()
        self.assertLess(len(text.splitlines()), 100)
        for adr in ("ADR-0004", "ADR-0005", "ADR-0006", "ADR-0007"):
            self.assertIn(adr, text)
        self.assertEqual(json.loads((AGENT / "root/.claude/settings.json").read_text()), {})
        self.assertIn("../CLAUDE.md", (AGENT / "scope/CLAUDE.md").read_text())
        self.assertIn("ADR-0005", (AGENT / "README.md").read_text())

    def test_shared_ignore_excludes_personal_scope_and_root_agent_settings(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            shutil.copyfile(ROOT / "shared/config/.gitignore", root / ".gitignore")
            run = subprocess.run(["git", "check-ignore", "--stdin"], cwd=root,
                input=".claude/settings.local.json\nnative/.claude/settings.local.json\n.claude/settings.json\n",
                text=True, capture_output=True)
            self.assertEqual(set(run.stdout.splitlines()),
                             {".claude/settings.local.json", "native/.claude/settings.local.json"})


if __name__ == "__main__":
    unittest.main()
