#!/usr/bin/env python3
"""Deterministic floor for a human-reviewed messaging QA process."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path


FILLER = (
    "i wanted to reach out",
    "following up",
    "circling back",
    "closing the loop",
    "hope you're well",
    "hope you are well",
    "touching base",
    "just checking in",
)
HEDGES = re.compile(r"\b(perhaps|maybe|possibly|potentially|i think|sort of|kind of)\b", re.I)
GRAMMAR_SMELL = re.compile(
    r"\b(\w{2,})\s+\1\b|,\s*,|\b(a|an|the)\s+(a|an|the)\b",
    re.I,
)
STOP_WORDS = set("the and that with have from into what where when who were this your".split())


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def detect_columns(
    rows: list[dict[str, str]], id_column: str | None, message_column: str | None
) -> tuple[str, str]:
    fields = list(rows[0])
    message_column = message_column or max(
        fields, key=lambda field: sum(len(row.get(field) or "") for row in rows)
    )
    return id_column or fields[0], message_column


def normalize(text: str) -> str:
    return " ".join(re.findall(r"[\w']+", text.lower()))


def strip_salutation(text: str) -> str:
    return re.sub(r"^\s*(hi|hey|hello|dear)\s+[\w.'-]+\s*,?\s*", "", text, flags=re.I)


def shared_edge(texts: list[str], *, first: bool, size: int = 5) -> str | None:
    candidates: Counter[str] = Counter()
    for text in texts:
        words = normalize(strip_salutation(text) if first else text).split()
        if len(words) >= size:
            token = " ".join(words[:size] if first else words[-size:])
            candidates[token] += 1
    if not candidates:
        return None
    value, count = candidates.most_common(1)[0]
    return value if count > len(texts) * 0.60 else None


def load_terms(path: Path | None) -> list[str]:
    if not path:
        return []
    return [line.strip().lower() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def baseline_survival(old: str, new: str) -> str | None:
    quoted = re.findall(r":\s*([^.]{15,180})\.", old)
    if not quoted or old == new:
        return None
    distinctive = [
        word.lower().strip(",\"'")
        for word in quoted[0].split()
        if len(word) > 4 and word.lower() not in STOP_WORDS
    ]
    if len(distinctive) < 3:
        return None
    survived = sum(word in new.lower() for word in distinctive)
    if survived / len(distinctive) < 0.34:
        return f"source language mostly vanished ({survived}/{len(distinctive)} terms remain)"
    return None


def lint(
    items: list[tuple[str, str]],
    collision_terms: list[str],
    baseline: dict[str, str],
) -> dict[str, list[str]]:
    texts = [text for _, text in items]
    opener = shared_edge(texts, first=True)
    closer = shared_edge(texts, first=False)
    issues: dict[str, list[str]] = {}
    repeated: dict[str, set[str]] = {}

    def add(row_id: str, message: str) -> None:
        issues.setdefault(row_id, []).append(message)

    for row_id, text in items:
        lowered = text.lower()
        normalized = normalize(strip_salutation(text))
        if opener and not normalized.startswith(opener):
            add(row_id, "missing shared opener")
        if closer and not normalize(text).endswith(closer):
            add(row_id, "missing shared closer")
        if "—" in text:
            add(row_id, "em dash")
        for phrase in FILLER:
            if phrase in lowered:
                add(row_id, f"filler phrase: {phrase}")
        if match := HEDGES.search(text):
            add(row_id, f"hedge word: {match.group(0)}")
        if GRAMMAR_SMELL.search(text):
            add(row_id, "possible grammar corruption")
        for term in collision_terms:
            if term in lowered:
                add(row_id, f"positioning collision: {term}")
        word_count = len(text.split())
        if word_count < 25 or word_count > 160:
            add(row_id, f"word-count outlier: {word_count}")
        if old := baseline.get(row_id):
            if problem := baseline_survival(old, text):
                add(row_id, problem)

        words = normalized.split()
        for index in range(max(0, len(words) - 3)):
            phrase = " ".join(words[index : index + 4])
            repeated.setdefault(phrase, set()).add(row_id)

    for phrase, row_ids in repeated.items():
        if len(row_ids) >= 3:
            for row_id in row_ids:
                add(row_id, f"repeated four-word phrase across {len(row_ids)} rows: {phrase}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--id-col")
    parser.add_argument("--msg-col")
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--collision-terms", type=Path)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    rows = read_rows(args.csv_path)
    if not rows:
        print("empty CSV")
        return 1
    id_column, message_column = detect_columns(rows, args.id_col, args.msg_col)
    items = [(row[id_column], row.get(message_column) or "") for row in rows]

    baseline: dict[str, str] = {}
    if args.baseline:
        old_rows = read_rows(args.baseline)
        old_id, old_message = detect_columns(old_rows, args.id_col, args.msg_col)
        baseline = {row[old_id]: row.get(old_message) or "" for row in old_rows}

    issues = lint(items, load_terms(args.collision_terms), baseline)
    if args.verbose:
        for row_id, _ in items:
            row_issues = issues.get(row_id, [])
            verdict = "PASS" if not row_issues else "FAIL"
            print(f"[{verdict}] {row_id}: {'; '.join(row_issues)}")

    total = sum(len(row_issues) for row_issues in issues.values())
    if total:
        print(f"{total} mechanical violations across {len(issues)} rows")
        return 1
    print(f"MECHANICALLY CLEAN: {len(items)} rows. Human row-by-row review is still required.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
