#!/usr/bin/env python3
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
"""
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
Plotting script for H->WW->lvqq analysis
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
Produces paper-style plots with stacked backgrounds and signal overlay
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
"""

# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
import ROOT
# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
import os
# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
import sys

# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
from ml_config import SIGNAL_SAMPLES, ZH_OTHER_SAMPLES

# Suppress ROOT info messages
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
ROOT.gROOT.SetBatch(True)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
ROOT.gErrorIgnoreLevel = ROOT.kWarning

# ============================================================
# Configuration
# ============================================================

# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
inputDir = "output/h_hww_lvqq/histmaker/ecm240/"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
outputDir = "plots_lvqq/"

# Integrated luminosity (pb^-1)
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
intLumi = 10.8e6  # 10.8 ab^-1 at 240 GeV

# qq flavors to merge into one "Z/gamma->qq" entry for plotting
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
QQ_MERGE = ["wz3p6_ee_uu_ecm240", "wz3p6_ee_dd_ecm240", "wz3p6_ee_cc_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
            "wz3p6_ee_ss_ecm240", "wz3p6_ee_bb_ecm240"]

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
MERGED_GROUPS = {
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wz3p6_ee_qq_ecm240": QQ_MERGE,
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_hadZH_HWW_ecm240": SIGNAL_SAMPLES,
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_hadZH_Hbb_ecm240": [sample for sample in ZH_OTHER_SAMPLES if "_Hbb_" in sample],
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_hadZH_Htautau_ecm240": [sample for sample in ZH_OTHER_SAMPLES if "_Htautau_" in sample],
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_hadZH_Hgg_ecm240": [sample for sample in ZH_OTHER_SAMPLES if "_Hgg_" in sample],
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_hadZH_Hcc_ecm240": [sample for sample in ZH_OTHER_SAMPLES if "_Hcc_" in sample],
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_hadZH_HZZ_ecm240": [sample for sample in ZH_OTHER_SAMPLES if "_HZZ_" in sample],
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
}

# Process definitions: (filename, label, color, isSignal)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
processes = [
    # Backgrounds (will be stacked, order matters: bottom to top)
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    ("wz3p6_ee_tautau_ecm240", "#tau#tau", ROOT.kGray + 1, False),
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    ("wzp6_ee_hadZH_HZZ_ecm240", "ZH(ZZ)", ROOT.kCyan - 7, False),
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    ("wzp6_ee_hadZH_Hcc_ecm240", "ZH(cc)", ROOT.kCyan - 3, False),
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    ("wzp6_ee_hadZH_Hgg_ecm240", "ZH(gg)", ROOT.kCyan + 1, False),
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    ("wzp6_ee_hadZH_Htautau_ecm240", "ZH(#tau#tau)", ROOT.kCyan + 3, False),
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    ("wzp6_ee_hadZH_Hbb_ecm240", "ZH(bb)", ROOT.kTeal - 7, False),
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    ("wz3p6_ee_qq_ecm240", "Z/#gamma#rightarrowqq", ROOT.kGreen + 2, False),
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    ("p8_ee_ZZ_ecm240", "ZZ", ROOT.kAzure + 1, False),
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    ("p8_ee_WW_ecm240", "WW", ROOT.kOrange - 3, False),
    # Signal (summed over all hadronic-Z production modes)
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    ("wzp6_ee_hadZH_HWW_ecm240", "ZH (H#rightarrowWW)", ROOT.kRed + 1, True),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
]

# Histograms to plot: (name, xtitle, rebin, xmin, xmax, logy)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
histograms = [
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ("cutFlow", "Cut stage", 1, -0.5, 8.5, True),
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    ("lepton_p", "Lepton momentum [GeV]", 4, 0, 150, False),
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    ("lepton_iso", "Lepton isolation", 2, 0, 1, False),
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    ("missingEnergy_e", "Missing energy [GeV]", 4, 0, 150, False),
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    ("missingEnergy_p", "Missing momentum [GeV]", 4, 0, 150, False),
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    ("missingMass", "Missing mass [GeV]", 4, 0, 240, False),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ("cosTheta_miss", "|cos(#theta_{miss})|", 1, 0, 1, False),
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    ("visibleEnergy", "Visible energy (no lepton) [GeV]", 4, 0, 250, False),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ("njets", "Number of jets", 1, 0, 10, True),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ("jet0_p", "Jet 0 momentum [GeV]", 4, 0, 120, False),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ("jet1_p", "Jet 1 momentum [GeV]", 4, 0, 120, False),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ("jet2_p", "Jet 2 momentum [GeV]", 4, 0, 120, False),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ("jet3_p", "Jet 3 momentum [GeV]", 4, 0, 120, False),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ("Zcand_m", "m_{Z cand} [GeV]", 4, 0, 200, False),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ("Wstar_m", "m_{W*} [GeV]", 4, 0, 150, False),  # W* is off-shell, expect ~40 GeV
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ("Wlep_m", "m_{W_{lep}} [GeV]", 4, 0, 200, False),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ("Hcand_m", "m_{H cand} [GeV]", 4, 0, 300, False),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ("Hcand_m_afterZ", "m_{H cand} (after Z cut) [GeV]", 4, 0, 300, False),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ("Hcand_m_final", "m_{H cand} (final) [GeV]", 4, 0, 300, False),
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    ("recoil_m", "Recoil mass [GeV]", 4, 50, 200, False),
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    ("recoil_m_afterZ", "Recoil mass (after Z cut) [GeV]", 4, 50, 200, False),
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    ("deltaZ", "|m_{jj} - m_{Z}| [GeV]", 4, 0, 50, False),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
]

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
CUT_LABELS = [
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "All",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "1lep p>20",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "ISO",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "Veto p>5",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "MET E>20",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "4jets",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "Z win",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "Recoil",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
]
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
CUT_IDS = [f"cut{i}" for i in range(len(CUT_LABELS))]
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
PERCENT_COL_WIDTH = 12

# ============================================================
# Style settings
# ============================================================

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def setStyle():
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ROOT.gStyle.SetOptStat(0)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ROOT.gStyle.SetOptTitle(0)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ROOT.gStyle.SetPadTickX(1)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ROOT.gStyle.SetPadTickY(1)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ROOT.gStyle.SetHistLineWidth(2)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ROOT.gStyle.SetLegendBorderSize(0)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ROOT.gStyle.SetLegendFillColor(0)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ROOT.gStyle.SetLegendFont(42)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ROOT.gStyle.SetLegendTextSize(0.035)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ROOT.gStyle.SetPadLeftMargin(0.14)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ROOT.gStyle.SetPadRightMargin(0.05)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ROOT.gStyle.SetPadTopMargin(0.08)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ROOT.gStyle.SetPadBottomMargin(0.12)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ROOT.gStyle.SetTitleFont(42, "XYZ")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ROOT.gStyle.SetTitleSize(0.045, "XYZ")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ROOT.gStyle.SetLabelFont(42, "XYZ")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ROOT.gStyle.SetLabelSize(0.04, "XYZ")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ROOT.gStyle.SetTitleOffset(1.3, "Y")

# ============================================================
# Helper functions
# ============================================================

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def getHist(filename, histname):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    """Load histogram from file (already scaled by framework).

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    Some entries are logical groups summed over multiple processed samples.
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    """
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if filename in MERGED_GROUPS:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h_merged = None
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        for sample_name in MERGED_GROUPS[filename]:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h = getHist(sample_name, histname)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            if h is None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
                continue
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            if h_merged is None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
                h_merged = h.Clone(f"{histname}_{filename}_merged")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
                h_merged.SetDirectory(0)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            else:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
                h_merged.Add(h)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        return h_merged

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    filepath = os.path.join(inputDir, filename + ".root")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if not os.path.exists(filepath):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        print(f"Warning: {filepath} not found")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        return None

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    f = ROOT.TFile.Open(filepath)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    h = f.Get(histname)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if not h:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        print(f"Warning: {histname} not found in {filepath}")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        f.Close()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        return None

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    h.SetDirectory(0)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    f.Close()

    # NOTE: Histograms from fccanalysis with doScale=True are ALREADY
    # normalized to xsec * intLumi. Do NOT scale again here!

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    return h


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def collectCutflowData():
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    """Collect cutflow yields for all configured processes."""

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ncuts = len(CUT_LABELS)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    process_rows = []
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    process_eff_rows = []
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    total_sig = [0.0] * ncuts
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    total_bkg = [0.0] * ncuts

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for fname, label, color, isSignal in processes:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h = getHist(fname, "cutFlow")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        if h is None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            continue

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        values = [h.GetBinContent(i + 1) for i in range(ncuts)]
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        process_rows.append((label, values, isSignal))

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        base = values[0] if values and values[0] > 0 else 0.0
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        eff_values = [100.0 * val / base if base > 0 else None for val in values]
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        process_eff_rows.append((label, eff_values, isSignal))

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        for i, val in enumerate(values):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            if isSignal:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
                total_sig[i] += val
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            else:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
                total_bkg[i] += val

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    s_over_b = []
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    s_over_sqrt_b = []
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for s, b in zip(total_sig, total_bkg):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        if b > 0:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            s_over_b.append(s / b)
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
            s_over_sqrt_b.append(s / (b ** 0.5))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        else:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            s_over_b.append(None)
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
            s_over_sqrt_b.append(None)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    sig_base = total_sig[0] if total_sig and total_sig[0] > 0 else 0.0
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    bkg_base = total_bkg[0] if total_bkg and total_bkg[0] > 0 else 0.0
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    total_sig_eff = [100.0 * val / sig_base if sig_base > 0 else None for val in total_sig]
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    total_bkg_eff = [100.0 * val / bkg_base if bkg_base > 0 else None for val in total_bkg]

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    return {
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "cut_labels": CUT_LABELS,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "cut_ids": CUT_IDS,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "process_rows": process_rows,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "process_eff_rows": process_eff_rows,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "total_sig": total_sig,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "total_bkg": total_bkg,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "total_sig_eff": total_sig_eff,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "total_bkg_eff": total_bkg_eff,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "s_over_b": s_over_b,
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        "s_over_sqrt_b": s_over_sqrt_b,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    }


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def _format_table_row(label, values, float_fmt=".0f"):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    row = f"{label:<25}"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for val in values:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        if val is None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            row += f"{'--':>10}"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        else:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            row += f"{val:>10{float_fmt}}"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    return row


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def _format_percent_row(label, values):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    row = f"{label:<25}"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for val in values:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        if val is None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            row += f"{'--':>{PERCENT_COL_WIDTH}}"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        else:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            row += f"{f'{val:.2f}%':>{PERCENT_COL_WIDTH}}"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    return row


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def _format_cut_header(cut_keys, value_width=10):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    header = f"{'Process':<25}"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for key in cut_keys:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        header += f"{key:>{value_width}}"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    return header


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def writeCutflowText(summary):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    """Write cutflow table to a plain-text file."""

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    os.makedirs(outputDir, exist_ok=True)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    outpath = os.path.join(outputDir, "cutFlow_cutflow.txt")

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines = []
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append("=" * 80)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append("CUTFLOW TABLE (normalized to 10.8 ab^-1)")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append("=" * 80)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    header = f"{'Process':<25}"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for lab in summary["cut_labels"]:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        header += f"{lab:>10}"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(header)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append("-" * 95)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for label, values, isSignal in summary["process_rows"]:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        lines.append(_format_table_row(label, values, ".0f"))

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append("-" * 95)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(_format_table_row("Total Signal", summary["total_sig"], ".1f"))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(_format_table_row("Total Background", summary["total_bkg"], ".1f"))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append("-" * 95)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(_format_table_row("S/B", summary["s_over_b"], ".4f"))
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    lines.append(_format_table_row("S/sqrt(B)", summary["s_over_sqrt_b"], ".1f"))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append("=" * 95)

# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
    with open(outpath, "w", encoding="ascii") as f:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        f.write("\n".join(lines) + "\n")


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def writeCutflowLatex(summary):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    """Write cutflow table to a LaTeX file."""

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    os.makedirs(outputDir, exist_ok=True)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    outpath = os.path.join(outputDir, "cutFlow_cutflow.tex")

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    cols = "l" + "r" * len(summary["cut_labels"])
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines = [
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        r"\begin{tabular}{" + cols + r"}",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        r"\hline",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ]

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    header = ["Process"] + summary["cut_labels"]
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(" & ".join(header) + r" \\")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(r"\hline")

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for label, values, isSignal in summary["process_rows"]:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        row = [label] + [f"{val:.0f}" for val in values]
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        lines.append(" & ".join(row) + r" \\")

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(r"\hline")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(" & ".join(["Total Signal"] + [f"{v:.1f}" for v in summary["total_sig"]]) + r" \\")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(" & ".join(["Total Background"] + [f"{v:.1f}" for v in summary["total_bkg"]]) + r" \\")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(r"\hline")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(" & ".join(["S/B"] + [("--" if v is None else f"{v:.4f}") for v in summary["s_over_b"]]) + r" \\")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    lines.append(" & ".join(["S/$\\sqrt{B}$"] + [("--" if v is None else f"{v:.1f}") for v in summary["s_over_sqrt_b"]]) + r" \\")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(r"\hline")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(r"\end{tabular}")

# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
    with open(outpath, "w", encoding="ascii") as f:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        f.write("\n".join(lines) + "\n")


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def makeCutflowPdf(summary):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    """Render a cutflow table as a PDF, similar to standard FCCAnalysis outputs."""

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    os.makedirs(outputDir, exist_ok=True)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    outpath = os.path.join(outputDir, "cutFlow_cutflow.pdf")

# [Visualization] ROOT histogram composition for publication-grade shapes; stacked backgrounds preserve rate information while showing signal overlay.
    c = ROOT.TCanvas("cutflow_table", "", 1800, 700)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    c.cd()

# [Visualization] ROOT histogram composition for publication-grade shapes; stacked backgrounds preserve rate information while showing signal overlay.
    title = ROOT.TLatex()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    title.SetNDC()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    title.SetTextFont(42)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    title.SetTextSize(0.035)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    title.DrawLatex(0.03, 0.95, "Cutflow table, normalized to 10.8 ab^{-1}")

# [Visualization] ROOT histogram composition for publication-grade shapes; stacked backgrounds preserve rate information while showing signal overlay.
    latex = ROOT.TLatex()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    latex.SetNDC()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    latex.SetTextFont(42)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    latex.SetTextSize(0.024)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    x_process = 0.03
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    x_start = 0.32
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    x_end = 0.97
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ncuts = len(summary["cut_labels"])
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    x_cuts = [x_start + i * (x_end - x_start) / max(1, ncuts - 1) for i in range(ncuts)]

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    y = 0.88
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    latex.SetTextAlign(13)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    latex.DrawLatex(x_process, y, "Process")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    latex.SetTextAlign(23)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for x, label in zip(x_cuts, summary["cut_labels"]):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        latex.DrawLatex(x, y, label)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    rows = []
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for label, values, isSignal in summary["process_rows"]:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        rows.append((label, values))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    rows.append(("Total Signal", summary["total_sig"]))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    rows.append(("Total Background", summary["total_bkg"]))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    rows.append(("S/B", summary["s_over_b"]))
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    rows.append(("S/sqrt(B)", summary["s_over_sqrt_b"]))

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    y -= 0.07
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for label, values in rows:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        latex.SetTextAlign(13)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        latex.DrawLatex(x_process, y, label)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        latex.SetTextAlign(23)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        for x, val in zip(x_cuts, values):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            if val is None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
                txt = "--"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            elif label in ("S/B",):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
                txt = f"{val:.4f}"
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
            elif label in ("S/sqrt(B)",):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
                txt = f"{val:.1f}"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            elif label.startswith("Total"):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
                txt = f"{val:.1f}"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            else:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
                txt = f"{val:.0f}"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            latex.DrawLatex(x, y, txt)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        y -= 0.06

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    c.SaveAs(outpath)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    c.SaveAs(outpath.replace(".pdf", ".png"))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    c.Close()


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def writeCutflowEfficiencyText(summary):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    """Write cumulative cut efficiencies in percent to a plain-text file."""

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    os.makedirs(outputDir, exist_ok=True)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    outpath = os.path.join(outputDir, "cutFlow_efficiency.txt")

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    rule = "-" * (25 + PERCENT_COL_WIDTH * len(summary["cut_ids"]))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines = []
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append("=" * 80)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append("CUTFLOW EFFICIENCY TABLE [%], cumulative w.r.t. cut0 (All)")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append("=" * 80)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(_format_cut_header(summary["cut_ids"], PERCENT_COL_WIDTH))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(rule)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for label, values, isSignal in summary["process_eff_rows"]:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        lines.append(_format_percent_row(label, values))

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(rule)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(_format_percent_row("Total Signal eff", summary["total_sig_eff"]))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(_format_percent_row("Total Bkg eff", summary["total_bkg_eff"]))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append("=" * len(rule))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append("")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append("Cut definitions:")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for cut_id, label in zip(summary["cut_ids"], summary["cut_labels"]):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        lines.append(f"  {cut_id}: {label}")

# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
    with open(outpath, "w", encoding="ascii") as f:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        f.write("\n".join(lines) + "\n")

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def writeCutflowEfficiencyLatex(summary):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    """Write cumulative cut efficiencies in percent to a LaTeX file."""

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    os.makedirs(outputDir, exist_ok=True)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    outpath = os.path.join(outputDir, "cutFlow_efficiency.tex")

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    cols = "l" + "r" * len(summary["cut_ids"])
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ncols = len(summary["cut_ids"]) + 1
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines = [
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        r"\begin{tabular}{" + cols + r"}",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        r"\hline",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ]

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    header = ["Process"] + summary["cut_ids"]
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(" & ".join(header) + r" \\")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(r"\hline")

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for label, values, isSignal in summary["process_eff_rows"]:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        row = [label] + [("--" if v is None else f"{v:.2f}\\%") for v in values]
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        lines.append(" & ".join(row) + r" \\")

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(r"\hline")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(" & ".join(["Total Signal eff"] + [("--" if v is None else f"{v:.2f}\\%") for v in summary["total_sig_eff"]]) + r" \\")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(" & ".join(["Total Bkg eff"] + [("--" if v is None else f"{v:.2f}\\%") for v in summary["total_bkg_eff"]]) + r" \\")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(r"\hline")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(rf"\multicolumn{{{ncols}}}{{l}}{{Cut definitions:}} \\")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for cut_id, label in zip(summary["cut_ids"], summary["cut_labels"]):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        safe_label = label.replace("_", r"\_").replace("%", r"\%")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        lines.append(rf"\multicolumn{{{ncols}}}{{l}}{{{cut_id}: {safe_label}}} \\")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(r"\hline")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    lines.append(r"\end{tabular}")

# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
    with open(outpath, "w", encoding="ascii") as f:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        f.write("\n".join(lines) + "\n")

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def makeCutflowEfficiencyPdf(summary):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    """Render a cumulative cut-efficiency table as a PDF."""

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    os.makedirs(outputDir, exist_ok=True)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    outpath = os.path.join(outputDir, "cutFlow_efficiency.pdf")

# [Visualization] ROOT histogram composition for publication-grade shapes; stacked backgrounds preserve rate information while showing signal overlay.
    c = ROOT.TCanvas("cutflow_eff_table", "", 1800, 850)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    c.cd()

# [Visualization] ROOT histogram composition for publication-grade shapes; stacked backgrounds preserve rate information while showing signal overlay.
    title = ROOT.TLatex()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    title.SetNDC()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    title.SetTextFont(42)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    title.SetTextSize(0.035)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    title.DrawLatex(0.03, 0.95, "Cutflow efficiencies [%], cumulative w.r.t. cut0 (All)")

# [Visualization] ROOT histogram composition for publication-grade shapes; stacked backgrounds preserve rate information while showing signal overlay.
    latex = ROOT.TLatex()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    latex.SetNDC()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    latex.SetTextFont(42)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    latex.SetTextSize(0.024)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    x_process = 0.03
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    x_start = 0.32
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    x_end = 0.97
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ncuts = len(summary["cut_ids"])
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    x_cuts = [x_start + i * (x_end - x_start) / max(1, ncuts - 1) for i in range(ncuts)]

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    y = 0.88
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    latex.SetTextAlign(13)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    latex.DrawLatex(x_process, y, "Process")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    latex.SetTextAlign(23)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for x, label in zip(x_cuts, summary["cut_ids"]):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        latex.DrawLatex(x, y, label)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    rows = []
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for label, values, isSignal in summary["process_eff_rows"]:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        rows.append((label, values))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    rows.append(("Total Signal eff", summary["total_sig_eff"]))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    rows.append(("Total Bkg eff", summary["total_bkg_eff"]))

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    y -= 0.07
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for label, values in rows:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        latex.SetTextAlign(13)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        latex.DrawLatex(x_process, y, label)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        latex.SetTextAlign(23)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        for x, val in zip(x_cuts, values):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            txt = "--" if val is None else f"{val:.2f}%"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            latex.DrawLatex(x, y, txt)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        y -= 0.06

# [Visualization] ROOT histogram composition for publication-grade shapes; stacked backgrounds preserve rate information while showing signal overlay.
    legend = ROOT.TLatex()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    legend.SetNDC()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    legend.SetTextFont(42)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    legend.SetTextSize(0.020)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    legend.SetTextAlign(13)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    legend.DrawLatex(0.03, 0.24, "Cut definitions:")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for idx, (cut_id, label) in enumerate(zip(summary["cut_ids"], summary["cut_labels"])):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        x = 0.03 + (idx % 2) * 0.44
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        yy = 0.20 - (idx // 2) * 0.04
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        legend.DrawLatex(x, yy, f"{cut_id}: {label}")

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    c.SaveAs(outpath)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    c.SaveAs(outpath.replace(".pdf", ".png"))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    c.Close()

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def makePlot(histname, xtitle, rebin, xmin, xmax, logy):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    """Create a single plot with stacked backgrounds and signal overlay"""

    # Create canvas
# [Visualization] ROOT histogram composition for publication-grade shapes; stacked backgrounds preserve rate information while showing signal overlay.
    c = ROOT.TCanvas("c", "", 800, 700)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    c.cd()

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if logy:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        c.SetLogy()

    # Prepare histograms
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    bkg_hists = []
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    sig_hists = []

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for fname, label, color, isSignal in processes:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h = getHist(fname, histname)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        if h is None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            continue

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        if rebin > 1:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h.Rebin(rebin)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h.SetLineColor(color)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h.SetLineWidth(2)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        if isSignal:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h.SetFillStyle(0)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            sig_hists.append((h, label, color))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        else:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h.SetFillColor(color)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h.SetFillStyle(1001)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            bkg_hists.append((h, label, color))

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if not bkg_hists and not sig_hists:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        print(f"Warning: No histograms found for {histname}")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        return

    # Create THStack for backgrounds
# [Visualization] ROOT histogram composition for publication-grade shapes; stacked backgrounds preserve rate information while showing signal overlay.
    hs = ROOT.THStack("hs", "")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for h, label, color in bkg_hists:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        hs.Add(h)

    # Sum signals for combined overlay
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    h_sig_sum = None
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for h, label, color in sig_hists:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        if h_sig_sum is None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h_sig_sum = h.Clone("h_sig_sum")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        else:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h_sig_sum.Add(h)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if h_sig_sum:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h_sig_sum.SetLineColor(ROOT.kRed+1)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h_sig_sum.SetLineWidth(3)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h_sig_sum.SetFillStyle(0)

    # Determine y-axis range
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ymax = 0
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if hs.GetNhists() > 0:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ymax = max(ymax, hs.GetMaximum())
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if h_sig_sum:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ymax = max(ymax, h_sig_sum.GetMaximum())

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if logy:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ymin = 0.1
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ymax *= 50
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    else:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ymin = 0
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ymax *= 1.5

    # Draw
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if hs.GetNhists() > 0:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        hs.Draw("HIST")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        hs.GetXaxis().SetTitle(xtitle)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        hs.GetYaxis().SetTitle("Events")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        hs.GetXaxis().SetRangeUser(xmin, xmax)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        hs.SetMinimum(ymin)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        hs.SetMaximum(ymax)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        hs.GetXaxis().SetTitleSize(0.045)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        hs.GetYaxis().SetTitleSize(0.045)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        hs.GetXaxis().SetLabelSize(0.04)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        hs.GetYaxis().SetLabelSize(0.04)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        hs.GetYaxis().SetTitleOffset(1.3)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if h_sig_sum:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h_sig_sum.Draw("HIST SAME")

    # Legend
# [Visualization] ROOT histogram composition for publication-grade shapes; stacked backgrounds preserve rate information while showing signal overlay.
    leg = ROOT.TLegend(0.60, 0.65, 0.92, 0.88)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    leg.SetTextSize(0.032)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if h_sig_sum:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        leg.AddEntry(h_sig_sum, "Signal (ZH, H#rightarrowWW)", "l")

    # Add backgrounds in reverse order (top to bottom in legend)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for h, label, color in reversed(bkg_hists):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        leg.AddEntry(h, label, "f")

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    leg.Draw()

    # CMS-style label
# [Visualization] ROOT histogram composition for publication-grade shapes; stacked backgrounds preserve rate information while showing signal overlay.
    latex = ROOT.TLatex()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    latex.SetNDC()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    latex.SetTextFont(42)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    latex.SetTextSize(0.04)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    latex.DrawLatex(0.14, 0.93, "#bf{FCC-ee} #it{Simulation}")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    latex.SetTextSize(0.035)
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    latex.DrawLatex(0.70, 0.93, "#sqrt{s} = 240 GeV, 10.8 ab^{-1}")

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    os.makedirs(outputDir, exist_ok=True)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    c.SaveAs(os.path.join(outputDir, f"{histname}.pdf"))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    c.SaveAs(os.path.join(outputDir, f"{histname}.png"))

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    c.Close()


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def makeCutflowTable():
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    """Print cutflow table and save text/tex/pdf outputs."""

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    summary = collectCutflowData()

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print("\n" + "=" * 80)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print("CUTFLOW TABLE (normalized to 10.8 ab^-1)")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print("=" * 80)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    header = f"{'Process':<25}"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for lab in summary["cut_labels"]:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        header += f"{lab:>10}"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print(header)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print("-" * 95)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for label, values, isSignal in summary["process_rows"]:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        print(_format_table_row(label, values, ".0f"))

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print("-" * 95)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print(_format_table_row("Total Signal", summary["total_sig"], ".1f"))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print(_format_table_row("Total Background", summary["total_bkg"], ".1f"))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print("-" * 95)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print(_format_table_row("S/B", summary["s_over_b"], ".4f"))
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    print(_format_table_row("S/sqrt(B)", summary["s_over_sqrt_b"], ".1f"))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print("=" * 95 + "\n")

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print("\n" + "=" * 80)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print("CUTFLOW EFFICIENCY TABLE [%], cumulative w.r.t. cut0 (All)")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print("=" * 80)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    rule = "-" * (25 + PERCENT_COL_WIDTH * len(summary["cut_ids"]))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print(_format_cut_header(summary["cut_ids"], PERCENT_COL_WIDTH))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print(rule)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for label, values, isSignal in summary["process_eff_rows"]:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        print(_format_percent_row(label, values))

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print(rule)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print(_format_percent_row("Total Signal eff", summary["total_sig_eff"]))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print(_format_percent_row("Total Bkg eff", summary["total_bkg_eff"]))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print("=" * len(rule))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print("Cut definitions:")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for cut_id, label in zip(summary["cut_ids"], summary["cut_labels"]):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        print(f"  {cut_id}: {label}")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print()

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    writeCutflowText(summary)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    writeCutflowLatex(summary)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    makeCutflowPdf(summary)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    writeCutflowEfficiencyText(summary)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    writeCutflowEfficiencyLatex(summary)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    makeCutflowEfficiencyPdf(summary)


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def makeNormalizedPlot(histname, xtitle, rebin, xmin, xmax, logy=False):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    """Create normalized stacked plot (signal and background both normalized to unit area)"""

# [Visualization] ROOT histogram composition for publication-grade shapes; stacked backgrounds preserve rate information while showing signal overlay.
    c = ROOT.TCanvas("c", "", 800, 700)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    c.cd()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if logy:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        c.SetLogy()

    # Prepare histograms
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    bkg_hists = []
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    sig_hists = []

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for fname, label, color, isSignal in processes:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h = getHist(fname, histname)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        if h is None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            continue

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        if rebin > 1:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h.Rebin(rebin)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h.SetLineColor(color)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h.SetLineWidth(2)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        if isSignal:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h.SetFillStyle(0)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            sig_hists.append((h, label, color))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        else:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h.SetFillColor(color)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h.SetFillStyle(1001)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            bkg_hists.append((h, label, color))

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if not bkg_hists and not sig_hists:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        print(f"Warning: No histograms found for {histname}")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        return

    # Sum all backgrounds
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    h_bkg_sum = None
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for h, label, color in bkg_hists:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        if h_bkg_sum is None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h_bkg_sum = h.Clone("h_bkg_sum")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        else:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h_bkg_sum.Add(h)

    # Sum all signals
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    h_sig_sum = None
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for h, label, color in sig_hists:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        if h_sig_sum is None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h_sig_sum = h.Clone("h_sig_sum")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        else:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h_sig_sum.Add(h)

    # Normalize both to unit area
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if h_bkg_sum and h_bkg_sum.Integral() > 0:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h_bkg_sum.Scale(1.0 / h_bkg_sum.Integral())
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if h_sig_sum and h_sig_sum.Integral() > 0:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h_sig_sum.Scale(1.0 / h_sig_sum.Integral())

    # Style
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if h_bkg_sum:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h_bkg_sum.SetFillColor(ROOT.kAzure+1)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h_bkg_sum.SetFillStyle(3004)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h_bkg_sum.SetLineColor(ROOT.kAzure+1)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h_bkg_sum.SetLineWidth(2)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if h_sig_sum:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h_sig_sum.SetLineColor(ROOT.kRed+1)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h_sig_sum.SetLineWidth(3)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h_sig_sum.SetFillStyle(0)

    # Determine y-axis range
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ymax = 0
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if h_bkg_sum:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ymax = max(ymax, h_bkg_sum.GetMaximum())
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if h_sig_sum:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ymax = max(ymax, h_sig_sum.GetMaximum())

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if logy:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ymin = 1e-4
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ymax *= 10
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    else:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ymin = 0
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ymax *= 1.4

    # Draw
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    first = True
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if h_bkg_sum:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h_bkg_sum.GetXaxis().SetTitle(xtitle)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h_bkg_sum.GetYaxis().SetTitle("Normalized")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h_bkg_sum.GetXaxis().SetRangeUser(xmin, xmax)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h_bkg_sum.SetMinimum(ymin)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h_bkg_sum.SetMaximum(ymax)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h_bkg_sum.GetXaxis().SetTitleSize(0.045)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h_bkg_sum.GetYaxis().SetTitleSize(0.045)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h_bkg_sum.GetXaxis().SetLabelSize(0.04)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h_bkg_sum.GetYaxis().SetLabelSize(0.04)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h_bkg_sum.GetYaxis().SetTitleOffset(1.3)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h_bkg_sum.Draw("HIST")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        first = False

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if h_sig_sum:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        if first:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h_sig_sum.GetXaxis().SetTitle(xtitle)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h_sig_sum.GetYaxis().SetTitle("Normalized")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h_sig_sum.GetXaxis().SetRangeUser(xmin, xmax)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h_sig_sum.SetMinimum(ymin)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h_sig_sum.SetMaximum(ymax)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h_sig_sum.GetXaxis().SetTitleSize(0.045)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h_sig_sum.GetYaxis().SetTitleSize(0.045)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h_sig_sum.GetXaxis().SetLabelSize(0.04)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h_sig_sum.GetYaxis().SetLabelSize(0.04)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h_sig_sum.GetYaxis().SetTitleOffset(1.3)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h_sig_sum.Draw("HIST")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        else:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h_sig_sum.Draw("HIST SAME")

    # Legend
# [Visualization] ROOT histogram composition for publication-grade shapes; stacked backgrounds preserve rate information while showing signal overlay.
    leg = ROOT.TLegend(0.60, 0.75, 0.92, 0.88)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    leg.SetTextSize(0.032)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if h_sig_sum:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        leg.AddEntry(h_sig_sum, "Signal (ZH, H#rightarrowWW)", "l")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if h_bkg_sum:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        leg.AddEntry(h_bkg_sum, "Background (all)", "f")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    leg.Draw()

    # CMS-style label
# [Visualization] ROOT histogram composition for publication-grade shapes; stacked backgrounds preserve rate information while showing signal overlay.
    latex = ROOT.TLatex()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    latex.SetNDC()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    latex.SetTextFont(42)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    latex.SetTextSize(0.04)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    latex.DrawLatex(0.14, 0.93, "#bf{FCC-ee} #it{Simulation} (normalized)")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    latex.SetTextSize(0.035)
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    latex.DrawLatex(0.70, 0.93, "#sqrt{s} = 240 GeV")

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    os.makedirs(outputDir, exist_ok=True)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    c.SaveAs(os.path.join(outputDir, f"{histname}_norm.pdf"))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    c.SaveAs(os.path.join(outputDir, f"{histname}_norm.png"))

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    c.Close()


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def makeComparisonPlot(histname, xtitle, rebin, xmin, xmax):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    """Create shape comparison plot (normalized to unit area)"""

# [Visualization] ROOT histogram composition for publication-grade shapes; stacked backgrounds preserve rate information while showing signal overlay.
    c = ROOT.TCanvas("c", "", 800, 600)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    c.cd()

    # Only compare signal vs main backgrounds
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    compare = [
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
        ("wzp6_ee_hadZH_HWW_ecm240", "Signal (ZH, H#rightarrowWW)", ROOT.kRed+1),
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
        ("p8_ee_WW_ecm240", "WW bkg", ROOT.kOrange-3),
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
        ("p8_ee_ZZ_ecm240", "ZZ bkg", ROOT.kAzure+1),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ]

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    hists = []
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for fname, label, color in compare:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h = getHist(fname, histname)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        if h is None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            continue

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        if rebin > 1:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h.Rebin(rebin)

        # Normalize to unit area
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        if h.Integral() > 0:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h.Scale(1.0 / h.Integral())

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h.SetLineColor(color)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h.SetLineWidth(3)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h.SetFillStyle(0)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        hists.append((h, label))

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if not hists:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        return

    # Find y-axis range
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ymax = max(h.GetMaximum() for h, _ in hists) * 1.4

    # Draw
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for i, (h, label) in enumerate(hists):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h.GetXaxis().SetTitle(xtitle)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h.GetYaxis().SetTitle("Normalized")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h.GetXaxis().SetRangeUser(xmin, xmax)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h.SetMaximum(ymax)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        h.SetMinimum(0)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        if i == 0:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h.Draw("HIST")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        else:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            h.Draw("HIST SAME")

    # Legend
# [Visualization] ROOT histogram composition for publication-grade shapes; stacked backgrounds preserve rate information while showing signal overlay.
    leg = ROOT.TLegend(0.60, 0.70, 0.92, 0.88)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for h, label in hists:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        leg.AddEntry(h, label, "l")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    leg.Draw()

    # Label
# [Visualization] ROOT histogram composition for publication-grade shapes; stacked backgrounds preserve rate information while showing signal overlay.
    latex = ROOT.TLatex()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    latex.SetNDC()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    latex.SetTextFont(42)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    latex.SetTextSize(0.04)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    latex.DrawLatex(0.14, 0.93, "#bf{FCC-ee} #it{Simulation} (shape comparison)")

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    os.makedirs(outputDir, exist_ok=True)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    c.SaveAs(os.path.join(outputDir, f"{histname}_shape.pdf"))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    c.SaveAs(os.path.join(outputDir, f"{histname}_shape.png"))

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    c.Close()


# ============================================================
# Main
# ============================================================

# [Entry] Module entry point for direct execution from CLI.
if __name__ == "__main__":

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    setStyle()

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print("=" * 60)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print("H->WW->lvqq Analysis Plotting Script")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print("=" * 60)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print(f"Input directory:  {inputDir}")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print(f"Output directory: {outputDir}")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print(f"Luminosity:       {intLumi/1e6:.1f} ab^-1")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print("=" * 60)

    # Check input directory
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if not os.path.exists(inputDir):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        print(f"ERROR: Input directory {inputDir} does not exist!")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        print("Please run the analysis first with:")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        print("  fccanalysis run h_hww_lvqq.py")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        sys.exit(1)

    # Make all stacked plots (unnormalized)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print("\nGenerating stacked plots (unnormalized)...")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for hname, xtitle, rebin, xmin, xmax, logy in histograms:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        print(f"  {hname}...")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        makePlot(hname, xtitle, rebin, xmin, xmax, logy)

    # Make normalized plots (signal vs background, both normalized to unit area)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print("\nGenerating normalized plots...")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    norm_hists = [
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        ("lepton_p", "Lepton momentum [GeV]", 4, 0, 150),
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        ("lepton_iso", "Lepton isolation", 2, 0, 1),
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        ("missingEnergy_e", "Missing energy [GeV]", 4, 0, 150),
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        ("missingEnergy_p", "Missing momentum [GeV]", 4, 0, 150),
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        ("missingMass", "Missing mass [GeV]", 4, 0, 240),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ("cosTheta_miss", "|cos(#theta_{miss})|", 1, 0, 1),
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        ("visibleEnergy", "Visible energy (no lepton) [GeV]", 4, 0, 250),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ("jet0_p", "Jet 0 momentum [GeV]", 4, 0, 120),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ("jet1_p", "Jet 1 momentum [GeV]", 4, 0, 120),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ("jet2_p", "Jet 2 momentum [GeV]", 4, 0, 120),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ("jet3_p", "Jet 3 momentum [GeV]", 4, 0, 120),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ("Zcand_m", "m_{Z cand} [GeV]", 4, 0, 200),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ("Wstar_m", "m_{W*} [GeV]", 4, 0, 150),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ("Wlep_m", "m_{W_{lep}} [GeV]", 4, 0, 200),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ("Hcand_m", "m_{H cand} [GeV]", 4, 50, 250),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ("Hcand_m_afterZ", "m_{H cand} (after Z cut) [GeV]", 4, 50, 250),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ("Hcand_m_final", "m_{H cand} (final) [GeV]", 4, 50, 250),
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        ("recoil_m", "Recoil mass [GeV]", 4, 50, 200),
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        ("recoil_m_afterZ", "Recoil mass (after Z cut) [GeV]", 4, 50, 200),
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        ("deltaZ", "|m_{jj} - m_{Z}| [GeV]", 4, 0, 50),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ]
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for hname, xtitle, rebin, xmin, xmax in norm_hists:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        print(f"  {hname}_norm...")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        makeNormalizedPlot(hname, xtitle, rebin, xmin, xmax)

    # Make shape comparison plots (signal vs WW vs ZZ separately)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print("\nGenerating shape comparison plots...")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    shape_hists = [
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ("Zcand_m", "m_{Z cand} [GeV]", 4, 0, 200),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ("Wstar_m", "m_{W*} [GeV]", 4, 0, 150),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ("Hcand_m", "m_{H cand} [GeV]", 4, 50, 250),
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        ("recoil_m", "Recoil mass [GeV]", 4, 50, 200),
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        ("deltaZ", "|m_{jj} - m_{Z}| [GeV]", 4, 0, 50),
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        ("lepton_p", "Lepton momentum [GeV]", 4, 0, 150),
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        ("lepton_iso", "Lepton isolation", 2, 0, 1),
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        ("missingEnergy_e", "Missing energy [GeV]", 4, 0, 150),
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        ("missingEnergy_p", "Missing momentum [GeV]", 4, 0, 150),
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        ("missingMass", "Missing mass [GeV]", 4, 0, 240),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ("cosTheta_miss", "|cos(#theta_{miss})|", 1, 0, 1),
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        ("visibleEnergy", "Visible energy (no lepton) [GeV]", 4, 0, 250),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ("jet0_p", "Jet 0 momentum [GeV]", 4, 0, 120),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ("jet1_p", "Jet 1 momentum [GeV]", 4, 0, 120),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ("jet2_p", "Jet 2 momentum [GeV]", 4, 0, 120),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ("jet3_p", "Jet 3 momentum [GeV]", 4, 0, 120),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ]
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for hname, xtitle, rebin, xmin, xmax in shape_hists:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        print(f"  {hname}_shape...")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        makeComparisonPlot(hname, xtitle, rebin, xmin, xmax)

    # Print cutflow table
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    makeCutflowTable()

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print(f"All plots saved to: {outputDir}")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print("Done!")
