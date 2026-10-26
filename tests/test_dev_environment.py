"""Behavioral contracts for the dev-environment, ADR-0000 and ring 0 templates."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
DEV = ROOT / "templates/dev_environment"
AGENT = ROOT / "templates/agent_instructions"


class DevSetupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.repo = base / "repo"
        self.home = base / "home"
        self.home.mkdir()
        # Isolate from the machine's own Git configuration.
        self.env = {**os.environ, "HOME": str(self.home), "GIT_CONFIG_GLOBAL": str(self.home / "gitconfig"),
                    "GIT_CONFIG_NOSYSTEM": "1"}
        self.git("init", "-q", "-b", "main", str(self.repo), cwd=base)
        self.git("remote", "add", "origin", "https://github.com/dlworrell/example.git")
        self.git("config", "--local", "--replace-all", "remote.origin.fetch", "+refs/heads/main:refs/remotes/origin/main")
        (self.repo / "scripts").mkdir()
        shutil.copy(DEV / "scripts/dev-setup.sh", self.repo / "scripts/dev-setup.sh")
        shutil.copy(DEV / ".gitmessage", self.repo / ".gitmessage")

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args, cwd=None):
        return subprocess.run(["git", *args], cwd=cwd or self.repo, env=self.env, check=True,
                              capture_output=True, text=True).stdout.strip()

    def setup(self, *args):
        return subprocess.run(["bash", "scripts/dev-setup.sh", *args], cwd=self.repo, env=self.env,
                              capture_output=True, text=True)

    def signing_key(self) -> Path:
        """A stand-in key pair; the script must never read or print the private half."""
        key = self.home / "signing"
        key.write_text("-----BEGIN OPENSSH " + "PRIVATE KEY-----\nPRIVATE-MATERIAL-THAT-MUST-NOT-LEAK\n"
                       "-----END OPENSSH " + "PRIVATE KEY-----\n")
        (self.home / "signing.pub").write_text("ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIStandIn test\n")
        return key

    def test_check_reports_without_changing_anything(self):
        before = self.git("config", "--local", "--list")
        run = self.setup("--check")
        self.assertEqual(run.returncode, 1)
        self.assertIn("needs-you no signing key", run.stdout)
        self.assertIn("fixable   origin fetches only some branches", run.stdout)
        self.assertIn("fixable   git pull merges instead of rebasing", run.stdout)
        self.assertEqual(self.git("config", "--local", "--list"), before)

    def test_fix_applies_safe_settings_and_never_prints_the_key(self):
        key = self.signing_key()
        self.git("config", "--global", "user.name", "Test Person")
        self.git("config", "--global", "user.email", "test@example.com")
        self.git("config", "--global", "gpg.format", "ssh")
        self.git("config", "--global", "user.signingkey", str(key) + ".pub")
        run = self.setup("--fix")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("fixed     origin fetches every branch", run.stdout)
        self.assertEqual(self.git("config", "--local", "commit.gpgsign"), "true")
        self.assertEqual(self.git("config", "--local", "pull.rebase"), "false")
        self.assertEqual(self.git("config", "--local", "commit.template"), ".gitmessage")
        self.assertNotIn("PRIVATE-MATERIAL-THAT-MUST-NOT-LEAK", run.stdout + run.stderr)
        self.assertIn("SSH signing key configured", run.stdout)
        again = self.setup("--check")
        self.assertEqual(again.returncode, 0, again.stdout)
        self.assertNotIn("fixed", again.stdout)

    def test_branch_tracking_the_default_branch_needs_attention(self):
        self.git("config", "--global", "user.name", "T")
        self.git("config", "--global", "user.email", "t@example.com")
        self.git("commit", "-q", "--allow-empty", "-m", "init", "--no-gpg-sign")
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")
        self.git("switch", "-q", "-c", "feat/x", "--track", "origin/main")
        run = self.setup("--check")
        self.assertIn("feat/x tracks origin/main", run.stdout)

    def test_misuse_exits_2(self):
        self.assertEqual(self.setup("--rebase").returncode, 2)


class RingZeroTemplateTests(unittest.TestCase):
    def test_adr0000_template_is_the_standard_text(self):
        text = (ROOT / "templates/adr/ADR-0000-catylist-code-of-conduct.md").read_text()
        for needle in ("Ring: 0", "Code version: 1.1.0", "{{ADOPTED_DATE}}", "{{CATYLIST_REVISION}}",
                       "never renumbered, amended or superseded here", "Don't be a dick."):
            self.assertIn(needle, text)

    def test_agent_files_route_to_ring0_and_require_the_title_line(self):
        claude = (AGENT / "root/CLAUDE.md").read_text()
        agents = (AGENT / "root/AGENTS.md").read_text()
        for text in (claude, agents):
            self.assertIn("ADR-0000-catylist-code-of-conduct.md", text)
            self.assertIn("ADR-0011", text)
            self.assertIn("**<Agent> for @<prompting user>**", text)
            self.assertIn("scripts/dev-setup.sh --check", text)
            self.assertLess(len(text.splitlines()), 100)
        self.assertEqual(claude.split("## Ring 0", 1)[1], agents.split("## Ring 0", 1)[1])

    def test_code_of_conduct_points_to_ring0_and_preserves_the_community_text(self):
        text = (ROOT / "CODE_OF_CONDUCT.md").read_text()
        self.assertIn("Catylist Code of Conduct", text)
        self.assertIn("**Love everyone as you love yourself.**", text)
        self.assertIn("## Wheaton's Law\n\nBe excellent to each other.", text)
        self.assertNotRegex(text, r"(?m)^###\s+Law\s+\d")  # never restates the Code (Law 7)

    def test_pull_request_template_asks_for_the_adr_line(self):
        text = (ROOT / ".github/pull_request_template.md").read_text()
        self.assertRegex(text, r"(?m)^ADR: ")
        self.assertIn("for @<prompting user>", text)


if __name__ == "__main__":
    unittest.main()
