#!/usr/bin/env python3
"""Compare the pre-reorganization 106-item publication index with the current catalog.

This script is diagnostic only: it never edits publication files.  It reports
catalog multiplicity lost during the subject-folder migration and, where
possible, identifies the current canonical item with the same PDF bytes.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = "6a2ce29ddc308747d75ca82f58c3b35604a8b744"


def norm_title(value: str) -> str:
    value = (value or "").casefold().replace("—", "-").replace("–", "-")
    return re.sub(r"\s+", " ", value).strip()


def git_bytes(path: str) -> bytes | None:
    path = unquote((path or "").strip())
    if not path or path.endswith("/") or path.startswith(("http://", "https://")):
        return None
    proc = subprocess.run(
        ["git", "show", f"{BASE}:{path}"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return proc.stdout if proc.returncode == 0 else None


def main() -> None:
    old_raw = subprocess.run(
        ["git", "show", f"{BASE}:docs/search-index.json"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        check=True,
    ).stdout
    old = json.loads(old_raw)["items"]
    current = json.loads((ROOT / "scripts/publications.json").read_text())["items"]

    old_groups: dict[str, list[dict]] = defaultdict(list)
    cur_groups: dict[str, list[dict]] = defaultdict(list)
    for item in old:
        old_groups[norm_title(item.get("title", ""))].append(item)
    for item in current:
        cur_groups[norm_title(item.get("title", ""))].append(item)

    current_by_sha: dict[str, list[dict]] = defaultdict(list)
    for item in current:
        if item.get("sha256"):
            current_by_sha[item["sha256"]].append(item)

    losses = []
    for key, old_items in old_groups.items():
        keep = len(cur_groups.get(key, []))
        for old_item in old_items[keep:]:
            archive_path = old_item.get("archive_path", "")
            blob = git_bytes(archive_path)
            digest = hashlib.sha256(blob).hexdigest() if blob is not None else None
            hash_matches = [
                {"title": x.get("title"), "id": x.get("id"), "sha256": digest}
                for x in current_by_sha.get(digest or "", [])
            ]
            losses.append(
                {
                    "title": old_item.get("title"),
                    "kind": old_item.get("kind"),
                    "category": old_item.get("category"),
                    "href": old_item.get("href"),
                    "pdf": old_item.get("pdf"),
                    "source": old_item.get("source"),
                    "archive_path": archive_path,
                    "quote": old_item.get("quote"),
                    "quote_attribution": old_item.get("quote_attribution"),
                    "old_pdf_sha256": digest,
                    "same_bytes_as_current": hash_matches,
                    "reason": "title multiplicity reduced" if keep else "title absent from current catalog",
                }
            )

    report = {
        "baseline_commit": BASE,
        "old_count": len(old),
        "current_count": len(current),
        "count_difference": len(old) - len(current),
        "loss_count_by_title_multiplicity": len(losses),
        "current_only_title_count": sum(
            max(0, len(items) - len(old_groups.get(key, [])))
            for key, items in cur_groups.items()
        ),
        "losses": losses,
    }
    out = ROOT / "recovery_106_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    if len(old) != 106:
        raise SystemExit(f"Unexpected baseline count: {len(old)}")
    print(f"RECOVERY: old={len(old)} current={len(current)} losses={len(losses)}")


if __name__ == "__main__":
    main()
