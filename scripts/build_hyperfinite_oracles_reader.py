#!/usr/bin/env python3
"""Build the standard publication reader for The Hyperfinite Oracles of DATA MIND 3.2."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "papers" / "hyperfinite_oracles_data_mind_3_2" / "index.html"

PAGE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>The Hyperfinite Oracles of DATA MIND 3.2</title>
<meta name="description" content="Canonical reader for The Hyperfinite Oracles of DATA MIND 3.2 by Brian Tenneson.">
<link rel="canonical" href="https://btenneson.github.io/pub/papers/hyperfinite_oracles_data_mind_3_2/">
<style>
:root{color-scheme:light dark;--b:#8885}
*{box-sizing:border-box}
body{margin:0;font-family:system-ui}
header{padding:1rem;border-bottom:1px solid var(--b)}
h1{font-size:1.2rem;margin:0 0 .3rem}
.sub{opacity:.76;margin:.35rem 0 .8rem}
.links{display:flex;gap:.55rem;flex-wrap:wrap}
.links a{padding:.45rem .65rem;border:1px solid var(--b);border-radius:8px;text-decoration:none;font-weight:650}
iframe{width:100%;height:calc(100vh - 180px);min-height:560px;border:0}
</style>
</head>
<body>
<header>
<h1><b>The Hyperfinite Oracles of DATA MIND 3.2</b></h1>
<p class="sub">DATA MIND 3.2 · Brian Tenneson · September 2026</p>
<nav class="links" id="links"></nav>
</header>
<iframe id="reader" title="The Hyperfinite Oracles of DATA MIND 3.2 PDF reader"></iframe>
<script>
const p='https://raw.githubusercontent.com/btenneson/pub/main/cs.LO_Logic_in_Computer_Science/The_Hyperfinite_Oracles_of_DATA_MIND_3_2.pdf';
const source='./source.html';
const library='/pub/';
const v='https://mozilla.github.io/pdf.js/web/viewer.html?file='+encodeURIComponent(p);
document.getElementById('reader').src=v;
document.getElementById('links').innerHTML='<a href="'+library+'">← Publication Library</a><a href="'+v+'" target="_blank" rel="noopener">Open full-screen reader</a><a href="'+p+'">PDF</a><a href="'+source+'">LaTeX source</a>';
</script>
</body>
</html>
'''


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(PAGE, encoding="utf-8")
    check = OUT.read_text(encoding="utf-8")
    assert "<iframe" in check
    assert "'/pub/'" in check
    assert "Open full-screen reader" in check
    assert "The_Hyperfinite_Oracles_of_DATA_MIND_3_2.pdf" in check
    assert "source.html" in check
    assert "../../../" not in check
    print("Built standard publication reader:", OUT)


if __name__ == "__main__":
    main()
