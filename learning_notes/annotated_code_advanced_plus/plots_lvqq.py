#!/usr/bin/env python3
# Diagnostic plotting layer for cutflow and variable distributions, producing paper-ready stacked/normalized comparisons.
#
# This is a line-by-line annotated rewrite for learning and review.
# The executable logic remains unchanged; only explanatory comments were added.

"""
Plotting script for H->WW->lvqq analysis
Produces paper-style plots with stacked backgrounds and signal overlay
"""

# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import ROOT
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import os
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import sys

# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
from ml_config import SIGNAL_SAMPLES, ZH_OTHER_SAMPLES

# Suppress ROOT info messages
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
ROOT.gROOT.SetBatch(True)
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
ROOT.gErrorIgnoreLevel = ROOT.kWarning

# ============================================================
# Configuration
# ============================================================

# [Context] Supporting line for the active lvqq analysis stage.
inputDir = "output/h_hww_lvqq/histmaker/ecm240/"
# [Context] Supporting line for the active lvqq analysis stage.
outputDir = "plots_lvqq/"

# Integrated luminosity (pb^-1)
# [Context] Supporting line for the active lvqq analysis stage.
intLumi = 10.8e6  # 10.8 ab^-1 at 240 GeV

# qq flavors to merge into one "Z/gamma->qq" entry for plotting
# [Workflow] Configuration binding; this line defines a stable contract across modules.
QQ_MERGE = ["wz3p6_ee_uu_ecm240", "wz3p6_ee_dd_ecm240", "wz3p6_ee_cc_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
            "wz3p6_ee_ss_ecm240", "wz3p6_ee_bb_ecm240"]

# [Workflow] Configuration binding; this line defines a stable contract across modules.
MERGED_GROUPS = {
# [Context] Supporting line for the active lvqq analysis stage.
    "wz3p6_ee_qq_ecm240": QQ_MERGE,
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_hadZH_HWW_ecm240": SIGNAL_SAMPLES,
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_hadZH_Hbb_ecm240": [sample for sample in ZH_OTHER_SAMPLES if "_Hbb_" in sample],
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_hadZH_Htautau_ecm240": [sample for sample in ZH_OTHER_SAMPLES if "_Htautau_" in sample],
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_hadZH_Hgg_ecm240": [sample for sample in ZH_OTHER_SAMPLES if "_Hgg_" in sample],
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_hadZH_Hcc_ecm240": [sample for sample in ZH_OTHER_SAMPLES if "_Hcc_" in sample],
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_hadZH_HZZ_ecm240": [sample for sample in ZH_OTHER_SAMPLES if "_HZZ_" in sample],
# [Context] Supporting line for the active lvqq analysis stage.
}

# Process definitions: (filename, label, color, isSignal)
# [Context] Supporting line for the active lvqq analysis stage.
processes = [
    # Backgrounds (will be stacked, order matters: bottom to top)
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ("wz3p6_ee_tautau_ecm240", "#tau#tau", ROOT.kGray + 1, False),
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ("wzp6_ee_hadZH_HZZ_ecm240", "ZH(ZZ)", ROOT.kCyan - 7, False),
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ("wzp6_ee_hadZH_Hcc_ecm240", "ZH(cc)", ROOT.kCyan - 3, False),
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ("wzp6_ee_hadZH_Hgg_ecm240", "ZH(gg)", ROOT.kCyan + 1, False),
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ("wzp6_ee_hadZH_Htautau_ecm240", "ZH(#tau#tau)", ROOT.kCyan + 3, False),
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ("wzp6_ee_hadZH_Hbb_ecm240", "ZH(bb)", ROOT.kTeal - 7, False),
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ("wz3p6_ee_qq_ecm240", "Z/#gamma#rightarrowqq", ROOT.kGreen + 2, False),
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ("p8_ee_ZZ_ecm240", "ZZ", ROOT.kAzure + 1, False),
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ("p8_ee_WW_ecm240", "WW", ROOT.kOrange - 3, False),
    # Signal (summed over all hadronic-Z production modes)
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ("wzp6_ee_hadZH_HWW_ecm240", "ZH (H#rightarrowWW)", ROOT.kRed + 1, True),
# [Context] Supporting line for the active lvqq analysis stage.
]

# Histograms to plot: (name, xtitle, rebin, xmin, xmax, logy)
# [Context] Supporting line for the active lvqq analysis stage.
histograms = [
# [Context] Supporting line for the active lvqq analysis stage.
    ("cutFlow", "Cut stage", 1, -0.5, 8.5, True),
# [Context] Supporting line for the active lvqq analysis stage.
    ("lepton_p", "Lepton momentum [GeV]", 4, 0, 150, False),
# [Context] Supporting line for the active lvqq analysis stage.
    ("lepton_iso", "Lepton isolation", 2, 0, 1, False),
# [Context] Supporting line for the active lvqq analysis stage.
    ("missingEnergy_e", "Missing energy [GeV]", 4, 0, 150, False),
# [Context] Supporting line for the active lvqq analysis stage.
    ("missingEnergy_p", "Missing momentum [GeV]", 4, 0, 150, False),
# [Context] Supporting line for the active lvqq analysis stage.
    ("missingMass", "Missing mass [GeV]", 4, 0, 240, False),
# [Context] Supporting line for the active lvqq analysis stage.
    ("cosTheta_miss", "|cos(#theta_{miss})|", 1, 0, 1, False),
# [Context] Supporting line for the active lvqq analysis stage.
    ("visibleEnergy", "Visible energy (no lepton) [GeV]", 4, 0, 250, False),
# [Context] Supporting line for the active lvqq analysis stage.
    ("njets", "Number of jets", 1, 0, 10, True),
# [Context] Supporting line for the active lvqq analysis stage.
    ("jet0_p", "Jet 0 momentum [GeV]", 4, 0, 120, False),
# [Context] Supporting line for the active lvqq analysis stage.
    ("jet1_p", "Jet 1 momentum [GeV]", 4, 0, 120, False),
# [Context] Supporting line for the active lvqq analysis stage.
    ("jet2_p", "Jet 2 momentum [GeV]", 4, 0, 120, False),
# [Context] Supporting line for the active lvqq analysis stage.
    ("jet3_p", "Jet 3 momentum [GeV]", 4, 0, 120, False),
# [Context] Supporting line for the active lvqq analysis stage.
    ("Zcand_m", "m_{Z cand} [GeV]", 4, 0, 200, False),
# [Context] Supporting line for the active lvqq analysis stage.
    ("Wstar_m", "m_{W*} [GeV]", 4, 0, 150, False),  # W* is off-shell, expect ~40 GeV
# [Context] Supporting line for the active lvqq analysis stage.
    ("Wlep_m", "m_{W_{lep}} [GeV]", 4, 0, 200, False),
# [Context] Supporting line for the active lvqq analysis stage.
    ("Hcand_m", "m_{H cand} [GeV]", 4, 0, 300, False),
# [Context] Supporting line for the active lvqq analysis stage.
    ("Hcand_m_afterZ", "m_{H cand} (after Z cut) [GeV]", 4, 0, 300, False),
# [Context] Supporting line for the active lvqq analysis stage.
    ("Hcand_m_final", "m_{H cand} (final) [GeV]", 4, 0, 300, False),
# [Context] Supporting line for the active lvqq analysis stage.
    ("recoil_m", "Recoil mass [GeV]", 4, 50, 200, False),
# [Context] Supporting line for the active lvqq analysis stage.
    ("recoil_m_afterZ", "Recoil mass (after Z cut) [GeV]", 4, 50, 200, False),
# [Context] Supporting line for the active lvqq analysis stage.
    ("deltaZ", "|m_{jj} - m_{Z}| [GeV]", 4, 0, 50, False),
# [Context] Supporting line for the active lvqq analysis stage.
]

# [Workflow] Configuration binding; this line defines a stable contract across modules.
CUT_LABELS = [
# [Context] Supporting line for the active lvqq analysis stage.
    "All",
# [Context] Supporting line for the active lvqq analysis stage.
    "1lep p>20",
# [Context] Supporting line for the active lvqq analysis stage.
    "ISO",
# [Context] Supporting line for the active lvqq analysis stage.
    "Veto p>5",
# [Context] Supporting line for the active lvqq analysis stage.
    "MET E>20",
# [Context] Supporting line for the active lvqq analysis stage.
    "4jets",
# [Context] Supporting line for the active lvqq analysis stage.
    "Z win",
# [Context] Supporting line for the active lvqq analysis stage.
    "Recoil",
# [Context] Supporting line for the active lvqq analysis stage.
]
# [Workflow] Configuration binding; this line defines a stable contract across modules.
CUT_IDS = [f"cut{i}" for i in range(len(CUT_LABELS))]
# [Workflow] Configuration binding; this line defines a stable contract across modules.
PERCENT_COL_WIDTH = 12

# ============================================================
# Style settings
# ============================================================

# [Workflow] plots_lvqq.py function setStyle: modularize one operation for deterministic pipeline control.
def setStyle():
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ROOT.gStyle.SetOptStat(0)
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ROOT.gStyle.SetOptTitle(0)
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ROOT.gStyle.SetPadTickX(1)
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ROOT.gStyle.SetPadTickY(1)
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ROOT.gStyle.SetHistLineWidth(2)
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ROOT.gStyle.SetLegendBorderSize(0)
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ROOT.gStyle.SetLegendFillColor(0)
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ROOT.gStyle.SetLegendFont(42)
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ROOT.gStyle.SetLegendTextSize(0.035)
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ROOT.gStyle.SetPadLeftMargin(0.14)
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ROOT.gStyle.SetPadRightMargin(0.05)
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ROOT.gStyle.SetPadTopMargin(0.08)
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ROOT.gStyle.SetPadBottomMargin(0.12)
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ROOT.gStyle.SetTitleFont(42, "XYZ")
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ROOT.gStyle.SetTitleSize(0.045, "XYZ")
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ROOT.gStyle.SetLabelFont(42, "XYZ")
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ROOT.gStyle.SetLabelSize(0.04, "XYZ")
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    ROOT.gStyle.SetTitleOffset(1.3, "Y")

# ============================================================
# Helper functions
# ============================================================

# [Workflow] plots_lvqq.py function getHist: modularize one operation for deterministic pipeline control.
def getHist(filename, histname):
    """Load histogram from file (already scaled by framework).

    Some entries are logical groups summed over multiple processed samples.
    """
# [Context] Supporting line for the active lvqq analysis stage.
    if filename in MERGED_GROUPS:
# [Context] Supporting line for the active lvqq analysis stage.
        h_merged = None
# [Context] Supporting line for the active lvqq analysis stage.
        for sample_name in MERGED_GROUPS[filename]:
# [Context] Supporting line for the active lvqq analysis stage.
            h = getHist(sample_name, histname)
# [Context] Supporting line for the active lvqq analysis stage.
            if h is None:
# [Context] Supporting line for the active lvqq analysis stage.
                continue
# [Context] Supporting line for the active lvqq analysis stage.
            if h_merged is None:
# [Context] Supporting line for the active lvqq analysis stage.
                h_merged = h.Clone(f"{histname}_{filename}_merged")
# [Context] Supporting line for the active lvqq analysis stage.
                h_merged.SetDirectory(0)
# [Context] Supporting line for the active lvqq analysis stage.
            else:
# [Context] Supporting line for the active lvqq analysis stage.
                h_merged.Add(h)
# [Workflow] Return value hands the constructed object/metric to the next module stage.
        return h_merged

# [Context] Supporting line for the active lvqq analysis stage.
    filepath = os.path.join(inputDir, filename + ".root")
# [Context] Supporting line for the active lvqq analysis stage.
    if not os.path.exists(filepath):
# [Context] Supporting line for the active lvqq analysis stage.
        print(f"Warning: {filepath} not found")
# [Workflow] Return value hands the constructed object/metric to the next module stage.
        return None

# [I/O] Open/write ROOT containers for high-throughput HEP data exchange.
    f = ROOT.TFile.Open(filepath)
# [Context] Supporting line for the active lvqq analysis stage.
    h = f.Get(histname)
# [Context] Supporting line for the active lvqq analysis stage.
    if not h:
# [Context] Supporting line for the active lvqq analysis stage.
        print(f"Warning: {histname} not found in {filepath}")
# [Context] Supporting line for the active lvqq analysis stage.
        f.Close()
# [Workflow] Return value hands the constructed object/metric to the next module stage.
        return None

# [Context] Supporting line for the active lvqq analysis stage.
    h.SetDirectory(0)
# [Context] Supporting line for the active lvqq analysis stage.
    f.Close()

    # NOTE: Histograms from fccanalysis with doScale=True are ALREADY
    # normalized to xsec * intLumi. Do NOT scale again here!

# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return h


# [Workflow] plots_lvqq.py function collectCutflowData: modularize one operation for deterministic pipeline control.
def collectCutflowData():
    """Collect cutflow yields for all configured processes."""

# [Context] Supporting line for the active lvqq analysis stage.
    ncuts = len(CUT_LABELS)
# [Context] Supporting line for the active lvqq analysis stage.
    process_rows = []
# [Context] Supporting line for the active lvqq analysis stage.
    process_eff_rows = []
# [Context] Supporting line for the active lvqq analysis stage.
    total_sig = [0.0] * ncuts
# [Context] Supporting line for the active lvqq analysis stage.
    total_bkg = [0.0] * ncuts

# [Context] Supporting line for the active lvqq analysis stage.
    for fname, label, color, isSignal in processes:
# [Context] Supporting line for the active lvqq analysis stage.
        h = getHist(fname, "cutFlow")
# [Context] Supporting line for the active lvqq analysis stage.
        if h is None:
# [Context] Supporting line for the active lvqq analysis stage.
            continue

# [Context] Supporting line for the active lvqq analysis stage.
        values = [h.GetBinContent(i + 1) for i in range(ncuts)]
# [Context] Supporting line for the active lvqq analysis stage.
        process_rows.append((label, values, isSignal))

# [Context] Supporting line for the active lvqq analysis stage.
        base = values[0] if values and values[0] > 0 else 0.0
# [Context] Supporting line for the active lvqq analysis stage.
        eff_values = [100.0 * val / base if base > 0 else None for val in values]
# [Context] Supporting line for the active lvqq analysis stage.
        process_eff_rows.append((label, eff_values, isSignal))

# [Context] Supporting line for the active lvqq analysis stage.
        for i, val in enumerate(values):
# [Context] Supporting line for the active lvqq analysis stage.
            if isSignal:
# [Context] Supporting line for the active lvqq analysis stage.
                total_sig[i] += val
# [Context] Supporting line for the active lvqq analysis stage.
            else:
# [Context] Supporting line for the active lvqq analysis stage.
                total_bkg[i] += val

# [Physics] Event- and significance-like metrics for sensitivity interpretation.
    s_over_b = []
# [Physics] Event- and significance-like metrics for sensitivity interpretation.
    s_over_sqrt_b = []
# [Context] Supporting line for the active lvqq analysis stage.
    for s, b in zip(total_sig, total_bkg):
# [Context] Supporting line for the active lvqq analysis stage.
        if b > 0:
# [Physics] Event- and significance-like metrics for sensitivity interpretation.
            s_over_b.append(s / b)
# [Physics] Event- and significance-like metrics for sensitivity interpretation.
            s_over_sqrt_b.append(s / (b ** 0.5))
# [Context] Supporting line for the active lvqq analysis stage.
        else:
# [Physics] Event- and significance-like metrics for sensitivity interpretation.
            s_over_b.append(None)
# [Physics] Event- and significance-like metrics for sensitivity interpretation.
            s_over_sqrt_b.append(None)

# [Context] Supporting line for the active lvqq analysis stage.
    sig_base = total_sig[0] if total_sig and total_sig[0] > 0 else 0.0
# [Context] Supporting line for the active lvqq analysis stage.
    bkg_base = total_bkg[0] if total_bkg and total_bkg[0] > 0 else 0.0
# [Context] Supporting line for the active lvqq analysis stage.
    total_sig_eff = [100.0 * val / sig_base if sig_base > 0 else None for val in total_sig]
# [Context] Supporting line for the active lvqq analysis stage.
    total_bkg_eff = [100.0 * val / bkg_base if bkg_base > 0 else None for val in total_bkg]

# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return {
# [Context] Supporting line for the active lvqq analysis stage.
        "cut_labels": CUT_LABELS,
# [Context] Supporting line for the active lvqq analysis stage.
        "cut_ids": CUT_IDS,
# [Context] Supporting line for the active lvqq analysis stage.
        "process_rows": process_rows,
# [Context] Supporting line for the active lvqq analysis stage.
        "process_eff_rows": process_eff_rows,
# [Context] Supporting line for the active lvqq analysis stage.
        "total_sig": total_sig,
# [Context] Supporting line for the active lvqq analysis stage.
        "total_bkg": total_bkg,
# [Context] Supporting line for the active lvqq analysis stage.
        "total_sig_eff": total_sig_eff,
# [Context] Supporting line for the active lvqq analysis stage.
        "total_bkg_eff": total_bkg_eff,
# [Physics] Event- and significance-like metrics for sensitivity interpretation.
        "s_over_b": s_over_b,
# [Physics] Event- and significance-like metrics for sensitivity interpretation.
        "s_over_sqrt_b": s_over_sqrt_b,
# [Context] Supporting line for the active lvqq analysis stage.
    }


# [Workflow] plots_lvqq.py function _format_table_row: modularize one operation for deterministic pipeline control.
def _format_table_row(label, values, float_fmt=".0f"):
# [Context] Supporting line for the active lvqq analysis stage.
    row = f"{label:<25}"
# [Context] Supporting line for the active lvqq analysis stage.
    for val in values:
# [Context] Supporting line for the active lvqq analysis stage.
        if val is None:
# [Context] Supporting line for the active lvqq analysis stage.
            row += f"{'--':>10}"
# [Context] Supporting line for the active lvqq analysis stage.
        else:
# [Context] Supporting line for the active lvqq analysis stage.
            row += f"{val:>10{float_fmt}}"
# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return row


# [Workflow] plots_lvqq.py function _format_percent_row: modularize one operation for deterministic pipeline control.
def _format_percent_row(label, values):
# [Context] Supporting line for the active lvqq analysis stage.
    row = f"{label:<25}"
# [Context] Supporting line for the active lvqq analysis stage.
    for val in values:
# [Context] Supporting line for the active lvqq analysis stage.
        if val is None:
# [Context] Supporting line for the active lvqq analysis stage.
            row += f"{'--':>{PERCENT_COL_WIDTH}}"
# [Context] Supporting line for the active lvqq analysis stage.
        else:
# [Context] Supporting line for the active lvqq analysis stage.
            row += f"{f'{val:.2f}%':>{PERCENT_COL_WIDTH}}"
# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return row


# [Workflow] plots_lvqq.py function _format_cut_header: modularize one operation for deterministic pipeline control.
def _format_cut_header(cut_keys, value_width=10):
# [Context] Supporting line for the active lvqq analysis stage.
    header = f"{'Process':<25}"
# [Context] Supporting line for the active lvqq analysis stage.
    for key in cut_keys:
# [Context] Supporting line for the active lvqq analysis stage.
        header += f"{key:>{value_width}}"
# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return header


# [Workflow] plots_lvqq.py function writeCutflowText: modularize one operation for deterministic pipeline control.
def writeCutflowText(summary):
    """Write cutflow table to a plain-text file."""

# [Context] Supporting line for the active lvqq analysis stage.
    os.makedirs(outputDir, exist_ok=True)
# [Context] Supporting line for the active lvqq analysis stage.
    outpath = os.path.join(outputDir, "cutFlow_cutflow.txt")

# [Context] Supporting line for the active lvqq analysis stage.
    lines = []
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append("=" * 80)
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append("CUTFLOW TABLE (normalized to 10.8 ab^-1)")
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append("=" * 80)

# [Context] Supporting line for the active lvqq analysis stage.
    header = f"{'Process':<25}"
# [Context] Supporting line for the active lvqq analysis stage.
    for lab in summary["cut_labels"]:
# [Context] Supporting line for the active lvqq analysis stage.
        header += f"{lab:>10}"
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append(header)
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append("-" * 95)

# [Context] Supporting line for the active lvqq analysis stage.
    for label, values, isSignal in summary["process_rows"]:
# [Context] Supporting line for the active lvqq analysis stage.
        lines.append(_format_table_row(label, values, ".0f"))

# [Context] Supporting line for the active lvqq analysis stage.
    lines.append("-" * 95)
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append(_format_table_row("Total Signal", summary["total_sig"], ".1f"))
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append(_format_table_row("Total Background", summary["total_bkg"], ".1f"))
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append("-" * 95)
# [Physics] Event- and significance-like metrics for sensitivity interpretation.
    lines.append(_format_table_row("S/B", summary["s_over_b"], ".4f"))
# [Physics] Event- and significance-like metrics for sensitivity interpretation.
    lines.append(_format_table_row("S/sqrt(B)", summary["s_over_sqrt_b"], ".1f"))
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append("=" * 95)

# [Context] Supporting line for the active lvqq analysis stage.
    with open(outpath, "w", encoding="ascii") as f:
# [Context] Supporting line for the active lvqq analysis stage.
        f.write("\n".join(lines) + "\n")


# [Workflow] plots_lvqq.py function writeCutflowLatex: modularize one operation for deterministic pipeline control.
def writeCutflowLatex(summary):
    """Write cutflow table to a LaTeX file."""

# [Context] Supporting line for the active lvqq analysis stage.
    os.makedirs(outputDir, exist_ok=True)
# [Context] Supporting line for the active lvqq analysis stage.
    outpath = os.path.join(outputDir, "cutFlow_cutflow.tex")

# [Context] Supporting line for the active lvqq analysis stage.
    cols = "l" + "r" * len(summary["cut_labels"])
# [Context] Supporting line for the active lvqq analysis stage.
    lines = [
# [Context] Supporting line for the active lvqq analysis stage.
        r"\begin{tabular}{" + cols + r"}",
# [Context] Supporting line for the active lvqq analysis stage.
        r"\hline",
# [Context] Supporting line for the active lvqq analysis stage.
    ]

# [Context] Supporting line for the active lvqq analysis stage.
    header = ["Process"] + summary["cut_labels"]
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append(" & ".join(header) + r" \\")
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append(r"\hline")

# [Context] Supporting line for the active lvqq analysis stage.
    for label, values, isSignal in summary["process_rows"]:
# [Context] Supporting line for the active lvqq analysis stage.
        row = [label] + [f"{val:.0f}" for val in values]
# [Context] Supporting line for the active lvqq analysis stage.
        lines.append(" & ".join(row) + r" \\")

# [Context] Supporting line for the active lvqq analysis stage.
    lines.append(r"\hline")
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append(" & ".join(["Total Signal"] + [f"{v:.1f}" for v in summary["total_sig"]]) + r" \\")
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append(" & ".join(["Total Background"] + [f"{v:.1f}" for v in summary["total_bkg"]]) + r" \\")
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append(r"\hline")
# [Physics] Event- and significance-like metrics for sensitivity interpretation.
    lines.append(" & ".join(["S/B"] + [("--" if v is None else f"{v:.4f}") for v in summary["s_over_b"]]) + r" \\")
# [Physics] Event- and significance-like metrics for sensitivity interpretation.
    lines.append(" & ".join(["S/$\\sqrt{B}$"] + [("--" if v is None else f"{v:.1f}") for v in summary["s_over_sqrt_b"]]) + r" \\")
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append(r"\hline")
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append(r"\end{tabular}")

# [Context] Supporting line for the active lvqq analysis stage.
    with open(outpath, "w", encoding="ascii") as f:
# [Context] Supporting line for the active lvqq analysis stage.
        f.write("\n".join(lines) + "\n")


# [Workflow] plots_lvqq.py function makeCutflowPdf: modularize one operation for deterministic pipeline control.
def makeCutflowPdf(summary):
    """Render a cutflow table as a PDF, similar to standard FCCAnalysis outputs."""

# [Context] Supporting line for the active lvqq analysis stage.
    os.makedirs(outputDir, exist_ok=True)
# [Context] Supporting line for the active lvqq analysis stage.
    outpath = os.path.join(outputDir, "cutFlow_cutflow.pdf")

# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    c = ROOT.TCanvas("cutflow_table", "", 1800, 700)
# [Context] Supporting line for the active lvqq analysis stage.
    c.cd()

# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    title = ROOT.TLatex()
# [Context] Supporting line for the active lvqq analysis stage.
    title.SetNDC()
# [Context] Supporting line for the active lvqq analysis stage.
    title.SetTextFont(42)
# [Context] Supporting line for the active lvqq analysis stage.
    title.SetTextSize(0.035)
# [Context] Supporting line for the active lvqq analysis stage.
    title.DrawLatex(0.03, 0.95, "Cutflow table, normalized to 10.8 ab^{-1}")

# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    latex = ROOT.TLatex()
# [Context] Supporting line for the active lvqq analysis stage.
    latex.SetNDC()
# [Context] Supporting line for the active lvqq analysis stage.
    latex.SetTextFont(42)
# [Context] Supporting line for the active lvqq analysis stage.
    latex.SetTextSize(0.024)

# [Context] Supporting line for the active lvqq analysis stage.
    x_process = 0.03
# [Context] Supporting line for the active lvqq analysis stage.
    x_start = 0.32
# [Context] Supporting line for the active lvqq analysis stage.
    x_end = 0.97
# [Context] Supporting line for the active lvqq analysis stage.
    ncuts = len(summary["cut_labels"])
# [Context] Supporting line for the active lvqq analysis stage.
    x_cuts = [x_start + i * (x_end - x_start) / max(1, ncuts - 1) for i in range(ncuts)]

# [Context] Supporting line for the active lvqq analysis stage.
    y = 0.88
# [Context] Supporting line for the active lvqq analysis stage.
    latex.SetTextAlign(13)
# [Context] Supporting line for the active lvqq analysis stage.
    latex.DrawLatex(x_process, y, "Process")
# [Context] Supporting line for the active lvqq analysis stage.
    latex.SetTextAlign(23)
# [Context] Supporting line for the active lvqq analysis stage.
    for x, label in zip(x_cuts, summary["cut_labels"]):
# [Context] Supporting line for the active lvqq analysis stage.
        latex.DrawLatex(x, y, label)

# [Context] Supporting line for the active lvqq analysis stage.
    rows = []
# [Context] Supporting line for the active lvqq analysis stage.
    for label, values, isSignal in summary["process_rows"]:
# [Context] Supporting line for the active lvqq analysis stage.
        rows.append((label, values))
# [Context] Supporting line for the active lvqq analysis stage.
    rows.append(("Total Signal", summary["total_sig"]))
# [Context] Supporting line for the active lvqq analysis stage.
    rows.append(("Total Background", summary["total_bkg"]))
# [Physics] Event- and significance-like metrics for sensitivity interpretation.
    rows.append(("S/B", summary["s_over_b"]))
# [Physics] Event- and significance-like metrics for sensitivity interpretation.
    rows.append(("S/sqrt(B)", summary["s_over_sqrt_b"]))

# [Context] Supporting line for the active lvqq analysis stage.
    y -= 0.07
# [Context] Supporting line for the active lvqq analysis stage.
    for label, values in rows:
# [Context] Supporting line for the active lvqq analysis stage.
        latex.SetTextAlign(13)
# [Context] Supporting line for the active lvqq analysis stage.
        latex.DrawLatex(x_process, y, label)
# [Context] Supporting line for the active lvqq analysis stage.
        latex.SetTextAlign(23)
# [Context] Supporting line for the active lvqq analysis stage.
        for x, val in zip(x_cuts, values):
# [Context] Supporting line for the active lvqq analysis stage.
            if val is None:
# [Context] Supporting line for the active lvqq analysis stage.
                txt = "--"
# [Context] Supporting line for the active lvqq analysis stage.
            elif label in ("S/B",):
# [Context] Supporting line for the active lvqq analysis stage.
                txt = f"{val:.4f}"
# [Context] Supporting line for the active lvqq analysis stage.
            elif label in ("S/sqrt(B)",):
# [Context] Supporting line for the active lvqq analysis stage.
                txt = f"{val:.1f}"
# [Context] Supporting line for the active lvqq analysis stage.
            elif label.startswith("Total"):
# [Context] Supporting line for the active lvqq analysis stage.
                txt = f"{val:.1f}"
# [Context] Supporting line for the active lvqq analysis stage.
            else:
# [Context] Supporting line for the active lvqq analysis stage.
                txt = f"{val:.0f}"
# [Context] Supporting line for the active lvqq analysis stage.
            latex.DrawLatex(x, y, txt)
# [Context] Supporting line for the active lvqq analysis stage.
        y -= 0.06

# [Context] Supporting line for the active lvqq analysis stage.
    c.SaveAs(outpath)
# [Context] Supporting line for the active lvqq analysis stage.
    c.SaveAs(outpath.replace(".pdf", ".png"))
# [Context] Supporting line for the active lvqq analysis stage.
    c.Close()


# [Workflow] plots_lvqq.py function writeCutflowEfficiencyText: modularize one operation for deterministic pipeline control.
def writeCutflowEfficiencyText(summary):
    """Write cumulative cut efficiencies in percent to a plain-text file."""

# [Context] Supporting line for the active lvqq analysis stage.
    os.makedirs(outputDir, exist_ok=True)
# [Context] Supporting line for the active lvqq analysis stage.
    outpath = os.path.join(outputDir, "cutFlow_efficiency.txt")

# [Context] Supporting line for the active lvqq analysis stage.
    rule = "-" * (25 + PERCENT_COL_WIDTH * len(summary["cut_ids"]))
# [Context] Supporting line for the active lvqq analysis stage.
    lines = []
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append("=" * 80)
# [Cutflow] Stage-tracking variable for acceptance and efficiency accounting.
    lines.append("CUTFLOW EFFICIENCY TABLE [%], cumulative w.r.t. cut0 (All)")
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append("=" * 80)
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append(_format_cut_header(summary["cut_ids"], PERCENT_COL_WIDTH))
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append(rule)

# [Context] Supporting line for the active lvqq analysis stage.
    for label, values, isSignal in summary["process_eff_rows"]:
# [Context] Supporting line for the active lvqq analysis stage.
        lines.append(_format_percent_row(label, values))

# [Context] Supporting line for the active lvqq analysis stage.
    lines.append(rule)
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append(_format_percent_row("Total Signal eff", summary["total_sig_eff"]))
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append(_format_percent_row("Total Bkg eff", summary["total_bkg_eff"]))
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append("=" * len(rule))
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append("")
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append("Cut definitions:")
# [Context] Supporting line for the active lvqq analysis stage.
    for cut_id, label in zip(summary["cut_ids"], summary["cut_labels"]):
# [Context] Supporting line for the active lvqq analysis stage.
        lines.append(f"  {cut_id}: {label}")

# [Context] Supporting line for the active lvqq analysis stage.
    with open(outpath, "w", encoding="ascii") as f:
# [Context] Supporting line for the active lvqq analysis stage.
        f.write("\n".join(lines) + "\n")

# [Workflow] plots_lvqq.py function writeCutflowEfficiencyLatex: modularize one operation for deterministic pipeline control.
def writeCutflowEfficiencyLatex(summary):
    """Write cumulative cut efficiencies in percent to a LaTeX file."""

# [Context] Supporting line for the active lvqq analysis stage.
    os.makedirs(outputDir, exist_ok=True)
# [Context] Supporting line for the active lvqq analysis stage.
    outpath = os.path.join(outputDir, "cutFlow_efficiency.tex")

# [Context] Supporting line for the active lvqq analysis stage.
    cols = "l" + "r" * len(summary["cut_ids"])
# [Context] Supporting line for the active lvqq analysis stage.
    ncols = len(summary["cut_ids"]) + 1
# [Context] Supporting line for the active lvqq analysis stage.
    lines = [
# [Context] Supporting line for the active lvqq analysis stage.
        r"\begin{tabular}{" + cols + r"}",
# [Context] Supporting line for the active lvqq analysis stage.
        r"\hline",
# [Context] Supporting line for the active lvqq analysis stage.
    ]

# [Context] Supporting line for the active lvqq analysis stage.
    header = ["Process"] + summary["cut_ids"]
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append(" & ".join(header) + r" \\")
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append(r"\hline")

# [Context] Supporting line for the active lvqq analysis stage.
    for label, values, isSignal in summary["process_eff_rows"]:
# [Context] Supporting line for the active lvqq analysis stage.
        row = [label] + [("--" if v is None else f"{v:.2f}\\%") for v in values]
# [Context] Supporting line for the active lvqq analysis stage.
        lines.append(" & ".join(row) + r" \\")

# [Context] Supporting line for the active lvqq analysis stage.
    lines.append(r"\hline")
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append(" & ".join(["Total Signal eff"] + [("--" if v is None else f"{v:.2f}\\%") for v in summary["total_sig_eff"]]) + r" \\")
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append(" & ".join(["Total Bkg eff"] + [("--" if v is None else f"{v:.2f}\\%") for v in summary["total_bkg_eff"]]) + r" \\")
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append(r"\hline")
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append(rf"\multicolumn{{{ncols}}}{{l}}{{Cut definitions:}} \\")
# [Context] Supporting line for the active lvqq analysis stage.
    for cut_id, label in zip(summary["cut_ids"], summary["cut_labels"]):
# [Context] Supporting line for the active lvqq analysis stage.
        safe_label = label.replace("_", r"\_").replace("%", r"\%")
# [Context] Supporting line for the active lvqq analysis stage.
        lines.append(rf"\multicolumn{{{ncols}}}{{l}}{{{cut_id}: {safe_label}}} \\")
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append(r"\hline")
# [Context] Supporting line for the active lvqq analysis stage.
    lines.append(r"\end{tabular}")

# [Context] Supporting line for the active lvqq analysis stage.
    with open(outpath, "w", encoding="ascii") as f:
# [Context] Supporting line for the active lvqq analysis stage.
        f.write("\n".join(lines) + "\n")

# [Workflow] plots_lvqq.py function makeCutflowEfficiencyPdf: modularize one operation for deterministic pipeline control.
def makeCutflowEfficiencyPdf(summary):
    """Render a cumulative cut-efficiency table as a PDF."""

# [Context] Supporting line for the active lvqq analysis stage.
    os.makedirs(outputDir, exist_ok=True)
# [Context] Supporting line for the active lvqq analysis stage.
    outpath = os.path.join(outputDir, "cutFlow_efficiency.pdf")

# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    c = ROOT.TCanvas("cutflow_eff_table", "", 1800, 850)
# [Context] Supporting line for the active lvqq analysis stage.
    c.cd()

# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    title = ROOT.TLatex()
# [Context] Supporting line for the active lvqq analysis stage.
    title.SetNDC()
# [Context] Supporting line for the active lvqq analysis stage.
    title.SetTextFont(42)
# [Context] Supporting line for the active lvqq analysis stage.
    title.SetTextSize(0.035)
# [Cutflow] Stage-tracking variable for acceptance and efficiency accounting.
    title.DrawLatex(0.03, 0.95, "Cutflow efficiencies [%], cumulative w.r.t. cut0 (All)")

# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    latex = ROOT.TLatex()
# [Context] Supporting line for the active lvqq analysis stage.
    latex.SetNDC()
# [Context] Supporting line for the active lvqq analysis stage.
    latex.SetTextFont(42)
# [Context] Supporting line for the active lvqq analysis stage.
    latex.SetTextSize(0.024)

# [Context] Supporting line for the active lvqq analysis stage.
    x_process = 0.03
# [Context] Supporting line for the active lvqq analysis stage.
    x_start = 0.32
# [Context] Supporting line for the active lvqq analysis stage.
    x_end = 0.97
# [Context] Supporting line for the active lvqq analysis stage.
    ncuts = len(summary["cut_ids"])
# [Context] Supporting line for the active lvqq analysis stage.
    x_cuts = [x_start + i * (x_end - x_start) / max(1, ncuts - 1) for i in range(ncuts)]

# [Context] Supporting line for the active lvqq analysis stage.
    y = 0.88
# [Context] Supporting line for the active lvqq analysis stage.
    latex.SetTextAlign(13)
# [Context] Supporting line for the active lvqq analysis stage.
    latex.DrawLatex(x_process, y, "Process")
# [Context] Supporting line for the active lvqq analysis stage.
    latex.SetTextAlign(23)
# [Context] Supporting line for the active lvqq analysis stage.
    for x, label in zip(x_cuts, summary["cut_ids"]):
# [Context] Supporting line for the active lvqq analysis stage.
        latex.DrawLatex(x, y, label)

# [Context] Supporting line for the active lvqq analysis stage.
    rows = []
# [Context] Supporting line for the active lvqq analysis stage.
    for label, values, isSignal in summary["process_eff_rows"]:
# [Context] Supporting line for the active lvqq analysis stage.
        rows.append((label, values))
# [Context] Supporting line for the active lvqq analysis stage.
    rows.append(("Total Signal eff", summary["total_sig_eff"]))
# [Context] Supporting line for the active lvqq analysis stage.
    rows.append(("Total Bkg eff", summary["total_bkg_eff"]))

# [Context] Supporting line for the active lvqq analysis stage.
    y -= 0.07
# [Context] Supporting line for the active lvqq analysis stage.
    for label, values in rows:
# [Context] Supporting line for the active lvqq analysis stage.
        latex.SetTextAlign(13)
# [Context] Supporting line for the active lvqq analysis stage.
        latex.DrawLatex(x_process, y, label)
# [Context] Supporting line for the active lvqq analysis stage.
        latex.SetTextAlign(23)
# [Context] Supporting line for the active lvqq analysis stage.
        for x, val in zip(x_cuts, values):
# [Context] Supporting line for the active lvqq analysis stage.
            txt = "--" if val is None else f"{val:.2f}%"
# [Context] Supporting line for the active lvqq analysis stage.
            latex.DrawLatex(x, y, txt)
# [Context] Supporting line for the active lvqq analysis stage.
        y -= 0.06

# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    legend = ROOT.TLatex()
# [Context] Supporting line for the active lvqq analysis stage.
    legend.SetNDC()
# [Context] Supporting line for the active lvqq analysis stage.
    legend.SetTextFont(42)
# [Context] Supporting line for the active lvqq analysis stage.
    legend.SetTextSize(0.020)
# [Context] Supporting line for the active lvqq analysis stage.
    legend.SetTextAlign(13)
# [Context] Supporting line for the active lvqq analysis stage.
    legend.DrawLatex(0.03, 0.24, "Cut definitions:")
# [Context] Supporting line for the active lvqq analysis stage.
    for idx, (cut_id, label) in enumerate(zip(summary["cut_ids"], summary["cut_labels"])):
# [Context] Supporting line for the active lvqq analysis stage.
        x = 0.03 + (idx % 2) * 0.44
# [Context] Supporting line for the active lvqq analysis stage.
        yy = 0.20 - (idx // 2) * 0.04
# [Context] Supporting line for the active lvqq analysis stage.
        legend.DrawLatex(x, yy, f"{cut_id}: {label}")

# [Context] Supporting line for the active lvqq analysis stage.
    c.SaveAs(outpath)
# [Context] Supporting line for the active lvqq analysis stage.
    c.SaveAs(outpath.replace(".pdf", ".png"))
# [Context] Supporting line for the active lvqq analysis stage.
    c.Close()

# [Workflow] plots_lvqq.py function makePlot: modularize one operation for deterministic pipeline control.
def makePlot(histname, xtitle, rebin, xmin, xmax, logy):
    """Create a single plot with stacked backgrounds and signal overlay"""

    # Create canvas
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    c = ROOT.TCanvas("c", "", 800, 700)
# [Context] Supporting line for the active lvqq analysis stage.
    c.cd()

# [Context] Supporting line for the active lvqq analysis stage.
    if logy:
# [Context] Supporting line for the active lvqq analysis stage.
        c.SetLogy()

    # Prepare histograms
# [Context] Supporting line for the active lvqq analysis stage.
    bkg_hists = []
# [Context] Supporting line for the active lvqq analysis stage.
    sig_hists = []

# [Context] Supporting line for the active lvqq analysis stage.
    for fname, label, color, isSignal in processes:
# [Context] Supporting line for the active lvqq analysis stage.
        h = getHist(fname, histname)
# [Context] Supporting line for the active lvqq analysis stage.
        if h is None:
# [Context] Supporting line for the active lvqq analysis stage.
            continue

# [Context] Supporting line for the active lvqq analysis stage.
        if rebin > 1:
# [Context] Supporting line for the active lvqq analysis stage.
            h.Rebin(rebin)

# [Context] Supporting line for the active lvqq analysis stage.
        h.SetLineColor(color)
# [Context] Supporting line for the active lvqq analysis stage.
        h.SetLineWidth(2)

# [Context] Supporting line for the active lvqq analysis stage.
        if isSignal:
# [Context] Supporting line for the active lvqq analysis stage.
            h.SetFillStyle(0)
# [Context] Supporting line for the active lvqq analysis stage.
            sig_hists.append((h, label, color))
# [Context] Supporting line for the active lvqq analysis stage.
        else:
# [Context] Supporting line for the active lvqq analysis stage.
            h.SetFillColor(color)
# [Context] Supporting line for the active lvqq analysis stage.
            h.SetFillStyle(1001)
# [Context] Supporting line for the active lvqq analysis stage.
            bkg_hists.append((h, label, color))

# [Context] Supporting line for the active lvqq analysis stage.
    if not bkg_hists and not sig_hists:
# [Context] Supporting line for the active lvqq analysis stage.
        print(f"Warning: No histograms found for {histname}")
# [Workflow] Return value hands the constructed object/metric to the next module stage.
        return

    # Create THStack for backgrounds
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    hs = ROOT.THStack("hs", "")
# [Context] Supporting line for the active lvqq analysis stage.
    for h, label, color in bkg_hists:
# [Context] Supporting line for the active lvqq analysis stage.
        hs.Add(h)

    # Sum signals for combined overlay
# [Context] Supporting line for the active lvqq analysis stage.
    h_sig_sum = None
# [Context] Supporting line for the active lvqq analysis stage.
    for h, label, color in sig_hists:
# [Context] Supporting line for the active lvqq analysis stage.
        if h_sig_sum is None:
# [Context] Supporting line for the active lvqq analysis stage.
            h_sig_sum = h.Clone("h_sig_sum")
# [Context] Supporting line for the active lvqq analysis stage.
        else:
# [Context] Supporting line for the active lvqq analysis stage.
            h_sig_sum.Add(h)

# [Context] Supporting line for the active lvqq analysis stage.
    if h_sig_sum:
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
        h_sig_sum.SetLineColor(ROOT.kRed+1)
# [Context] Supporting line for the active lvqq analysis stage.
        h_sig_sum.SetLineWidth(3)
# [Context] Supporting line for the active lvqq analysis stage.
        h_sig_sum.SetFillStyle(0)

    # Determine y-axis range
# [Context] Supporting line for the active lvqq analysis stage.
    ymax = 0
# [Context] Supporting line for the active lvqq analysis stage.
    if hs.GetNhists() > 0:
# [Context] Supporting line for the active lvqq analysis stage.
        ymax = max(ymax, hs.GetMaximum())
# [Context] Supporting line for the active lvqq analysis stage.
    if h_sig_sum:
# [Context] Supporting line for the active lvqq analysis stage.
        ymax = max(ymax, h_sig_sum.GetMaximum())

# [Context] Supporting line for the active lvqq analysis stage.
    if logy:
# [Context] Supporting line for the active lvqq analysis stage.
        ymin = 0.1
# [Context] Supporting line for the active lvqq analysis stage.
        ymax *= 50
# [Context] Supporting line for the active lvqq analysis stage.
    else:
# [Context] Supporting line for the active lvqq analysis stage.
        ymin = 0
# [Context] Supporting line for the active lvqq analysis stage.
        ymax *= 1.5

    # Draw
# [Context] Supporting line for the active lvqq analysis stage.
    if hs.GetNhists() > 0:
# [Context] Supporting line for the active lvqq analysis stage.
        hs.Draw("HIST")
# [Context] Supporting line for the active lvqq analysis stage.
        hs.GetXaxis().SetTitle(xtitle)
# [Context] Supporting line for the active lvqq analysis stage.
        hs.GetYaxis().SetTitle("Events")
# [Context] Supporting line for the active lvqq analysis stage.
        hs.GetXaxis().SetRangeUser(xmin, xmax)
# [Context] Supporting line for the active lvqq analysis stage.
        hs.SetMinimum(ymin)
# [Context] Supporting line for the active lvqq analysis stage.
        hs.SetMaximum(ymax)
# [Context] Supporting line for the active lvqq analysis stage.
        hs.GetXaxis().SetTitleSize(0.045)
# [Context] Supporting line for the active lvqq analysis stage.
        hs.GetYaxis().SetTitleSize(0.045)
# [Context] Supporting line for the active lvqq analysis stage.
        hs.GetXaxis().SetLabelSize(0.04)
# [Context] Supporting line for the active lvqq analysis stage.
        hs.GetYaxis().SetLabelSize(0.04)
# [Context] Supporting line for the active lvqq analysis stage.
        hs.GetYaxis().SetTitleOffset(1.3)

# [Context] Supporting line for the active lvqq analysis stage.
    if h_sig_sum:
# [Context] Supporting line for the active lvqq analysis stage.
        h_sig_sum.Draw("HIST SAME")

    # Legend
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    leg = ROOT.TLegend(0.60, 0.65, 0.92, 0.88)
# [Context] Supporting line for the active lvqq analysis stage.
    leg.SetTextSize(0.032)

# [Context] Supporting line for the active lvqq analysis stage.
    if h_sig_sum:
# [Context] Supporting line for the active lvqq analysis stage.
        leg.AddEntry(h_sig_sum, "Signal (ZH, H#rightarrowWW)", "l")

    # Add backgrounds in reverse order (top to bottom in legend)
# [Context] Supporting line for the active lvqq analysis stage.
    for h, label, color in reversed(bkg_hists):
# [Context] Supporting line for the active lvqq analysis stage.
        leg.AddEntry(h, label, "f")

# [Context] Supporting line for the active lvqq analysis stage.
    leg.Draw()

    # CMS-style label
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    latex = ROOT.TLatex()
# [Context] Supporting line for the active lvqq analysis stage.
    latex.SetNDC()
# [Context] Supporting line for the active lvqq analysis stage.
    latex.SetTextFont(42)
# [Context] Supporting line for the active lvqq analysis stage.
    latex.SetTextSize(0.04)
# [Context] Supporting line for the active lvqq analysis stage.
    latex.DrawLatex(0.14, 0.93, "#bf{FCC-ee} #it{Simulation}")
# [Context] Supporting line for the active lvqq analysis stage.
    latex.SetTextSize(0.035)
# [Context] Supporting line for the active lvqq analysis stage.
    latex.DrawLatex(0.70, 0.93, "#sqrt{s} = 240 GeV, 10.8 ab^{-1}")

# [Context] Supporting line for the active lvqq analysis stage.
    os.makedirs(outputDir, exist_ok=True)
# [Context] Supporting line for the active lvqq analysis stage.
    c.SaveAs(os.path.join(outputDir, f"{histname}.pdf"))
# [Context] Supporting line for the active lvqq analysis stage.
    c.SaveAs(os.path.join(outputDir, f"{histname}.png"))

# [Context] Supporting line for the active lvqq analysis stage.
    c.Close()


# [Workflow] plots_lvqq.py function makeCutflowTable: modularize one operation for deterministic pipeline control.
def makeCutflowTable():
    """Print cutflow table and save text/tex/pdf outputs."""

# [Context] Supporting line for the active lvqq analysis stage.
    summary = collectCutflowData()

# [Context] Supporting line for the active lvqq analysis stage.
    print("\n" + "=" * 80)
# [Context] Supporting line for the active lvqq analysis stage.
    print("CUTFLOW TABLE (normalized to 10.8 ab^-1)")
# [Context] Supporting line for the active lvqq analysis stage.
    print("=" * 80)
# [Context] Supporting line for the active lvqq analysis stage.
    header = f"{'Process':<25}"
# [Context] Supporting line for the active lvqq analysis stage.
    for lab in summary["cut_labels"]:
# [Context] Supporting line for the active lvqq analysis stage.
        header += f"{lab:>10}"
# [Context] Supporting line for the active lvqq analysis stage.
    print(header)
# [Context] Supporting line for the active lvqq analysis stage.
    print("-" * 95)

# [Context] Supporting line for the active lvqq analysis stage.
    for label, values, isSignal in summary["process_rows"]:
# [Context] Supporting line for the active lvqq analysis stage.
        print(_format_table_row(label, values, ".0f"))

# [Context] Supporting line for the active lvqq analysis stage.
    print("-" * 95)
# [Context] Supporting line for the active lvqq analysis stage.
    print(_format_table_row("Total Signal", summary["total_sig"], ".1f"))
# [Context] Supporting line for the active lvqq analysis stage.
    print(_format_table_row("Total Background", summary["total_bkg"], ".1f"))
# [Context] Supporting line for the active lvqq analysis stage.
    print("-" * 95)
# [Physics] Event- and significance-like metrics for sensitivity interpretation.
    print(_format_table_row("S/B", summary["s_over_b"], ".4f"))
# [Physics] Event- and significance-like metrics for sensitivity interpretation.
    print(_format_table_row("S/sqrt(B)", summary["s_over_sqrt_b"], ".1f"))
# [Context] Supporting line for the active lvqq analysis stage.
    print("=" * 95 + "\n")

# [Context] Supporting line for the active lvqq analysis stage.
    print("\n" + "=" * 80)
# [Cutflow] Stage-tracking variable for acceptance and efficiency accounting.
    print("CUTFLOW EFFICIENCY TABLE [%], cumulative w.r.t. cut0 (All)")
# [Context] Supporting line for the active lvqq analysis stage.
    print("=" * 80)
# [Context] Supporting line for the active lvqq analysis stage.
    rule = "-" * (25 + PERCENT_COL_WIDTH * len(summary["cut_ids"]))
# [Context] Supporting line for the active lvqq analysis stage.
    print(_format_cut_header(summary["cut_ids"], PERCENT_COL_WIDTH))
# [Context] Supporting line for the active lvqq analysis stage.
    print(rule)

# [Context] Supporting line for the active lvqq analysis stage.
    for label, values, isSignal in summary["process_eff_rows"]:
# [Context] Supporting line for the active lvqq analysis stage.
        print(_format_percent_row(label, values))

# [Context] Supporting line for the active lvqq analysis stage.
    print(rule)
# [Context] Supporting line for the active lvqq analysis stage.
    print(_format_percent_row("Total Signal eff", summary["total_sig_eff"]))
# [Context] Supporting line for the active lvqq analysis stage.
    print(_format_percent_row("Total Bkg eff", summary["total_bkg_eff"]))
# [Context] Supporting line for the active lvqq analysis stage.
    print("=" * len(rule))
# [Context] Supporting line for the active lvqq analysis stage.
    print("Cut definitions:")
# [Context] Supporting line for the active lvqq analysis stage.
    for cut_id, label in zip(summary["cut_ids"], summary["cut_labels"]):
# [Context] Supporting line for the active lvqq analysis stage.
        print(f"  {cut_id}: {label}")
# [Context] Supporting line for the active lvqq analysis stage.
    print()

# [Context] Supporting line for the active lvqq analysis stage.
    writeCutflowText(summary)
# [Context] Supporting line for the active lvqq analysis stage.
    writeCutflowLatex(summary)
# [Context] Supporting line for the active lvqq analysis stage.
    makeCutflowPdf(summary)
# [Context] Supporting line for the active lvqq analysis stage.
    writeCutflowEfficiencyText(summary)
# [Context] Supporting line for the active lvqq analysis stage.
    writeCutflowEfficiencyLatex(summary)
# [Context] Supporting line for the active lvqq analysis stage.
    makeCutflowEfficiencyPdf(summary)


# [Workflow] plots_lvqq.py function makeNormalizedPlot: modularize one operation for deterministic pipeline control.
def makeNormalizedPlot(histname, xtitle, rebin, xmin, xmax, logy=False):
    """Create normalized stacked plot (signal and background both normalized to unit area)"""

# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    c = ROOT.TCanvas("c", "", 800, 700)
# [Context] Supporting line for the active lvqq analysis stage.
    c.cd()
# [Context] Supporting line for the active lvqq analysis stage.
    if logy:
# [Context] Supporting line for the active lvqq analysis stage.
        c.SetLogy()

    # Prepare histograms
# [Context] Supporting line for the active lvqq analysis stage.
    bkg_hists = []
# [Context] Supporting line for the active lvqq analysis stage.
    sig_hists = []

# [Context] Supporting line for the active lvqq analysis stage.
    for fname, label, color, isSignal in processes:
# [Context] Supporting line for the active lvqq analysis stage.
        h = getHist(fname, histname)
# [Context] Supporting line for the active lvqq analysis stage.
        if h is None:
# [Context] Supporting line for the active lvqq analysis stage.
            continue

# [Context] Supporting line for the active lvqq analysis stage.
        if rebin > 1:
# [Context] Supporting line for the active lvqq analysis stage.
            h.Rebin(rebin)

# [Context] Supporting line for the active lvqq analysis stage.
        h.SetLineColor(color)
# [Context] Supporting line for the active lvqq analysis stage.
        h.SetLineWidth(2)

# [Context] Supporting line for the active lvqq analysis stage.
        if isSignal:
# [Context] Supporting line for the active lvqq analysis stage.
            h.SetFillStyle(0)
# [Context] Supporting line for the active lvqq analysis stage.
            sig_hists.append((h, label, color))
# [Context] Supporting line for the active lvqq analysis stage.
        else:
# [Context] Supporting line for the active lvqq analysis stage.
            h.SetFillColor(color)
# [Context] Supporting line for the active lvqq analysis stage.
            h.SetFillStyle(1001)
# [Context] Supporting line for the active lvqq analysis stage.
            bkg_hists.append((h, label, color))

# [Context] Supporting line for the active lvqq analysis stage.
    if not bkg_hists and not sig_hists:
# [Context] Supporting line for the active lvqq analysis stage.
        print(f"Warning: No histograms found for {histname}")
# [Workflow] Return value hands the constructed object/metric to the next module stage.
        return

    # Sum all backgrounds
# [Context] Supporting line for the active lvqq analysis stage.
    h_bkg_sum = None
# [Context] Supporting line for the active lvqq analysis stage.
    for h, label, color in bkg_hists:
# [Context] Supporting line for the active lvqq analysis stage.
        if h_bkg_sum is None:
# [Context] Supporting line for the active lvqq analysis stage.
            h_bkg_sum = h.Clone("h_bkg_sum")
# [Context] Supporting line for the active lvqq analysis stage.
        else:
# [Context] Supporting line for the active lvqq analysis stage.
            h_bkg_sum.Add(h)

    # Sum all signals
# [Context] Supporting line for the active lvqq analysis stage.
    h_sig_sum = None
# [Context] Supporting line for the active lvqq analysis stage.
    for h, label, color in sig_hists:
# [Context] Supporting line for the active lvqq analysis stage.
        if h_sig_sum is None:
# [Context] Supporting line for the active lvqq analysis stage.
            h_sig_sum = h.Clone("h_sig_sum")
# [Context] Supporting line for the active lvqq analysis stage.
        else:
# [Context] Supporting line for the active lvqq analysis stage.
            h_sig_sum.Add(h)

    # Normalize both to unit area
# [Context] Supporting line for the active lvqq analysis stage.
    if h_bkg_sum and h_bkg_sum.Integral() > 0:
# [Context] Supporting line for the active lvqq analysis stage.
        h_bkg_sum.Scale(1.0 / h_bkg_sum.Integral())
# [Context] Supporting line for the active lvqq analysis stage.
    if h_sig_sum and h_sig_sum.Integral() > 0:
# [Context] Supporting line for the active lvqq analysis stage.
        h_sig_sum.Scale(1.0 / h_sig_sum.Integral())

    # Style
# [Context] Supporting line for the active lvqq analysis stage.
    if h_bkg_sum:
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
        h_bkg_sum.SetFillColor(ROOT.kAzure+1)
# [Context] Supporting line for the active lvqq analysis stage.
        h_bkg_sum.SetFillStyle(3004)
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
        h_bkg_sum.SetLineColor(ROOT.kAzure+1)
# [Context] Supporting line for the active lvqq analysis stage.
        h_bkg_sum.SetLineWidth(2)

# [Context] Supporting line for the active lvqq analysis stage.
    if h_sig_sum:
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
        h_sig_sum.SetLineColor(ROOT.kRed+1)
# [Context] Supporting line for the active lvqq analysis stage.
        h_sig_sum.SetLineWidth(3)
# [Context] Supporting line for the active lvqq analysis stage.
        h_sig_sum.SetFillStyle(0)

    # Determine y-axis range
# [Context] Supporting line for the active lvqq analysis stage.
    ymax = 0
# [Context] Supporting line for the active lvqq analysis stage.
    if h_bkg_sum:
# [Context] Supporting line for the active lvqq analysis stage.
        ymax = max(ymax, h_bkg_sum.GetMaximum())
# [Context] Supporting line for the active lvqq analysis stage.
    if h_sig_sum:
# [Context] Supporting line for the active lvqq analysis stage.
        ymax = max(ymax, h_sig_sum.GetMaximum())

# [Context] Supporting line for the active lvqq analysis stage.
    if logy:
# [Context] Supporting line for the active lvqq analysis stage.
        ymin = 1e-4
# [Context] Supporting line for the active lvqq analysis stage.
        ymax *= 10
# [Context] Supporting line for the active lvqq analysis stage.
    else:
# [Context] Supporting line for the active lvqq analysis stage.
        ymin = 0
# [Context] Supporting line for the active lvqq analysis stage.
        ymax *= 1.4

    # Draw
# [Context] Supporting line for the active lvqq analysis stage.
    first = True
# [Context] Supporting line for the active lvqq analysis stage.
    if h_bkg_sum:
# [Context] Supporting line for the active lvqq analysis stage.
        h_bkg_sum.GetXaxis().SetTitle(xtitle)
# [Context] Supporting line for the active lvqq analysis stage.
        h_bkg_sum.GetYaxis().SetTitle("Normalized")
# [Context] Supporting line for the active lvqq analysis stage.
        h_bkg_sum.GetXaxis().SetRangeUser(xmin, xmax)
# [Context] Supporting line for the active lvqq analysis stage.
        h_bkg_sum.SetMinimum(ymin)
# [Context] Supporting line for the active lvqq analysis stage.
        h_bkg_sum.SetMaximum(ymax)
# [Context] Supporting line for the active lvqq analysis stage.
        h_bkg_sum.GetXaxis().SetTitleSize(0.045)
# [Context] Supporting line for the active lvqq analysis stage.
        h_bkg_sum.GetYaxis().SetTitleSize(0.045)
# [Context] Supporting line for the active lvqq analysis stage.
        h_bkg_sum.GetXaxis().SetLabelSize(0.04)
# [Context] Supporting line for the active lvqq analysis stage.
        h_bkg_sum.GetYaxis().SetLabelSize(0.04)
# [Context] Supporting line for the active lvqq analysis stage.
        h_bkg_sum.GetYaxis().SetTitleOffset(1.3)
# [Context] Supporting line for the active lvqq analysis stage.
        h_bkg_sum.Draw("HIST")
# [Context] Supporting line for the active lvqq analysis stage.
        first = False

# [Context] Supporting line for the active lvqq analysis stage.
    if h_sig_sum:
# [Context] Supporting line for the active lvqq analysis stage.
        if first:
# [Context] Supporting line for the active lvqq analysis stage.
            h_sig_sum.GetXaxis().SetTitle(xtitle)
# [Context] Supporting line for the active lvqq analysis stage.
            h_sig_sum.GetYaxis().SetTitle("Normalized")
# [Context] Supporting line for the active lvqq analysis stage.
            h_sig_sum.GetXaxis().SetRangeUser(xmin, xmax)
# [Context] Supporting line for the active lvqq analysis stage.
            h_sig_sum.SetMinimum(ymin)
# [Context] Supporting line for the active lvqq analysis stage.
            h_sig_sum.SetMaximum(ymax)
# [Context] Supporting line for the active lvqq analysis stage.
            h_sig_sum.GetXaxis().SetTitleSize(0.045)
# [Context] Supporting line for the active lvqq analysis stage.
            h_sig_sum.GetYaxis().SetTitleSize(0.045)
# [Context] Supporting line for the active lvqq analysis stage.
            h_sig_sum.GetXaxis().SetLabelSize(0.04)
# [Context] Supporting line for the active lvqq analysis stage.
            h_sig_sum.GetYaxis().SetLabelSize(0.04)
# [Context] Supporting line for the active lvqq analysis stage.
            h_sig_sum.GetYaxis().SetTitleOffset(1.3)
# [Context] Supporting line for the active lvqq analysis stage.
            h_sig_sum.Draw("HIST")
# [Context] Supporting line for the active lvqq analysis stage.
        else:
# [Context] Supporting line for the active lvqq analysis stage.
            h_sig_sum.Draw("HIST SAME")

    # Legend
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    leg = ROOT.TLegend(0.60, 0.75, 0.92, 0.88)
# [Context] Supporting line for the active lvqq analysis stage.
    leg.SetTextSize(0.032)
# [Context] Supporting line for the active lvqq analysis stage.
    if h_sig_sum:
# [Context] Supporting line for the active lvqq analysis stage.
        leg.AddEntry(h_sig_sum, "Signal (ZH, H#rightarrowWW)", "l")
# [Context] Supporting line for the active lvqq analysis stage.
    if h_bkg_sum:
# [Context] Supporting line for the active lvqq analysis stage.
        leg.AddEntry(h_bkg_sum, "Background (all)", "f")
# [Context] Supporting line for the active lvqq analysis stage.
    leg.Draw()

    # CMS-style label
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    latex = ROOT.TLatex()
# [Context] Supporting line for the active lvqq analysis stage.
    latex.SetNDC()
# [Context] Supporting line for the active lvqq analysis stage.
    latex.SetTextFont(42)
# [Context] Supporting line for the active lvqq analysis stage.
    latex.SetTextSize(0.04)
# [Context] Supporting line for the active lvqq analysis stage.
    latex.DrawLatex(0.14, 0.93, "#bf{FCC-ee} #it{Simulation} (normalized)")
# [Context] Supporting line for the active lvqq analysis stage.
    latex.SetTextSize(0.035)
# [Context] Supporting line for the active lvqq analysis stage.
    latex.DrawLatex(0.70, 0.93, "#sqrt{s} = 240 GeV")

# [Context] Supporting line for the active lvqq analysis stage.
    os.makedirs(outputDir, exist_ok=True)
# [Context] Supporting line for the active lvqq analysis stage.
    c.SaveAs(os.path.join(outputDir, f"{histname}_norm.pdf"))
# [Context] Supporting line for the active lvqq analysis stage.
    c.SaveAs(os.path.join(outputDir, f"{histname}_norm.png"))

# [Context] Supporting line for the active lvqq analysis stage.
    c.Close()


# [Workflow] plots_lvqq.py function makeComparisonPlot: modularize one operation for deterministic pipeline control.
def makeComparisonPlot(histname, xtitle, rebin, xmin, xmax):
    """Create shape comparison plot (normalized to unit area)"""

# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    c = ROOT.TCanvas("c", "", 800, 600)
# [Context] Supporting line for the active lvqq analysis stage.
    c.cd()

    # Only compare signal vs main backgrounds
# [Context] Supporting line for the active lvqq analysis stage.
    compare = [
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
        ("wzp6_ee_hadZH_HWW_ecm240", "Signal (ZH, H#rightarrowWW)", ROOT.kRed+1),
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
        ("p8_ee_WW_ecm240", "WW bkg", ROOT.kOrange-3),
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
        ("p8_ee_ZZ_ecm240", "ZZ bkg", ROOT.kAzure+1),
# [Context] Supporting line for the active lvqq analysis stage.
    ]

# [Context] Supporting line for the active lvqq analysis stage.
    hists = []
# [Context] Supporting line for the active lvqq analysis stage.
    for fname, label, color in compare:
# [Context] Supporting line for the active lvqq analysis stage.
        h = getHist(fname, histname)
# [Context] Supporting line for the active lvqq analysis stage.
        if h is None:
# [Context] Supporting line for the active lvqq analysis stage.
            continue

# [Context] Supporting line for the active lvqq analysis stage.
        if rebin > 1:
# [Context] Supporting line for the active lvqq analysis stage.
            h.Rebin(rebin)

        # Normalize to unit area
# [Context] Supporting line for the active lvqq analysis stage.
        if h.Integral() > 0:
# [Context] Supporting line for the active lvqq analysis stage.
            h.Scale(1.0 / h.Integral())

# [Context] Supporting line for the active lvqq analysis stage.
        h.SetLineColor(color)
# [Context] Supporting line for the active lvqq analysis stage.
        h.SetLineWidth(3)
# [Context] Supporting line for the active lvqq analysis stage.
        h.SetFillStyle(0)
# [Context] Supporting line for the active lvqq analysis stage.
        hists.append((h, label))

# [Context] Supporting line for the active lvqq analysis stage.
    if not hists:
# [Workflow] Return value hands the constructed object/metric to the next module stage.
        return

    # Find y-axis range
# [Context] Supporting line for the active lvqq analysis stage.
    ymax = max(h.GetMaximum() for h, _ in hists) * 1.4

    # Draw
# [Context] Supporting line for the active lvqq analysis stage.
    for i, (h, label) in enumerate(hists):
# [Context] Supporting line for the active lvqq analysis stage.
        h.GetXaxis().SetTitle(xtitle)
# [Context] Supporting line for the active lvqq analysis stage.
        h.GetYaxis().SetTitle("Normalized")
# [Context] Supporting line for the active lvqq analysis stage.
        h.GetXaxis().SetRangeUser(xmin, xmax)
# [Context] Supporting line for the active lvqq analysis stage.
        h.SetMaximum(ymax)
# [Context] Supporting line for the active lvqq analysis stage.
        h.SetMinimum(0)
# [Context] Supporting line for the active lvqq analysis stage.
        if i == 0:
# [Context] Supporting line for the active lvqq analysis stage.
            h.Draw("HIST")
# [Context] Supporting line for the active lvqq analysis stage.
        else:
# [Context] Supporting line for the active lvqq analysis stage.
            h.Draw("HIST SAME")

    # Legend
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    leg = ROOT.TLegend(0.60, 0.70, 0.92, 0.88)
# [Context] Supporting line for the active lvqq analysis stage.
    for h, label in hists:
# [Context] Supporting line for the active lvqq analysis stage.
        leg.AddEntry(h, label, "l")
# [Context] Supporting line for the active lvqq analysis stage.
    leg.Draw()

    # Label
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
    latex = ROOT.TLatex()
# [Context] Supporting line for the active lvqq analysis stage.
    latex.SetNDC()
# [Context] Supporting line for the active lvqq analysis stage.
    latex.SetTextFont(42)
# [Context] Supporting line for the active lvqq analysis stage.
    latex.SetTextSize(0.04)
# [Context] Supporting line for the active lvqq analysis stage.
    latex.DrawLatex(0.14, 0.93, "#bf{FCC-ee} #it{Simulation} (shape comparison)")

# [Context] Supporting line for the active lvqq analysis stage.
    os.makedirs(outputDir, exist_ok=True)
# [Context] Supporting line for the active lvqq analysis stage.
    c.SaveAs(os.path.join(outputDir, f"{histname}_shape.pdf"))
# [Context] Supporting line for the active lvqq analysis stage.
    c.SaveAs(os.path.join(outputDir, f"{histname}_shape.png"))

# [Context] Supporting line for the active lvqq analysis stage.
    c.Close()


# ============================================================
# Main
# ============================================================

# [Context] Supporting line for the active lvqq analysis stage.
if __name__ == "__main__":

# [Context] Supporting line for the active lvqq analysis stage.
    setStyle()

# [Context] Supporting line for the active lvqq analysis stage.
    print("=" * 60)
# [Context] Supporting line for the active lvqq analysis stage.
    print("H->WW->lvqq Analysis Plotting Script")
# [Context] Supporting line for the active lvqq analysis stage.
    print("=" * 60)
# [Context] Supporting line for the active lvqq analysis stage.
    print(f"Input directory:  {inputDir}")
# [Context] Supporting line for the active lvqq analysis stage.
    print(f"Output directory: {outputDir}")
# [Context] Supporting line for the active lvqq analysis stage.
    print(f"Luminosity:       {intLumi/1e6:.1f} ab^-1")
# [Context] Supporting line for the active lvqq analysis stage.
    print("=" * 60)

    # Check input directory
# [Context] Supporting line for the active lvqq analysis stage.
    if not os.path.exists(inputDir):
# [Context] Supporting line for the active lvqq analysis stage.
        print(f"ERROR: Input directory {inputDir} does not exist!")
# [Context] Supporting line for the active lvqq analysis stage.
        print("Please run the analysis first with:")
# [Context] Supporting line for the active lvqq analysis stage.
        print("  fccanalysis run h_hww_lvqq.py")
# [Context] Supporting line for the active lvqq analysis stage.
        sys.exit(1)

    # Make all stacked plots (unnormalized)
# [Context] Supporting line for the active lvqq analysis stage.
    print("\nGenerating stacked plots (unnormalized)...")
# [Context] Supporting line for the active lvqq analysis stage.
    for hname, xtitle, rebin, xmin, xmax, logy in histograms:
# [Context] Supporting line for the active lvqq analysis stage.
        print(f"  {hname}...")
# [Context] Supporting line for the active lvqq analysis stage.
        makePlot(hname, xtitle, rebin, xmin, xmax, logy)

    # Make normalized plots (signal vs background, both normalized to unit area)
# [Context] Supporting line for the active lvqq analysis stage.
    print("\nGenerating normalized plots...")
# [Context] Supporting line for the active lvqq analysis stage.
    norm_hists = [
# [Context] Supporting line for the active lvqq analysis stage.
        ("lepton_p", "Lepton momentum [GeV]", 4, 0, 150),
# [Context] Supporting line for the active lvqq analysis stage.
        ("lepton_iso", "Lepton isolation", 2, 0, 1),
# [Context] Supporting line for the active lvqq analysis stage.
        ("missingEnergy_e", "Missing energy [GeV]", 4, 0, 150),
# [Context] Supporting line for the active lvqq analysis stage.
        ("missingEnergy_p", "Missing momentum [GeV]", 4, 0, 150),
# [Context] Supporting line for the active lvqq analysis stage.
        ("missingMass", "Missing mass [GeV]", 4, 0, 240),
# [Context] Supporting line for the active lvqq analysis stage.
        ("cosTheta_miss", "|cos(#theta_{miss})|", 1, 0, 1),
# [Context] Supporting line for the active lvqq analysis stage.
        ("visibleEnergy", "Visible energy (no lepton) [GeV]", 4, 0, 250),
# [Context] Supporting line for the active lvqq analysis stage.
        ("jet0_p", "Jet 0 momentum [GeV]", 4, 0, 120),
# [Context] Supporting line for the active lvqq analysis stage.
        ("jet1_p", "Jet 1 momentum [GeV]", 4, 0, 120),
# [Context] Supporting line for the active lvqq analysis stage.
        ("jet2_p", "Jet 2 momentum [GeV]", 4, 0, 120),
# [Context] Supporting line for the active lvqq analysis stage.
        ("jet3_p", "Jet 3 momentum [GeV]", 4, 0, 120),
# [Context] Supporting line for the active lvqq analysis stage.
        ("Zcand_m", "m_{Z cand} [GeV]", 4, 0, 200),
# [Context] Supporting line for the active lvqq analysis stage.
        ("Wstar_m", "m_{W*} [GeV]", 4, 0, 150),
# [Context] Supporting line for the active lvqq analysis stage.
        ("Wlep_m", "m_{W_{lep}} [GeV]", 4, 0, 200),
# [Context] Supporting line for the active lvqq analysis stage.
        ("Hcand_m", "m_{H cand} [GeV]", 4, 50, 250),
# [Context] Supporting line for the active lvqq analysis stage.
        ("Hcand_m_afterZ", "m_{H cand} (after Z cut) [GeV]", 4, 50, 250),
# [Context] Supporting line for the active lvqq analysis stage.
        ("Hcand_m_final", "m_{H cand} (final) [GeV]", 4, 50, 250),
# [Context] Supporting line for the active lvqq analysis stage.
        ("recoil_m", "Recoil mass [GeV]", 4, 50, 200),
# [Context] Supporting line for the active lvqq analysis stage.
        ("recoil_m_afterZ", "Recoil mass (after Z cut) [GeV]", 4, 50, 200),
# [Context] Supporting line for the active lvqq analysis stage.
        ("deltaZ", "|m_{jj} - m_{Z}| [GeV]", 4, 0, 50),
# [Context] Supporting line for the active lvqq analysis stage.
    ]
# [Context] Supporting line for the active lvqq analysis stage.
    for hname, xtitle, rebin, xmin, xmax in norm_hists:
# [Context] Supporting line for the active lvqq analysis stage.
        print(f"  {hname}_norm...")
# [Context] Supporting line for the active lvqq analysis stage.
        makeNormalizedPlot(hname, xtitle, rebin, xmin, xmax)

    # Make shape comparison plots (signal vs WW vs ZZ separately)
# [Context] Supporting line for the active lvqq analysis stage.
    print("\nGenerating shape comparison plots...")
# [Context] Supporting line for the active lvqq analysis stage.
    shape_hists = [
# [Context] Supporting line for the active lvqq analysis stage.
        ("Zcand_m", "m_{Z cand} [GeV]", 4, 0, 200),
# [Context] Supporting line for the active lvqq analysis stage.
        ("Wstar_m", "m_{W*} [GeV]", 4, 0, 150),
# [Context] Supporting line for the active lvqq analysis stage.
        ("Hcand_m", "m_{H cand} [GeV]", 4, 50, 250),
# [Context] Supporting line for the active lvqq analysis stage.
        ("recoil_m", "Recoil mass [GeV]", 4, 50, 200),
# [Context] Supporting line for the active lvqq analysis stage.
        ("deltaZ", "|m_{jj} - m_{Z}| [GeV]", 4, 0, 50),
# [Context] Supporting line for the active lvqq analysis stage.
        ("lepton_p", "Lepton momentum [GeV]", 4, 0, 150),
# [Context] Supporting line for the active lvqq analysis stage.
        ("lepton_iso", "Lepton isolation", 2, 0, 1),
# [Context] Supporting line for the active lvqq analysis stage.
        ("missingEnergy_e", "Missing energy [GeV]", 4, 0, 150),
# [Context] Supporting line for the active lvqq analysis stage.
        ("missingEnergy_p", "Missing momentum [GeV]", 4, 0, 150),
# [Context] Supporting line for the active lvqq analysis stage.
        ("missingMass", "Missing mass [GeV]", 4, 0, 240),
# [Context] Supporting line for the active lvqq analysis stage.
        ("cosTheta_miss", "|cos(#theta_{miss})|", 1, 0, 1),
# [Context] Supporting line for the active lvqq analysis stage.
        ("visibleEnergy", "Visible energy (no lepton) [GeV]", 4, 0, 250),
# [Context] Supporting line for the active lvqq analysis stage.
        ("jet0_p", "Jet 0 momentum [GeV]", 4, 0, 120),
# [Context] Supporting line for the active lvqq analysis stage.
        ("jet1_p", "Jet 1 momentum [GeV]", 4, 0, 120),
# [Context] Supporting line for the active lvqq analysis stage.
        ("jet2_p", "Jet 2 momentum [GeV]", 4, 0, 120),
# [Context] Supporting line for the active lvqq analysis stage.
        ("jet3_p", "Jet 3 momentum [GeV]", 4, 0, 120),
# [Context] Supporting line for the active lvqq analysis stage.
    ]
# [Context] Supporting line for the active lvqq analysis stage.
    for hname, xtitle, rebin, xmin, xmax in shape_hists:
# [Context] Supporting line for the active lvqq analysis stage.
        print(f"  {hname}_shape...")
# [Context] Supporting line for the active lvqq analysis stage.
        makeComparisonPlot(hname, xtitle, rebin, xmin, xmax)

    # Print cutflow table
# [Context] Supporting line for the active lvqq analysis stage.
    makeCutflowTable()

# [Context] Supporting line for the active lvqq analysis stage.
    print(f"All plots saved to: {outputDir}")
# [Context] Supporting line for the active lvqq analysis stage.
    print("Done!")
