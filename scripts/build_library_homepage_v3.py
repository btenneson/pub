#!/usr/bin/env python3
"""Build the publication homepage in a curated overall order.

The ranking is intentionally silent on the public site: no scores, rank numbers,
or badges are emitted.  The order itself is the only signal.  Search, A-Z, and
subject sorting remain available to visitors.

All extraction/parsing logic stays in build_library_homepage_v2.py so this file
only adds a stable editorial ordering layer.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
V2_PATH = HERE / "build_library_homepage_v2.py"

spec = importlib.util.spec_from_file_location("publication_builder_v2", V2_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load {V2_PATH}")
v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)

# Overall editorial order, strongest first.  Keep this private to the builder:
# the generated site deliberately does not expose rank numbers or scores.
RANKED_HREFS = (
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
    "papers/data_atp_creativity_treatise_v0_1/",
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


def order_key(item: dict) -> tuple:
    href = str(item.get("href") or "")
    if href in RANK:
        return (0, RANK[href])
    # New unranked material is still deterministic until it is curated.
    return (
        1,
        0 if item.get("kind") == "Core paper" else 1,
        str(item.get("title") or "").casefold(),
        href.casefold(),
    )


def main() -> None:
    items = v2.extract_core() + v2.extract_ads()
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

    # Preserve the special AMLD guided-reading wing across all future rebuilds.
    wing_link = '<a href="AMLD_Reading_Wing/">AMLD guided reading wing</a>'
    nav = '<nav class="toplinks">'
    if wing_link not in page:
        if nav not in page:
            raise RuntimeError("Homepage navigation block not found")
        page = page.replace(nav, nav + wing_link, 1)

    v2.OUT_HTML.write_text(page, encoding="utf-8")
    print(f"wrote {len(items)} searchable items in curated overall order")


if __name__ == "__main__":
    main()
