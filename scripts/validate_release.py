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
CATALOG_PATH = ROOT / "docs" / "catalog" / "projects.json"

TEXT_DENYLIST = {
    "/Users/": "private absolute macOS path",
    "/home/": "private absolute Linux path",
    "justuss@": "private email address",
    "nimbleway.com": "company-internal address or domain",
    "BEGIN PRIVATE KEY": "private key material",
    "BEGIN RSA PRIVATE KEY": "private key material",
    "BEGIN EC PRIVATE KEY": "private key material",
    "BEGIN OPENSSH PRIVATE KEY": "private key material",
}
SECRET_PATTERNS = {
    "GitHub token": re.compile(r"\bgh(?:o|p|s|u|r)_[A-Za-z0-9]{20,}\b"),
    "GitHub fine-grained token": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "Google API key": re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    "Slack token": re.compile(r"\bxox(?:a|b|p|r|s)-[A-Za-z0-9-]{16,}\b"),
    "Stripe live key": re.compile(r"\b(?:sk|rk)_live_[A-Za-z0-9]{16,}\b"),
    "generic secret assignment": re.compile(
        r"(?i)\b(?:api[_-]?key|token|password|client[_-]?secret)\b\s*[:=]\s*['\"](?!REPLACE_|example|placeholder)[^'\"\s]{12,}"
    ),
    "bearer token": re.compile(r"(?i)\bBearer\s+(?!<|REPLACE_|example)[A-Za-z0-9._~-]{16,}"),
    "private email address": re.compile(
        r"(?i)\b[A-Z0-9._%+-]+@(?!example\.(?:com|org)\b|users\.noreply\.github\.com\b)[A-Z0-9.-]+\.[A-Z]{2,}\b"
    ),
}

FORBIDDEN_PATH_PARTS = {
    ".env",
    "archive",
    "data",
    "fixtures-private",
    "logs",
    "output",
    "outputs",
    "private",
    "tmp",
}

FORBIDDEN_FILENAMES = {
    ".git-credentials",
    ".netrc",
    ".npmrc",
    "credentials.json",
    "secrets.json",
    "token.json",
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
        relative_parts = {part.lower() for part in relative.parts}
        if relative.name.lower() in FORBIDDEN_FILENAMES:
            fail(errors, f"{relative}: forbidden sensitive filename")
        forbidden_parts = sorted(relative_parts & FORBIDDEN_PATH_PARTS)
        if forbidden_parts:
            fail(errors, f"{relative}: forbidden private/runtime path part {forbidden_parts[0]!r}")
        for needle, label in TEXT_DENYLIST.items():
            if needle in text:
                fail(errors, f"{relative}: {label}: {needle}")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                fail(errors, f"{relative}: possible {label}")


def validate_catalog(errors: list[str]) -> None:
    try:
        catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(errors, "docs/catalog/projects.json: catalog is required")
        return
    except json.JSONDecodeError as exc:
        fail(errors, f"docs/catalog/projects.json: invalid JSON: {exc}")
        return

    projects = catalog.get("projects")
    if catalog.get("schema_version") != 1 or not isinstance(projects, list):
        fail(errors, "docs/catalog/projects.json: schema_version=1 and projects[] are required")
        return

    required = {"id", "title", "kind", "status", "public_surface", "kept_private"}
    seen: set[str] = set()
    for index, project in enumerate(projects):
        if not isinstance(project, dict):
            fail(errors, f"docs/catalog/projects.json: projects[{index}] must be an object")
            continue
        missing = sorted(required - set(project))
        if missing:
            fail(errors, f"docs/catalog/projects.json: projects[{index}] missing {', '.join(missing)}")
        project_id = project.get("id")
        if not isinstance(project_id, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", project_id):
            fail(errors, f"docs/catalog/projects.json: projects[{index}].id must be kebab-case")
        elif project_id in seen:
            fail(errors, f"docs/catalog/projects.json: duplicate project id {project_id!r}")
        else:
            seen.add(project_id)
        if project.get("kind") not in {"architecture", "concept", "skill", "standalone"}:
            fail(errors, f"docs/catalog/projects.json: {project_id!r} has invalid kind")
        if project.get("status") not in {"published", "documented", "queued"}:
            fail(errors, f"docs/catalog/projects.json: {project_id!r} has invalid status")
        public_surface = project.get("public_surface")
        if not isinstance(public_surface, str) or not public_surface:
            fail(errors, f"docs/catalog/projects.json: {project_id!r} requires public_surface")
        elif public_surface.startswith("https://"):
            if not public_surface.startswith("https://github.com/justus20santiago-web/"):
                fail(errors, f"docs/catalog/projects.json: {project_id!r} has an unapproved external surface")
        elif public_surface.startswith(("http://", "/")) or ".." in Path(public_surface).parts:
            fail(errors, f"docs/catalog/projects.json: {project_id!r} has an unsafe public surface")
        elif not (ROOT / public_surface).is_file():
            fail(errors, f"docs/catalog/projects.json: {project_id!r} surface does not exist: {public_surface}")

        kept_private = project.get("kept_private")
        if not isinstance(kept_private, list) or not kept_private:
            fail(errors, f"docs/catalog/projects.json: {project_id!r} requires a non-empty kept_private list")
        elif any(not isinstance(item, str) or not item.strip() for item in kept_private):
            fail(errors, f"docs/catalog/projects.json: {project_id!r} kept_private values must be non-empty strings")


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
    validate_catalog(errors)
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
