#!/usr/bin/env python3
"""Build a public, client-side semantic PDF passage index for GitHub Pages.

The source of truth is docs/search-index.json, which already excludes hidden
publications. Embeddings are precomputed; visitors' queries stay in the browser.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SOURCE = DOCS / "search-index.json"
META = DOCS / "semantic-index.json"
VECTORS = DOCS / "semantic-vectors.i8"
MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHARS = 950
OVERLAP = 120


def chunks(text: str):
    """Overlapping character windows, preferably ending at a word boundary."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return
    start = 0
    while start < len(text):
        end = min(start + CHARS, len(text))
        if end < len(text):
            break_at = text.rfind(" ", start + CHARS // 2, end)
            if break_at > start:
                end = break_at
        chunk = text[start:end].strip()
        if len(chunk) > 30:
            yield chunk
        if end == len(text):
            break
        start = max(start + 1, end - OVERLAP)


def main():
    import fitz
    import numpy as np
    from sentence_transformers import SentenceTransformer

    catalog = json.loads(SOURCE.read_text(encoding="utf-8"))
    publications = []
    passages = []
    records = []
    missing = []
    pdf_pages = 0

    for item in catalog["items"]:
        # A second privacy gate, even if a catalog-generation rule changes.
        if item.get("visibility") == "hidden":
            continue
        pub = {
            "title": item["title"],
            "href": item["href"],
            "subject": item.get("category", item.get("subject", "")),
            "kind": item.get("kind", ""),
            "archived": item.get("visibility") == "archive",
            "pdf": item.get("pdf", ""),
        }
        article = len(publications)
        publications.append(pub)
        intro = " ".join(
            str(item.get(k, "")) for k in ("title", "card_text", "quote", "category", "authors")
        ).strip()
        if intro:
            passages.append(intro[:1200])
            records.append({"a": article, "p": 0, "s": intro[:360]})

        rel = item.get("pdf")
        if not rel:
            continue
        pdf_path = (DOCS / rel).resolve()
        if not pdf_path.is_relative_to(DOCS.resolve()):
            raise ValueError("PDF path leaves public docs folder: " + rel)
        if not pdf_path.is_file():
            missing.append(rel)
            continue
        try:
            with fitz.open(pdf_path) as document:
                if document.needs_pass:
                    missing.append(rel + " (encrypted)")
                    continue
                for number, page in enumerate(document, 1):
                    pdf_pages += 1
                    text = page.get_text("text", sort=True)
                    for part in chunks(text):
                        passages.append(pub["title"] + ". " + part)
                        records.append({"a": article, "p": number, "s": part[:360]})
        except Exception as exc:
            raise RuntimeError("Could not parse " + rel) from exc

    if not records:
        raise RuntimeError("No public documents found for semantic index")
    print(
        f"Indexing {len(records)} passages from {len(publications)} public catalog entries "
        f"({pdf_pages} PDF pages; {len(missing)} unavailable PDFs).",
        flush=True,
    )
    model = SentenceTransformer(MODEL, device="cpu")
    embeddings = model.encode(
        passages, batch_size=48, show_progress_bar=True,
        convert_to_numpy=True, normalize_embeddings=True,
    )
    if embeddings.ndim != 2 or embeddings.shape[0] != len(records):
        raise RuntimeError("Embedding count does not match passage count")
    if embeddings.shape[1] != 384:
        raise RuntimeError("Unexpected model vector width: " + str(embeddings.shape[1]))
    # Symmetric signed-int8 quantization: compact enough for a static site.
    vectors = np.rint(np.clip(embeddings * 127, -127, 127)).astype(np.int8)
    VECTORS.write_bytes(vectors.tobytes(order="C"))
    metadata = {
        "schema": 1,
        "model": MODEL,
        "dimensions": 384,
        "format": "signed-int8-row-major-scale-127",
        "vector_file": "semantic-vectors.i8",
        "passage_count": len(records),
        "publications": publications,
        "passages": records,
        "unavailable_pdfs": missing,
    }
    META.write_text(
        json.dumps(metadata, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    check = len(records) * 384
    if VECTORS.stat().st_size != check:
        raise RuntimeError("Vector byte length mismatch")
    print(f"Wrote {META} and {VECTORS} ({check} vector bytes).", flush=True)


if __name__ == "__main__":
    main()
