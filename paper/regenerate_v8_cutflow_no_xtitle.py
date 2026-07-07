#!/usr/bin/env python3
"""Regenerate the v8 cutflow plot with paper-friendly cut labels.

This intentionally runs only the single cutFlow plot from ``plots_lvqq.py``.
It avoids the full plotting workflow and keeps the paper figure reproducible
from the frozen v8 histmaker outputs.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path


TAG = "cut_sig100_bkg100_v8_split_local"
REPO = Path(__file__).resolve().parents[1]
PLOT_DIR = REPO / f"plots_lvqq_{TAG}"
NOTE_FIG_DIR = PLOT_DIR / "FCC_ee_HWW_qqlvqq_polished_source (1)" / "figs"
PAPER_CUT_LABELS = [
    "All events",
    "Cut 1 lepton",
    "Cut 2 iso.",
    "Cut 3 veto",
    "Cut 4 MET",
    "Cut 5 4-jet",
    "Cut 6 Nconst",
    "Cut 7 mZ",
    "Cut 8 pZ",
]


def main() -> None:
    os.environ["LVQQ_OUTPUT_TAG"] = TAG

    import plots_lvqq  # noqa: PLC0415

    plots_lvqq.CUT_LABELS = PAPER_CUT_LABELS
    plots_lvqq.setStyle()
    plots_lvqq.makePlot("cutFlow", "", 1, 0.0, float(len(plots_lvqq.CUT_LABELS)), True)

    NOTE_FIG_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PLOT_DIR / "cutFlow.pdf", NOTE_FIG_DIR / "overall_cutflow_named.pdf")
    shutil.copy2(PLOT_DIR / "cutFlow.png", NOTE_FIG_DIR / "overall_cutflow_named.png")
    print(f"Wrote {NOTE_FIG_DIR / 'overall_cutflow_named.pdf'}")


if __name__ == "__main__":
    main()
