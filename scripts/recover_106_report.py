#!/usr/bin/env python3
"""Compare the pre-reorganization 106-item index with the current catalog.

Diagnostic only.  The report distinguishes harmless title/route renames from
entries actually collapsed by content deduplication.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit
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
        ["git", "show", f"{BASE}:{path}"], cwd=ROOT,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False,
    )
    return proc.stdout if proc.returncode == 0 else None


def old_blob(item: dict) -> tuple[bytes | None, str | None]:
    candidates = []
    for key in ("archive_path", "pdf", "href"):
        raw = item.get(key) or ""
        if raw.startswith(("http://", "https://")):
            raw = urlsplit(raw).path
            marker = "/btenneson/pub/"
            if marker in raw:
                raw = raw.split(marker, 1)[1]
            elif raw.startswith("/btenneson/pub/blob/main/"):
                raw = raw.split("/btenneson/pub/blob/main/", 1)[1]
        raw = unquote(raw).lstrip("/")
        if not raw or raw.endswith("/"):
            continue
        candidates += [raw, f"docs/{raw}"]
    seen = set()
    for path in candidates:
        if path in seen:
            continue
        seen.add(path)
        blob = git_bytes(path)
        if blob is not None:
            return blob, path
    return None, None


def compact(item: dict) -> dict:
    return {
        "title": item.get("title"),
        "kind": item.get("kind"),
        "category": item.get("category"),
        "href": item.get("href"),
        "pdf": item.get("pdf"),
        "source": item.get("source"),
        "archive_path": item.get("archive_path"),
        "quote": item.get("quote"),
        "quote_attribution": item.get("quote_attribution"),
    }


def main() -> None:
    old = json.loads(subprocess.run(
        ["git", "show", f"{BASE}:docs/search-index.json"], cwd=ROOT,
        stdout=subprocess.PIPE, check=True,
    ).stdout)["items"]
    current = json.loads((ROOT / "scripts/publications.json").read_text())["items"]

    # Resolve old PDF bytes even when the historical index omitted archive_path.
    old_sha = []
    old_path = []
    for item in old:
        blob, path = old_blob(item)
        old_sha.append(hashlib.sha256(blob).hexdigest() if blob is not None else None)
        old_path.append(path)

    cur_sha = [item.get("sha256") for item in current]
    old_sha_count = Counter(x for x in old_sha if x)
    cur_sha_count = Counter(x for x in cur_sha if x)
    current_by_sha = defaultdict(list)
    for item in current:
        if item.get("sha256"):
            current_by_sha[item["sha256"]].append(item)

    # One current card can represent one historical occurrence of a PDF.  Any
    # further historical occurrences of the same bytes are true collapsed cards.
    collapsed = []
    used_per_sha = Counter()
    for i, item in enumerate(old):
        digest = old_sha[i]
        if not digest:
            continue
        used_per_sha[digest] += 1
        if used_per_sha[digest] <= cur_sha_count.get(digest, 0):
            continue
        rec = compact(item)
        rec.update({
            "resolved_old_path": old_path[i],
            "old_pdf_sha256": digest,
            "same_bytes_as_current": [
                {"title": x.get("title"), "id": x.get("id"), "sha256": digest}
                for x in current_by_sha.get(digest, [])
            ],
            "reason": "historical card collapsed by identical PDF bytes",
        })
        collapsed.append(rec)

    # Match non-PDF/text/story entries by normalized title multiplicity.  This
    # catches a true catalog loss that cannot be compared by PDF hash, while
    # excluding ordinary title changes for PDF-backed entries.
    old_no_sha = defaultdict(list)
    cur_no_sha = defaultdict(list)
    for i, item in enumerate(old):
        if not old_sha[i]:
            old_no_sha[norm_title(item.get("title", ""))].append(item)
    for item in current:
        if not item.get("sha256"):
            cur_no_sha[norm_title(item.get("title", ""))].append(item)
    nonpdf_losses = []
    for key, items in old_no_sha.items():
        keep = len(cur_no_sha.get(key, []))
        for item in items[keep:]:
            rec = compact(item)
            rec["reason"] = "historical non-PDF card absent from current catalog"
            nonpdf_losses.append(rec)

    # Renames are old titles absent by name whose bytes still have exactly one
    # current representative.  They are reported for audit but are not losses.
    current_titles = Counter(norm_title(x.get("title", "")) for x in current)
    renames = []
    consumed = Counter()
    for i, item in enumerate(old):
        key = norm_title(item.get("title", ""))
        if current_titles.get(key, 0):
            current_titles[key] -= 1
            continue
        digest = old_sha[i]
        if digest and current_by_sha.get(digest):
            consumed[digest] += 1
            if consumed[digest] <= cur_sha_count[digest]:
                renames.append({
                    "old_title": item.get("title"),
                    "current_title": current_by_sha[digest][0].get("title"),
                    "sha256": digest,
                })

    report = {
        "baseline_commit": BASE,
        "old_count": len(old),
        "current_count": len(current),
        "count_difference": len(old) - len(current),
        "old_pdf_occurrences": sum(old_sha_count.values()),
        "current_pdf_occurrences": sum(cur_sha_count.values()),
        "collapsed_pdf_card_count": len(collapsed),
        "nonpdf_loss_count": len(nonpdf_losses),
        "true_loss_count": len(collapsed) + len(nonpdf_losses),
        "renamed_but_preserved_count": len(renames),
        "collapsed_pdf_cards": collapsed,
        "nonpdf_losses": nonpdf_losses,
        "renamed_but_preserved": renames,
    }
    (ROOT / "recovery_106_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if len(old) != 106:
        raise SystemExit(f"Unexpected baseline count: {len(old)}")
    print(
        f"RECOVERY: old={len(old)} current={len(current)} "
        f"true_losses={report['true_loss_count']}"
    )


if __name__ == "__main__":
    main()
