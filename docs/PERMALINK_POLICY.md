# Publication Permalink Policy

This repository follows a **never break published URLs** policy for public research documents.

## 1. Existing published GitHub PDF paths are immutable

Once a PDF path has been shared publicly, the file at that repository path should not be moved or deleted solely for reorganization. Existing `github.com/.../blob/...pdf` links remain valid archival links even when a better reader URL is introduced.

## 2. Canonical reader URLs live under `/papers/<slug>/`

The preferred public link for a paper is its GitHub Pages reader page:

`https://btenneson.github.io/pub/papers/<slug>/`

These reader URLs are intended for Substack posts, social links, bibliographies when an HTML landing page is appropriate, and general reader-facing use.

## 3. Canonical reader pages are stable identifiers

A canonical paper page should not be renamed after publication. A newer PDF version may be linked from the same canonical page when appropriate, while older versions remain archived in GitHub.

If a canonical page must ever move, its old path must remain as an HTML redirect to the replacement. Redirect stubs are permanent compatibility files and should not be deleted during cleanup.

## 4. Aliases are redirects, not duplicate identities

Short names, former titles, former classifications, or other historical reader URLs may be implemented as static HTML redirect pages. Each alias points to exactly one canonical paper URL.

## 5. Repository files remain the archival record

The reader page should link to:

- a browser reader that does not depend on GitHub's `blob` PDF preview;
- the PDF download;
- the LaTeX or other source when available;
- the legacy GitHub PDF page for archival continuity.

The canonical reader layer does not replace the repository archive.

## 6. PDF filenames

For generated publication PDFs, prefer stable ASCII filenames using underscores rather than spaces. Avoid changing a filename after it has been publicly linked. If a corrected or revised file requires a new filename, retain the old file and point the canonical page to the recommended version.

## 7. Substack policy

New Substack posts should prefer the canonical reader URL as the **Read paper** link. A PDF may also be attached directly to Substack as a download fallback. Previously published Substack links do not need to be changed unless desired.

## 8. Reader implementation

Canonical reader pages should avoid depending on GitHub's `blob` PDF renderer. The initial implementation uses Mozilla PDF.js with the archived PDF as the document source, while preserving direct download and GitHub archive links as fallbacks.

## 9. Change-control rule

Before deleting, renaming, or moving a publication file or reader page, first determine whether its URL has been published. When uncertain, preserve the old path and add a redirect or compatibility copy rather than breaking the URL.
