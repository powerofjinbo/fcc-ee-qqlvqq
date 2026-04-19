#!/usr/bin/env python3
"""
Plotting script for H->WW->lvqq analysis
Produces paper-style plots with stacked backgrounds and signal overlay
"""

import ROOT
import os
import sys
import math

from ml_config import SIGNAL_SAMPLES, ZH_OTHER_SAMPLES

# Suppress ROOT info messages
ROOT.gROOT.SetBatch(True)
ROOT.gErrorIgnoreLevel = ROOT.kWarning

# ============================================================
# Configuration
# ============================================================

inputDir = "output/h_hww_lvqq/histmaker/ecm240/"
outputDir = "plots_lvqq/"

# Integrated luminosity (pb^-1)
intLumi = 10.8e6  # 10.8 ab^-1 at 240 GeV

# qq flavors to merge into one "Z/gamma->qq" entry for plotting
QQ_MERGE = ["wz3p6_ee_uu_ecm240", "wz3p6_ee_dd_ecm240", "wz3p6_ee_cc_ecm240",
            "wz3p6_ee_ss_ecm240", "wz3p6_ee_bb_ecm240"]

MERGED_GROUPS = {
    "wz3p6_ee_qq_ecm240": QQ_MERGE,
    "wzp6_ee_hadZH_HWW_ecm240": SIGNAL_SAMPLES,
    "wzp6_ee_hadZH_Hbb_ecm240": [sample for sample in ZH_OTHER_SAMPLES if "_Hbb_" in sample],
    "wzp6_ee_hadZH_Htautau_ecm240": [sample for sample in ZH_OTHER_SAMPLES if "_Htautau_" in sample],
    "wzp6_ee_hadZH_Hgg_ecm240": [sample for sample in ZH_OTHER_SAMPLES if "_Hgg_" in sample],
    "wzp6_ee_hadZH_Hcc_ecm240": [sample for sample in ZH_OTHER_SAMPLES if "_Hcc_" in sample],
    "wzp6_ee_hadZH_HZZ_ecm240": [sample for sample in ZH_OTHER_SAMPLES if "_HZZ_" in sample],
}

# Process definitions: (filename, label, color, isSignal)
processes = [
    # Backgrounds (will be stacked, order matters: bottom to top)
    ("wz3p6_ee_tautau_ecm240", "#tau#tau", ROOT.kGray + 1, False),
    ("wzp6_ee_hadZH_HZZ_ecm240", "ZH(ZZ)", ROOT.kCyan - 7, False),
    ("wzp6_ee_hadZH_Hcc_ecm240", "ZH(cc)", ROOT.kCyan - 3, False),
    ("wzp6_ee_hadZH_Hgg_ecm240", "ZH(gg)", ROOT.kCyan + 1, False),
    ("wzp6_ee_hadZH_Htautau_ecm240", "ZH(#tau#tau)", ROOT.kCyan + 3, False),
    ("wzp6_ee_hadZH_Hbb_ecm240", "ZH(bb)", ROOT.kTeal - 7, False),
    ("wz3p6_ee_qq_ecm240", "Z/#gamma#rightarrowqq", ROOT.kGreen + 2, False),
    ("p8_ee_ZZ_ecm240", "ZZ", ROOT.kAzure + 1, False),
    ("p8_ee_WW_ecm240", "WW", ROOT.kOrange - 3, False),
    # Signal (summed over all hadronic-Z production modes)
    ("wzp6_ee_hadZH_HWW_ecm240", "ZH (H#rightarrowWW)", ROOT.kRed + 1, True),
]

# Histograms to plot: (name, xtitle, rebin, xmin, xmax, logy)
histograms = [
    ("cutFlow", "Cut stage", 1, -0.5, 8.5, True),
    ("n_leptons_p20", "Number of leptons with p > 20 GeV", 1, -0.5, 5.5, True),
    ("lepton_p", "Lepton momentum [GeV]", 4, 0, 150, False),
    ("lepton_iso", "Lepton isolation", 2, 0, 1, False),
    ("n_leptons_p5", "Number of leptons with p > 5 GeV", 1, -0.5, 5.5, True),
    ("missingEnergy_e", "Missing energy [GeV]", 4, 0, 150, False),
    ("missingEnergy_p", "Missing momentum [GeV]", 4, 0, 150, False),
    ("missingMass", "Missing mass [GeV]", 4, 0, 240, False),
    ("cosTheta_miss", "|cos(#theta_{miss})|", 1, 0, 1, False),
    ("visibleEnergy", "Visible energy (no lepton) [GeV]", 4, 0, 250, False),
    ("njets", "Number of jets", 1, 0, 10, True),
    ("jet0_p", "Jet 0 momentum [GeV]", 4, 0, 120, False),
    ("jet1_p", "Jet 1 momentum [GeV]", 4, 0, 120, False),
    ("jet2_p", "Jet 2 momentum [GeV]", 4, 0, 120, False),
    ("jet3_p", "Jet 3 momentum [GeV]", 4, 0, 120, False),
    ("Zcand_m", "m_{Z cand} [GeV]", 4, 0, 200, False),
    ("Wstar_m", "m_{W*} [GeV]", 4, 0, 150, False),  # W* is off-shell, expect ~40 GeV
    ("Wlep_m", "m_{W_{lep}} [GeV]", 4, 0, 200, False),
    ("Hcand_m", "m_{H cand} [GeV]", 4, 0, 300, False),
    ("Hcand_m_afterZ", "m_{H cand} (after Z cut) [GeV]", 4, 0, 300, False),
    ("Hcand_m_final", "m_{H cand} (final) [GeV]", 4, 0, 300, False),
    ("recoil_m", "Recoil mass [GeV]", 4, 50, 200, False),
    ("recoil_m_afterZ", "Recoil mass (after Z cut) [GeV]", 4, 50, 200, False),
    ("deltaZ", "|m_{jj} - m_{Z}| [GeV]", 4, 0, 50, False),
]

CUT_DIAGNOSTICS = [
    {
        "name": "cut1_exactly_one_lepton",
        "hist": "n_leptons_p20",
        "xtitle": "Number of leptons with p > 20 GeV",
        "rebin": 1,
        "xmin": -0.5,
        "xmax": 5.5,
        "logy": True,
        "kind": "eq_bin",
        "value": 1,
        "label": "Cut 1: exactly one lepton with p > 20 GeV",
    },
    {
        "name": "cut2_lepton_isolation",
        "hist": "lepton_iso",
        "xtitle": "Lepton isolation",
        "rebin": 2,
        "xmin": 0.0,
        "xmax": 1.0,
        "logy": False,
        "kind": "lt",
        "value": 0.15,
        "label": "Cut 2: require lepton isolation < 0.15",
    },
    {
        "name": "cut3_extra_lepton_veto",
        "hist": "n_leptons_p5",
        "xtitle": "Number of leptons with p > 5 GeV",
        "rebin": 1,
        "xmin": -0.5,
        "xmax": 5.5,
        "logy": True,
        "kind": "eq_bin",
        "value": 1,
        "label": "Cut 3: veto extra leptons above 5 GeV",
    },
    {
        "name": "cut4_missing_energy",
        "hist": "missingEnergy_e",
        "xtitle": "Missing energy [GeV]",
        "rebin": 4,
        "xmin": 0.0,
        "xmax": 150.0,
        "logy": False,
        "kind": "gt",
        "value": 20.0,
        "label": "Cut 4: require E_{miss} > 20 GeV",
    },
    {
        "name": "cut5_exactly_four_jets",
        "hist": "njets",
        "xtitle": "Number of jets",
        "rebin": 1,
        "xmin": 0.0,
        "xmax": 8.0,
        "logy": True,
        "kind": "eq_bin",
        "value": 4,
        "label": "Cut 5: require exactly 4 Durham jets",
        "legend": (0.66, 0.62, 0.92, 0.88),
        "legend_text_size": 0.026,
    },
    {
        "name": "cut6_z_mass_window",
        "hist": "Zcand_m",
        "xtitle": "m_{Z cand} [GeV]",
        "rebin": 4,
        "xmin": 40.0,
        "xmax": 150.0,
        "logy": False,
        "kind": "window",
        "lo": 91.19 - 15.0,
        "hi": 91.19 + 15.0,
        "label": "Cut 6: require |m_{Z,cand} - 91.2| < 15 GeV",
    },
    {
        "name": "cut7_recoil_window",
        "hist": "recoil_m_afterZ",
        "xtitle": "Recoil mass (after Z cut) [GeV]",
        "rebin": 4,
        "xmin": 50.0,
        "xmax": 200.0,
        "logy": False,
        "kind": "window",
        "lo": 125.0 - 20.0,
        "hi": 125.0 + 20.0,
        "label": "Cut 7: require |m_{recoil} - 125| < 20 GeV",
    },
]

CUT_LABELS = [
    "All",
    "1lep p>20",
    "ISO",
    "Veto p>5",
    "MET E>20",
    "4jets",
    "Z win",
    "Recoil",
]
CUT_IDS = [f"cut{i}" for i in range(len(CUT_LABELS))]
PERCENT_COL_WIDTH = 12

# ============================================================
# Style settings
# ============================================================

def setStyle():
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetPadTickX(1)
    ROOT.gStyle.SetPadTickY(1)
    ROOT.gStyle.SetHistLineWidth(2)
    ROOT.gStyle.SetLegendBorderSize(0)
    ROOT.gStyle.SetLegendFillColor(0)
    ROOT.gStyle.SetLegendFont(42)
    ROOT.gStyle.SetLegendTextSize(0.035)
    ROOT.gStyle.SetPadLeftMargin(0.14)
    ROOT.gStyle.SetPadRightMargin(0.05)
    ROOT.gStyle.SetPadTopMargin(0.08)
    ROOT.gStyle.SetPadBottomMargin(0.12)
    ROOT.gStyle.SetTitleFont(42, "XYZ")
    ROOT.gStyle.SetTitleSize(0.045, "XYZ")
    ROOT.gStyle.SetLabelFont(42, "XYZ")
    ROOT.gStyle.SetLabelSize(0.04, "XYZ")
    ROOT.gStyle.SetTitleOffset(1.3, "Y")

# ============================================================
# Helper functions
# ============================================================

def getHist(filename, histname):
    """Load histogram from file (already scaled by framework).

    Some entries are logical groups summed over multiple processed samples.
    """
    if filename in MERGED_GROUPS:
        h_merged = None
        for sample_name in MERGED_GROUPS[filename]:
            h = getHist(sample_name, histname)
            if h is None:
                continue
            if h_merged is None:
                h_merged = h.Clone(f"{histname}_{filename}_merged")
                h_merged.SetDirectory(0)
            else:
                h_merged.Add(h)
        return h_merged

    filepath = os.path.join(inputDir, filename + ".root")
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found")
        return None

    f = ROOT.TFile.Open(filepath)
    h = f.Get(histname)
    if not h:
        print(f"Warning: {histname} not found in {filepath}")
        f.Close()
        return None

    h.SetDirectory(0)
    f.Close()

    # NOTE: Histograms from fccanalysis with doScale=True are ALREADY
    # normalized to xsec * intLumi. Do NOT scale again here!

    return h


def _nice_scale_factor(raw_scale):
    """Round a signal scale factor to a readable 1/2/5 x 10^n value."""
    if raw_scale <= 1:
        return 1
    exponent = math.floor(math.log10(raw_scale))
    base = 10 ** exponent
    for multiplier in (1, 2, 5, 10):
        candidate = multiplier * base
        if raw_scale <= candidate:
            return int(candidate)
    return int(10 * base)


def _draw_cut_guides(config, ymin, ymax):
    """Draw cut threshold/window guides on the active pad."""
    line_color = ROOT.kGray + 2
    lines = []
    labels = []

    def _make_line(x):
        line = ROOT.TLine(x, ymin, x, ymax)
        line.SetLineColor(line_color)
        line.SetLineStyle(7)
        line.SetLineWidth(3)
        line.Draw()
        lines.append(line)

    kind = config["kind"]
    if kind == "lt":
        _make_line(config["value"])
    elif kind == "gt":
        _make_line(config["value"])
    elif kind == "window":
        _make_line(config["lo"])
        _make_line(config["hi"])
    elif kind == "eq_bin":
        center = config["value"]
        _make_line(center - 0.5)
        _make_line(center + 0.5)

    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextFont(42)
    latex.SetTextSize(0.030)
    latex.SetTextColor(line_color)
    latex.DrawLatex(0.15, 0.82, config["label"])
    labels.append(latex)
    return lines, labels


def makeCutDiagnosticPlot(config):
    """Create one plot per analysis cut with the corresponding cut guide."""

    histname = config["hist"]
    xtitle = config["xtitle"]
    rebin = config["rebin"]
    xmin = config["xmin"]
    xmax = config["xmax"]
    logy = config["logy"]

    c = ROOT.TCanvas(f"c_{config['name']}", "", 850, 700)
    c.cd()
    if logy:
        c.SetLogy()

    bkg_hists = []
    sig_hists = []
    for fname, label, color, isSignal in processes:
        h = getHist(fname, histname)
        if h is None:
            continue

        if rebin > 1:
            h.Rebin(rebin)

        h.SetLineColor(color)
        h.SetLineWidth(2)
        if isSignal:
            h.SetFillStyle(0)
            sig_hists.append((h, label, color))
        else:
            h.SetFillColor(color)
            h.SetFillStyle(1001)
            bkg_hists.append((h, label, color))

    if not bkg_hists and not sig_hists:
        print(f"Warning: No histograms found for {histname}")
        return

    hs = ROOT.THStack(f"hs_{config['name']}", "")
    for h, _, _ in bkg_hists:
        hs.Add(h)

    h_sig_sum = None
    for h, _, _ in sig_hists:
        if h_sig_sum is None:
            h_sig_sum = h.Clone(f"h_sig_sum_{config['name']}")
            h_sig_sum.SetDirectory(0)
        else:
            h_sig_sum.Add(h)

    bkg_max = hs.GetMaximum() if hs.GetNhists() > 0 else 0.0
    sig_max = h_sig_sum.GetMaximum() if h_sig_sum else 0.0
    signal_scale = 1
    if h_sig_sum and sig_max > 0 and bkg_max > 0:
        signal_scale = _nice_scale_factor(0.25 * bkg_max / sig_max)
        if signal_scale > 1:
            h_sig_sum.Scale(signal_scale)

    if h_sig_sum:
        h_sig_sum.SetLineColor(ROOT.kRed + 1)
        h_sig_sum.SetLineWidth(3)
        h_sig_sum.SetFillStyle(0)

    ymax = max(bkg_max, h_sig_sum.GetMaximum() if h_sig_sum else 0.0)
    if logy:
        ymin = 0.1
        ymax *= 80
    else:
        ymin = 0.0
        ymax *= 1.55

    if hs.GetNhists() > 0:
        hs.Draw("HIST")
        hs.GetXaxis().SetTitle(xtitle)
        hs.GetYaxis().SetTitle("Events")
        hs.GetXaxis().SetRangeUser(xmin, xmax)
        hs.SetMinimum(ymin)
        hs.SetMaximum(ymax)
        hs.GetXaxis().SetTitleSize(0.045)
        hs.GetYaxis().SetTitleSize(0.045)
        hs.GetXaxis().SetLabelSize(0.04)
        hs.GetYaxis().SetLabelSize(0.04)
        hs.GetYaxis().SetTitleOffset(1.3)

    if h_sig_sum:
        h_sig_sum.Draw("HIST SAME")

    guide_lines, guide_labels = _draw_cut_guides(config, ymin, ymax)

    legend_coords = config.get("legend", (0.56, 0.58, 0.92, 0.88))
    leg = ROOT.TLegend(*legend_coords)
    leg.SetTextSize(config.get("legend_text_size", 0.031))
    if h_sig_sum:
        sig_label = "Signal (ZH, H#rightarrowWW)"
        if signal_scale > 1:
            sig_label += f" #times {signal_scale}"
        leg.AddEntry(h_sig_sum, sig_label, "l")
    for h, label, _ in reversed(bkg_hists):
        leg.AddEntry(h, label, "f")
    leg.Draw()

    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextFont(42)
    latex.SetTextSize(0.040)
    latex.DrawLatex(0.14, 0.93, "#bf{FCC-ee} #it{Simulation}")
    latex.SetTextSize(0.035)
    latex.DrawLatex(0.66, 0.93, "#sqrt{s} = 240 GeV, 10.8 ab^{-1}")

    outdir = os.path.join(outputDir, "cut_diagnostics")
    os.makedirs(outdir, exist_ok=True)
    c.SaveAs(os.path.join(outdir, f"{config['name']}.pdf"))
    c.SaveAs(os.path.join(outdir, f"{config['name']}.png"))
    c.Close()


def collectCutflowData():
    """Collect cutflow yields for all configured processes."""

    ncuts = len(CUT_LABELS)
    process_rows = []
    process_eff_rows = []
    total_sig = [0.0] * ncuts
    total_bkg = [0.0] * ncuts

    for fname, label, color, isSignal in processes:
        h = getHist(fname, "cutFlow")
        if h is None:
            continue

        values = [h.GetBinContent(i + 1) for i in range(ncuts)]
        process_rows.append((label, values, isSignal))

        base = values[0] if values and values[0] > 0 else 0.0
        eff_values = [100.0 * val / base if base > 0 else None for val in values]
        process_eff_rows.append((label, eff_values, isSignal))

        for i, val in enumerate(values):
            if isSignal:
                total_sig[i] += val
            else:
                total_bkg[i] += val

    s_over_b = []
    s_over_sqrt_b = []
    for s, b in zip(total_sig, total_bkg):
        if b > 0:
            s_over_b.append(s / b)
            s_over_sqrt_b.append(s / (b ** 0.5))
        else:
            s_over_b.append(None)
            s_over_sqrt_b.append(None)

    sig_base = total_sig[0] if total_sig and total_sig[0] > 0 else 0.0
    bkg_base = total_bkg[0] if total_bkg and total_bkg[0] > 0 else 0.0
    total_sig_eff = [100.0 * val / sig_base if sig_base > 0 else None for val in total_sig]
    total_bkg_eff = [100.0 * val / bkg_base if bkg_base > 0 else None for val in total_bkg]

    return {
        "cut_labels": CUT_LABELS,
        "cut_ids": CUT_IDS,
        "process_rows": process_rows,
        "process_eff_rows": process_eff_rows,
        "total_sig": total_sig,
        "total_bkg": total_bkg,
        "total_sig_eff": total_sig_eff,
        "total_bkg_eff": total_bkg_eff,
        "s_over_b": s_over_b,
        "s_over_sqrt_b": s_over_sqrt_b,
    }


def _format_table_row(label, values, float_fmt=".0f"):
    row = f"{label:<25}"
    for val in values:
        if val is None:
            row += f"{'--':>10}"
        else:
            row += f"{val:>10{float_fmt}}"
    return row


def _format_percent_row(label, values):
    row = f"{label:<25}"
    for val in values:
        if val is None:
            row += f"{'--':>{PERCENT_COL_WIDTH}}"
        else:
            row += f"{f'{val:.2f}%':>{PERCENT_COL_WIDTH}}"
    return row


def _format_cut_header(cut_keys, value_width=10):
    header = f"{'Process':<25}"
    for key in cut_keys:
        header += f"{key:>{value_width}}"
    return header


def writeCutflowText(summary):
    """Write cutflow table to a plain-text file."""

    os.makedirs(outputDir, exist_ok=True)
    outpath = os.path.join(outputDir, "cutFlow_cutflow.txt")

    lines = []
    lines.append("=" * 80)
    lines.append("CUTFLOW TABLE (normalized to 10.8 ab^-1)")
    lines.append("=" * 80)

    header = f"{'Process':<25}"
    for lab in summary["cut_labels"]:
        header += f"{lab:>10}"
    lines.append(header)
    lines.append("-" * 95)

    for label, values, isSignal in summary["process_rows"]:
        lines.append(_format_table_row(label, values, ".0f"))

    lines.append("-" * 95)
    lines.append(_format_table_row("Total Signal", summary["total_sig"], ".1f"))
    lines.append(_format_table_row("Total Background", summary["total_bkg"], ".1f"))
    lines.append("-" * 95)
    lines.append(_format_table_row("S/B", summary["s_over_b"], ".4f"))
    lines.append(_format_table_row("S/sqrt(B)", summary["s_over_sqrt_b"], ".1f"))
    lines.append("=" * 95)

    with open(outpath, "w", encoding="ascii") as f:
        f.write("\n".join(lines) + "\n")


def writeCutflowLatex(summary):
    """Write cutflow table to a LaTeX file."""

    os.makedirs(outputDir, exist_ok=True)
    outpath = os.path.join(outputDir, "cutFlow_cutflow.tex")

    cols = "l" + "r" * len(summary["cut_labels"])
    lines = [
        r"\begin{tabular}{" + cols + r"}",
        r"\hline",
    ]

    header = ["Process"] + summary["cut_labels"]
    lines.append(" & ".join(header) + r" \\")
    lines.append(r"\hline")

    for label, values, isSignal in summary["process_rows"]:
        row = [label] + [f"{val:.0f}" for val in values]
        lines.append(" & ".join(row) + r" \\")

    lines.append(r"\hline")
    lines.append(" & ".join(["Total Signal"] + [f"{v:.1f}" for v in summary["total_sig"]]) + r" \\")
    lines.append(" & ".join(["Total Background"] + [f"{v:.1f}" for v in summary["total_bkg"]]) + r" \\")
    lines.append(r"\hline")
    lines.append(" & ".join(["S/B"] + [('--' if v is None else f"{v:.4f}") for v in summary["s_over_b"]]) + r" \\")
    lines.append(" & ".join(["S/$\\sqrt{B}$"] + [('--' if v is None else f"{v:.1f}") for v in summary["s_over_sqrt_b"]]) + r" \\")
    lines.append(r"\hline")
    lines.append(r"\end{tabular}")

    with open(outpath, "w", encoding="ascii") as f:
        f.write("\n".join(lines) + "\n")


def makeCutflowPdf(summary):
    """Render a cutflow table as a PDF, similar to standard FCCAnalysis outputs."""

    os.makedirs(outputDir, exist_ok=True)
    outpath = os.path.join(outputDir, "cutFlow_cutflow.pdf")

    c = ROOT.TCanvas("cutflow_table", "", 1800, 700)
    c.cd()

    title = ROOT.TLatex()
    title.SetNDC()
    title.SetTextFont(42)
    title.SetTextSize(0.035)
    title.DrawLatex(0.03, 0.95, "Cutflow table, normalized to 10.8 ab^{-1}")

    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextFont(42)
    latex.SetTextSize(0.024)

    x_process = 0.03
    x_start = 0.32
    x_end = 0.97
    ncuts = len(summary["cut_labels"])
    x_cuts = [x_start + i * (x_end - x_start) / max(1, ncuts - 1) for i in range(ncuts)]

    y = 0.88
    latex.SetTextAlign(13)
    latex.DrawLatex(x_process, y, "Process")
    latex.SetTextAlign(23)
    for x, label in zip(x_cuts, summary["cut_labels"]):
        latex.DrawLatex(x, y, label)

    rows = []
    for label, values, isSignal in summary["process_rows"]:
        rows.append((label, values))
    rows.append(("Total Signal", summary["total_sig"]))
    rows.append(("Total Background", summary["total_bkg"]))
    rows.append(("S/B", summary["s_over_b"]))
    rows.append(("S/sqrt(B)", summary["s_over_sqrt_b"]))

    y -= 0.07
    for label, values in rows:
        latex.SetTextAlign(13)
        latex.DrawLatex(x_process, y, label)
        latex.SetTextAlign(23)
        for x, val in zip(x_cuts, values):
            if val is None:
                txt = "--"
            elif label in ("S/B",):
                txt = f"{val:.4f}"
            elif label in ("S/sqrt(B)",):
                txt = f"{val:.1f}"
            elif label.startswith("Total"):
                txt = f"{val:.1f}"
            else:
                txt = f"{val:.0f}"
            latex.DrawLatex(x, y, txt)
        y -= 0.06

    c.SaveAs(outpath)
    c.SaveAs(outpath.replace(".pdf", ".png"))
    c.Close()


def writeCutflowEfficiencyText(summary):
    """Write cumulative cut efficiencies in percent to a plain-text file."""

    os.makedirs(outputDir, exist_ok=True)
    outpath = os.path.join(outputDir, "cutFlow_efficiency.txt")

    rule = "-" * (25 + PERCENT_COL_WIDTH * len(summary["cut_ids"]))
    lines = []
    lines.append("=" * 80)
    lines.append("CUTFLOW EFFICIENCY TABLE [%], cumulative w.r.t. cut0 (All)")
    lines.append("=" * 80)
    lines.append(_format_cut_header(summary["cut_ids"], PERCENT_COL_WIDTH))
    lines.append(rule)

    for label, values, isSignal in summary["process_eff_rows"]:
        lines.append(_format_percent_row(label, values))

    lines.append(rule)
    lines.append(_format_percent_row("Total Signal eff", summary["total_sig_eff"]))
    lines.append(_format_percent_row("Total Bkg eff", summary["total_bkg_eff"]))
    lines.append("=" * len(rule))
    lines.append("")
    lines.append("Cut definitions:")
    for cut_id, label in zip(summary["cut_ids"], summary["cut_labels"]):
        lines.append(f"  {cut_id}: {label}")

    with open(outpath, "w", encoding="ascii") as f:
        f.write("\n".join(lines) + "\n")

def writeCutflowEfficiencyLatex(summary):
    """Write cumulative cut efficiencies in percent to a LaTeX file."""

    os.makedirs(outputDir, exist_ok=True)
    outpath = os.path.join(outputDir, "cutFlow_efficiency.tex")

    cols = "l" + "r" * len(summary["cut_ids"])
    ncols = len(summary["cut_ids"]) + 1
    lines = [
        r"\begin{tabular}{" + cols + r"}",
        r"\hline",
    ]

    header = ["Process"] + summary["cut_ids"]
    lines.append(" & ".join(header) + r" \\")
    lines.append(r"\hline")

    for label, values, isSignal in summary["process_eff_rows"]:
        row = [label] + [("--" if v is None else f"{v:.2f}\\%") for v in values]
        lines.append(" & ".join(row) + r" \\")

    lines.append(r"\hline")
    lines.append(" & ".join(["Total Signal eff"] + [("--" if v is None else f"{v:.2f}\\%") for v in summary["total_sig_eff"]]) + r" \\")
    lines.append(" & ".join(["Total Bkg eff"] + [("--" if v is None else f"{v:.2f}\\%") for v in summary["total_bkg_eff"]]) + r" \\")
    lines.append(r"\hline")
    lines.append(rf"\multicolumn{{{ncols}}}{{l}}{{Cut definitions:}} \\")
    for cut_id, label in zip(summary["cut_ids"], summary["cut_labels"]):
        safe_label = label.replace("_", r"\_").replace("%", r"\%")
        lines.append(rf"\multicolumn{{{ncols}}}{{l}}{{{cut_id}: {safe_label}}} \\")
    lines.append(r"\hline")
    lines.append(r"\end{tabular}")

    with open(outpath, "w", encoding="ascii") as f:
        f.write("\n".join(lines) + "\n")

def makeCutflowEfficiencyPdf(summary):
    """Render a cumulative cut-efficiency table as a PDF."""

    os.makedirs(outputDir, exist_ok=True)
    outpath = os.path.join(outputDir, "cutFlow_efficiency.pdf")

    c = ROOT.TCanvas("cutflow_eff_table", "", 1800, 850)
    c.cd()

    title = ROOT.TLatex()
    title.SetNDC()
    title.SetTextFont(42)
    title.SetTextSize(0.035)
    title.DrawLatex(0.03, 0.95, "Cutflow efficiencies [%], cumulative w.r.t. cut0 (All)")

    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextFont(42)
    latex.SetTextSize(0.024)

    x_process = 0.03
    x_start = 0.32
    x_end = 0.97
    ncuts = len(summary["cut_ids"])
    x_cuts = [x_start + i * (x_end - x_start) / max(1, ncuts - 1) for i in range(ncuts)]

    y = 0.88
    latex.SetTextAlign(13)
    latex.DrawLatex(x_process, y, "Process")
    latex.SetTextAlign(23)
    for x, label in zip(x_cuts, summary["cut_ids"]):
        latex.DrawLatex(x, y, label)

    rows = []
    for label, values, isSignal in summary["process_eff_rows"]:
        rows.append((label, values))
    rows.append(("Total Signal eff", summary["total_sig_eff"]))
    rows.append(("Total Bkg eff", summary["total_bkg_eff"]))

    y -= 0.07
    for label, values in rows:
        latex.SetTextAlign(13)
        latex.DrawLatex(x_process, y, label)
        latex.SetTextAlign(23)
        for x, val in zip(x_cuts, values):
            txt = "--" if val is None else f"{val:.2f}%"
            latex.DrawLatex(x, y, txt)
        y -= 0.06

    legend = ROOT.TLatex()
    legend.SetNDC()
    legend.SetTextFont(42)
    legend.SetTextSize(0.020)
    legend.SetTextAlign(13)
    legend.DrawLatex(0.03, 0.24, "Cut definitions:")
    for idx, (cut_id, label) in enumerate(zip(summary["cut_ids"], summary["cut_labels"])):
        x = 0.03 + (idx % 2) * 0.44
        yy = 0.20 - (idx // 2) * 0.04
        legend.DrawLatex(x, yy, f"{cut_id}: {label}")

    c.SaveAs(outpath)
    c.SaveAs(outpath.replace(".pdf", ".png"))
    c.Close()

def makePlot(histname, xtitle, rebin, xmin, xmax, logy):
    """Create a single plot with stacked backgrounds and signal overlay"""

    # Create canvas
    c = ROOT.TCanvas("c", "", 800, 700)
    c.cd()

    if logy:
        c.SetLogy()

    # Prepare histograms
    bkg_hists = []
    sig_hists = []

    for fname, label, color, isSignal in processes:
        h = getHist(fname, histname)
        if h is None:
            continue

        if rebin > 1:
            h.Rebin(rebin)

        h.SetLineColor(color)
        h.SetLineWidth(2)

        if isSignal:
            h.SetFillStyle(0)
            sig_hists.append((h, label, color))
        else:
            h.SetFillColor(color)
            h.SetFillStyle(1001)
            bkg_hists.append((h, label, color))

    if not bkg_hists and not sig_hists:
        print(f"Warning: No histograms found for {histname}")
        return

    # Create THStack for backgrounds
    hs = ROOT.THStack("hs", "")
    for h, label, color in bkg_hists:
        hs.Add(h)

    # Sum signals for combined overlay
    h_sig_sum = None
    for h, label, color in sig_hists:
        if h_sig_sum is None:
            h_sig_sum = h.Clone("h_sig_sum")
        else:
            h_sig_sum.Add(h)

    if h_sig_sum:
        h_sig_sum.SetLineColor(ROOT.kRed+1)
        h_sig_sum.SetLineWidth(3)
        h_sig_sum.SetFillStyle(0)

    # Determine y-axis range
    ymax = 0
    if hs.GetNhists() > 0:
        ymax = max(ymax, hs.GetMaximum())
    if h_sig_sum:
        ymax = max(ymax, h_sig_sum.GetMaximum())

    if logy:
        ymin = 0.1
        ymax *= 50
    else:
        ymin = 0
        ymax *= 1.5

    # Draw
    if hs.GetNhists() > 0:
        hs.Draw("HIST")
        hs.GetXaxis().SetTitle(xtitle)
        hs.GetYaxis().SetTitle("Events")
        hs.GetXaxis().SetRangeUser(xmin, xmax)
        hs.SetMinimum(ymin)
        hs.SetMaximum(ymax)
        hs.GetXaxis().SetTitleSize(0.045)
        hs.GetYaxis().SetTitleSize(0.045)
        hs.GetXaxis().SetLabelSize(0.04)
        hs.GetYaxis().SetLabelSize(0.04)
        hs.GetYaxis().SetTitleOffset(1.3)

    if h_sig_sum:
        h_sig_sum.Draw("HIST SAME")

    # Legend
    leg = ROOT.TLegend(0.60, 0.65, 0.92, 0.88)
    leg.SetTextSize(0.032)

    if h_sig_sum:
        leg.AddEntry(h_sig_sum, "Signal (ZH, H#rightarrowWW)", "l")

    # Add backgrounds in reverse order (top to bottom in legend)
    for h, label, color in reversed(bkg_hists):
        leg.AddEntry(h, label, "f")

    leg.Draw()

    # CMS-style label
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextFont(42)
    latex.SetTextSize(0.04)
    latex.DrawLatex(0.14, 0.93, "#bf{FCC-ee} #it{Simulation}")
    latex.SetTextSize(0.035)
    latex.DrawLatex(0.70, 0.93, "#sqrt{s} = 240 GeV, 10.8 ab^{-1}")

    os.makedirs(outputDir, exist_ok=True)
    c.SaveAs(os.path.join(outputDir, f"{histname}.pdf"))
    c.SaveAs(os.path.join(outputDir, f"{histname}.png"))

    c.Close()


def makeCutflowTable():
    """Print cutflow table and save text/tex/pdf outputs."""

    summary = collectCutflowData()

    print("\n" + "=" * 80)
    print("CUTFLOW TABLE (normalized to 10.8 ab^-1)")
    print("=" * 80)
    header = f"{'Process':<25}"
    for lab in summary["cut_labels"]:
        header += f"{lab:>10}"
    print(header)
    print("-" * 95)

    for label, values, isSignal in summary["process_rows"]:
        print(_format_table_row(label, values, ".0f"))

    print("-" * 95)
    print(_format_table_row("Total Signal", summary["total_sig"], ".1f"))
    print(_format_table_row("Total Background", summary["total_bkg"], ".1f"))
    print("-" * 95)
    print(_format_table_row("S/B", summary["s_over_b"], ".4f"))
    print(_format_table_row("S/sqrt(B)", summary["s_over_sqrt_b"], ".1f"))
    print("=" * 95 + "\n")

    print("\n" + "=" * 80)
    print("CUTFLOW EFFICIENCY TABLE [%], cumulative w.r.t. cut0 (All)")
    print("=" * 80)
    rule = "-" * (25 + PERCENT_COL_WIDTH * len(summary["cut_ids"]))
    print(_format_cut_header(summary["cut_ids"], PERCENT_COL_WIDTH))
    print(rule)

    for label, values, isSignal in summary["process_eff_rows"]:
        print(_format_percent_row(label, values))

    print(rule)
    print(_format_percent_row("Total Signal eff", summary["total_sig_eff"]))
    print(_format_percent_row("Total Bkg eff", summary["total_bkg_eff"]))
    print("=" * len(rule))
    print("Cut definitions:")
    for cut_id, label in zip(summary["cut_ids"], summary["cut_labels"]):
        print(f"  {cut_id}: {label}")
    print()

    writeCutflowText(summary)
    writeCutflowLatex(summary)
    makeCutflowPdf(summary)
    writeCutflowEfficiencyText(summary)
    writeCutflowEfficiencyLatex(summary)
    makeCutflowEfficiencyPdf(summary)


def makeNormalizedPlot(histname, xtitle, rebin, xmin, xmax, logy=False):
    """Create normalized stacked plot (signal and background both normalized to unit area)"""

    c = ROOT.TCanvas("c", "", 800, 700)
    c.cd()
    if logy:
        c.SetLogy()

    # Prepare histograms
    bkg_hists = []
    sig_hists = []

    for fname, label, color, isSignal in processes:
        h = getHist(fname, histname)
        if h is None:
            continue

        if rebin > 1:
            h.Rebin(rebin)

        h.SetLineColor(color)
        h.SetLineWidth(2)

        if isSignal:
            h.SetFillStyle(0)
            sig_hists.append((h, label, color))
        else:
            h.SetFillColor(color)
            h.SetFillStyle(1001)
            bkg_hists.append((h, label, color))

    if not bkg_hists and not sig_hists:
        print(f"Warning: No histograms found for {histname}")
        return

    # Sum all backgrounds
    h_bkg_sum = None
    for h, label, color in bkg_hists:
        if h_bkg_sum is None:
            h_bkg_sum = h.Clone("h_bkg_sum")
        else:
            h_bkg_sum.Add(h)

    # Sum all signals
    h_sig_sum = None
    for h, label, color in sig_hists:
        if h_sig_sum is None:
            h_sig_sum = h.Clone("h_sig_sum")
        else:
            h_sig_sum.Add(h)

    # Normalize both to unit area
    if h_bkg_sum and h_bkg_sum.Integral() > 0:
        h_bkg_sum.Scale(1.0 / h_bkg_sum.Integral())
    if h_sig_sum and h_sig_sum.Integral() > 0:
        h_sig_sum.Scale(1.0 / h_sig_sum.Integral())

    # Style
    if h_bkg_sum:
        h_bkg_sum.SetFillColor(ROOT.kAzure+1)
        h_bkg_sum.SetFillStyle(3004)
        h_bkg_sum.SetLineColor(ROOT.kAzure+1)
        h_bkg_sum.SetLineWidth(2)

    if h_sig_sum:
        h_sig_sum.SetLineColor(ROOT.kRed+1)
        h_sig_sum.SetLineWidth(3)
        h_sig_sum.SetFillStyle(0)

    # Determine y-axis range
    ymax = 0
    if h_bkg_sum:
        ymax = max(ymax, h_bkg_sum.GetMaximum())
    if h_sig_sum:
        ymax = max(ymax, h_sig_sum.GetMaximum())

    if logy:
        ymin = 1e-4
        ymax *= 10
    else:
        ymin = 0
        ymax *= 1.4

    # Draw
    first = True
    if h_bkg_sum:
        h_bkg_sum.GetXaxis().SetTitle(xtitle)
        h_bkg_sum.GetYaxis().SetTitle("Normalized")
        h_bkg_sum.GetXaxis().SetRangeUser(xmin, xmax)
        h_bkg_sum.SetMinimum(ymin)
        h_bkg_sum.SetMaximum(ymax)
        h_bkg_sum.GetXaxis().SetTitleSize(0.045)
        h_bkg_sum.GetYaxis().SetTitleSize(0.045)
        h_bkg_sum.GetXaxis().SetLabelSize(0.04)
        h_bkg_sum.GetYaxis().SetLabelSize(0.04)
        h_bkg_sum.GetYaxis().SetTitleOffset(1.3)
        h_bkg_sum.Draw("HIST")
        first = False

    if h_sig_sum:
        if first:
            h_sig_sum.GetXaxis().SetTitle(xtitle)
            h_sig_sum.GetYaxis().SetTitle("Normalized")
            h_sig_sum.GetXaxis().SetRangeUser(xmin, xmax)
            h_sig_sum.SetMinimum(ymin)
            h_sig_sum.SetMaximum(ymax)
            h_sig_sum.GetXaxis().SetTitleSize(0.045)
            h_sig_sum.GetYaxis().SetTitleSize(0.045)
            h_sig_sum.GetXaxis().SetLabelSize(0.04)
            h_sig_sum.GetYaxis().SetLabelSize(0.04)
            h_sig_sum.GetYaxis().SetTitleOffset(1.3)
            h_sig_sum.Draw("HIST")
        else:
            h_sig_sum.Draw("HIST SAME")

    # Legend
    leg = ROOT.TLegend(0.60, 0.75, 0.92, 0.88)
    leg.SetTextSize(0.032)
    if h_sig_sum:
        leg.AddEntry(h_sig_sum, "Signal (ZH, H#rightarrowWW)", "l")
    if h_bkg_sum:
        leg.AddEntry(h_bkg_sum, "Background (all)", "f")
    leg.Draw()

    # CMS-style label
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextFont(42)
    latex.SetTextSize(0.04)
    latex.DrawLatex(0.14, 0.93, "#bf{FCC-ee} #it{Simulation} (normalized)")
    latex.SetTextSize(0.035)
    latex.DrawLatex(0.70, 0.93, "#sqrt{s} = 240 GeV")

    os.makedirs(outputDir, exist_ok=True)
    c.SaveAs(os.path.join(outputDir, f"{histname}_norm.pdf"))
    c.SaveAs(os.path.join(outputDir, f"{histname}_norm.png"))

    c.Close()


def makeComparisonPlot(histname, xtitle, rebin, xmin, xmax):
    """Create shape comparison plot (normalized to unit area)"""

    c = ROOT.TCanvas("c", "", 800, 600)
    c.cd()

    # Only compare signal vs main backgrounds
    compare = [
        ("wzp6_ee_hadZH_HWW_ecm240", "Signal (ZH, H#rightarrowWW)", ROOT.kRed+1),
        ("p8_ee_WW_ecm240", "WW bkg", ROOT.kOrange-3),
        ("p8_ee_ZZ_ecm240", "ZZ bkg", ROOT.kAzure+1),
    ]

    hists = []
    for fname, label, color in compare:
        h = getHist(fname, histname)
        if h is None:
            continue

        if rebin > 1:
            h.Rebin(rebin)

        # Normalize to unit area
        if h.Integral() > 0:
            h.Scale(1.0 / h.Integral())

        h.SetLineColor(color)
        h.SetLineWidth(3)
        h.SetFillStyle(0)
        hists.append((h, label))

    if not hists:
        return

    # Find y-axis range
    ymax = max(h.GetMaximum() for h, _ in hists) * 1.4

    # Draw
    for i, (h, label) in enumerate(hists):
        h.GetXaxis().SetTitle(xtitle)
        h.GetYaxis().SetTitle("Normalized")
        h.GetXaxis().SetRangeUser(xmin, xmax)
        h.SetMaximum(ymax)
        h.SetMinimum(0)
        if i == 0:
            h.Draw("HIST")
        else:
            h.Draw("HIST SAME")

    # Legend
    leg = ROOT.TLegend(0.60, 0.70, 0.92, 0.88)
    for h, label in hists:
        leg.AddEntry(h, label, "l")
    leg.Draw()

    # Label
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextFont(42)
    latex.SetTextSize(0.04)
    latex.DrawLatex(0.14, 0.93, "#bf{FCC-ee} #it{Simulation} (shape comparison)")

    os.makedirs(outputDir, exist_ok=True)
    c.SaveAs(os.path.join(outputDir, f"{histname}_shape.pdf"))
    c.SaveAs(os.path.join(outputDir, f"{histname}_shape.png"))

    c.Close()


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    setStyle()

    print("=" * 60)
    print("H->WW->lvqq Analysis Plotting Script")
    print("=" * 60)
    print(f"Input directory:  {inputDir}")
    print(f"Output directory: {outputDir}")
    print(f"Luminosity:       {intLumi/1e6:.1f} ab^-1")
    print("=" * 60)

    # Check input directory
    if not os.path.exists(inputDir):
        print(f"ERROR: Input directory {inputDir} does not exist!")
        print("Please run the analysis first with:")
        print("  fccanalysis run h_hww_lvqq.py")
        sys.exit(1)

    # Make all stacked plots (unnormalized)
    print("\nGenerating stacked plots (unnormalized)...")
    for hname, xtitle, rebin, xmin, xmax, logy in histograms:
        print(f"  {hname}...")
        makePlot(hname, xtitle, rebin, xmin, xmax, logy)

    # Make normalized plots (signal vs background, both normalized to unit area)
    print("\nGenerating normalized plots...")
    norm_hists = [
        ("lepton_p", "Lepton momentum [GeV]", 4, 0, 150),
        ("lepton_iso", "Lepton isolation", 2, 0, 1),
        ("missingEnergy_e", "Missing energy [GeV]", 4, 0, 150),
        ("missingEnergy_p", "Missing momentum [GeV]", 4, 0, 150),
        ("missingMass", "Missing mass [GeV]", 4, 0, 240),
        ("cosTheta_miss", "|cos(#theta_{miss})|", 1, 0, 1),
        ("visibleEnergy", "Visible energy (no lepton) [GeV]", 4, 0, 250),
        ("jet0_p", "Jet 0 momentum [GeV]", 4, 0, 120),
        ("jet1_p", "Jet 1 momentum [GeV]", 4, 0, 120),
        ("jet2_p", "Jet 2 momentum [GeV]", 4, 0, 120),
        ("jet3_p", "Jet 3 momentum [GeV]", 4, 0, 120),
        ("Zcand_m", "m_{Z cand} [GeV]", 4, 0, 200),
        ("Wstar_m", "m_{W*} [GeV]", 4, 0, 150),
        ("Wlep_m", "m_{W_{lep}} [GeV]", 4, 0, 200),
        ("Hcand_m", "m_{H cand} [GeV]", 4, 50, 250),
        ("Hcand_m_afterZ", "m_{H cand} (after Z cut) [GeV]", 4, 50, 250),
        ("Hcand_m_final", "m_{H cand} (final) [GeV]", 4, 50, 250),
        ("recoil_m", "Recoil mass [GeV]", 4, 50, 200),
        ("recoil_m_afterZ", "Recoil mass (after Z cut) [GeV]", 4, 50, 200),
        ("deltaZ", "|m_{jj} - m_{Z}| [GeV]", 4, 0, 50),
    ]
    for hname, xtitle, rebin, xmin, xmax in norm_hists:
        print(f"  {hname}_norm...")
        makeNormalizedPlot(hname, xtitle, rebin, xmin, xmax)

    # Make shape comparison plots (signal vs WW vs ZZ separately)
    print("\nGenerating shape comparison plots...")
    shape_hists = [
        ("Zcand_m", "m_{Z cand} [GeV]", 4, 0, 200),
        ("Wstar_m", "m_{W*} [GeV]", 4, 0, 150),
        ("Hcand_m", "m_{H cand} [GeV]", 4, 50, 250),
        ("recoil_m", "Recoil mass [GeV]", 4, 50, 200),
        ("deltaZ", "|m_{jj} - m_{Z}| [GeV]", 4, 0, 50),
        ("lepton_p", "Lepton momentum [GeV]", 4, 0, 150),
        ("lepton_iso", "Lepton isolation", 2, 0, 1),
        ("missingEnergy_e", "Missing energy [GeV]", 4, 0, 150),
        ("missingEnergy_p", "Missing momentum [GeV]", 4, 0, 150),
        ("missingMass", "Missing mass [GeV]", 4, 0, 240),
        ("cosTheta_miss", "|cos(#theta_{miss})|", 1, 0, 1),
        ("visibleEnergy", "Visible energy (no lepton) [GeV]", 4, 0, 250),
        ("jet0_p", "Jet 0 momentum [GeV]", 4, 0, 120),
        ("jet1_p", "Jet 1 momentum [GeV]", 4, 0, 120),
        ("jet2_p", "Jet 2 momentum [GeV]", 4, 0, 120),
        ("jet3_p", "Jet 3 momentum [GeV]", 4, 0, 120),
    ]
    for hname, xtitle, rebin, xmin, xmax in shape_hists:
        print(f"  {hname}_shape...")
        makeComparisonPlot(hname, xtitle, rebin, xmin, xmax)

    # Print cutflow table
    makeCutflowTable()

    # Dedicated plots for each analysis cut
    print("\nGenerating cut-diagnostic plots...")
    for config in CUT_DIAGNOSTICS:
        print(f"  {config['name']}...")
        makeCutDiagnosticPlot(config)

    print(f"All plots saved to: {outputDir}")
    print("Done!")
