#!/usr/bin/env python3
"""Validate the public-release boundary and portable artifacts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / "n8n" / "workflows"
SKILL_ROOT = ROOT / "skills"

TEXT_DENYLIST = {
    "/Users/": "private absolute macOS path",
    "justuss@": "private email address",
    "nimbleway.com": "company-internal address or domain",
    "BEGIN PRIVATE KEY": "private key material",
    "BEGIN OPENSSH PRIVATE KEY": "private key material",
}
SECRET_PATTERNS = {
    "GitHub token": re.compile(r"\bgh(?:o|p|s|u|r)_[A-Za-z0-9]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "generic secret assignment": re.compile(
        r"(?i)\b(?:api[_-]?key|token|password|client[_-]?secret)\b\s*[:=]\s*['\"](?!REPLACE_|example|placeholder)[^'\"\s]{12,}"
    ),
    "bearer token": re.compile(r"(?i)\bBearer\s+(?!<|REPLACE_|example)[A-Za-z0-9._~-]{16,}"),
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def scan_text(errors: list[str]) -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path == Path(__file__).resolve():
            # This file necessarily contains the denylist literals it enforces.
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        relative = path.relative_to(ROOT)
        for needle, label in TEXT_DENYLIST.items():
            if needle in text:
                fail(errors, f"{relative}: {label}: {needle}")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                fail(errors, f"{relative}: possible {label}")


def walk_credentials(value: Any, path: str = "root") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(value, dict):
        if "credentials" in value and isinstance(value["credentials"], dict):
            for credential_type, credential in value["credentials"].items():
                if isinstance(credential, dict) and isinstance(credential.get("id"), str):
                    found.append((f"{path}.credentials.{credential_type}.id", credential["id"]))
        for key, child in value.items():
            found.extend(walk_credentials(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(walk_credentials(child, f"{path}[{index}]"))
    return found


def validate_workflows(errors: list[str]) -> None:
    workflows = sorted(WORKFLOW_DIR.glob("*.json"))
    if len(workflows) < 2:
        fail(errors, "n8n/workflows: expected at least two workflow exports")
    for path in workflows:
        relative = path.relative_to(ROOT)
        try:
            workflow = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(errors, f"{relative}: invalid JSON: {exc}")
            continue

        if workflow.get("active") is not False:
            fail(errors, f"{relative}: workflow must be inactive")
        if not workflow.get("description"):
            fail(errors, f"{relative}: workflow description is required")
        for forbidden in ("pinData", "staticData", "executionData", "activeVersionId"):
            if forbidden in workflow:
                fail(errors, f"{relative}: forbidden runtime field {forbidden}")

        nodes = workflow.get("nodes")
        connections = workflow.get("connections")
        if not isinstance(nodes, list) or not isinstance(connections, dict):
            fail(errors, f"{relative}: nodes must be a list and connections an object")
            continue
        names = [node.get("name") for node in nodes if isinstance(node, dict)]
        if len(names) != len(set(names)) or any(not name for name in names):
            fail(errors, f"{relative}: node names must be present and unique")
        name_set = set(names)

        for source, outputs in connections.items():
            if source not in name_set:
                fail(errors, f"{relative}: connection source is missing node {source!r}")
            for output_group in outputs.get("main", []):
                for edge in output_group or []:
                    if edge.get("node") not in name_set:
                        fail(errors, f"{relative}: connection target is missing node {edge.get('node')!r}")

        for node in nodes:
            if node.get("onError") == "continueErrorOutput":
                main_outputs = connections.get(node["name"], {}).get("main", [])
                if len(main_outputs) < 2 or not main_outputs[1]:
                    fail(errors, f"{relative}: {node['name']!r} enables an error output but does not wire it")

        for location, credential_id in walk_credentials(workflow):
            if not credential_id.startswith("REPLACE_"):
                fail(errors, f"{relative}: real-looking credential id at {location}")


def validate_skills(errors: list[str]) -> None:
    skill_files = sorted(SKILL_ROOT.glob("*/SKILL.md"))
    if len(skill_files) < 3:
        fail(errors, "skills: expected at least three portable skills")
    for path in skill_files:
        relative = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            fail(errors, f"{relative}: missing YAML frontmatter")
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            fail(errors, f"{relative}: unterminated YAML frontmatter")
            continue
        frontmatter = parts[1]
        if not re.search(r"(?m)^name:\s*\S+", frontmatter):
            fail(errors, f"{relative}: frontmatter requires name")
        if not re.search(r"(?m)^description:\s*\S+", frontmatter):
            fail(errors, f"{relative}: frontmatter requires description")


def main() -> int:
    errors: list[str] = []
    scan_text(errors)
    validate_workflows(errors)
    validate_skills(errors)
    if errors:
        print("PUBLIC RELEASE VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PUBLIC RELEASE VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
