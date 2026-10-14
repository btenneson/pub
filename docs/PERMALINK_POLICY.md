# Publication policy

Canonical public readers live at `/pub/<arXiv-subject-folder>/<publication-slug>/`.
Featured research is listed in the main gallery; historical, superseded, duplicate-format, coursework, external-reference and unavailable entries are listed separately at `/pub/archive/`. The reviewed catalog retains 141 entries, including 20 historical aliases; individual reader permalinks and original files remain available. Distinct archived versions are preserved instead of deleted.

Subject labels are editorial classifications based on arXiv subject names, not claims of submission or endorsement. Stories receive a thematic classification and are labeled as fiction.

No publications are stored in `/pub/papers/`. Former public URLs are recorded in `redirects.json`; GitHub Pages' custom 404 page sends browser visits to their replacement. This is a browser redirect, not an HTTP 301: clients without JavaScript and automated link checkers will still receive HTTP 404 for retired paths. Use the new canonical URLs when sharing.

Original repository archive paths outside the public docs tree remain preserved. Existing PDF citations are not rewritten; former reader links use the compatibility map.

`scripts/publications.json` is the single reviewed catalog. Run `python scripts/build_publications.py` and `python scripts/audit_subject_catalog.py` after edits. Quoted words must occur on the cited page; do not fabricate quotes for unreadable files. A damaged publication is explicitly listed in the research archive as unavailable until a valid replacement is supplied. Known mathematical errors should be labeled prominently without erasing the historical record.

AI-assisted audits and revisions are internal editorial or mathematical reviews, not independent peer review, formal machine verification, or institutional certification. Preliminary and conditional results should be read with their stated hypotheses.
