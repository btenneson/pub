#!/usr/bin/env python3
"""Build the publication site with reviewed historical catalog-context aliases.

The canonical publication catalog remains scripts/publications.json. Historical
contexts in scripts/publication_aliases.json get their own reader/card while
reusing the already-verified canonical document. No duplicate PDF is created.
"""
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "scripts" / "publications.json"
ALIASES = ROOT / "scripts" / "publication_aliases.json"
BUILDER = ROOT / "scripts" / "build_publications.py"


def expanded_catalog():
    data = json.loads(CATALOG.read_text())
    base = data["items"]
    by_id = {x["id"]: x for x in base}
    aliases = json.loads(ALIASES.read_text())["items"]
    expanded = [dict(x) for x in base]
    for n, alias in enumerate(aliases):
        canonical_id = alias["canonical_id"]
        if canonical_id not in by_id:
            raise SystemExit(f"Alias canonical_id not found: {canonical_id}")
        canonical = by_id[canonical_id]
        x = dict(canonical)
        x["id"] = f"{canonical['subject']}/{alias['id_suffix']}"
        x["href"] = x["id"] + "/"
        x["title"] = alias["title"]
        x["kind"] = alias["kind"]
        x["catalog_alias_of"] = canonical_id
        # Reuse the canonical PDF/source. Do not copy a historical binary back.
        x["archive_path"] = ""
        x["source_file"] = ""
        x["order"] = 2000 + n
        x["classification_note"] = (
            "Historical catalog context restored from the 106-item pre-migration "
            f"publication library. This card shares its verified document with “{canonical['title']}”."
        )
        expanded.append(x)
    out = dict(data)
    out["items"] = expanded
    return out


def main():
    original = CATALOG.read_bytes()
    try:
        expanded = expanded_catalog()
        if len(expanded["items"]) != 106:
            raise SystemExit(f"Expected 106 cards after restoration, got {len(expanded['items'])}")
        CATALOG.write_text(json.dumps(expanded, ensure_ascii=False, indent=2) + "\n")
        subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, check=True)
    finally:
        CATALOG.write_bytes(original)


if __name__ == "__main__":
    main()
