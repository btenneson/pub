#!/usr/bin/env python3
"""Build the publication homepage and preserve the AMLD guided-reading wing link."""
from pathlib import Path
import importlib.util

HERE = Path(__file__).resolve().parent
V3_PATH = HERE / "build_library_homepage_v3.py"
spec = importlib.util.spec_from_file_location("publication_builder_v3", V3_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load {V3_PATH}")
v3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v3)


def main() -> None:
    v3.main()
    index = HERE.parent / "docs" / "index.html"
    page = index.read_text(encoding="utf-8")
    link = '<a href="AMLD_Reading_Wing/">AMLD guided reading wing</a>'
    if link not in page:
        needle = '<nav class="toplinks">'
        if needle not in page:
            raise RuntimeError("Homepage navigation block not found")
        page = page.replace(needle, needle + link, 1)
        index.write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main()
