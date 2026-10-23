"""Tests for the shared .gitignore's credential and secret patterns.

Run with: python3 -m unittest discover -s tests
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHARED = ROOT / "shared" / "config" / ".gitignore"
BLOCK_START = "# Environment, credentials, and secrets\n"

SENSITIVE = (
    ".env",
    ".env.production",
    "config/.env.local",
    ".envrc",
    "server.pem",
    "certs/tls.key",
    "AuthKey_ABC123.p8",
    "signing.p12",
    "release.keystore",
    "vault.kdbx",
    "id_rsa",
    "deploy/id_ed25519",
    "github_rsa",
    ".netrc",
    ".git-credentials",
    ".npmrc",
    ".pypirc",
    ".docker/config.json",
    ".aws/credentials",
    "credentials.json",
    "client_secret_123.apps.googleusercontent.com.json",
    "my-project-service-account.json",
    "secrets.yaml",
    ".streamlit/secrets.toml",
    "api.secret",
    "local.settings.json",
    "terraform.tfstate",
    "terraform.tfstate.backup",
    "prod.tfvars",
    ".terraform/providers.lock",
    "kubeconfig",
    "cluster.kubeconfig",
)

ORDINARY = (
    ".env.example",
    ".env.sample",
    ".env.template",
    "id_rsa.pub",
    "deploy/id_ed25519.pub",
    "prod.tfvars.example",
    ".github/workflows/ci.yml",
    "src/key.c",
    "src/keys.h",
    "docs/secrets-handling.md",
    "package.json",
    "README.md",
)


def _ignored(directory: Path, path: str) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", "-q", "--no-index", path],
        cwd=directory,
        check=False,
    )
    if result.returncode not in (0, 1):
        raise AssertionError(f"git check-ignore failed for {path}")
    return result.returncode == 0


@unittest.skipUnless(shutil.which("git"), "git is required")
class SharedGitignoreTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        cls.repo = Path(cls._tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=cls.repo, check=True)
        shutil.copyfile(SHARED, cls.repo / ".gitignore")

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def test_credentials_and_secret_files_are_ignored(self) -> None:
        for path in SENSITIVE:
            with self.subTest(path=path):
                self.assertTrue(_ignored(self.repo, path), f"{path} is not ignored")

    def test_examples_public_keys_and_ordinary_files_are_not_ignored(self) -> None:
        for path in ORDINARY:
            with self.subTest(path=path):
                self.assertFalse(_ignored(self.repo, path), f"{path} is ignored")


class RepositoryGitignoreTest(unittest.TestCase):
    def test_repository_carries_the_shared_secret_block(self) -> None:
        shared = SHARED.read_text(encoding="utf-8")
        own = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(BLOCK_START, shared)
        self.assertIn(BLOCK_START, own)
        shared_block = shared[shared.index(BLOCK_START) :].splitlines()
        own_block = [
            line
            for line in own[own.index(BLOCK_START) :].splitlines()
            if not line.startswith("# (Same block as")
        ]
        self.assertEqual(own_block, shared_block)


if __name__ == "__main__":
    unittest.main()
