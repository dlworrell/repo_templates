#!/usr/bin/env python3
"""Project Zero repository inspection, remediation, reporting, and certification.

The engine is intentionally standard-library-only so the same command runs in a
fresh GitHub Actions runner or an existing working tree without bootstrapping a
Python environment.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

SAFE_STUBS: dict[str, str] = {
    "SECURITY.md": "# Security Policy\n\nReport security concerns privately to the repository owner.\n",
    "CONTRIBUTING.md": "# Contributing\n\nChanges require a focused branch, reviewable commits, validation evidence, and a pull request.\n",
    "GOVERNANCE.md": "# Governance\n\nThis repository is governed by the Catalyst AES and AEMS authority chain.\n",
    "repo.yaml": "repository:\n  id: TODO\n  name: TODO\n  purpose: TODO\n  owner: TODO\n  lifecycle: project-zero\n",
    "p0.yaml": "project_zero:\n  profile: default\n  target_level: P0-9\n  certification_required: true\n",
    ".github/pull_request_template.md": "## Objective\n\n## Governing specification or ADR\n\n## Validation evidence\n\n## Security and recovery impact\n",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Project Zero against a repository working tree.")
    parser.add_argument("mode", choices=("inspect", "plan", "remediate", "verify", "certify"))
    parser.add_argument("--root", default=".", help="Repository working-tree root")
    parser.add_argument(
        "--profile",
        default=".aems/project-zero/profiles/default/profile.json",
        help="Profile JSON path, relative to --root unless absolute",
    )
    parser.add_argument("--output", default="build/project-zero-report", help="Report output directory")
    parser.add_argument("--repository-state", choices=("existing", "new"), default="existing")
    return parser.parse_args()


def git_value(root: Path, *args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), *args], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def load_profile(root: Path, value: str) -> tuple[Path, dict[str, Any]]:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    with path.open("r", encoding="utf-8") as stream:
        return path, json.load(stream)


def inventory(root: Path, output: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    output_resolved = output.resolve()
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue
        try:
            path.resolve().relative_to(output_resolved)
            continue
        except ValueError:
            pass
        relative = path.relative_to(root).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        records.append({"path": relative, "size": path.stat().st_size, "sha256": digest})
    return records


def assess(root: Path, profile: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for required in profile.get("required_files", []):
        if not (root / required).is_file():
            findings.append(
                {
                    "id": f"P0-MISSING-{len(findings) + 1:04d}",
                    "severity": "high",
                    "domain": "repository-baseline",
                    "title": f"Required file is missing: {required}",
                    "path": required,
                    "remediation": "Create the required file through a reviewed remediation pull request.",
                }
            )
    for recommended in profile.get("recommended_directories", []):
        if not (root / recommended).is_dir():
            findings.append(
                {
                    "id": f"P0-MISSING-{len(findings) + 1:04d}",
                    "severity": "medium",
                    "domain": "repository-structure",
                    "title": f"Recommended directory is missing: {recommended}",
                    "path": recommended,
                    "remediation": "Create the directory when its first governed artifact is added.",
                }
            )
    workflows = root / ".github" / "workflows"
    workflow_text = ""
    if workflows.is_dir():
        for workflow in workflows.glob("*.y*ml"):
            workflow_text += workflow.read_text(encoding="utf-8", errors="replace")
    for fragment in profile.get("required_workflow_fragments", []):
        if fragment not in workflow_text:
            findings.append(
                {
                    "id": f"P0-WORKFLOW-{len(findings) + 1:04d}",
                    "severity": "high",
                    "domain": "automation",
                    "title": f"Required workflow capability is absent: {fragment}",
                    "path": ".github/workflows",
                    "remediation": "Install or update a governed workflow containing the required capability.",
                }
            )
    model = profile.get("branch_model")
    if model:
        findings.extend(assess_branch_model(root, model, len(findings)))
    return findings


def _trigger_block(text: str) -> str:
    """The workflow's top-level ``on:`` block (or inline value), as text."""
    match = re.search(r"^(?:on|\"on\"|'on'):[ \t]*(.*)$", text, re.MULTILINE)
    if not match:
        return ""
    if match.group(1).strip():
        return match.group(1)
    block = []
    for line in text[match.end():].splitlines()[1:]:
        if line.strip() and not line.startswith((" ", "\t")):
            break
        block.append(line)
    return "\n".join(block)


def runs_on_branches(text: str, branches: list[str]) -> bool:
    """True if a workflow's push trigger covers every listed branch.

    A push trigger with no branch filter covers all branches; otherwise each
    branch must be named in the trigger block.
    """
    block = _trigger_block(text)
    if not block:
        return False
    if not block.startswith(("\n", " ")) and "\n" not in block:  # inline: on: push / on: [push, ...]
        return "push" in block
    push = re.search(r"^([ \t]+)push:[ \t]*(.*)$", block, re.MULTILINE)
    if not push:
        return False
    indent = len(push.group(1))
    sub = []
    for line in block[push.end():].splitlines()[1:]:
        if line.strip() and len(line) - len(line.lstrip()) <= indent:
            break
        sub.append(line)
    filters = "\n".join(sub)
    if not re.search(r"^\s*branches(?:-ignore)?:", filters, re.MULTILINE):
        return True
    return all(re.search(rf"(?<![\w/-]){re.escape(b)}(?![\w/-])", filters) for b in branches)


def branch_exists(root: Path, branch: str) -> bool | None:
    """Whether ``branch`` exists on origin (or locally); None if unknowable."""
    remote = git_value(root, "ls-remote", "--heads", "origin", branch)
    if remote is not None:
        return bool(remote)
    for ref in (f"refs/remotes/origin/{branch}", f"refs/heads/{branch}"):
        if git_value(root, "rev-parse", "--verify", "--quiet", ref):
            return True
    # Without an origin remote the local branches are the whole answer.
    return False if git_value(root, "remote", "get-url", "origin") is None else None


def assess_branch_model(root: Path, model: dict[str, Any], offset: int = 0) -> list[dict[str, Any]]:
    """Catylist ADR-0013: daily, fitment and release branches.

    Reports missing long-lived branches, CI that does not run on them, and a
    release workflow without the owner's approval gate. Remediation is a
    reviewed adoption pull request, so these findings are report-only.
    """
    severity = model.get("severity", "medium")
    adr = model.get("adr", "Catylist ADR-0013")
    branches = list(model.get("branches", ["dev-daily", "fitment"]))
    findings: list[dict[str, Any]] = []

    def add(title: str, path: str, remediation: str) -> None:
        findings.append({"id": f"P0-BRANCH-{offset + len(findings) + 1:04d}", "severity": severity,
                         "domain": "branch-model", "title": title, "path": path,
                         "remediation": f"{remediation} ({adr})."})

    for branch in branches:
        exists = branch_exists(root, branch)
        if exists is None:
            add(f"Could not confirm that the {branch} branch exists", branch,
                f"Run Project Zero where origin is reachable, or create {branch} from the default branch")
        elif not exists:
            add(f"Long-lived branch is missing: {branch}", branch,
                f"Create {branch} from the default branch, then apply protect-integration-branches through AEMS")
    workflows = sorted((root / ".github" / "workflows").glob("*.y*ml")) if (root / ".github" / "workflows").is_dir() else []
    texts = {w: w.read_text(encoding="utf-8", errors="replace") for w in workflows}
    if not any(runs_on_branches(t, branches) for t in texts.values()):
        add(f"No workflow runs on pushes to {', '.join(branches)}", ".github/workflows",
            "Add the branches to CI's push trigger, or install repo_templates shared/github/workflows/ci.yml")
    gate = model.get("release_environment", "release")
    if not any("workflow_dispatch" in t and re.search(rf"^\s*environment:\s*{re.escape(gate)}\s*$", t, re.MULTILINE)
               for t in texts.values()):
        add(f"No release workflow parks at the '{gate}' environment for owner approval", ".github/workflows",
            "Install repo_templates shared/github/workflows/release.yml with the repository's own test command")
    return findings


def remediate(root: Path, findings: list[dict[str, Any]]) -> list[str]:
    changes: list[str] = []
    missing_paths = {item.get("path") for item in findings}
    for relative, contents in SAFE_STUBS.items():
        path = root / relative
        if relative not in missing_paths or path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
        changes.append(relative)
    return changes


def readiness(findings: list[dict[str, Any]]) -> tuple[str, str]:
    critical = sum(item["severity"] == "critical" for item in findings)
    high = sum(item["severity"] == "high" for item in findings)
    if critical or high:
        return "P0-2", "REMEDIATION REQUIRED"
    if findings:
        return "P0-6", "CONDITIONALLY READY"
    return "P0-9", "CERTIFIABLE"


def write_reports(
    root: Path,
    profile_path: Path,
    profile: dict[str, Any],
    output: Path,
    args: argparse.Namespace,
    records: list[dict[str, Any]],
    findings: list[dict[str, Any]],
    changes: list[str],
) -> None:
    output.mkdir(parents=True, exist_ok=True)
    level, result = readiness(findings)
    counts = {severity: sum(item["severity"] == severity for item in findings) for severity in ("critical", "high", "medium", "low", "informational")}
    run = {
        "schema_version": "0.1.0",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "mode": args.mode,
        "repository_state": args.repository_state,
        "repository": git_value(root, "config", "--get", "remote.origin.url") or root.name,
        "commit": git_value(root, "rev-parse", "HEAD"),
        "branch": git_value(root, "rev-parse", "--abbrev-ref", "HEAD"),
        "profile": str(profile_path.relative_to(root) if profile_path.is_relative_to(root) else profile_path),
        "profile_id": profile.get("profile_id"),
        "readiness_level": level,
        "result": result,
        "finding_counts": counts,
        "remediation_changes": changes,
    }
    (output / "run-manifest.json").write_text(json.dumps(run, indent=2) + "\n", encoding="utf-8")
    (output / "repository-inventory.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    (output / "findings.json").write_text(json.dumps(findings, indent=2) + "\n", encoding="utf-8")
    (output / "remediation-plan.json").write_text(
        json.dumps({"findings": findings, "applied_changes": changes}, indent=2) + "\n", encoding="utf-8"
    )
    summary = [
        "# Project Zero Assessment",
        "",
        f"- **Repository:** `{run['repository']}`",
        f"- **Mode:** `{args.mode}`",
        f"- **Profile:** `{run['profile_id']}`",
        f"- **Current readiness:** `{level}`",
        f"- **Result:** **{result}**",
        f"- **Critical:** {counts['critical']}",
        f"- **High:** {counts['high']}",
        f"- **Medium:** {counts['medium']}",
        f"- **Files inventoried:** {len(records)}",
        f"- **Safe remediation files created:** {len(changes)}",
        "",
        "## Findings",
        "",
    ]
    if findings:
        summary.extend(f"- **{item['severity'].upper()}** `{item['id']}` — {item['title']}" for item in findings)
    else:
        summary.append("No findings.")
    (output / "executive-summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    output = Path(args.output)
    if not output.is_absolute():
        output = root / output
    profile_path, profile = load_profile(root, args.profile)
    records = inventory(root, output)
    findings = assess(root, profile)
    changes: list[str] = []
    if args.mode == "remediate":
        changes = remediate(root, findings)
        findings = assess(root, profile)
    write_reports(root, profile_path, profile, output, args, records, findings, changes)
    _, result = readiness(findings)
    print(f"PROJECT_ZERO_RESULT={result}")
    print(f"PROJECT_ZERO_REPORT={output}")
    if args.mode in {"verify", "certify"} and result != "CERTIFIABLE":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
