#!/usr/bin/env python3
"""Build the publication homepage as a PDF catalogue.

This layer deliberately leaves the curated v3 builder intact. It runs v3 first,
then:
  * removes any non-PDF experimental/support entries,
  * discovers every unique PDF elsewhere in the repository,
  * collapses byte-identical duplicate PDF copies to one catalogue card,
  * keeps existing reader/ADS/experimental metadata when available,
  * promotes the NSA + certified-trading paper to the lead card, and
  * injects the final item list back into the generated homepage and search index.

Generated mirrors under docs/ and build payloads under .build/ are not scanned as
new source publications; their canonical source PDFs are indexed instead.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path
from urllib.parse import quote, unquote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
V3_PATH = HERE / "build_library_homepage_v3.py"
LEAD_HREF = "papers/nsa_and_trading_speedup/"
LEAD_QUOTE = (
    "A hyperfinite witness or advantageous traded presentation is semantic compression; "
    "a speed-up theorem requires a standard extractor, a complete cost model, and a "
    "certificate-preserving return translation."
)
LEAD_ATTRIBUTION = "Brian Tenneson"
GITHUB_BLOB = "https://github.com/btenneson/pub/blob/main/"
RAW = "https://raw.githubusercontent.com/btenneson/pub/main/"

spec = importlib.util.spec_from_file_location("publication_builder_v3", V3_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load {V3_PATH}")
v3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v3)


def is_pdf_path(value: object) -> bool:
    s = str(value or "").split("?", 1)[0].split("#", 1)[0]
    return s.lower().endswith(".pdf")


def item_is_pdf_backed(item: dict) -> bool:
    return any(
        is_pdf_path(item.get(k))
        for k in ("archive_path", "pdf", "href")
    )


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_archive_path(item: dict) -> Path | None:
    rel = str(item.get("archive_path") or "").strip().replace("\\", "/")
    if not rel or rel.startswith(("http://", "https://")):
        return None
    p = ROOT / rel
    return p if p.is_file() and is_pdf_path(p.name) else None


def title_from_pdf_path(path: Path) -> str:
    stem = unquote(path.stem)
    stem = re.sub(r"\s+\(\d+\)$", "", stem)
    stem = stem.replace("_", " ")
    stem = re.sub(r"\s+", " ", stem).strip()
    return stem or path.name


def preferred_source_key(path: Path) -> tuple:
    """Choose a sensible canonical path when identical PDFs occur repeatedly."""
    rel = path.relative_to(ROOT).as_posix()
    top = rel.split("/", 1)[0]
    top_rank = {
        "cs.LO_Logic_in_Computer_Science": 0,
        "cs.AI_Artificial_Intelligence": 1,
        "cs.LG_Machine_Learning": 2,
        "math.LO_Logic": 3,
        "math.LO — Logic": 4,
        "math.NT_Number_Theory": 5,
        "math.NT — Number Theory": 6,
        "math.CO_Combinatorics": 7,
        "math.AC_Commutative_Algebra": 8,
        "q-bio.QM — Quantitative Methods": 9,
        "Automated_Logical_Deciders_and_Conjecture_Settling": 10,
        "AMLD_Reading_Wing": 11,
        "ADS": 12,
        "pub.experimental": 13,
        "documents and their sources": 20,
    }.get(top, 15)
    copied = bool(re.search(r" \(\d+\)\.pdf$", path.name, re.I))
    return (top_rank, copied, len(rel), rel.casefold())


def discover_unique_pdf_items(existing: list[dict]) -> list[dict]:
    represented: set[str] = set()
    for item in existing:
        p = resolve_archive_path(item)
        if p is not None:
            represented.add(digest(p))

    by_hash: dict[str, list[Path]] = {}
    for p in ROOT.rglob("*"):
        if not p.is_file() or not is_pdf_path(p.name):
            continue
        rel = p.relative_to(ROOT)
        if not rel.parts:
            continue
        if rel.parts[0] in {"docs", ".build", ".git"}:
            continue
        by_hash.setdefault(digest(p), []).append(p)

    additions: list[dict] = []
    for sha, copies in sorted(by_hash.items()):
        if sha in represented:
            continue
        p = min(copies, key=preferred_source_key)
        rel = p.relative_to(ROOT).as_posix()
        enc = quote(rel, safe="/")
        title = title_from_pdf_path(p)
        category = v3.v2.category_for(title, rel)
        additions.append(
            {
                "title": title,
                "kind": "PDF archive",
                "category": category,
                "tags": ["pdf"],
                "href": GITHUB_BLOB + enc,
                "pdf": RAW + enc,
                "source": "",
                "archive_path": rel,
                "search": " ".join([title, category, "pdf archive", rel]),
            }
        )
        represented.add(sha)
    return additions


def patch_homepage_data(items: list[dict]) -> None:
    page = v3.v2.OUT_HTML.read_text(encoding="utf-8")
    data = json.dumps(items, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    pattern = re.compile(r"const DATA=.*?;\nconst q=", re.S)
    replacement = "const DATA=" + data + ";\nconst q="
    page, n = pattern.subn(lambda _m: replacement, page, count=1)
    if n != 1:
        raise RuntimeError("Could not replace homepage DATA payload")

    page = re.sub(
        r"Index generated from .*?</footer>",
        "Index generated from the publication readers and all unique source PDFs in the repository; "
        "byte-identical duplicate copies collapse to one card. Search, A-Z, and subject sorting remain available.</footer>",
        page,
        count=1,
        flags=re.S,
    )
    v3.v2.OUT_HTML.write_text(page, encoding="utf-8")


def main() -> None:
    # Preserve v3's curated metadata and card renderer, then extend its data.
    v3.main()
    payload = json.loads(v3.v2.OUT_JSON.read_text(encoding="utf-8"))

    # The public catalogue is a PDF catalogue. Reader HTML and source files are
    # supporting infrastructure, not independent cards.
    items = [dict(x) for x in payload.get("items", []) if item_is_pdf_backed(x)]
    items.extend(discover_unique_pdf_items(items))

    lead = None
    rest: list[dict] = []
    for item in items:
        if str(item.get("href") or "") == LEAD_HREF:
            item["quote"] = LEAD_QUOTE
            item["quote_attribution"] = LEAD_ATTRIBUTION
            item["search"] = " ".join(
                [str(item.get("search") or ""), LEAD_QUOTE, LEAD_ATTRIBUTION]
            ).strip()
            lead = item
        else:
            rest.append(item)

    rest.sort(key=v3.order_key)
    if lead is None:
        raise RuntimeError(
            "Lead NSA/trading reader was not found. Expected docs/papers/nsa_and_trading_speedup/index.html"
        )
    items = [lead] + rest

    final_payload = {"schema_version": 1, "count": len(items), "items": items}
    v3.v2.OUT_JSON.write_text(
        json.dumps(final_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    patch_homepage_data(items)

    print("PDF catalogue items:", len(items))
    print("Lead item:", items[0]["href"])
    print("Archive-only additions:", sum(x.get("kind") == "PDF archive" for x in items))


if __name__ == "__main__":
    main()
