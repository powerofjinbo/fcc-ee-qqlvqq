# `paper/`

This directory is the publication layer of the repository.
It does not define the event selection or the ML model itself.

Its job is to take the plots, tables, and fit results produced by the analysis
workflow and package them into a note/paper.

Main files:

- `main.tex`
  - The LaTeX source of the note.
  - This is the final write-up that consumes figures and numbers from the
    earlier stages.

- `generate_supporting_figures.py`
  - Builds extra paper figures from saved analysis outputs.
  - Examples: pairing-validation plots, `sqrt(d34)` distribution, and the
    signal Feynman diagram.

- `sync_paper_figures.py`
  - Collects the figures needed by the paper into `paper/figs/`.
  - Also auto-generates `appendix_plots.tex` for the appendix figure pages.

- `appendix_plots.tex`
  - Auto-generated LaTeX fragment for the appendix plots.

Workflow position:

1. Run the physics and ML stages.
2. Produce the paper-ready figures.
3. Sync them into `paper/figs/`.
4. Compile `main.tex`.

From the top-level driver this corresponds to:

```bash
python3 run_lvqq.py paper
```

So the role split is:

- analysis code decides what the result is
- `paper/` decides how that result is presented
