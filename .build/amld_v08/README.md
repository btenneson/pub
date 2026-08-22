# AMLD textbook v0.8 build payload

These five base64 chunks are a lossless bzip2-compressed copy of `What_Checks_the_Proof_AMLD_Textbook_v0_8.tex`. The workflow `.github/workflows/compile_what_checks_proof_amld_v0_8.yml` concatenates them in numeric order, decodes and decompresses the LaTeX source, compiles the PDF, and publishes both source and PDF into the permanent archive paths.

They are retained as reproducible build inputs so the publication can be rebuilt without committing binary PDF bytes through the connector.
