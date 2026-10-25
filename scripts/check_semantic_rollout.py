#!/usr/bin/env python3
"""Fail closed if the semantic-search rollout damages a published library item.

Run from the repository root with the public baseline commit as argv[1].
This check compares the pull request to its current base and never edits files.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=sys.argv[1] if len(sys.argv)>1 else "origin/main"
PROTECTED_PAGES=(
    "docs/index.html",
    "docs/cs.LO_Logic_in_Computer_Science/index.html",
    "docs/archive/index.html",
)
PROTECTED_FIELDS=(
    "title", "href", "card_text", "quote", "quote_attribution",
    "quote_also_on_card", "status", "visibility", "order", "pdf",
    "authors", "kind", "subject", "publication_date",
    "classification_note",
)

def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)

def original(path):
    return git("show", BASE + ":" + path)

def require(condition, message):
    if not condition:
        raise SystemExit("SEMANTIC ROLLOUT BLOCKED: " + message)

def verify():
    changed=git("diff", "--name-status", BASE, "HEAD").decode().splitlines()
    for change in changed:
        parts=change.split("\t")
        status=parts[0]
        paths=parts[1:]
        require(not status.startswith(("D", "R")), "A file was deleted or renamed: " + change)
        for path in paths:
            if path.startswith("docs/") and path.endswith(".pdf"):
                require(False,"Existing PDF was modified: " + path)
            if path.startswith("docs/") and path.endswith("/index.html"):
                require(False, "An existing reader or catalog page changed: " + path)
            if path=="docs/index.html":
                require(False,"The curated home page changed")
            if path=="docs/archive/index.html":
                require(False,"The research archive page changed")
    for path in PROTECTED_PAGES:
        require((ROOT/path).read_bytes()==original(path),
                "Curated page is not byte-for-byte preserved: "+path)

    # Preserve every original publication's public-facing metadata. New entries
    # are permitted; a numeric quote-page correction does not rewrite a card.
    for name in ("scripts/publications.json", "docs/search-index.json"):
        old=json.loads(original(name))
        new=json.loads((ROOT/name).read_text(encoding="utf-8"))
        prior={item["id"]:item for item in old["items"]}
        revised={item["id"]:item for item in new["items"]}
        require(len(revised)==len(new["items"]), "Duplicate ID in "+name)
        for identity,item in prior.items():
            require(identity in revised,"Publication removed from "+name+": "+identity)
            for field in PROTECTED_FIELDS:
                require(item.get(field)==revised[identity].get(field),
                        name+" changed "+field+" of "+identity)

    source=json.loads((ROOT/"docs/search-index.json").read_text(encoding="utf-8"))
    data=json.loads((ROOT/"docs/semantic-index.json").read_text(encoding="utf-8"))
    visible=[item for item in source["items"] if item.get("visibility")!="hidden"]
    require(len(visible)==len(data["publications"]),"Publication count mismatch")
    require(source["count"]==len(source["items"]),"Catalog count mismatch")
    require(data["schema"]==1 and data["dimensions"]==384,"Unexpected vector schema")
    require(data["passage_count"]>0 and data["passage_count"]==len(data["passages"]),
            "PDF passage counts are invalid")
    require((ROOT/"docs/semantic-vectors.i8").stat().st_size==
            384*data["passage_count"],"Vector file length mismatch")
    require(not data.get("unavailable_pdfs"),"Some public PDFs were unavailable")
    for orig,new in zip(visible,data["publications"]):
        require(orig["href"]==new["href"],"Semantic index catalog order mismatch")
        require(new["archived"]==(orig.get("visibility")=="archive"),
                "Archive visibility mismatch")
    print("PASS: curated cards/pages, original records, PDF files,")
    print("      archive visibility,  and semantic vectors preserved.")
    print(f"PASS: {len(visible)} indexed publications / {data['passage_count']} passages.")

if __name__=="__main__":
    verify()
