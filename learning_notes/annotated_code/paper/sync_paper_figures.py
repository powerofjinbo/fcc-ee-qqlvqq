# Annotated rewrite generated for: paper/sync_paper_figures.py
# L1 [Original comment]: #!/usr/bin/env python3
#!/usr/bin/env python3
# L2 [Executable statement]: """Collect the figures used by the paper into a single directory."""
"""Collect the figures used by the paper into a single directory."""
# L3 [Blank separator]: 

# L4 [Import statement]: from __future__ import annotations
from __future__ import annotations
# L5 [Blank separator]: 

# L6 [Import statement]: import shutil
import shutil
# L7 [Import statement]: from pathlib import Path
from pathlib import Path
# L8 [Blank separator]: 

# L9 [Blank separator]: 

# L10 [Executable statement]: THIS_DIR = Path(__file__).resolve().parent
THIS_DIR = Path(__file__).resolve().parent
# L11 [Executable statement]: ANALYSIS_DIR = THIS_DIR.parent
ANALYSIS_DIR = THIS_DIR.parent
# L12 [Executable statement]: SOURCE_DIR = ANALYSIS_DIR / "ml" / "models" / "xgboost_bdt_v6" / "plots"
SOURCE_DIR = ANALYSIS_DIR / "ml" / "models" / "xgboost_bdt_v6" / "plots"
# L13 [Executable statement]: TARGET_DIR = THIS_DIR / "figs"
TARGET_DIR = THIS_DIR / "figs"
# L14 [Blank separator]: 

# L15 [Executable statement]: FIGURE_STEMS = [
FIGURE_STEMS = [
# L16 [Executable statement]:     "feynman_diagram",
    "feynman_diagram",
# L17 [Executable statement]:     "pairing_validation",
    "pairing_validation",
# L18 [Executable statement]:     "roc_curve",
    "roc_curve",
# L19 [Executable statement]:     "d34_distribution",
    "d34_distribution",
# L20 [Executable statement]:     "fit_templates",
    "fit_templates",
# L21 [Executable statement]:     "bdt_cut_scan",
    "bdt_cut_scan",
# L22 [Executable statement]: ]
]
# L23 [Blank separator]: 

# L24 [Executable statement]: APPENDIX_WIDE_PLOTS = [
APPENDIX_WIDE_PLOTS = [
# L25 [Executable statement]:     "cutFlow",
    "cutFlow",
# L26 [Executable statement]: ]
]
# L27 [Blank separator]: 

# L28 [Executable statement]: APPENDIX_PAIRED_PLOTS = [
APPENDIX_PAIRED_PLOTS = [
# L29 [Executable statement]:     "deltaZ_shape",
    "deltaZ_shape",
# L30 [Executable statement]:     "Wstar_m_shape",
    "Wstar_m_shape",
# L31 [Executable statement]:     "recoil_m_afterZ_norm",
    "recoil_m_afterZ_norm",
# L32 [Executable statement]:     "Hcand_m_final_norm",
    "Hcand_m_final_norm",
# L33 [Executable statement]:     "cosTheta_miss_shape",
    "cosTheta_miss_shape",
# L34 [Executable statement]:     "visibleEnergy_shape",
    "visibleEnergy_shape",
# L35 [Executable statement]: ]
]
# L36 [Blank separator]: 

# L37 [Executable statement]: APPENDIX_PLOT_STEMS = [*APPENDIX_WIDE_PLOTS, *APPENDIX_PAIRED_PLOTS]
APPENDIX_PLOT_STEMS = [*APPENDIX_WIDE_PLOTS, *APPENDIX_PAIRED_PLOTS]
# L38 [Blank separator]: 

# L39 [Executable statement]: PLOT_LABELS = {
PLOT_LABELS = {
# L40 [Executable statement]:     "cutFlow": "Stacked cutflow yields",
    "cutFlow": "Stacked cutflow yields",
# L41 [Executable statement]:     "cosTheta_miss": r"$|\cos\theta_{\mathrm{miss}}|$",
    "cosTheta_miss": r"$|\cos\theta_{\mathrm{miss}}|$",
# L42 [Executable statement]:     "visibleEnergy": "Visible energy excluding the selected lepton",
    "visibleEnergy": "Visible energy excluding the selected lepton",
# L43 [Executable statement]:     "Wstar_m": "Reconstructed hadronic W* candidate mass",
    "Wstar_m": "Reconstructed hadronic W* candidate mass",
# L44 [Executable statement]:     "Hcand_m_final": "Reconstructed Higgs-candidate mass after the final recoil cut",
    "Hcand_m_final": "Reconstructed Higgs-candidate mass after the final recoil cut",
# L45 [Executable statement]:     "recoil_m_afterZ": "Recoil mass after the Z-mass cut",
    "recoil_m_afterZ": "Recoil mass after the Z-mass cut",
# L46 [Executable statement]:     "deltaZ": r"$|m_{jj}-m_Z|$ from the Z-priority pairing",
    "deltaZ": r"$|m_{jj}-m_Z|$ from the Z-priority pairing",
# L47 [Executable statement]: }
}
# L48 [Blank separator]: 

# L49 [Blank separator]: 

# L50 [Function definition]: def caption_for_plot(stem: str) -> str:
def caption_for_plot(stem: str) -> str:
# L51 [Conditional block]:     if stem == "cutFlow":
    if stem == "cutFlow":
# L52 [Function return]:         return "Stacked event yields across the sequential event selection."
        return "Stacked event yields across the sequential event selection."
# L53 [Conditional block]:     if stem == "deltaZ_shape":
    if stem == "deltaZ_shape":
# L54 [Function return]:         return r"Unit-area comparison of $|m_{jj}-m_Z|$, showing how the Z-priority pairing concentrates the signal near the on-shell Z mass."
        return r"Unit-area comparison of $|m_{jj}-m_Z|$, showing how the Z-priority pairing concentrates the signal near the on-shell Z mass."
# L55 [Conditional block]:     if stem == "Wstar_m_shape":
    if stem == "Wstar_m_shape":
# L56 [Function return]:         return r"Unit-area comparison of the reconstructed $W^*$ mass, illustrating the broad off-shell signal structure relative to the diboson backgrounds."
        return r"Unit-area comparison of the reconstructed $W^*$ mass, illustrating the broad off-shell signal structure relative to the diboson backgrounds."
# L57 [Conditional block]:     if stem == "recoil_m_afterZ_norm":
    if stem == "recoil_m_afterZ_norm":
# L58 [Function return]:         return "Unit-area recoil-mass comparison after the Z-mass requirement, highlighting the Higgs recoil peak used in the final event selection."
        return "Unit-area recoil-mass comparison after the Z-mass requirement, highlighting the Higgs recoil peak used in the final event selection."
# L59 [Conditional block]:     if stem == "Hcand_m_final_norm":
    if stem == "Hcand_m_final_norm":
# L60 [Function return]:         return "Unit-area Higgs-candidate mass comparison after the final recoil selection."
        return "Unit-area Higgs-candidate mass comparison after the final recoil selection."
# L61 [Conditional block]:     if stem == "cosTheta_miss_shape":
    if stem == "cosTheta_miss_shape":
# L62 [Function return]:         return r"Signal-versus-diboson shape comparison of $|\cos\theta_{\mathrm{miss}}|$, which helps suppress forward missing-momentum topologies."
        return r"Signal-versus-diboson shape comparison of $|\cos\theta_{\mathrm{miss}}|$, which helps suppress forward missing-momentum topologies."
# L63 [Conditional block]:     if stem == "visibleEnergy_shape":
    if stem == "visibleEnergy_shape":
# L64 [Function return]:         return "Signal-versus-diboson comparison of the visible energy excluding the selected lepton, probing the semi-leptonic event balance."
        return "Signal-versus-diboson comparison of the visible energy excluding the selected lepton, probing the semi-leptonic event balance."
# L65 [Executable statement]:     raise KeyError(f"Unsupported appendix plot stem: {stem}")
    raise KeyError(f"Unsupported appendix plot stem: {stem}")
# L66 [Blank separator]: 

# L67 [Blank separator]: 

# L68 [Function definition]: def write_appendix_tex(tex_path: Path) -> None:
def write_appendix_tex(tex_path: Path) -> None:
# L69 [Executable statement]:     lines: list[str] = []
    lines: list[str] = []
# L70 [Executable statement]:     lines.append("% Auto-generated by paper/sync_paper_figures.py")
    lines.append("% Auto-generated by paper/sync_paper_figures.py")
# L71 [Executable statement]:     lines.append(r"\clearpage")
    lines.append(r"\clearpage")
# L72 [Blank separator]: 

# L73 [Loop over iterable]:     for stem in APPENDIX_WIDE_PLOTS:
    for stem in APPENDIX_WIDE_PLOTS:
# L74 [Executable statement]:         lines.append(r"\begin{figure}[p]")
        lines.append(r"\begin{figure}[p]")
# L75 [Executable statement]:         lines.append(r"  \centering")
        lines.append(r"  \centering")
# L76 [Executable statement]:         lines.append(rf"  \includegraphics[width=0.92\textwidth]{{figs/plots_lvqq/{stem}.pdf}}")
        lines.append(rf"  \includegraphics[width=0.92\textwidth]{{figs/plots_lvqq/{stem}.pdf}}")
# L77 [Executable statement]:         lines.append(rf"  \caption{{{caption_for_plot(stem)}}}")
        lines.append(rf"  \caption{{{caption_for_plot(stem)}}}")
# L78 [Executable statement]:         lines.append(rf"  \label{{fig:appendix:{stem}}}")
        lines.append(rf"  \label{{fig:appendix:{stem}}}")
# L79 [Executable statement]:         lines.append(r"\end{figure}")
        lines.append(r"\end{figure}")
# L80 [Executable statement]:         lines.append("")
        lines.append("")
# L81 [Blank separator]: 

# L82 [Executable statement]:     paired = list(APPENDIX_PAIRED_PLOTS)
    paired = list(APPENDIX_PAIRED_PLOTS)
# L83 [Loop over iterable]:     for idx in range(0, len(paired), 2):
    for idx in range(0, len(paired), 2):
# L84 [Executable statement]:         left = paired[idx]
        left = paired[idx]
# L85 [Executable statement]:         right = paired[idx + 1] if idx + 1 < len(paired) else None
        right = paired[idx + 1] if idx + 1 < len(paired) else None
# L86 [Executable statement]:         lines.append(r"\begin{figure}[p]")
        lines.append(r"\begin{figure}[p]")
# L87 [Executable statement]:         lines.append(r"  \centering")
        lines.append(r"  \centering")
# L88 [Executable statement]:         lines.append(r"  \begin{minipage}[t]{0.48\textwidth}")
        lines.append(r"  \begin{minipage}[t]{0.48\textwidth}")
# L89 [Executable statement]:         lines.append(r"    \centering")
        lines.append(r"    \centering")
# L90 [Executable statement]:         lines.append(rf"    \includegraphics[width=\textwidth]{{figs/plots_lvqq/{left}.pdf}}")
        lines.append(rf"    \includegraphics[width=\textwidth]{{figs/plots_lvqq/{left}.pdf}}")
# L91 [Executable statement]:         lines.append(rf"    \par\smallskip{{\footnotesize {caption_for_plot(left)}}}")
        lines.append(rf"    \par\smallskip{{\footnotesize {caption_for_plot(left)}}}")
# L92 [Executable statement]:         lines.append(r"  \end{minipage}")
        lines.append(r"  \end{minipage}")
# L93 [Conditional block]:         if right is not None:
        if right is not None:
# L94 [Executable statement]:             lines.append(r"  \hfill")
            lines.append(r"  \hfill")
# L95 [Executable statement]:             lines.append(r"  \begin{minipage}[t]{0.48\textwidth}")
            lines.append(r"  \begin{minipage}[t]{0.48\textwidth}")
# L96 [Executable statement]:             lines.append(r"    \centering")
            lines.append(r"    \centering")
# L97 [Executable statement]:             lines.append(rf"    \includegraphics[width=\textwidth]{{figs/plots_lvqq/{right}.pdf}}")
            lines.append(rf"    \includegraphics[width=\textwidth]{{figs/plots_lvqq/{right}.pdf}}")
# L98 [Executable statement]:             lines.append(rf"    \par\smallskip{{\footnotesize {caption_for_plot(right)}}}")
            lines.append(rf"    \par\smallskip{{\footnotesize {caption_for_plot(right)}}}")
# L99 [Executable statement]:             lines.append(r"  \end{minipage}")
            lines.append(r"  \end{minipage}")
# L100 [Executable statement]:         lines.append(r"\end{figure}")
        lines.append(r"\end{figure}")
# L101 [Executable statement]:         lines.append("")
        lines.append("")
# L102 [Blank separator]: 

# L103 [Executable statement]:     tex_path.write_text("\n".join(lines) + "\n")
    tex_path.write_text("\n".join(lines) + "\n")
# L104 [Blank separator]: 

# L105 [Blank separator]: 

# L106 [Function definition]: def main() -> None:
def main() -> None:
# L107 [Executable statement]:     TARGET_DIR.mkdir(parents=True, exist_ok=True)
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
# L108 [Executable statement]:     appendix_dir = TARGET_DIR / "plots_lvqq"
    appendix_dir = TARGET_DIR / "plots_lvqq"
# L109 [Executable statement]:     appendix_dir.mkdir(parents=True, exist_ok=True)
    appendix_dir.mkdir(parents=True, exist_ok=True)
# L110 [Blank separator]: 

# L111 [Executable statement]:     wanted_root_files = {f"{stem}{ext}" for stem in FIGURE_STEMS for ext in (".pdf", ".png")}
    wanted_root_files = {f"{stem}{ext}" for stem in FIGURE_STEMS for ext in (".pdf", ".png")}
# L112 [Loop over iterable]:     for path in TARGET_DIR.iterdir():
    for path in TARGET_DIR.iterdir():
# L113 [Conditional block]:         if path.is_file() and path.name not in wanted_root_files:
        if path.is_file() and path.name not in wanted_root_files:
# L114 [Executable statement]:             path.unlink()
            path.unlink()
# L115 [Blank separator]: 

# L116 [Executable statement]:     wanted_appendix_files = {f"{stem}.pdf" for stem in APPENDIX_PLOT_STEMS}
    wanted_appendix_files = {f"{stem}.pdf" for stem in APPENDIX_PLOT_STEMS}
# L117 [Loop over iterable]:     for path in appendix_dir.glob("*.pdf"):
    for path in appendix_dir.glob("*.pdf"):
# L118 [Conditional block]:         if path.name not in wanted_appendix_files:
        if path.name not in wanted_appendix_files:
# L119 [Executable statement]:             path.unlink()
            path.unlink()
# L120 [Blank separator]: 

# L121 [Executable statement]:     missing: list[str] = []
    missing: list[str] = []
# L122 [Loop over iterable]:     for stem in FIGURE_STEMS:
    for stem in FIGURE_STEMS:
# L123 [Loop over iterable]:         for ext in (".pdf", ".png"):
        for ext in (".pdf", ".png"):
# L124 [Executable statement]:             src = SOURCE_DIR / f"{stem}{ext}"
            src = SOURCE_DIR / f"{stem}{ext}"
# L125 [Executable statement]:             dst = TARGET_DIR / src.name
            dst = TARGET_DIR / src.name
# L126 [Conditional block]:             if src.exists():
            if src.exists():
# L127 [Executable statement]:                 shutil.copy2(src, dst)
                shutil.copy2(src, dst)
# L128 [Else-if conditional]:             elif ext == ".pdf":
            elif ext == ".pdf":
# L129 [Executable statement]:                 missing.append(src.name)
                missing.append(src.name)
# L130 [Blank separator]: 

# L131 [Executable statement]:     appendix_source_dir = ANALYSIS_DIR / "plots_lvqq"
    appendix_source_dir = ANALYSIS_DIR / "plots_lvqq"
# L132 [Loop over iterable]:     for stem in APPENDIX_PLOT_STEMS:
    for stem in APPENDIX_PLOT_STEMS:
# L133 [Executable statement]:         src = appendix_source_dir / f"{stem}.pdf"
        src = appendix_source_dir / f"{stem}.pdf"
# L134 [Executable statement]:         dst = appendix_dir / src.name
        dst = appendix_dir / src.name
# L135 [Conditional block]:         if src.exists():
        if src.exists():
# L136 [Executable statement]:             shutil.copy2(src, dst)
            shutil.copy2(src, dst)
# L137 [Else branch]:         else:
        else:
# L138 [Executable statement]:             missing.append(str(src.relative_to(ANALYSIS_DIR)))
            missing.append(str(src.relative_to(ANALYSIS_DIR)))
# L139 [Blank separator]: 

# L140 [Executable statement]:     write_appendix_tex(THIS_DIR / "appendix_plots.tex")
    write_appendix_tex(THIS_DIR / "appendix_plots.tex")
# L141 [Blank separator]: 

# L142 [Conditional block]:     if missing:
    if missing:
# L143 [Executable statement]:         missing_text = ", ".join(sorted(missing))
        missing_text = ", ".join(sorted(missing))
# L144 [Executable statement]:         raise SystemExit(f"Missing required paper figure(s): {missing_text}")
        raise SystemExit(f"Missing required paper figure(s): {missing_text}")
# L145 [Blank separator]: 

# L146 [Runtime log output]:     print(f"Synced paper figures to {TARGET_DIR}")
    print(f"Synced paper figures to {TARGET_DIR}")
# L147 [Blank separator]: 

# L148 [Blank separator]: 

# L149 [Conditional block]: if __name__ == "__main__":
if __name__ == "__main__":
# L150 [Executable statement]:     main()
    main()
