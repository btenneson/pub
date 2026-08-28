#!/usr/bin/env python3
"""Temporary QC helper for the authored-library quotation rollout."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "docs" / "search-index.json"
OUT = ROOT / "scripts" / "feature_quotes_full.json"
BUILDER = ROOT / "scripts" / "build_library_homepage_v3.py"
EXPERIMENTAL_GITHUB = "https://github.com/btenneson/pub/blob/main/"

EXCLUDED = {
    "papers/external_theorem_proving_survey_2404_09939v3/",
    "pub.experimental/Ternary_Logic_and_Logic_with_Independence.pdf",
}

HEADING_BOOST = {
    "abstract": 24,
    "executive summary": 22,
    "summary": 18,
    "research objective": 18,
    "core proposal": 18,
    "purpose": 17,
    "overview": 15,
    "introduction": 12,
    "conclusion": 18,
    "conclusions": 18,
    "results": 16,
    "discussion": 13,
    "interpretation": 14,
    "main result": 19,
}

KEY_WEIGHTS = {
    "proof": 5,
    "theorem": 4,
    "search": 5,
    "verif": 5,
    "certificate": 5,
    "settlement": 5,
    "settle": 5,
    "machine": 4,
    "algorithm": 4,
    "model": 3,
    "system": 3,
    "learning": 3,
    "data": 2,
    "result": 3,
    "analysis": 2,
    "control": 3,
    "distance": 3,
    "simulation": 3,
    "conjecture": 4,
    "formal": 3,
    "prediction": 2,
    "performance": 2,
    "clinical": 2,
    "treatment": 2,
    "patient": 1,
    "dose": 2,
    "concentration": 2,
    "statistics": 2,
    "regression": 3,
    "classification": 2,
    "risk": 2,
    "objective": 2,
    "discovery": 4,
    "induction": 3,
    "logic": 3,
    "mathemat": 3,
    "experiment": 3,
    "evidence": 2,
    "policy": 3,
    "structure": 3,
    "optimal": 3,
    "framework": 3,
    "creativity": 4,
    "premise": 3,
    "inference": 3,
    "halting": 3,
    "density": 2,
    "depth": 2,
    "surjection": 2,
    "function": 1,
}

BANNED = (
    "statement regarding academic integrity",
    "large language models (llms) were utilized",
    "searches included combinations of",
    "citation search should focus",
    "i used the following code",
    "import numpy",
    "import pandas",
    "organized as follows",
    "the remainder of this paper",
    "table of contents",
    "suggested citation",
    "all rights reserved",
    "research status:",
)

META_PREFIXES = (
    "copyright",
    "version ",
    "keywords",
    "references",
    "acknowledg",
    "contact",
    "author",
    "prepared for",
    "research brief for",
    "draft ",
    "date:",
    "figure ",
    "table ",
    "definition ",
    "theorem ",
    "lemma ",
    "proposition ",
    "corollary ",
    "proof.",
    "scope and claim status",
    "scientific-status note",
)


def extract(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    if path.suffix.lower() == ".pdf":
        try:
            p = subprocess.run(
                ["pdftotext", "-f", "1", "-l", "40", "-layout", str(path), "-"],
                capture_output=True,
                text=True,
                timeout=75,
            )
            return p.stdout
        except Exception:
            return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def clean_text(text: str) -> str:
    text = text.replace("\ufeff", " ").replace("\u00ad", "")
    text = text.replace("ﬁ", "fi").replace("ﬂ", "fl").replace("\x15", "-")
    text = re.sub(r"([A-Za-z])-[ \t]*\n[ \t]*([a-z])", r"\1\2", text)
    return text


def paragraph_records(text: str) -> list[tuple[str, str]]:
    text = clean_text(text).replace("\f", "\n\n")
    lines = text.splitlines()
    counts: dict[str, int] = {}
    for raw in lines:
        s = re.sub(r"\s+", " ", raw).strip()
        if 4 <= len(s) <= 120:
            counts[s] = counts.get(s, 0) + 1
    repeated = {s for s, n in counts.items() if n >= 3}

    out: list[tuple[str, str]] = []
    current: list[str] = []
    heading = ""

    def flush() -> None:
        nonlocal current
        if current:
            p = re.sub(r"\s+", " ", " ".join(current)).strip()
            if p:
                out.append((heading, p))
            current = []

    for raw in lines:
        s = re.sub(r"\s+", " ", raw).strip()
        if not s:
            flush()
            continue
        low = s.casefold()
        if s in repeated:
            continue
        if re.fullmatch(r"[-–—]?\s*\d{1,4}\s*[-–—]?", s):
            continue
        if "copyright ©" in low or "copyright (c)" in low:
            continue
        if re.search(r"https?://|www\.|\S+@\S+", s):
            continue
        if re.fullmatch(
            r"(brian\s+tenneson|currently unaffiliated|m\.?s\.?[,]?\s*applied data science|m\.?a\.?[,]?\s*mathematics)",
            s,
            re.I,
        ):
            continue
        if re.search(r"\.{4,}\s*\d+\s*$", s):
            continue
        if len(s) <= 90 and not re.search(r"[.!?][”\"]?$", s) and len(s.split()) <= 12:
            flush()
            heading = s.casefold().strip(" :.-0123456789")
            continue
        current.append(s)
    flush()
    return out


def normalize_words(s: str) -> list[str]:
    return [w.casefold() for w in re.findall(r"[A-Za-z]{4,}", s)]


def strip_label(s: str) -> str:
    s = re.sub(
        r"^\s*(?:\d+(?:\.\d+)*\s+)?(?:abstract|purpose|core proposal|executive summary|summary|overview|introduction|experimental setting)\s*[:.—-]*\s*",
        "",
        s,
        flags=re.I,
    )
    s = re.sub(r"^\s*\d+(?:\.\d+)*\s+", "", s)
    return s.strip(' “”"')


def sentences(p: str) -> list[str]:
    # Quote marks are kept outside the fixed-width lookbehind.
    parts = re.split(r'(?<=[.!?])(?:[”"])?\s+(?=[A-Z“"(])', p)
    return [strip_label(x) for x in parts if strip_label(x)]


def usable(s: str, title: str) -> bool:
    if not 70 <= len(s) <= 340:
        return False
    low = s.casefold()
    if not re.search(r"[.!?][”\"]?$", s):
        return False
    if low.startswith(META_PREFIXES):
        return False
    if any(x in low for x in BANNED):
        return False
    if re.search(r"https?://|www\.|\S+@\S+", s):
        return False
    if re.search(r"\b(?:doi|isbn)\b", low):
        return False
    if re.match(r"^\(?\d+(?:\.\d+)+(?:\)|\s)", s):
        return False
    if s.count("=") > 2 or sum(c in "{}[]" for c in s) > 6:
        return False
    if sum(c.isalpha() for c in s) < max(48, int(len(s) * 0.60)):
        return False
    ratio = SequenceMatcher(
        None,
        re.sub(r"\W+", " ", low),
        re.sub(r"\W+", " ", title.casefold()),
    ).ratio()
    tw, sw = set(normalize_words(title)), set(normalize_words(s))
    overlap = len(tw & sw) / len(tw) if tw else 0
    if ratio > 0.62 or (overlap > 0.72 and len(s) < max(150, 2 * len(title))):
        return False
    return True


def choose(text: str, title: str) -> str:
    recs = paragraph_records(text)
    title_words = set(normalize_words(title))
    candidates: list[tuple[float, int, int, int, str]] = []
    for pi, (heading, paragraph) in enumerate(recs):
        hb = 0
        for key, value in HEADING_BOOST.items():
            if heading == key or heading.startswith(key + " "):
                hb = max(hb, value)
        for si, s in enumerate(sentences(paragraph)):
            if not usable(s, title):
                continue
            low = s.casefold()
            score = float(hb)
            score += sum(v for k, v in KEY_WEIGHTS.items() if k in low)
            score += 1.2 * sum(1 for w in title_words if w in low)
            if any(
                x in low
                for x in (
                    "we show",
                    "we prove",
                    "we find",
                    "this paper",
                    "this work",
                    "the result",
                    "the central",
                    "the key",
                    "the goal",
                    "the purpose",
                    "the practical",
                    "the machine",
                    "the model",
                    "the analysis",
                    "the experiment",
                    "we treat",
                    "we define",
                    "we propose",
                    "the results suggest",
                )
            ):
                score += 5
            if any(
                x in low
                for x in (
                    "therefore",
                    "thus",
                    "however",
                    "rather than",
                    "not merely",
                    "precisely",
                    "exactly",
                    "in other words",
                    "the point is",
                    "the distinction",
                )
            ):
                score += 2
            if 95 <= len(s) <= 270:
                score += 4
            if pi < 18:
                score += max(0, 4 - pi / 5)
            score -= 1.5 * len(re.findall(r"\[[0-9,;\- ]+\]", s))
            candidates.append((score, -abs(len(s) - 185), -pi, -si, s))
    if not candidates:
        return ""
    candidates.sort(reverse=True)
    return candidates[0][-1]


def polish(s: str) -> str:
    repairs = {
        "signi cant": "significant",
        "signi ficant": "significant",
        " nding": " finding",
        " ndings": " findings",
        "veri ed": "verified",
        "speci c": "specific",
        "classi cation": "classification",
        "coef cient": "coefficient",
        "con dence": "confidence",
        "in nite": "infinite",
        "de nition": "definition",
        " rst ": " first ",
        " e ect": " effect",
        " e ective": " effective",
        "di erent": "different",
        "su cient": "sufficient",
    }
    for old, new in repairs.items():
        s = s.replace(old, new)
    return re.sub(r"\s+", " ", s).strip()


def attribution(text: str) -> str:
    head = re.sub(r"\s+", " ", clean_text(text)[:5000]).casefold()
    patterns = (
        r"collaborat(?:ed|ion).*chatgpt",
        r"developed.*chatgpt",
        r"assist(?:ed|ance).*chatgpt",
        r"assist(?:ed|ance).*openai",
        r"research.*assisted by openai",
        r"chatgpt.*collaborat",
    )
    return (
        "Brian Tenneson and ChatGPT"
        if any(re.search(p, head) for p in patterns)
        else "Brian Tenneson"
    )


def build_quotes() -> dict[str, dict[str, str]]:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    extra: dict[str, dict[str, str]] = {}
    failures: list[tuple[str, str]] = []
    for item in index["items"]:
        href = item.get("href", "")
        if href in EXCLUDED or item.get("quote"):
            continue
        rel = unquote(item.get("archive_path") or item.get("href") or "")
        path = ROOT / rel if rel else Path("/nonexistent")
        text = extract(path)
        quote = polish(choose(text, item.get("title", "")))
        if not quote:
            failures.append((item.get("title", ""), rel))
            continue
        extra[href] = {
            "quote": quote,
            "quote_attribution": attribution(text),
        }
    if failures:
        raise SystemExit("NO_CLEAN_QUOTE " + repr(failures))
    return extra


def patch_builder() -> None:
    s = BUILDER.read_text(encoding="utf-8")
    marker = "\n\ndef experimental_title(path: Path) -> str:\n"
    loader = '''\n\n# Additional curated quotations for the authored publication library.\nFEATURE_QUOTES_FILE = HERE / "feature_quotes_full.json"\nif FEATURE_QUOTES_FILE.exists():\n    FEATURE_QUOTES.update(json.loads(FEATURE_QUOTES_FILE.read_text(encoding="utf-8")))\n'''
    if 'FEATURE_QUOTES_FILE = HERE / "feature_quotes_full.json"' not in s:
        if marker not in s:
            raise SystemExit("quote loader insertion marker missing")
        s = s.replace(marker, loader + marker, 1)

    old = '''    for item in items:\n        feature = FEATURE_QUOTES.get(str(item.get("href") or ""))\n        if feature:\n'''
    new = '''    for item in items:\n        href = str(item.get("href") or "")\n        feature = FEATURE_QUOTES.get(href)\n        if feature is None and href.startswith(EXPERIMENTAL_GITHUB):\n            feature = FEATURE_QUOTES.get(href[len(EXPERIMENTAL_GITHUB):])\n        if feature:\n'''
    if old in s:
        s = s.replace(old, new, 1)
    elif "href.startswith(EXPERIMENTAL_GITHUB)" not in s:
        raise SystemExit("quote matching patch marker missing")
    BUILDER.write_text(s, encoding="utf-8")


def validate() -> None:
    d = json.loads(INDEX.read_text(encoding="utf-8"))
    assert d["count"] == 72 == len(d["items"])
    quoted = [x for x in d["items"] if x.get("quote")]
    assert len(quoted) == 70, len(quoted)
    for item in d["items"]:
        if item["href"] in EXCLUDED:
            assert not item.get("quote"), item["title"]
        else:
            q = item.get("quote", "")
            assert q, item["title"]
            assert 55 <= len(q) <= 340, (item["title"], q)
            assert item.get("quote_attribution") in {
                "Brian Tenneson",
                "Brian Tenneson and ChatGPT",
            }
            assert "Statement regarding academic integrity" not in q
            assert "import numpy" not in q
    print("VALIDATED_72_TOTAL_70_QUOTED_2_EXTERNAL")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    extra = build_quotes()
    OUT.write_text(json.dumps(extra, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("NEW_QUOTES", len(extra), "TOTAL", 9 + len(extra))
    for href, value in extra.items():
        print("QUOTE", href, "|", value["quote_attribution"], "|", value["quote"])

    if args.apply:
        patch_builder()
        subprocess.run(["python", "scripts/build_library_homepage_v3.py"], cwd=ROOT, check=True)
        subprocess.run(["python", "scripts/fix_experimental_page_links.py"], cwd=ROOT, check=True)
        validate()


if __name__ == "__main__":
    main()
