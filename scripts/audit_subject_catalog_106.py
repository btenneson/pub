#!/usr/bin/env python3
"""Audit the restored subject publication catalog, including declared aliases."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
from html.parser import HTMLParser
import hashlib, html, json, re, unicodedata
import fitz

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def norm(s):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", s or "")).strip().replace("- ", "")


class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []
    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if k in ("href", "src") and v:
                self.links.append(v)


def main():
    data = json.loads((DOCS / "search-index.json").read_text())
    items = data["items"]
    assert data["count"] == len(items)
    assert len(items) >= 106, f"Publication catalog regressed below 106 cards: {len(items)}"
    assert not (DOCS / "papers").exists(), "Obsolete papers directory returned"

    ids = [x["id"] for x in items]
    assert len(ids) == len(set(ids)), "Duplicate publication id"
    by_id = {x["id"]: x for x in items}
    canonical_sha = set()
    aliases = 0
    pdf_cards = 0
    unavailable = []
    paths = [DOCS / "index.html", DOCS / "404.html"]

    for x in items:
        assert x["id"].startswith(x["subject"] + "/"), x["id"]
        reader = DOCS / x["href"] / "index.html"
        assert reader.is_file(), reader
        paths += [reader, DOCS / x["subject"] / "index.html"]
        for key in ("source", "source_file", "download", "text"):
            if x.get(key):
                assert (DOCS / x[key]).is_file(), x[key]

        if x.get("pdf"):
            pdf = DOCS / x["pdf"]
            assert pdf.is_file(), pdf
            digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
            assert digest == x["sha256"], (x["title"], digest, x.get("sha256"))
            alias_of = x.get("catalog_alias_of")
            if alias_of:
                aliases += 1
                parent = by_id.get(alias_of)
                assert parent, ("missing alias canonical", x["id"], alias_of)
                assert parent.get("pdf"), ("alias canonical has no PDF", alias_of)
                assert parent.get("sha256") == digest, ("alias PDF differs from canonical", x["id"], alias_of)
            else:
                assert digest not in canonical_sha, ("undeclared duplicate PDF card", x["title"])
                canonical_sha.add(digest)
            doc = fitz.open(pdf)
            assert len(doc) > 0, pdf
            assert all(doc[i].get_text().strip() for i in range(len(doc))), ("empty/unreadable page", pdf)
            q = norm(x.get("quote", ""))
            assert q, ("missing quote", x["title"])
            page = x.get("quote_page")
            assert page and 1 <= page <= len(doc), ("invalid quote page", x["title"], page)
            assert q in norm(doc[page - 1].get_text()), ("quote not in cited page", x["title"], q)
            pdf_cards += 1
        elif x.get("status"):
            unavailable.append(x["title"])
        else:
            assert x.get("text") and x.get("quote"), x["title"]
            plain = re.sub("<[^>]+>", " ", (DOCS / x["text"]).read_text())
            assert norm(x["quote"]) in norm(html.unescape(plain)), ("text quote mismatch", x["title"])

    assert aliases == 20, f"Expected 20 restored historical contexts, found {aliases}"

    for p in set(paths):
        parser = Links(); parser.feed(p.read_text())
        for link in parser.links:
            u = urlsplit(link)
            if u.scheme or u.netloc or not u.path:
                continue
            path = unquote(u.path)
            target = (DOCS / path[len("/pub/"):]) if path.startswith("/pub/") else p.parent / path
            if target.is_dir(): target /= "index.html"
            assert target.exists(), (p, link)

    redirects = json.loads((DOCS / "redirects.json").read_text())
    for old, new in redirects.items():
        target = DOCS / new
        if target.is_dir(): target /= "index.html"
        assert target.exists(), ("redirect target missing", old, new)

    print(f"PASS: {len(items)} cards, including {aliases} declared historical contexts; {pdf_cards} PDF-backed cards verified.")
    print("Explicitly unavailable:", ", ".join(unavailable) or "none")


if __name__ == "__main__":
    main()
