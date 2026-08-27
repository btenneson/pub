#!/usr/bin/env python3
"""Rebuild every publication project touched by the live-self-citation repair.

The first link-repair pass can modify both standalone article .tex files and
included references.tex files.  This script resolves each repaired file to its
actual LaTeX root, compiles the root, and replaces the already-published PDF
when that destination can be identified without guessing.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PAPERS = DOCS / "papers"
RAW = "https://raw.githubusercontent.com/btenneson/pub/main/"


def repaired_sources(log: Path) -> list[Path]:
    text = log.read_text(encoding="utf-8", errors="replace")
    paths: set[Path] = set()
    in_repairs = False
    for line in text.splitlines():
        if line.strip() == "## Repairs":
            in_repairs = True
            continue
        if in_repairs and line.startswith("## "):
            break
        if not in_repairs:
            continue
        m = re.match(r"- `([^`]+\.tex)`\s+—", line)
        if m:
            p = ROOT / m.group(1)
            if p.exists():
                paths.add(p.resolve())
    return sorted(paths)


def latex_roots(touched: Path) -> list[Path]:
    text = touched.read_text(encoding="utf-8", errors="replace")
    if "\\documentclass" in text:
        return [touched]
    roots: list[Path] = []
    for p in touched.parent.glob("*.tex"):
        if "\\documentclass" in p.read_text(encoding="utf-8", errors="replace"):
            roots.append(p.resolve())
    return sorted(roots)


def published_pdf_for(main: Path) -> tuple[Path | None, str]:
    parent_pdfs = [p for p in main.parent.glob("*.pdf") if p.is_file()]
    exact = main.with_suffix(".pdf")
    if exact.exists():
        return exact, "same-stem"
    if len(parent_pdfs) == 1:
        return parent_pdfs[0], "sole-pdf-in-project"

    # Some standalone sources are kept in the source directory while their
    # publication PDF is elsewhere.  Exact filename matching is unambiguous.
    matches = [p for p in ROOT.rglob(main.stem + ".pdf") if "docs/papers" not in p.as_posix()]
    matches = sorted({p.resolve() for p in matches})
    if len(matches) == 1:
        return matches[0], "unique-repository-stem"
    return None, "unresolved-pdf-destination"


def reader_mirrors(pdf: Path) -> list[Path]:
    rel = pdf.relative_to(ROOT).as_posix()
    out: list[Path] = []
    for page in PAPERS.glob("*/index.html"):
        text = page.read_text(encoding="utf-8", errors="replace")
        if RAW + rel in text:
            mirror = page.parent / pdf.name
            if mirror.exists():
                out.append(mirror)
    return out


def compile_one(main: Path, build_root: Path) -> dict:
    target, resolution = published_pdf_for(main)
    rec = {
        "main": main.relative_to(ROOT).as_posix(),
        "target": target.relative_to(ROOT).as_posix() if target else "",
        "resolution": resolution,
        "compiled": False,
        "published": False,
        "mirrors": [],
        "returncode": None,
    }
    if target is None:
        return rec

    out = build_root / re.sub(r"[^A-Za-z0-9_.-]+", "_", main.relative_to(ROOT).as_posix())
    out.mkdir(parents=True, exist_ok=True)
    cmd = [
        "latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error",
        f"-outdir={out}", main.name,
    ]
    proc = subprocess.run(
        cmd, cwd=main.parent, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    rec["returncode"] = proc.returncode
    built = out / (main.stem + ".pdf")
    rec["compiled"] = proc.returncode == 0 and built.exists() and built.stat().st_size > 0
    if not rec["compiled"]:
        (out / "compile.log").write_text(proc.stdout[-100000:], encoding="utf-8", errors="replace")
        rec["log"] = (out / "compile.log").relative_to(ROOT).as_posix()
        return rec

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(built, target)
    rec["published"] = True
    for mirror in reader_mirrors(target):
        shutil.copy2(built, mirror)
        rec["mirrors"].append(mirror.relative_to(ROOT).as_posix())
    return rec


def report_md(results: list[dict], touched: list[Path]) -> str:
    roots = {r["main"] for r in results}
    lines = [
        "# Citation-Link PDF Rebuild Audit", "",
        f"- Repaired source/include files considered: **{len(touched)}**",
        f"- Distinct LaTeX roots resolved: **{len(roots)}**",
        f"- Successfully compiled and republished: **{sum(bool(r['published']) for r in results)}**",
        f"- Compile failures: **{sum(not r['compiled'] and bool(r['target']) for r in results)}**",
        f"- Unresolved PDF destinations: **{sum(not bool(r['target']) for r in results)}**",
        "", "## Projects",
    ]
    for r in results:
        if r["published"]:
            status = "PASS"
        elif not r["target"]:
            status = "UNMAPPED"
        else:
            status = "COMPILE FAILED"
        dest = f" → `{r['target']}`" if r["target"] else ""
        lines.append(f"- **{status}** `{r['main']}`{dest} ({r['resolution']})")
    lines += ["", "## Touched files without a resolved LaTeX root"]
    rooted_parents = {str((ROOT / r["main"]).parent.resolve()) for r in results}
    no_root = [p for p in touched if str(p.parent.resolve()) not in rooted_parents and "\\documentclass" not in p.read_text(errors="replace")]
    if no_root:
        lines += [f"- `{p.relative_to(ROOT).as_posix()}`" for p in no_root]
    else:
        lines.append("- None.")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repair-log", default="docs/LINK_REPAIR_LOG.md")
    ap.add_argument("--report", default="docs/CITATION_REBUILD_AUDIT.md")
    ap.add_argument("--json", default="build/citation-rebuild-results.json")
    args = ap.parse_args()

    log = ROOT / args.repair_log
    touched = repaired_sources(log)
    roots: set[Path] = set()
    for p in touched:
        roots.update(latex_roots(p))

    build_root = ROOT / "build" / "citation-rebuild"
    build_root.mkdir(parents=True, exist_ok=True)
    results = [compile_one(p, build_root) for p in sorted(roots)]

    out_json = ROOT / args.json
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    report = ROOT / args.report
    report.write_text(report_md(results, touched), encoding="utf-8")

    print(json.dumps({
        "touched": len(touched),
        "roots": len(results),
        "published": sum(bool(r["published"]) for r in results),
        "compile_failed": sum(not r["compiled"] and bool(r["target"]) for r in results),
        "unmapped": sum(not bool(r["target"]) for r in results),
    }, indent=2))
    # Report exceptions rather than hiding them. The workflow will commit all
    # successes and the audit report even if a legacy project cannot rebuild.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
