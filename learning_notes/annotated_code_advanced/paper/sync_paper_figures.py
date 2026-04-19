#!/usr/bin/env python3
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
"""Collect the figures used by the paper into a single directory."""

# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
from __future__ import annotations

# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
import shutil
# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
from pathlib import Path


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
THIS_DIR = Path(__file__).resolve().parent
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
ANALYSIS_DIR = THIS_DIR.parent
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
SOURCE_DIR = ANALYSIS_DIR / "ml" / "models" / "xgboost_bdt_v6" / "plots"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
TARGET_DIR = THIS_DIR / "figs"

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
FIGURE_STEMS = [
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "feynman_diagram",
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    "pairing_validation",
# [ML] AUC / ROC are threshold-independent discrimination metrics; useful for checking class separation before relying on a fixed score cut in the fit.
    "roc_curve",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "d34_distribution",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "fit_templates",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "bdt_cut_scan",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
]

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
APPENDIX_WIDE_PLOTS = [
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "cutFlow",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
]

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
APPENDIX_PAIRED_PLOTS = [
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    "deltaZ_shape",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "Wstar_m_shape",
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    "recoil_m_afterZ_norm",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "Hcand_m_final_norm",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "cosTheta_miss_shape",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "visibleEnergy_shape",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
]

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
APPENDIX_PLOT_STEMS = [*APPENDIX_WIDE_PLOTS, *APPENDIX_PAIRED_PLOTS]

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
PLOT_LABELS = {
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "cutFlow": "Stacked cutflow yields",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "cosTheta_miss": r"$|\cos\theta_{\mathrm{miss}}|$",
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    "visibleEnergy": "Visible energy excluding the selected lepton",
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    "Wstar_m": "Reconstructed hadronic W* candidate mass",
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    "Hcand_m_final": "Reconstructed Higgs-candidate mass after the final recoil cut",
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    "recoil_m_afterZ": "Recoil mass after the Z-mass cut",
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    "deltaZ": r"$|m_{jj}-m_Z|$ from the Z-priority pairing",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
}


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def caption_for_plot(stem: str) -> str:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if stem == "cutFlow":
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        return "Stacked event yields across the sequential event selection."
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    if stem == "deltaZ_shape":
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        return r"Unit-area comparison of $|m_{jj}-m_Z|$, showing how the Z-priority pairing concentrates the signal near the on-shell Z mass."
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if stem == "Wstar_m_shape":
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        return r"Unit-area comparison of the reconstructed $W^*$ mass, illustrating the broad off-shell signal structure relative to the diboson backgrounds."
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    if stem == "recoil_m_afterZ_norm":
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        return "Unit-area recoil-mass comparison after the Z-mass requirement, highlighting the Higgs recoil peak used in the final event selection."
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if stem == "Hcand_m_final_norm":
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        return "Unit-area Higgs-candidate mass comparison after the final recoil selection."
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if stem == "cosTheta_miss_shape":
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        return r"Signal-versus-diboson shape comparison of $|\cos\theta_{\mathrm{miss}}|$, which helps suppress forward missing-momentum topologies."
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if stem == "visibleEnergy_shape":
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        return "Signal-versus-diboson comparison of the visible energy excluding the selected lepton, probing the semi-leptonic event balance."
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    raise KeyError(f"Unsupported appendix plot stem: {stem}")


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def write_appendix_tex(tex_path: Path) -> None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines: list[str] = []
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append("% Auto-generated by paper/sync_paper_figures.py")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(r"\clearpage")

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for stem in APPENDIX_WIDE_PLOTS:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        lines.append(r"\begin{figure}[p]")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        lines.append(r"  \centering")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        lines.append(rf"  \includegraphics[width=0.92\textwidth]{{figs/plots_lvqq/{stem}.pdf}}")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        lines.append(rf"  \caption{{{caption_for_plot(stem)}}}")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        lines.append(rf"  \label{{fig:appendix:{stem}}}")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        lines.append(r"\end{figure}")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        lines.append("")

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    paired = list(APPENDIX_PAIRED_PLOTS)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for idx in range(0, len(paired), 2):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        left = paired[idx]
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        right = paired[idx + 1] if idx + 1 < len(paired) else None
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        lines.append(r"\begin{figure}[p]")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        lines.append(r"  \centering")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        lines.append(r"  \begin{minipage}[t]{0.48\textwidth}")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        lines.append(r"    \centering")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        lines.append(rf"    \includegraphics[width=\textwidth]{{figs/plots_lvqq/{left}.pdf}}")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        lines.append(rf"    \par\smallskip{{\footnotesize {caption_for_plot(left)}}}")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        lines.append(r"  \end{minipage}")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        if right is not None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            lines.append(r"  \hfill")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            lines.append(r"  \begin{minipage}[t]{0.48\textwidth}")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            lines.append(r"    \centering")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            lines.append(rf"    \includegraphics[width=\textwidth]{{figs/plots_lvqq/{right}.pdf}}")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            lines.append(rf"    \par\smallskip{{\footnotesize {caption_for_plot(right)}}}")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            lines.append(r"  \end{minipage}")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        lines.append(r"\end{figure}")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        lines.append("")

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    tex_path.write_text("\n".join(lines) + "\n")


# [Workflow] Main orchestrator for this module; executes the full chain for this script only.
def main() -> None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    appendix_dir = TARGET_DIR / "plots_lvqq"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    appendix_dir.mkdir(parents=True, exist_ok=True)

# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
    wanted_root_files = {f"{stem}{ext}" for stem in FIGURE_STEMS for ext in (".pdf", ".png")}
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for path in TARGET_DIR.iterdir():
# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
        if path.is_file() and path.name not in wanted_root_files:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            path.unlink()

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    wanted_appendix_files = {f"{stem}.pdf" for stem in APPENDIX_PLOT_STEMS}
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for path in appendix_dir.glob("*.pdf"):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        if path.name not in wanted_appendix_files:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            path.unlink()

# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    missing: list[str] = []
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for stem in FIGURE_STEMS:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        for ext in (".pdf", ".png"):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            src = SOURCE_DIR / f"{stem}{ext}"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            dst = TARGET_DIR / src.name
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            if src.exists():
# [Packaging] Assemble only curated artifacts for reproducible paper build and prevent stale unrelated outputs from contaminating figures.
                shutil.copy2(src, dst)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            elif ext == ".pdf":
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
                missing.append(src.name)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    appendix_source_dir = ANALYSIS_DIR / "plots_lvqq"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for stem in APPENDIX_PLOT_STEMS:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        src = appendix_source_dir / f"{stem}.pdf"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        dst = appendix_dir / src.name
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        if src.exists():
# [Packaging] Assemble only curated artifacts for reproducible paper build and prevent stale unrelated outputs from contaminating figures.
            shutil.copy2(src, dst)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        else:
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
            missing.append(str(src.relative_to(ANALYSIS_DIR)))

# [Packaging] Assemble only curated artifacts for reproducible paper build and prevent stale unrelated outputs from contaminating figures.
    write_appendix_tex(THIS_DIR / "appendix_plots.tex")

# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    if missing:
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        missing_text = ", ".join(sorted(missing))
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        raise SystemExit(f"Missing required paper figure(s): {missing_text}")

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print(f"Synced paper figures to {TARGET_DIR}")


# [Entry] Module entry point for direct execution from CLI.
if __name__ == "__main__":
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    main()
