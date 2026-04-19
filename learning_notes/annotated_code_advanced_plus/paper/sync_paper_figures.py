#!/usr/bin/env python3
# Copy/collect paper assets and generate appendix TeX deterministically.
#
# This is a line-by-line annotated rewrite for learning and review.
# The executable logic remains unchanged; only explanatory comments were added.

"""Collect the figures used by the paper into a single directory."""

# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
from __future__ import annotations

# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import shutil
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
from pathlib import Path


# [Workflow] Configuration binding; this line defines a stable contract across modules.
THIS_DIR = Path(__file__).resolve().parent
# [Workflow] Configuration binding; this line defines a stable contract across modules.
ANALYSIS_DIR = THIS_DIR.parent
# [Workflow] Configuration binding; this line defines a stable contract across modules.
SOURCE_DIR = ANALYSIS_DIR / "ml" / "models" / "xgboost_bdt_v6" / "plots"
# [Workflow] Configuration binding; this line defines a stable contract across modules.
TARGET_DIR = THIS_DIR / "figs"

# [Workflow] Configuration binding; this line defines a stable contract across modules.
FIGURE_STEMS = [
# [Context] Supporting line for the active lvqq analysis stage.
    "feynman_diagram",
# [Context] Supporting line for the active lvqq analysis stage.
    "pairing_validation",
# [ML] ROC metrics provide threshold-independent ranking quality under class imbalance.
    "roc_curve",
# [Context] Supporting line for the active lvqq analysis stage.
    "d34_distribution",
# [Context] Supporting line for the active lvqq analysis stage.
    "fit_templates",
# [Context] Supporting line for the active lvqq analysis stage.
    "bdt_cut_scan",
# [Context] Supporting line for the active lvqq analysis stage.
]

# [Workflow] Configuration binding; this line defines a stable contract across modules.
APPENDIX_WIDE_PLOTS = [
# [Context] Supporting line for the active lvqq analysis stage.
    "cutFlow",
# [Context] Supporting line for the active lvqq analysis stage.
]

# [Workflow] Configuration binding; this line defines a stable contract across modules.
APPENDIX_PAIRED_PLOTS = [
# [Context] Supporting line for the active lvqq analysis stage.
    "deltaZ_shape",
# [Context] Supporting line for the active lvqq analysis stage.
    "Wstar_m_shape",
# [Context] Supporting line for the active lvqq analysis stage.
    "recoil_m_afterZ_norm",
# [Context] Supporting line for the active lvqq analysis stage.
    "Hcand_m_final_norm",
# [Context] Supporting line for the active lvqq analysis stage.
    "cosTheta_miss_shape",
# [Context] Supporting line for the active lvqq analysis stage.
    "visibleEnergy_shape",
# [Context] Supporting line for the active lvqq analysis stage.
]

# [Workflow] Configuration binding; this line defines a stable contract across modules.
APPENDIX_PLOT_STEMS = [*APPENDIX_WIDE_PLOTS, *APPENDIX_PAIRED_PLOTS]

# [Workflow] Configuration binding; this line defines a stable contract across modules.
PLOT_LABELS = {
# [Context] Supporting line for the active lvqq analysis stage.
    "cutFlow": "Stacked cutflow yields",
# [Context] Supporting line for the active lvqq analysis stage.
    "cosTheta_miss": r"$|\cos\theta_{\mathrm{miss}}|$",
# [Context] Supporting line for the active lvqq analysis stage.
    "visibleEnergy": "Visible energy excluding the selected lepton",
# [Context] Supporting line for the active lvqq analysis stage.
    "Wstar_m": "Reconstructed hadronic W* candidate mass",
# [Context] Supporting line for the active lvqq analysis stage.
    "Hcand_m_final": "Reconstructed Higgs-candidate mass after the final recoil cut",
# [Context] Supporting line for the active lvqq analysis stage.
    "recoil_m_afterZ": "Recoil mass after the Z-mass cut",
# [Context] Supporting line for the active lvqq analysis stage.
    "deltaZ": r"$|m_{jj}-m_Z|$ from the Z-priority pairing",
# [Context] Supporting line for the active lvqq analysis stage.
}


# [Physics] Centralize captions to keep terminology consistent across text and figures.
def caption_for_plot(stem: str) -> str:
# [Context] Supporting line for the active lvqq analysis stage.
    if stem == "cutFlow":
# [Workflow] Return value hands the constructed object/metric to the next module stage.
        return "Stacked event yields across the sequential event selection."
# [Context] Supporting line for the active lvqq analysis stage.
    if stem == "deltaZ_shape":
# [Workflow] Return value hands the constructed object/metric to the next module stage.
        return r"Unit-area comparison of $|m_{jj}-m_Z|$, showing how the Z-priority pairing concentrates the signal near the on-shell Z mass."
# [Context] Supporting line for the active lvqq analysis stage.
    if stem == "Wstar_m_shape":
# [Workflow] Return value hands the constructed object/metric to the next module stage.
        return r"Unit-area comparison of the reconstructed $W^*$ mass, illustrating the broad off-shell signal structure relative to the diboson backgrounds."
# [Context] Supporting line for the active lvqq analysis stage.
    if stem == "recoil_m_afterZ_norm":
# [Workflow] Return value hands the constructed object/metric to the next module stage.
        return "Unit-area recoil-mass comparison after the Z-mass requirement, highlighting the Higgs recoil peak used in the final event selection."
# [Context] Supporting line for the active lvqq analysis stage.
    if stem == "Hcand_m_final_norm":
# [Workflow] Return value hands the constructed object/metric to the next module stage.
        return "Unit-area Higgs-candidate mass comparison after the final recoil selection."
# [Context] Supporting line for the active lvqq analysis stage.
    if stem == "cosTheta_miss_shape":
# [Workflow] Return value hands the constructed object/metric to the next module stage.
        return r"Signal-versus-diboson shape comparison of $|\cos\theta_{\mathrm{miss}}|$, which helps suppress forward missing-momentum topologies."
# [Context] Supporting line for the active lvqq analysis stage.
    if stem == "visibleEnergy_shape":
# [Workflow] Return value hands the constructed object/metric to the next module stage.
        return "Signal-versus-diboson comparison of the visible energy excluding the selected lepton, probing the semi-leptonic event balance."
# [Context] Supporting line for the active lvqq analysis stage.
    raise KeyError(f"Unsupported appendix plot stem: {stem}")


# [Workflow] Auto-emit appendix TeX for deterministic and repeatable manuscripts.
def write_appendix_tex(tex_path: Path) -> None:
# [Context] Supporting line for the active lvqq analysis stage.
    lines: list[str] = []
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append("% Auto-generated by paper/sync_paper_figures.py")
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append(r"\clearpage")

# [Context] Supporting line for the active lvqq analysis stage.
    for stem in APPENDIX_WIDE_PLOTS:
# [Context] Supporting line for the active lvqq analysis stage.
        lines.append(r"\begin{figure}[p]")
# [Context] Supporting line for the active lvqq analysis stage.
        lines.append(r"  \centering")
# [Context] Supporting line for the active lvqq analysis stage.
        lines.append(rf"  \includegraphics[width=0.92\textwidth]{{figs/plots_lvqq/{stem}.pdf}}")
# [Context] Supporting line for the active lvqq analysis stage.
        lines.append(rf"  \caption{{{caption_for_plot(stem)}}}")
# [Context] Supporting line for the active lvqq analysis stage.
        lines.append(rf"  \label{{fig:appendix:{stem}}}")
# [Context] Supporting line for the active lvqq analysis stage.
        lines.append(r"\end{figure}")
# [Context] Supporting line for the active lvqq analysis stage.
        lines.append("")

# [Context] Supporting line for the active lvqq analysis stage.
    paired = list(APPENDIX_PAIRED_PLOTS)
# [Context] Supporting line for the active lvqq analysis stage.
    for idx in range(0, len(paired), 2):
# [Context] Supporting line for the active lvqq analysis stage.
        left = paired[idx]
# [Context] Supporting line for the active lvqq analysis stage.
        right = paired[idx + 1] if idx + 1 < len(paired) else None
# [Context] Supporting line for the active lvqq analysis stage.
        lines.append(r"\begin{figure}[p]")
# [Context] Supporting line for the active lvqq analysis stage.
        lines.append(r"  \centering")
# [Context] Supporting line for the active lvqq analysis stage.
        lines.append(r"  \begin{minipage}[t]{0.48\textwidth}")
# [Context] Supporting line for the active lvqq analysis stage.
        lines.append(r"    \centering")
# [Context] Supporting line for the active lvqq analysis stage.
        lines.append(rf"    \includegraphics[width=\textwidth]{{figs/plots_lvqq/{left}.pdf}}")
# [Context] Supporting line for the active lvqq analysis stage.
        lines.append(rf"    \par\smallskip{{\footnotesize {caption_for_plot(left)}}}")
# [Context] Supporting line for the active lvqq analysis stage.
        lines.append(r"  \end{minipage}")
# [Context] Supporting line for the active lvqq analysis stage.
        if right is not None:
# [Context] Supporting line for the active lvqq analysis stage.
            lines.append(r"  \hfill")
# [Context] Supporting line for the active lvqq analysis stage.
            lines.append(r"  \begin{minipage}[t]{0.48\textwidth}")
# [Context] Supporting line for the active lvqq analysis stage.
            lines.append(r"    \centering")
# [Context] Supporting line for the active lvqq analysis stage.
            lines.append(rf"    \includegraphics[width=\textwidth]{{figs/plots_lvqq/{right}.pdf}}")
# [Context] Supporting line for the active lvqq analysis stage.
            lines.append(rf"    \par\smallskip{{\footnotesize {caption_for_plot(right)}}}")
# [Context] Supporting line for the active lvqq analysis stage.
            lines.append(r"  \end{minipage}")
# [Context] Supporting line for the active lvqq analysis stage.
        lines.append(r"\end{figure}")
# [Context] Supporting line for the active lvqq analysis stage.
        lines.append("")

# [Context] Supporting line for the active lvqq analysis stage.
    tex_path.write_text("\n".join(lines) + "\n")


# [Workflow] Copy only required figure assets and fail if essential files are absent.
def main() -> None:
# [Context] Supporting line for the active lvqq analysis stage.
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
# [Context] Supporting line for the active lvqq analysis stage.
    appendix_dir = TARGET_DIR / "plots_lvqq"
# [Context] Supporting line for the active lvqq analysis stage.
    appendix_dir.mkdir(parents=True, exist_ok=True)

# [Context] Supporting line for the active lvqq analysis stage.
    wanted_root_files = {f"{stem}{ext}" for stem in FIGURE_STEMS for ext in (".pdf", ".png")}
# [Context] Supporting line for the active lvqq analysis stage.
    for path in TARGET_DIR.iterdir():
# [Context] Supporting line for the active lvqq analysis stage.
        if path.is_file() and path.name not in wanted_root_files:
# [Context] Supporting line for the active lvqq analysis stage.
            path.unlink()

# [Context] Supporting line for the active lvqq analysis stage.
    wanted_appendix_files = {f"{stem}.pdf" for stem in APPENDIX_PLOT_STEMS}
# [Context] Supporting line for the active lvqq analysis stage.
    for path in appendix_dir.glob("*.pdf"):
# [Context] Supporting line for the active lvqq analysis stage.
        if path.name not in wanted_appendix_files:
# [Context] Supporting line for the active lvqq analysis stage.
            path.unlink()

# [Context] Supporting line for the active lvqq analysis stage.
    missing: list[str] = []
# [Context] Supporting line for the active lvqq analysis stage.
    for stem in FIGURE_STEMS:
# [Context] Supporting line for the active lvqq analysis stage.
        for ext in (".pdf", ".png"):
# [Context] Supporting line for the active lvqq analysis stage.
            src = SOURCE_DIR / f"{stem}{ext}"
# [Context] Supporting line for the active lvqq analysis stage.
            dst = TARGET_DIR / src.name
# [Context] Supporting line for the active lvqq analysis stage.
            if src.exists():
# [Workflow] Copy exactly the curated deliverables to paper directories.
                shutil.copy2(src, dst)
# [Context] Supporting line for the active lvqq analysis stage.
            elif ext == ".pdf":
# [Context] Supporting line for the active lvqq analysis stage.
                missing.append(src.name)

# [Context] Supporting line for the active lvqq analysis stage.
    appendix_source_dir = ANALYSIS_DIR / "plots_lvqq"
# [Context] Supporting line for the active lvqq analysis stage.
    for stem in APPENDIX_PLOT_STEMS:
# [Context] Supporting line for the active lvqq analysis stage.
        src = appendix_source_dir / f"{stem}.pdf"
# [Context] Supporting line for the active lvqq analysis stage.
        dst = appendix_dir / src.name
# [Context] Supporting line for the active lvqq analysis stage.
        if src.exists():
# [Workflow] Copy exactly the curated deliverables to paper directories.
            shutil.copy2(src, dst)
# [Context] Supporting line for the active lvqq analysis stage.
        else:
# [Context] Supporting line for the active lvqq analysis stage.
            missing.append(str(src.relative_to(ANALYSIS_DIR)))

# [Context] Supporting line for the active lvqq analysis stage.
    write_appendix_tex(THIS_DIR / "appendix_plots.tex")

# [Context] Supporting line for the active lvqq analysis stage.
    if missing:
# [Context] Supporting line for the active lvqq analysis stage.
        missing_text = ", ".join(sorted(missing))
# [Context] Supporting line for the active lvqq analysis stage.
        raise SystemExit(f"Missing required paper figure(s): {missing_text}")

# [Context] Supporting line for the active lvqq analysis stage.
    print(f"Synced paper figures to {TARGET_DIR}")


# [Context] Supporting line for the active lvqq analysis stage.
if __name__ == "__main__":
# [Context] Supporting line for the active lvqq analysis stage.
    main()
