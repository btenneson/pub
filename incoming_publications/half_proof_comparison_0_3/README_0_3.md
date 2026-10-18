# Half a Proof, The Rest in Its Own Words

DATA MIND / AMLD+0 Research Note 0.3 — 18 October 2026

This release updates the title and adds a brief explanatory metaphor to version 0.2. It retains version 0.2's explicit six-point reader note describing the differences between the original and the normalized candidate proof.

## Files
- Half_Proof_Comparison_0_3.pdf
- Half_Proof_Comparison_0_3.tex
- candidate_proof.tex
- Exact_Addressing_3_3_2_Capstone_Section_15.tex
- verify_metrics.py

## Findings
Original reference proof: 395 whitespace-separated LaTeX tokens; disclosed prefix 197 (49.87%); withheld suffix 198. Normalized reconstructed proof 515 tokens, including a 333-token continuation. Same mathematical strategy; greater explanatory detail. No established blind trial, authenticated multiagent execution, or independent machine-verifier certificate.

Compile with `pdflatex Half_Proof_Comparison_0_3.tex` twice in the directory containing all source files.
