#!/usr/bin/env python3
"""Build the publication homepage in a curated overall order.

The ranking is intentionally silent on the public site: no scores, rank numbers,
or badges are emitted. The order itself is the only signal. Search, A-Z, and
subject sorting remain available to visitors.

Core-paper and ADS extraction stays in build_library_homepage_v2.py. Files kept
under pub.experimental are indexed into the same public catalogue without being
relocated. Exact binary copies of already-catalogued works are absorbed into the
existing card instead of appearing as duplicate publications.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path
from urllib.parse import quote, unquote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
V2_PATH = HERE / "build_library_homepage_v2.py"
EXPERIMENTAL_DIR = ROOT / "pub.experimental"
EXPERIMENTAL_GITHUB = "https://github.com/btenneson/pub/blob/main/"
EXPERIMENTAL_RAW = "https://raw.githubusercontent.com/btenneson/pub/main/"
BRAINSTORMING_NAME = "BRAINSTORMING-the_creativity_knobs_limits_natures_for_an_ATP.pdf"
BRAINSTORMING_HREF = EXPERIMENTAL_GITHUB + "pub.experimental/" + BRAINSTORMING_NAME

spec = importlib.util.spec_from_file_location("publication_builder_v2", V2_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load {V2_PATH}")
v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)

# Overall editorial order, strongest first. Keep this private to the builder:
# the generated site deliberately does not expose rank numbers or scores.
# The experimental BRAINSTORMING note is intentionally first while it is the
# active working item. The existing creativity treatise is the guaranteed
# fallback at #1 until that experimental note has been imported.
RANKED_HREFS = (
    BRAINSTORMING_HREF,
    "papers/data_atp_creativity_treatise_v0_1/",
    "papers/what_checks_the_proof_v6_80/",
    "papers/verified_settlement_search_v1_4/",
    "papers/shortest_settlement_optimal_control_v1_0/",
    "papers/search_dynamics_abel_v0_4/",
    "papers/proof_compass_theory/",
    "papers/universal_proof_horizon_operator/",
    "papers/reflective_compass_control_v0_2/",
    "papers/depths_of_induction_v47/",
    "papers/ald_certificate_halting_shared_lemma_pools/",
    "papers/data_4_2_quotient_density_compass/",
    "papers/depth_density_objective_atp_measurement/",
    "papers/conjecture_settling_ii/",
    "papers/automatic_logic_deciders_framework/",
    "papers/data_2_0_1_proof_horizon_architecture/",
    "papers/hilbert_space_filling_curve_theorem_search/",
    "papers/multi_dose_concentration_derivation_v6_1/",
    "papers/predator_8_004/",
    "papers/technical_companion_next_generation_atp/",
    "papers/ald_implementation_policies/",
    "papers/notald_massive_tied_ocean/",
    "papers/search_dynamics_discovery_v0_3/",
    "papers/search_dynamics_v0_2/",
    "papers/closed_form_surjection_n_to_q/",
    "papers/automated_logical_deciders_ald_001/",
    "papers/ald_research_notebook_001/",
    "ADS/machine_learning/Tenneson_ADS_652-final_report-version_2.pdf",
    "ADS/sports_performance/DEPTHS_2.PDF",
    "ADS/sports_performance/DEPTHS_1.PDF",
    "ADS/sports_performance/depth_of_simulation_-_19.pdf",
    "ADS/healthcare_biomedical/MANYDO_4.PDF",
    "papers/automated_logical_deciders_brochure/",
    "ADS/healthcare_biomedical/ADS_534-tenneson_homework_8_version_1.pdf",
    "ADS/healthcare_biomedical/tenneson_homework_7_version_4.pdf",
    "ADS/healthcare_biomedical/tenneson_homework_6_version_1.pdf",
    "ADS/statistical_methods/tenneson_homework_5_version_2.pdf",
    "ADS/healthcare_biomedical/tenneson_homework_3_version_5.pdf",
    "ADS/statistical_methods/tenneson_discussion_3.pdf",
    "papers/solving_sat_polynomial_time/",
    "papers/external_theorem_proving_survey_2404_09939v3/",
)
RANK = {href: i for i, href in enumerate(RANKED_HREFS)}


def experimental_title(path: Path) -> str:
    if path.name == BRAINSTORMING_NAME:
        return "BRAINSTORMING — the creativity knob(s)/limits/natures for an ATP"
    stem = unquote(path.stem)
    stem = re.sub(r"[_]+", " ", stem)
    stem = re.sub(r"\s+", " ", stem).strip()
    return stem or path.name


def experimental_path_key(path: Path) -> tuple:
    """Prefer a clean filename to a browser/download-style '(1)' copy."""
    copied = bool(re.search(r" \(\d+\)$", path.stem))
    return (copied, path.as_posix().casefold())


def extract_experimental() -> list[dict]:
    """Index actual files in pub.experimental without imposing authorship metadata."""
    if not EXPERIMENTAL_DIR.exists():
        return []
    items: list[dict] = []
    for path in sorted(EXPERIMENTAL_DIR.rglob("*"), key=experimental_path_key):
        if not path.is_file():
            continue
        rel_inside = path.relative_to(EXPERIMENTAL_DIR)
        if any(part.startswith(".") or part.startswith("_") for part in rel_inside.parts):
            continue
        if path.name in {"README.md", "MANIFEST.json"}:
            continue
        rel = path.relative_to(ROOT).as_posix()
        encoded = quote(rel, safe="/")
        href = EXPERIMENTAL_GITHUB + encoded
        ext = path.suffix.lower().lstrip(".") or "file"
        title = experimental_title(path)
        category = v2.category_for(title, rel)
        items.append({
            "title": title,
            "kind": "Experimental",
            "category": category,
            "tags": ["experimental", ext],
            "href": href,
            "pdf": (EXPERIMENTAL_RAW + encoded) if ext == "pdf" else "",
            "source": href if ext in {"tex", "md", "txt", "py"} else "",
            "archive_path": rel,
            "search": " ".join([title, category, "experimental pub.experimental", rel, ext]),
        })
    return items


def digest_for(item: dict) -> str | None:
    """Return the exact-content digest for a repository-local archived file."""
    rel = str(item.get("archive_path") or "").strip()
    if not rel:
        return None
    path = ROOT / rel
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def absorb_experimental(base_items: list[dict], experimental_items: list[dict]) -> list[dict]:
    """Merge experimental storage copies into one public publication catalogue.

    Existing core/ADS cards are never collapsed against one another. Only a
    pub.experimental item is absorbed when its bytes exactly match an item
    already in the catalogue. Experimental-only material remains a normal card.
    """
    out = list(base_items)
    by_digest: dict[str, dict] = {}
    for item in out:
        digest = digest_for(item)
        if digest and digest not in by_digest:
            by_digest[digest] = item

    for item in experimental_items:
        digest = digest_for(item)
        canonical = by_digest.get(digest) if digest else None
        if canonical is not None:
            rel = str(item.get("archive_path") or "")
            paths = canonical.setdefault("experimental_paths", [])
            if rel and rel not in paths:
                paths.append(rel)
            canonical["search"] = " ".join(
                [str(canonical.get("search") or ""), "pub.experimental", rel]
            ).strip()
            continue

        out.append(item)
        if digest:
            by_digest[digest] = item

    return out


def order_key(item: dict) -> tuple:
    href = str(item.get("href") or "")
    if href in RANK:
        return (0, RANK[href])
    # New unranked material is still deterministic until it is curated.
    kind_order = {"Core paper": 0, "Experimental": 1, "Applied Data Science": 2}
    return (
        1,
        kind_order.get(str(item.get("kind") or ""), 9),
        str(item.get("title") or "").casefold(),
        href.casefold(),
    )


def main() -> None:
    # pub.experimental is a storage namespace inside one catalogue, not a
    # second public library. Preserve its files; absorb exact duplicates.
    base_items = v2.extract_core() + v2.extract_ads()
    items = absorb_experimental(base_items, extract_experimental())
    items.sort(key=order_key)

    payload = {"schema_version": 1, "count": len(items), "items": items}
    v2.OUT_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    page = v2.build_html(items)
    old = "else a.sort((x,y)=>(x.kind==='Core paper'?0:1)-(y.kind==='Core paper'?0:1)||x.title.localeCompare(y.title));"
    new = "else {/* curated overall library order: preserve DATA order */}"
    if old not in page:
        raise RuntimeError("Expected default-sort code was not found in v2 output")
    page = page.replace(old, new, 1)

    # Keep guided reading navigation. Experimental storage is searchable from
    # the main catalogue and therefore does not need a competing wing link.
    nav = '<nav class="toplinks">'
    links = '<a href="AMLD_Reading_Wing/">AMLD guided reading wing</a>'
    if nav not in page:
        raise RuntimeError("Homepage navigation block not found")
    page = page.replace(nav, nav + links, 1)

    page = page.replace(
        "A searchable index of the core research-paper library and the Applied Data Science wing.",
        "A searchable index of the publication library and Applied Data Science material. Files stored under pub.experimental are included here without being relocated.",
        1,
    )
    page = page.replace(
        "Index generated from <code>docs/papers</code> and <code>docs/ADS/manifest.json</code>.",
        "Index generated from <code>docs/papers</code>, <code>pub.experimental</code>, and <code>docs/ADS/manifest.json</code>; exact storage duplicates are shown once.",
        1,
    )

    v2.OUT_HTML.write_text(page, encoding="utf-8")
    print(f"wrote {len(items)} searchable items in one integrated catalogue")


if __name__ == "__main__":
    main()
