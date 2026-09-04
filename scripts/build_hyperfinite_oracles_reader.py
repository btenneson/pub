#!/usr/bin/env python3
"""Build a true HTML reader for The Hyperfinite Oracles of DATA MIND 3.2."""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "documents and their sources" / "The_Hyperfinite_Oracles_of_DATA_MIND_3_2.tex"
OUT = ROOT / "docs" / "papers" / "hyperfinite_oracles_data_mind_3_2" / "index.html"

STYLE = r"""
<style>
:root{color-scheme:light dark;--bg:#f7f8fa;--panel:#fff;--text:#18212b;--muted:#5b6773;--line:#d7dde4;--accent:#245d83;--accent2:#eaf3f8}
@media(prefers-color-scheme:dark){:root{--bg:#11161b;--panel:#182028;--text:#eef4f8;--muted:#aab6c0;--line:#33414c;--accent:#7fc3ef;--accent2:#1d3341}}
body{margin:0;background:var(--bg);color:var(--text);font:17px/1.62 Georgia,serif;padding:24px}
body>*{max-width:900px;margin-left:auto;margin-right:auto}h1,h2,h3{font-family:system-ui,-apple-system,Segoe UI,sans-serif;line-height:1.2}a{color:var(--accent)}
nav#TOC{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px 18px;margin:20px auto}blockquote{border-left:3px solid var(--accent);background:var(--accent2);padding:10px 16px}.math.display{overflow-x:auto}
.reader-actions{position:sticky;top:0;z-index:10;display:flex;gap:10px;flex-wrap:wrap;padding:10px;background:color-mix(in srgb,var(--bg) 92%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line);font-family:system-ui,-apple-system,Segoe UI,sans-serif}
.reader-actions a{display:inline-block;text-decoration:none;font-weight:700;border:1px solid var(--line);border-radius:9px;padding:8px 12px;background:var(--panel)}
table{border-collapse:collapse;max-width:100%;display:block;overflow-x:auto}th,td{border:1px solid var(--line);padding:8px 10px}
</style>
"""

ACTIONS = """<div class=\"reader-actions\"><a href=\"../../../\">← Publication library</a><a href=\"./The_Hyperfinite_Oracles_of_DATA_MIND_3_2.pdf\">PDF</a><a href=\"./source.html\">LaTeX source</a></div>"""


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "pandoc",
            str(SRC),
            "--from=latex",
            "--to=html5",
            "--standalone",
            "--toc",
            "--mathjax=https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js",
            "--metadata",
            "title=The Hyperfinite Oracles of DATA MIND 3.2",
            "-o",
            str(OUT),
        ],
        check=True,
    )
    page = OUT.read_text(encoding="utf-8")
    page = page.replace("</head>", STYLE + "\n</head>", 1)
    page = page.replace("<body>", "<body>" + ACTIONS, 1)
    OUT.write_text(page, encoding="utf-8")

    check = OUT.read_text(encoding="utf-8")
    assert "window.location.replace" not in check
    assert "http-equiv=\"refresh\"" not in check
    assert "From logical omniscience to resource-indexed knowledge" in check
    assert "The hyperfinite settlement oracle" in check
    assert "MathJax" in check
    print("Built HTML reader:", OUT)


if __name__ == "__main__":
    main()
