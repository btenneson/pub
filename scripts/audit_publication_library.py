#!/usr/bin/env python3
"""Audit the publication archive and GitHub Pages reader/index invariants.

The audit is intentionally local and deterministic: it validates repository
paths rather than depending on transient network responses from GitHub Pages.
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PAPERS = DOCS / "papers"
INDEX = DOCS / "search-index.json"
RAW_PREFIX = "https://raw.githubusercontent.com/btenneson/pub/main/"
BLOB_PREFIX = "https://github.com/btenneson/pub/blob/main/"

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def clean(s: str) -> str:
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s))).strip()


def extract_pdf(text: str) -> str:
    for pat in (
        r"const\s+p\s*=\s*['\"]([^'\"]+\.pdf)['\"]",
        r"(https://raw\.githubusercontent\.com/btenneson/pub/main/[^\"'<>\s]+\.pdf)",
    ):
        m = re.search(pat, text, re.I)
        if m:
            return html.unescape(m.group(1))
    return ""


def repo_path_from_url(url: str, prefix: str) -> Path | None:
    if not url.startswith(prefix):
        return None
    rel = unquote(url[len(prefix):].split("#", 1)[0].split("?", 1)[0])
    return ROOT / rel


def local_href_exists(href: str) -> bool:
    href = href.split("#", 1)[0].split("?", 1)[0]
    if not href or href.startswith(("http://", "https://", "mailto:")):
        return True
    p = DOCS / unquote(href)
    if p.is_dir():
        p = p / "index.html"
    return p.exists()


def active_readers() -> dict[str, dict]:
    out: dict[str, dict] = {}
    if not PAPERS.exists():
        err("docs/papers is missing")
        return out
    for folder in sorted(p for p in PAPERS.iterdir() if p.is_dir()):
        page = folder / "index.html"
        if not page.exists():
            warn(f"reader directory lacks index.html: {folder.relative_to(ROOT)}")
            continue
        text = page.read_text(encoding="utf-8", errors="replace")
        if re.search(r"\bsuperseded\s+by\b", clean(text), re.I):
            continue
        pdf = extract_pdf(text)
        if not pdf:
            err(f"active reader exposes no PDF: {page.relative_to(ROOT)}")
            continue
        if not pdf.startswith(RAW_PREFIX):
            warn(f"active reader PDF is external rather than archive-local: {page.relative_to(ROOT)} -> {pdf}")
        else:
            target = repo_path_from_url(pdf, RAW_PREFIX)
            if target is None or not target.exists():
                err(f"reader PDF target missing: {page.relative_to(ROOT)} -> {pdf}")
        for src in re.findall(r"https://github\.com/btenneson/pub/blob/main/[^\"'<>\s]+\.tex", text, re.I):
            target = repo_path_from_url(html.unescape(src), BLOB_PREFIX)
            if target is not None and not target.exists():
                err(f"reader source target missing: {page.relative_to(ROOT)} -> {src}")
        out[folder.name] = {"page": page, "pdf": pdf}
    return out


def audit_search_index(readers: dict[str, dict]) -> None:
    if not INDEX.exists():
        err("docs/search-index.json is missing")
        return
    try:
        data = json.loads(INDEX.read_text(encoding="utf-8"))
    except Exception as exc:
        err(f"docs/search-index.json is invalid JSON: {exc}")
        return
    if data.get("schema_version") != 1:
        err("search-index schema_version must be 1")
    items = data.get("items") or []
    if data.get("count") != len(items):
        err("search-index count does not equal len(items)")
    seen_href: set[str] = set()
    core_slugs: set[str] = set()
    for item in items:
        href = str(item.get("href") or "")
        if href in seen_href:
            err(f"duplicate search-index href: {href}")
        seen_href.add(href)
        if not local_href_exists(href):
            err(f"search-index href does not resolve locally: {href}")
        if item.get("kind") == "Core paper":
            m = re.fullmatch(r"papers/([^/]+)/?", href)
            if m:
                core_slugs.add(m.group(1))
            archive = str(item.get("archive_path") or "")
            pdf = str(item.get("pdf") or "")
            if not archive or not pdf:
                err(f"core search-index item missing PDF metadata: {item.get('title')!r}")
            elif not (ROOT / unquote(archive)).exists():
                err(f"core search-index archive_path missing: {archive}")
    missing = sorted(set(readers) - core_slugs)
    extra = sorted(core_slugs - set(readers))
    if missing:
        err("active readers absent from search index: " + ", ".join(missing))
    if extra:
        err("search index contains non-active/superseded reader slugs: " + ", ".join(extra))


def audit_ads() -> None:
    manifest = DOCS / "ADS" / "manifest.json"
    if not manifest.exists():
        warn("ADS manifest is absent")
        return
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except Exception as exc:
        err(f"ADS manifest invalid JSON: {exc}")
        return
    for doc in data.get("documents", []):
        web_path = str(doc.get("web_path") or "")
        if web_path:
            p = DOCS / "ADS" / unquote(web_path)
            if not p.exists():
                err(f"ADS manifest web_path missing: {web_path}")


def main() -> int:
    for required in (DOCS / ".nojekyll", DOCS / "index.html", INDEX):
        if not required.exists():
            err(f"required publication-site file missing: {required.relative_to(ROOT)}")
    readers = active_readers()
    audit_search_index(readers)
    audit_ads()

    print(f"active canonical readers: {len(readers)}")
    print(f"warnings: {len(warnings)}")
    for msg in warnings:
        print("WARNING:", msg)
    print(f"errors: {len(errors)}")
    for msg in errors:
        print("ERROR:", msg)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
