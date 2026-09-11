# Publication policy

Canonical public readers live at `/pub/<arXiv-subject-folder>/<publication-slug>/`.
Each publication has one catalog card, a reader, a short source-checked quotation, and downloads for files that actually exist. Byte-identical PDFs share a card; distinct archived versions remain available.

Subject labels are editorial classifications based on arXiv subject names, not claims of submission or endorsement. Stories receive a thematic classification and are labeled as fiction.

No publications are stored in `/pub/papers/`. Former public URLs are recorded in `redirects.json`; GitHub Pages' custom 404 page sends browser visits to their replacement. This is a browser redirect, not an HTTP 301: clients without JavaScript and automated link checkers will still receive HTTP 404 for retired paths. Use the new canonical URLs when sharing.

Original repository archive paths outside the public docs tree remain preserved. Existing PDF citations are not rewritten; former reader links use the compatibility map.

`scripts/publications.json` is the single reviewed catalog. Run `python scripts/build_publications.py` and `python scripts/audit_subject_catalog.py` after edits. Quoted words must occur on the cited page; do not fabricate quotes for unreadable files. A damaged publication stays visibly listed as unavailable until a valid replacement is supplied.
