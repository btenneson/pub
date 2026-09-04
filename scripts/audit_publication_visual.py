#!/usr/bin/env python3
"""Render-level diagnostic for every item in docs/search-index.json.

Checks all indexed publication cards for local archive integrity, PDF page geometry,
blank pages, text escaping the page box, mixed page sizes, common encoding damage,
live reader/PDF delivery, and reader layout in headless Chrome at desktop + phone
widths. Writes JSON/Markdown reports and screenshots only for browser-flagged pages.
This script is diagnostic/read-only and intentionally returns success when it
finds publication defects so the report artifact is always retained.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import time
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin, unquote

import fitz
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageStat

RANK = {"critical": 4, "high": 3, "medium": 2, "low": 1, "ok": 0}
MOJIBAKE = ("\ufffd", "Ã", "Â", "â€", "â€™", "â€œ", "â€\u009d", "â€“", "â—")
VISIBLE_ERRORS = ("404 not found", "page not found", "failed to load pdf",
                  "error loading pdf", "file not found", "refused to connect")


def finding(severity: str, code: str, message: str, **extra) -> dict:
    out = {"severity": severity, "code": code, "message": message}
    out.update(extra)
    return out


def is_url(value: str) -> bool:
    return bool(re.match(r"^https?://", value or "", re.I))


def safe_name(value: str) -> str:
    return (re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_") or "item")[:110]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def local_reader(root: Path, href: str) -> Path | None:
    if not href or is_url(href):
        return None
    rel = unquote(href.split("?", 1)[0].split("#", 1)[0]).lstrip("/")
    p = root / "docs" / rel
    if href.endswith("/") or p.is_dir():
        p = p / "index.html"
    return p


def local_repo_file(root: Path, value: str) -> Path | None:
    if not value or is_url(value):
        return None
    rel = unquote(value.split("?", 1)[0].split("#", 1)[0]).lstrip("/")
    for p in (root / rel, root / "docs" / rel):
        if p.exists():
            return p
    return root / rel


def resolve_html_ref(root: Path, page: Path, ref: str) -> Path | None:
    ref = unquote(ref.split("?", 1)[0].split("#", 1)[0])
    if not ref or ref.startswith(("http://", "https://", "mailto:", "tel:", "data:", "javascript:")):
        return None
    # GitHub Pages project-site root is /pub/. Map that prefix back to docs/.
    if ref == "/pub" or ref == "/pub/":
        target = root / "docs" / "index.html"
    elif ref.startswith("/pub/"):
        target = root / "docs" / ref[len("/pub/"):]
    elif ref.startswith("/"):
        target = root / "docs" / ref.lstrip("/")
    else:
        target = (page.parent / ref).resolve()
    if target.is_dir():
        target = target / "index.html"
    return target


def inspect_reader_html(root: Path, page: Path) -> tuple[dict, list[dict]]:
    m = {"exists": page.exists(), "title": "", "viewport": False,
         "iframe_srcs": [], "broken_local_refs": [], "raw_latex_markers": 0}
    issues: list[dict] = []
    if not page.exists():
        return m, [finding("critical", "READER_MISSING", f"Missing reader: {page.relative_to(root)}")]
    raw = page.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(raw, "html.parser")
    m["title"] = soup.title.get_text(" ", strip=True) if soup.title else ""
    m["viewport"] = bool(soup.find("meta", attrs={"name": re.compile(r"^viewport$", re.I)}))
    if not m["viewport"]:
        issues.append(finding("medium", "NO_VIEWPORT", "Reader has no viewport meta tag."))
    m["iframe_srcs"] = [(x.get("src") or "") for x in soup.find_all("iframe")]
    if any(not x for x in m["iframe_srcs"]):
        issues.append(finding("high", "EMPTY_IFRAME", "Reader contains an iframe without src."))
    # Raw TeX is only suspicious when it leaks outside a code/pre presentation.
    stripped = re.sub(r"<(pre|code)\b[^>]*>.*?</\1>", "", raw, flags=re.I | re.S)
    m["raw_latex_markers"] = len(re.findall(r"\\(?:documentclass|begin\{|section\{|usepackage|end\{document\})", stripped))
    if m["raw_latex_markers"] >= 3:
        issues.append(finding("high", "RAW_LATEX_VISIBLE", f"Possible raw LaTeX leak ({m['raw_latex_markers']} markers)."))
    for tag in soup.find_all(["a", "img", "script", "link", "iframe"]):
        attr = "href" if tag.name in ("a", "link") else "src"
        ref = tag.get(attr) or ""
        target = resolve_html_ref(root, page, ref)
        if target is not None and not target.exists():
            m["broken_local_refs"].append(ref)
    for ref in m["broken_local_refs"][:12]:
        issues.append(finding("high", "BROKEN_LOCAL_REF", f"Broken local reader reference: {ref}"))
    return m, issues


def inspect_pdf(root: Path, path: Path) -> tuple[dict, list[dict]]:
    m = {"exists": path.exists(), "bytes": None, "sha256": None, "pages": None,
         "page_sizes": [], "blank_pages": [], "rotated_pages": [],
         "outside_text": [], "mojibake_pages": [], "extreme_font_pages": [],
         "mixed_page_sizes": False}
    issues: list[dict] = []
    if not path.exists():
        return m, [finding("critical", "PDF_MISSING", f"Missing PDF/archive file: {path.relative_to(root)}")]
    m["bytes"] = path.stat().st_size
    if m["bytes"] < 1024:
        issues.append(finding("critical", "PDF_TINY", f"PDF is only {m['bytes']} bytes."))
    with path.open("rb") as f:
        magic = f.read(5)
    if magic != b"%PDF-":
        issues.append(finding("critical", "PDF_BAD_MAGIC", f"File does not begin with %PDF- ({magic!r})."))
        return m, issues
    m["sha256"] = sha256(path)
    try:
        doc = fitz.open(path)
    except Exception as exc:
        return m, issues + [finding("critical", "PDF_OPEN_ERROR", f"PyMuPDF cannot open PDF: {exc}")]
    try:
        m["pages"] = doc.page_count
        if not doc.page_count:
            return m, issues + [finding("critical", "PDF_ZERO_PAGES", "PDF has zero pages.")]
        sizes = []
        for i in range(doc.page_count):
            p = doc.load_page(i)
            rect = p.rect
            w, h = float(rect.width), float(rect.height)
            sizes.append((w, h))
            m["page_sizes"].append([round(w, 1), round(h, 1)])
            if p.rotation % 360:
                m["rotated_pages"].append(i + 1)
            ar = w / h if h else 999
            if w < 250 or h < 250 or w > 1600 or h > 2200 or ar < .35 or ar > 2.85:
                issues.append(finding("high", "ODD_PAGE_GEOMETRY", f"Page {i+1}: unusual {w:.1f}×{h:.1f} pt geometry.", page=i+1))
            try:
                blocks = p.get_text("blocks", sort=False)
            except Exception:
                blocks = []
            escaped = 0
            for b in blocks:
                x0, y0, x1, y1 = map(float, b[:4])
                if x0 < rect.x0 - 4 or y0 < rect.y0 - 4 or x1 > rect.x1 + 4 or y1 > rect.y1 + 4:
                    escaped += 1
            if escaped:
                m["outside_text"].append({"page": i+1, "blocks": escaped})
                issues.append(finding("high", "TEXT_OUTSIDE_PAGE", f"Page {i+1}: {escaped} extracted text block(s) outside page box.", page=i+1))
            text = p.get_text("text") or ""
            normalized = re.sub(r"\s+", "", text)
            if len(normalized) < 10 and not p.get_images(full=True) and not p.get_drawings():
                m["blank_pages"].append(i + 1)
            if any(x in text for x in MOJIBAKE):
                m["mojibake_pages"].append(i + 1)
            extremes = []
            try:
                td = p.get_text("dict")
                for block in td.get("blocks", []):
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            fs = float(span.get("size") or 0)
                            if fs > 96 or (0 < fs < 2):
                                extremes.append(fs)
            except Exception:
                pass
            if extremes:
                m["extreme_font_pages"].append(i + 1)
        if m["blank_pages"]:
            sev = "high" if len(m["blank_pages"]) > 2 else "medium"
            issues.append(finding(sev, "BLANK_PAGES", f"Apparently blank pages: {m['blank_pages'][:30]}"))
        if m["mojibake_pages"]:
            issues.append(finding("medium", "MOJIBAKE_TEXT", f"Possible encoding corruption on pages {m['mojibake_pages'][:30]}"))
        if m["extreme_font_pages"]:
            issues.append(finding("low", "EXTREME_FONT_SIZE", f"Extreme extracted font sizes on pages {m['extreme_font_pages'][:30]}"))
        grouped = Counter((round(w/3)*3, round(h/3)*3) for w, h in sizes)
        if len(grouped) > 1:
            dominant_n = grouped.most_common(1)[0][1]
            minority = doc.page_count - dominant_n
            ratio = max(max(w for w,_ in sizes)/max(min(w for w,_ in sizes),1),
                        max(h for _,h in sizes)/max(min(h for _,h in sizes),1))
            m["mixed_page_sizes"] = True
            issues.append(finding("high" if ratio > 1.7 else "medium", "MIXED_PAGE_SIZES",
                                  f"{len(grouped)} page-size groups; {minority}/{doc.page_count} pages differ from the dominant size."))
    finally:
        doc.close()
    return m, issues


def http_probe(session: requests.Session, url: str) -> dict:
    out = {"url": url, "ok": False, "status": None, "content_type": "", "error": None}
    try:
        r = session.get(url, timeout=15, allow_redirects=True, stream=True,
                        headers={"User-Agent": "pub-101-visual-audit/1.0"})
        out["status"] = r.status_code
        out["content_type"] = r.headers.get("content-type", "")
        out["ok"] = bool(r.ok)
        r.close()
    except Exception as exc:
        out["error"] = f"{type(exc).__name__}: {exc}"
    return out


def make_browser():
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
    except Exception as exc:
        return None, f"selenium unavailable: {exc}"
    chrome = next((shutil.which(x) for x in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser") if shutil.which(x)), None)
    if not chrome:
        return None, "Chrome/Chromium not found"
    opt = Options()
    opt.binary_location = chrome
    for flag in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--hide-scrollbars"):
        opt.add_argument(flag)
    opt.add_argument("--window-size=1365,900")
    opt.set_capability("pageLoadStrategy", "eager")
    opt.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    try:
        d = webdriver.Chrome(options=opt)
        d.set_page_load_timeout(20)
        d.set_script_timeout(8)
        return d, None
    except Exception as exc:
        return None, f"Chrome WebDriver failed: {type(exc).__name__}: {exc}"


def browser_check(driver, url: str, screenshots: Path, label: str) -> tuple[dict, list[dict]]:
    m = {"loaded": False, "desktop_overflow": None, "mobile_overflow": None,
         "broken_images": None, "blank_iframes": None, "console_errors": [],
         "screenshot": None, "error": None}
    issues: list[dict] = []
    try:
        driver.set_window_size(1365, 900)
        driver.get(url)
        time.sleep(.65)
        m["loaded"] = True
        vals = driver.execute_script("""
          const d=document.documentElement,b=document.body;
          return {iw:innerWidth,sw:Math.max(d.scrollWidth,b?b.scrollWidth:0),
                  txt:(b&&b.innerText)||'',broken:[...document.images].filter(i=>i.complete&&i.naturalWidth===0).length,
                  blank:[...document.querySelectorAll('iframe')].filter(i=>!i.src||i.src==='about:blank').length};
        """)
        m["desktop_overflow"] = max(0, int(vals["sw"] - vals["iw"]))
        m["broken_images"] = int(vals["broken"])
        m["blank_iframes"] = int(vals["blank"])
        txt = (vals["txt"] or "").lower()
        if any(x in txt for x in VISIBLE_ERRORS):
            issues.append(finding("high", "VISIBLE_ERROR_TEXT", "Reader visibly contains error/404 text."))
        if m["desktop_overflow"] > 40:
            issues.append(finding("medium", "DESKTOP_OVERFLOW", f"Desktop horizontal overflow: {m['desktop_overflow']} px."))
        if m["broken_images"]:
            issues.append(finding("medium", "BROKEN_IMAGES", f"{m['broken_images']} broken image(s)."))
        if m["blank_iframes"]:
            issues.append(finding("high", "BLANK_IFRAME_RUNTIME", f"{m['blank_iframes']} blank iframe(s) at runtime."))
        driver.set_window_size(390, 844)
        time.sleep(.15)
        mob = driver.execute_script("""
          const d=document.documentElement,b=document.body;
          return {iw:innerWidth,sw:Math.max(d.scrollWidth,b?b.scrollWidth:0)};
        """)
        m["mobile_overflow"] = max(0, int(mob["sw"] - mob["iw"]))
        if m["mobile_overflow"] > 18:
            issues.append(finding("high" if m["mobile_overflow"] > 160 else "medium", "MOBILE_OVERFLOW",
                                  f"Phone-width horizontal overflow: {m['mobile_overflow']} px."))
        try:
            logs = driver.get_log("browser")
            severe = [x.get("message", "") for x in logs if x.get("level") == "SEVERE" and "favicon" not in x.get("message", "").lower()]
            m["console_errors"] = severe[:15]
            if severe:
                issues.append(finding("medium", "BROWSER_CONSOLE_ERRORS", f"Chrome reported {len(severe)} severe console error(s)."))
        except Exception:
            pass
    except Exception as exc:
        m["error"] = f"{type(exc).__name__}: {exc}"
        issues.append(finding("high", "BROWSER_LOAD_ERROR", m["error"]))
    if issues:
        try:
            screenshots.mkdir(parents=True, exist_ok=True)
            shot = screenshots / (safe_name(label) + ".png")
            driver.set_window_size(1365, 900)
            driver.save_screenshot(str(shot))
            m["screenshot"] = str(shot)
            im = Image.open(shot).convert("L").resize((100, 66))
            st = ImageStat.Stat(im)
            if st.mean[0] > 248 and st.var[0] < 8:
                issues.append(finding("high", "NEAR_BLANK_SCREENSHOT", "Reader screenshot is nearly blank."))
        except Exception:
            pass
    return m, issues


def worst(issues: list[dict]) -> str:
    if not issues:
        return "ok"
    return max(issues, key=lambda x: RANK.get(x["severity"], 0))["severity"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--out", default="diagnostics/pub-101-visual-audit")
    ap.add_argument("--live-base", default="https://btenneson.github.io/pub/")
    args = ap.parse_args()
    root = Path(args.repo_root).resolve()
    out = (root / args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    screenshots = out / "screenshots"
    data = json.loads((root / "docs" / "search-index.json").read_text(encoding="utf-8"))
    items = data.get("items", [])
    global_issues: list[dict] = []
    if data.get("count") != len(items):
        global_issues.append(finding("critical", "INDEX_COUNT_MISMATCH", f"Declared {data.get('count')}, found {len(items)} items."))
    if len(items) != 101:
        global_issues.append(finding("high", "NOT_101_ITEMS", f"Expected 101 items, found {len(items)}."))
    session = requests.Session()
    browser, browser_error = make_browser()
    if browser_error:
        global_issues.append(finding("medium", "BROWSER_UNAVAILABLE", browser_error))
    results = []
    for n, item in enumerate(items, 1):
        title = item.get("title") or f"Untitled {n}"
        href = item.get("href") or ""
        pdf = item.get("pdf") or ""
        archive = item.get("archive_path") or ""
        source = item.get("source") or ""
        issues: list[dict] = []
        rec = {"index": n, "title": title, "href": href, "pdf": pdf, "archive_path": archive,
               "source": source, "kind": item.get("kind"), "category": item.get("category"), "issues": issues}
        reader = local_reader(root, href)
        if reader is not None and (href.endswith("/") or reader.suffix.lower() in (".html", ".htm")):
            rec["html"], found = inspect_reader_html(root, reader)
            issues.extend(found)
        elif reader is not None and not reader.exists():
            issues.append(finding("critical", "HREF_TARGET_MISSING", f"Missing href target: {href}"))
        pdf_path = local_repo_file(root, archive) if archive else local_repo_file(root, pdf)
        if pdf_path is not None and pdf_path.suffix.lower() == ".pdf":
            rec["pdf_scan"], found = inspect_pdf(root, pdf_path)
            issues.extend(found)
        elif archive and pdf_path is not None and not pdf_path.exists():
            issues.append(finding("critical", "ARCHIVE_MISSING", f"Missing archive_path: {archive}"))
        live_reader = href if is_url(href) else urljoin(args.live_base, href)
        if href:
            rec["reader_http"] = http_probe(session, live_reader)
            if not rec["reader_http"]["ok"]:
                status = rec["reader_http"]["status"]
                issues.append(finding("critical" if status in (404,410) else "high", "READER_HTTP_FAIL",
                                      f"Reader delivery failed: status={status} error={rec['reader_http']['error']}"))
        if pdf:
            live_pdf = pdf if is_url(pdf) else urljoin(args.live_base, pdf)
            rec["pdf_http"] = http_probe(session, live_pdf)
            if not rec["pdf_http"]["ok"]:
                status = rec["pdf_http"]["status"]
                issues.append(finding("critical" if status in (404,410) else "high", "PDF_HTTP_FAIL",
                                      f"PDF delivery failed: status={status} error={rec['pdf_http']['error']}"))
            elif "pdf" not in rec["pdf_http"]["content_type"].lower():
                issues.append(finding("medium", "PDF_CONTENT_TYPE", f"PDF URL served {rec['pdf_http']['content_type']!r}."))
        if source:
            live_source = source if is_url(source) else urljoin(args.live_base, source)
            rec["source_http"] = http_probe(session, live_source)
            if not rec["source_http"]["ok"]:
                issues.append(finding("medium", "SOURCE_HTTP_FAIL", f"Source delivery failed: status={rec['source_http']['status']}"))
        if item.get("kind") == "Core paper" and not item.get("quote"):
            issues.append(finding("low", "MISSING_QUOTE", "Core-paper card has no quote."))
        if browser is not None and href and (href.endswith("/") or href.lower().endswith((".html", ".htm"))):
            rec["browser"], found = browser_check(browser, live_reader, screenshots, f"{n:03d}_{title}")
            issues.extend(found)
        rec["status"] = worst(issues)
        results.append(rec)
        print(f"AUDIT {n:03d}/{len(items)} {rec['status'].upper():8s} {title}", flush=True)
    if browser is not None:
        try: browser.quit()
        except Exception: pass
    counts = Counter(x["status"] for x in results)
    code_counts = Counter(i["code"] for x in results for i in x["issues"])
    summary = {"declared_count": data.get("count"), "audited_count": len(results),
               "status_counts": dict(counts), "issue_code_counts": dict(code_counts),
               "global_issues": global_issues, "live_base": args.live_base}
    (out / "audit.json").write_text(json.dumps({"summary":summary,"items":results}, indent=2, ensure_ascii=False), encoding="utf-8")
    ordered = sorted(results, key=lambda x: (-RANK.get(x["status"],0), x["index"]))
    md = ["# 101-item publication visual diagnostic", "", f"Audited **{len(results)}** indexed publications.", "",
          "## Severity counts", ""]
    for s in ("critical","high","medium","low","ok"):
        md.append(f"- **{s}**: {counts.get(s,0)}")
    if global_issues:
        md += ["", "## Global findings", ""] + [f"- **{x['severity'].upper()} {x['code']}** — {x['message']}" for x in global_issues]
    md += ["", "## Flagged publications", ""]
    for x in ordered:
        if x["status"] == "ok": continue
        md += [f"### {x['index']:03d}. {x['title']} — {x['status'].upper()}", ""]
        for i in sorted(x["issues"], key=lambda z: -RANK.get(z["severity"],0)):
            md.append(f"- **{i['severity'].upper()} {i['code']}** — {i['message']}")
        if x.get("browser",{}).get("screenshot"):
            md.append(f"- Screenshot: `{Path(x['browser']['screenshot']).relative_to(out)}`")
        md.append("")
    md += ["## Finding-code totals", ""] + [f"- `{k}`: {v}" for k,v in code_counts.most_common()]
    (out / "audit.md").write_text("\n".join(md)+"\n", encoding="utf-8")
    print("AUDIT_SUMMARY " + json.dumps(summary, ensure_ascii=False), flush=True)
    print("AUDIT_FLAGGED_BEGIN", flush=True)
    for x in ordered:
        if x["status"] != "ok":
            codes = ",".join(i["code"] for i in x["issues"])
            print(f"FLAG {x['index']:03d}|{x['status']}|{x['title']}|{codes}", flush=True)
    print("AUDIT_FLAGGED_END", flush=True)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
