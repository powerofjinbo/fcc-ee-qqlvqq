# Annotated rewrite generated for: plots_lvqq.py
# L1 [Original comment]: #!/usr/bin/env python3
#!/usr/bin/env python3
# L2 [Executable statement]: """
"""
# L3 [Executable statement]: Plotting script for H->WW->lvqq analysis
Plotting script for H->WW->lvqq analysis
# L4 [Executable statement]: Produces paper-style plots with stacked backgrounds and signal overlay
Produces paper-style plots with stacked backgrounds and signal overlay
# L5 [Executable statement]: """
"""
# L6 [Blank separator]: 

# L7 [Import statement]: import ROOT
import ROOT
# L8 [Import statement]: import os
import os
# L9 [Import statement]: import sys
import sys
# L10 [Blank separator]: 

# L11 [Import statement]: from ml_config import SIGNAL_SAMPLES, ZH_OTHER_SAMPLES
from ml_config import SIGNAL_SAMPLES, ZH_OTHER_SAMPLES
# L12 [Blank separator]: 

# L13 [Original comment]: # Suppress ROOT info messages
# Suppress ROOT info messages
# L14 [Executable statement]: ROOT.gROOT.SetBatch(True)
ROOT.gROOT.SetBatch(True)
# L15 [Executable statement]: ROOT.gErrorIgnoreLevel = ROOT.kWarning
ROOT.gErrorIgnoreLevel = ROOT.kWarning
# L16 [Blank separator]: 

# L17 [Original comment]: # ============================================================
# ============================================================
# L18 [Original comment]: # Configuration
# Configuration
# L19 [Original comment]: # ============================================================
# ============================================================
# L20 [Blank separator]: 

# L21 [Executable statement]: inputDir = "output/h_hww_lvqq/histmaker/ecm240/"
inputDir = "output/h_hww_lvqq/histmaker/ecm240/"
# L22 [Executable statement]: outputDir = "plots_lvqq/"
outputDir = "plots_lvqq/"
# L23 [Blank separator]: 

# L24 [Original comment]: # Integrated luminosity (pb^-1)
# Integrated luminosity (pb^-1)
# L25 [Executable statement]: intLumi = 10.8e6  # 10.8 ab^-1 at 240 GeV
intLumi = 10.8e6  # 10.8 ab^-1 at 240 GeV
# L26 [Blank separator]: 

# L27 [Original comment]: # qq flavors to merge into one "Z/gamma->qq" entry for plotting
# qq flavors to merge into one "Z/gamma->qq" entry for plotting
# L28 [Executable statement]: QQ_MERGE = ["wz3p6_ee_uu_ecm240", "wz3p6_ee_dd_ecm240", "wz3p6_ee_cc_ecm240",
QQ_MERGE = ["wz3p6_ee_uu_ecm240", "wz3p6_ee_dd_ecm240", "wz3p6_ee_cc_ecm240",
# L29 [Executable statement]:             "wz3p6_ee_ss_ecm240", "wz3p6_ee_bb_ecm240"]
            "wz3p6_ee_ss_ecm240", "wz3p6_ee_bb_ecm240"]
# L30 [Blank separator]: 

# L31 [Executable statement]: MERGED_GROUPS = {
MERGED_GROUPS = {
# L32 [Executable statement]:     "wz3p6_ee_qq_ecm240": QQ_MERGE,
    "wz3p6_ee_qq_ecm240": QQ_MERGE,
# L33 [Executable statement]:     "wzp6_ee_hadZH_HWW_ecm240": SIGNAL_SAMPLES,
    "wzp6_ee_hadZH_HWW_ecm240": SIGNAL_SAMPLES,
# L34 [Executable statement]:     "wzp6_ee_hadZH_Hbb_ecm240": [sample for sample in ZH_OTHER_SAMPLES if "_Hbb_" in sample],
    "wzp6_ee_hadZH_Hbb_ecm240": [sample for sample in ZH_OTHER_SAMPLES if "_Hbb_" in sample],
# L35 [Executable statement]:     "wzp6_ee_hadZH_Htautau_ecm240": [sample for sample in ZH_OTHER_SAMPLES if "_Htautau_" in sample],
    "wzp6_ee_hadZH_Htautau_ecm240": [sample for sample in ZH_OTHER_SAMPLES if "_Htautau_" in sample],
# L36 [Executable statement]:     "wzp6_ee_hadZH_Hgg_ecm240": [sample for sample in ZH_OTHER_SAMPLES if "_Hgg_" in sample],
    "wzp6_ee_hadZH_Hgg_ecm240": [sample for sample in ZH_OTHER_SAMPLES if "_Hgg_" in sample],
# L37 [Executable statement]:     "wzp6_ee_hadZH_Hcc_ecm240": [sample for sample in ZH_OTHER_SAMPLES if "_Hcc_" in sample],
    "wzp6_ee_hadZH_Hcc_ecm240": [sample for sample in ZH_OTHER_SAMPLES if "_Hcc_" in sample],
# L38 [Executable statement]:     "wzp6_ee_hadZH_HZZ_ecm240": [sample for sample in ZH_OTHER_SAMPLES if "_HZZ_" in sample],
    "wzp6_ee_hadZH_HZZ_ecm240": [sample for sample in ZH_OTHER_SAMPLES if "_HZZ_" in sample],
# L39 [Executable statement]: }
}
# L40 [Blank separator]: 

# L41 [Original comment]: # Process definitions: (filename, label, color, isSignal)
# Process definitions: (filename, label, color, isSignal)
# L42 [Executable statement]: processes = [
processes = [
# L43 [Original comment]:     # Backgrounds (will be stacked, order matters: bottom to top)
    # Backgrounds (will be stacked, order matters: bottom to top)
# L44 [Executable statement]:     ("wz3p6_ee_tautau_ecm240", "#tau#tau", ROOT.kGray + 1, False),
    ("wz3p6_ee_tautau_ecm240", "#tau#tau", ROOT.kGray + 1, False),
# L45 [Executable statement]:     ("wzp6_ee_hadZH_HZZ_ecm240", "ZH(ZZ)", ROOT.kCyan - 7, False),
    ("wzp6_ee_hadZH_HZZ_ecm240", "ZH(ZZ)", ROOT.kCyan - 7, False),
# L46 [Executable statement]:     ("wzp6_ee_hadZH_Hcc_ecm240", "ZH(cc)", ROOT.kCyan - 3, False),
    ("wzp6_ee_hadZH_Hcc_ecm240", "ZH(cc)", ROOT.kCyan - 3, False),
# L47 [Executable statement]:     ("wzp6_ee_hadZH_Hgg_ecm240", "ZH(gg)", ROOT.kCyan + 1, False),
    ("wzp6_ee_hadZH_Hgg_ecm240", "ZH(gg)", ROOT.kCyan + 1, False),
# L48 [Executable statement]:     ("wzp6_ee_hadZH_Htautau_ecm240", "ZH(#tau#tau)", ROOT.kCyan + 3, False),
    ("wzp6_ee_hadZH_Htautau_ecm240", "ZH(#tau#tau)", ROOT.kCyan + 3, False),
# L49 [Executable statement]:     ("wzp6_ee_hadZH_Hbb_ecm240", "ZH(bb)", ROOT.kTeal - 7, False),
    ("wzp6_ee_hadZH_Hbb_ecm240", "ZH(bb)", ROOT.kTeal - 7, False),
# L50 [Executable statement]:     ("wz3p6_ee_qq_ecm240", "Z/#gamma#rightarrowqq", ROOT.kGreen + 2, False),
    ("wz3p6_ee_qq_ecm240", "Z/#gamma#rightarrowqq", ROOT.kGreen + 2, False),
# L51 [Executable statement]:     ("p8_ee_ZZ_ecm240", "ZZ", ROOT.kAzure + 1, False),
    ("p8_ee_ZZ_ecm240", "ZZ", ROOT.kAzure + 1, False),
# L52 [Executable statement]:     ("p8_ee_WW_ecm240", "WW", ROOT.kOrange - 3, False),
    ("p8_ee_WW_ecm240", "WW", ROOT.kOrange - 3, False),
# L53 [Original comment]:     # Signal (summed over all hadronic-Z production modes)
    # Signal (summed over all hadronic-Z production modes)
# L54 [Executable statement]:     ("wzp6_ee_hadZH_HWW_ecm240", "ZH (H#rightarrowWW)", ROOT.kRed + 1, True),
    ("wzp6_ee_hadZH_HWW_ecm240", "ZH (H#rightarrowWW)", ROOT.kRed + 1, True),
# L55 [Executable statement]: ]
]
# L56 [Blank separator]: 

# L57 [Original comment]: # Histograms to plot: (name, xtitle, rebin, xmin, xmax, logy)
# Histograms to plot: (name, xtitle, rebin, xmin, xmax, logy)
# L58 [Executable statement]: histograms = [
histograms = [
# L59 [Executable statement]:     ("cutFlow", "Cut stage", 1, -0.5, 8.5, True),
    ("cutFlow", "Cut stage", 1, -0.5, 8.5, True),
# L60 [Executable statement]:     ("lepton_p", "Lepton momentum [GeV]", 4, 0, 150, False),
    ("lepton_p", "Lepton momentum [GeV]", 4, 0, 150, False),
# L61 [Executable statement]:     ("lepton_iso", "Lepton isolation", 2, 0, 1, False),
    ("lepton_iso", "Lepton isolation", 2, 0, 1, False),
# L62 [Executable statement]:     ("missingEnergy_e", "Missing energy [GeV]", 4, 0, 150, False),
    ("missingEnergy_e", "Missing energy [GeV]", 4, 0, 150, False),
# L63 [Executable statement]:     ("missingEnergy_p", "Missing momentum [GeV]", 4, 0, 150, False),
    ("missingEnergy_p", "Missing momentum [GeV]", 4, 0, 150, False),
# L64 [Executable statement]:     ("missingMass", "Missing mass [GeV]", 4, 0, 240, False),
    ("missingMass", "Missing mass [GeV]", 4, 0, 240, False),
# L65 [Executable statement]:     ("cosTheta_miss", "|cos(#theta_{miss})|", 1, 0, 1, False),
    ("cosTheta_miss", "|cos(#theta_{miss})|", 1, 0, 1, False),
# L66 [Executable statement]:     ("visibleEnergy", "Visible energy (no lepton) [GeV]", 4, 0, 250, False),
    ("visibleEnergy", "Visible energy (no lepton) [GeV]", 4, 0, 250, False),
# L67 [Executable statement]:     ("njets", "Number of jets", 1, 0, 10, True),
    ("njets", "Number of jets", 1, 0, 10, True),
# L68 [Executable statement]:     ("jet0_p", "Jet 0 momentum [GeV]", 4, 0, 120, False),
    ("jet0_p", "Jet 0 momentum [GeV]", 4, 0, 120, False),
# L69 [Executable statement]:     ("jet1_p", "Jet 1 momentum [GeV]", 4, 0, 120, False),
    ("jet1_p", "Jet 1 momentum [GeV]", 4, 0, 120, False),
# L70 [Executable statement]:     ("jet2_p", "Jet 2 momentum [GeV]", 4, 0, 120, False),
    ("jet2_p", "Jet 2 momentum [GeV]", 4, 0, 120, False),
# L71 [Executable statement]:     ("jet3_p", "Jet 3 momentum [GeV]", 4, 0, 120, False),
    ("jet3_p", "Jet 3 momentum [GeV]", 4, 0, 120, False),
# L72 [Executable statement]:     ("Zcand_m", "m_{Z cand} [GeV]", 4, 0, 200, False),
    ("Zcand_m", "m_{Z cand} [GeV]", 4, 0, 200, False),
# L73 [Executable statement]:     ("Wstar_m", "m_{W*} [GeV]", 4, 0, 150, False),  # W* is off-shell, expect ~40 GeV
    ("Wstar_m", "m_{W*} [GeV]", 4, 0, 150, False),  # W* is off-shell, expect ~40 GeV
# L74 [Executable statement]:     ("Wlep_m", "m_{W_{lep}} [GeV]", 4, 0, 200, False),
    ("Wlep_m", "m_{W_{lep}} [GeV]", 4, 0, 200, False),
# L75 [Executable statement]:     ("Hcand_m", "m_{H cand} [GeV]", 4, 0, 300, False),
    ("Hcand_m", "m_{H cand} [GeV]", 4, 0, 300, False),
# L76 [Executable statement]:     ("Hcand_m_afterZ", "m_{H cand} (after Z cut) [GeV]", 4, 0, 300, False),
    ("Hcand_m_afterZ", "m_{H cand} (after Z cut) [GeV]", 4, 0, 300, False),
# L77 [Executable statement]:     ("Hcand_m_final", "m_{H cand} (final) [GeV]", 4, 0, 300, False),
    ("Hcand_m_final", "m_{H cand} (final) [GeV]", 4, 0, 300, False),
# L78 [Executable statement]:     ("recoil_m", "Recoil mass [GeV]", 4, 50, 200, False),
    ("recoil_m", "Recoil mass [GeV]", 4, 50, 200, False),
# L79 [Executable statement]:     ("recoil_m_afterZ", "Recoil mass (after Z cut) [GeV]", 4, 50, 200, False),
    ("recoil_m_afterZ", "Recoil mass (after Z cut) [GeV]", 4, 50, 200, False),
# L80 [Executable statement]:     ("deltaZ", "|m_{jj} - m_{Z}| [GeV]", 4, 0, 50, False),
    ("deltaZ", "|m_{jj} - m_{Z}| [GeV]", 4, 0, 50, False),
# L81 [Executable statement]: ]
]
# L82 [Blank separator]: 

# L83 [Executable statement]: CUT_LABELS = [
CUT_LABELS = [
# L84 [Executable statement]:     "All",
    "All",
# L85 [Executable statement]:     "1lep p>20",
    "1lep p>20",
# L86 [Executable statement]:     "ISO",
    "ISO",
# L87 [Executable statement]:     "Veto p>5",
    "Veto p>5",
# L88 [Executable statement]:     "MET E>20",
    "MET E>20",
# L89 [Executable statement]:     "4jets",
    "4jets",
# L90 [Executable statement]:     "Z win",
    "Z win",
# L91 [Executable statement]:     "Recoil",
    "Recoil",
# L92 [Executable statement]: ]
]
# L93 [Executable statement]: CUT_IDS = [f"cut{i}" for i in range(len(CUT_LABELS))]
CUT_IDS = [f"cut{i}" for i in range(len(CUT_LABELS))]
# L94 [Executable statement]: PERCENT_COL_WIDTH = 12
PERCENT_COL_WIDTH = 12
# L95 [Blank separator]: 

# L96 [Original comment]: # ============================================================
# ============================================================
# L97 [Original comment]: # Style settings
# Style settings
# L98 [Original comment]: # ============================================================
# ============================================================
# L99 [Blank separator]: 

# L100 [Function definition]: def setStyle():
def setStyle():
# L101 [Executable statement]:     ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetOptStat(0)
# L102 [Executable statement]:     ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetOptTitle(0)
# L103 [Executable statement]:     ROOT.gStyle.SetPadTickX(1)
    ROOT.gStyle.SetPadTickX(1)
# L104 [Executable statement]:     ROOT.gStyle.SetPadTickY(1)
    ROOT.gStyle.SetPadTickY(1)
# L105 [Executable statement]:     ROOT.gStyle.SetHistLineWidth(2)
    ROOT.gStyle.SetHistLineWidth(2)
# L106 [Executable statement]:     ROOT.gStyle.SetLegendBorderSize(0)
    ROOT.gStyle.SetLegendBorderSize(0)
# L107 [Executable statement]:     ROOT.gStyle.SetLegendFillColor(0)
    ROOT.gStyle.SetLegendFillColor(0)
# L108 [Executable statement]:     ROOT.gStyle.SetLegendFont(42)
    ROOT.gStyle.SetLegendFont(42)
# L109 [Executable statement]:     ROOT.gStyle.SetLegendTextSize(0.035)
    ROOT.gStyle.SetLegendTextSize(0.035)
# L110 [Executable statement]:     ROOT.gStyle.SetPadLeftMargin(0.14)
    ROOT.gStyle.SetPadLeftMargin(0.14)
# L111 [Executable statement]:     ROOT.gStyle.SetPadRightMargin(0.05)
    ROOT.gStyle.SetPadRightMargin(0.05)
# L112 [Executable statement]:     ROOT.gStyle.SetPadTopMargin(0.08)
    ROOT.gStyle.SetPadTopMargin(0.08)
# L113 [Executable statement]:     ROOT.gStyle.SetPadBottomMargin(0.12)
    ROOT.gStyle.SetPadBottomMargin(0.12)
# L114 [Executable statement]:     ROOT.gStyle.SetTitleFont(42, "XYZ")
    ROOT.gStyle.SetTitleFont(42, "XYZ")
# L115 [Executable statement]:     ROOT.gStyle.SetTitleSize(0.045, "XYZ")
    ROOT.gStyle.SetTitleSize(0.045, "XYZ")
# L116 [Executable statement]:     ROOT.gStyle.SetLabelFont(42, "XYZ")
    ROOT.gStyle.SetLabelFont(42, "XYZ")
# L117 [Executable statement]:     ROOT.gStyle.SetLabelSize(0.04, "XYZ")
    ROOT.gStyle.SetLabelSize(0.04, "XYZ")
# L118 [Executable statement]:     ROOT.gStyle.SetTitleOffset(1.3, "Y")
    ROOT.gStyle.SetTitleOffset(1.3, "Y")
# L119 [Blank separator]: 

# L120 [Original comment]: # ============================================================
# ============================================================
# L121 [Original comment]: # Helper functions
# Helper functions
# L122 [Original comment]: # ============================================================
# ============================================================
# L123 [Blank separator]: 

# L124 [Function definition]: def getHist(filename, histname):
def getHist(filename, histname):
# L125 [Executable statement]:     """Load histogram from file (already scaled by framework).
    """Load histogram from file (already scaled by framework).
# L126 [Blank separator]: 

# L127 [Executable statement]:     Some entries are logical groups summed over multiple processed samples.
    Some entries are logical groups summed over multiple processed samples.
# L128 [Executable statement]:     """
    """
# L129 [Conditional block]:     if filename in MERGED_GROUPS:
    if filename in MERGED_GROUPS:
# L130 [Executable statement]:         h_merged = None
        h_merged = None
# L131 [Loop over iterable]:         for sample_name in MERGED_GROUPS[filename]:
        for sample_name in MERGED_GROUPS[filename]:
# L132 [Executable statement]:             h = getHist(sample_name, histname)
            h = getHist(sample_name, histname)
# L133 [Conditional block]:             if h is None:
            if h is None:
# L134 [Executable statement]:                 continue
                continue
# L135 [Conditional block]:             if h_merged is None:
            if h_merged is None:
# L136 [Executable statement]:                 h_merged = h.Clone(f"{histname}_{filename}_merged")
                h_merged = h.Clone(f"{histname}_{filename}_merged")
# L137 [Executable statement]:                 h_merged.SetDirectory(0)
                h_merged.SetDirectory(0)
# L138 [Else branch]:             else:
            else:
# L139 [Executable statement]:                 h_merged.Add(h)
                h_merged.Add(h)
# L140 [Function return]:         return h_merged
        return h_merged
# L141 [Blank separator]: 

# L142 [Executable statement]:     filepath = os.path.join(inputDir, filename + ".root")
    filepath = os.path.join(inputDir, filename + ".root")
# L143 [Conditional block]:     if not os.path.exists(filepath):
    if not os.path.exists(filepath):
# L144 [Runtime log output]:         print(f"Warning: {filepath} not found")
        print(f"Warning: {filepath} not found")
# L145 [Function return]:         return None
        return None
# L146 [Blank separator]: 

# L147 [Executable statement]:     f = ROOT.TFile.Open(filepath)
    f = ROOT.TFile.Open(filepath)
# L148 [Executable statement]:     h = f.Get(histname)
    h = f.Get(histname)
# L149 [Conditional block]:     if not h:
    if not h:
# L150 [Runtime log output]:         print(f"Warning: {histname} not found in {filepath}")
        print(f"Warning: {histname} not found in {filepath}")
# L151 [Executable statement]:         f.Close()
        f.Close()
# L152 [Function return]:         return None
        return None
# L153 [Blank separator]: 

# L154 [Executable statement]:     h.SetDirectory(0)
    h.SetDirectory(0)
# L155 [Executable statement]:     f.Close()
    f.Close()
# L156 [Blank separator]: 

# L157 [Original comment]:     # NOTE: Histograms from fccanalysis with doScale=True are ALREADY
    # NOTE: Histograms from fccanalysis with doScale=True are ALREADY
# L158 [Original comment]:     # normalized to xsec * intLumi. Do NOT scale again here!
    # normalized to xsec * intLumi. Do NOT scale again here!
# L159 [Blank separator]: 

# L160 [Function return]:     return h
    return h
# L161 [Blank separator]: 

# L162 [Blank separator]: 

# L163 [Function definition]: def collectCutflowData():
def collectCutflowData():
# L164 [Executable statement]:     """Collect cutflow yields for all configured processes."""
    """Collect cutflow yields for all configured processes."""
# L165 [Blank separator]: 

# L166 [Executable statement]:     ncuts = len(CUT_LABELS)
    ncuts = len(CUT_LABELS)
# L167 [Executable statement]:     process_rows = []
    process_rows = []
# L168 [Executable statement]:     process_eff_rows = []
    process_eff_rows = []
# L169 [Executable statement]:     total_sig = [0.0] * ncuts
    total_sig = [0.0] * ncuts
# L170 [Executable statement]:     total_bkg = [0.0] * ncuts
    total_bkg = [0.0] * ncuts
# L171 [Blank separator]: 

# L172 [Loop over iterable]:     for fname, label, color, isSignal in processes:
    for fname, label, color, isSignal in processes:
# L173 [Executable statement]:         h = getHist(fname, "cutFlow")
        h = getHist(fname, "cutFlow")
# L174 [Conditional block]:         if h is None:
        if h is None:
# L175 [Executable statement]:             continue
            continue
# L176 [Blank separator]: 

# L177 [Executable statement]:         values = [h.GetBinContent(i + 1) for i in range(ncuts)]
        values = [h.GetBinContent(i + 1) for i in range(ncuts)]
# L178 [Executable statement]:         process_rows.append((label, values, isSignal))
        process_rows.append((label, values, isSignal))
# L179 [Blank separator]: 

# L180 [Executable statement]:         base = values[0] if values and values[0] > 0 else 0.0
        base = values[0] if values and values[0] > 0 else 0.0
# L181 [Executable statement]:         eff_values = [100.0 * val / base if base > 0 else None for val in values]
        eff_values = [100.0 * val / base if base > 0 else None for val in values]
# L182 [Executable statement]:         process_eff_rows.append((label, eff_values, isSignal))
        process_eff_rows.append((label, eff_values, isSignal))
# L183 [Blank separator]: 

# L184 [Loop over iterable]:         for i, val in enumerate(values):
        for i, val in enumerate(values):
# L185 [Conditional block]:             if isSignal:
            if isSignal:
# L186 [Executable statement]:                 total_sig[i] += val
                total_sig[i] += val
# L187 [Else branch]:             else:
            else:
# L188 [Executable statement]:                 total_bkg[i] += val
                total_bkg[i] += val
# L189 [Blank separator]: 

# L190 [Executable statement]:     s_over_b = []
    s_over_b = []
# L191 [Executable statement]:     s_over_sqrt_b = []
    s_over_sqrt_b = []
# L192 [Loop over iterable]:     for s, b in zip(total_sig, total_bkg):
    for s, b in zip(total_sig, total_bkg):
# L193 [Conditional block]:         if b > 0:
        if b > 0:
# L194 [Executable statement]:             s_over_b.append(s / b)
            s_over_b.append(s / b)
# L195 [Executable statement]:             s_over_sqrt_b.append(s / (b ** 0.5))
            s_over_sqrt_b.append(s / (b ** 0.5))
# L196 [Else branch]:         else:
        else:
# L197 [Executable statement]:             s_over_b.append(None)
            s_over_b.append(None)
# L198 [Executable statement]:             s_over_sqrt_b.append(None)
            s_over_sqrt_b.append(None)
# L199 [Blank separator]: 

# L200 [Executable statement]:     sig_base = total_sig[0] if total_sig and total_sig[0] > 0 else 0.0
    sig_base = total_sig[0] if total_sig and total_sig[0] > 0 else 0.0
# L201 [Executable statement]:     bkg_base = total_bkg[0] if total_bkg and total_bkg[0] > 0 else 0.0
    bkg_base = total_bkg[0] if total_bkg and total_bkg[0] > 0 else 0.0
# L202 [Executable statement]:     total_sig_eff = [100.0 * val / sig_base if sig_base > 0 else None for val in total_sig]
    total_sig_eff = [100.0 * val / sig_base if sig_base > 0 else None for val in total_sig]
# L203 [Executable statement]:     total_bkg_eff = [100.0 * val / bkg_base if bkg_base > 0 else None for val in total_bkg]
    total_bkg_eff = [100.0 * val / bkg_base if bkg_base > 0 else None for val in total_bkg]
# L204 [Blank separator]: 

# L205 [Function return]:     return {
    return {
# L206 [Executable statement]:         "cut_labels": CUT_LABELS,
        "cut_labels": CUT_LABELS,
# L207 [Executable statement]:         "cut_ids": CUT_IDS,
        "cut_ids": CUT_IDS,
# L208 [Executable statement]:         "process_rows": process_rows,
        "process_rows": process_rows,
# L209 [Executable statement]:         "process_eff_rows": process_eff_rows,
        "process_eff_rows": process_eff_rows,
# L210 [Executable statement]:         "total_sig": total_sig,
        "total_sig": total_sig,
# L211 [Executable statement]:         "total_bkg": total_bkg,
        "total_bkg": total_bkg,
# L212 [Executable statement]:         "total_sig_eff": total_sig_eff,
        "total_sig_eff": total_sig_eff,
# L213 [Executable statement]:         "total_bkg_eff": total_bkg_eff,
        "total_bkg_eff": total_bkg_eff,
# L214 [Executable statement]:         "s_over_b": s_over_b,
        "s_over_b": s_over_b,
# L215 [Executable statement]:         "s_over_sqrt_b": s_over_sqrt_b,
        "s_over_sqrt_b": s_over_sqrt_b,
# L216 [Executable statement]:     }
    }
# L217 [Blank separator]: 

# L218 [Blank separator]: 

# L219 [Function definition]: def _format_table_row(label, values, float_fmt=".0f"):
def _format_table_row(label, values, float_fmt=".0f"):
# L220 [Executable statement]:     row = f"{label:<25}"
    row = f"{label:<25}"
# L221 [Loop over iterable]:     for val in values:
    for val in values:
# L222 [Conditional block]:         if val is None:
        if val is None:
# L223 [Executable statement]:             row += f"{'--':>10}"
            row += f"{'--':>10}"
# L224 [Else branch]:         else:
        else:
# L225 [Executable statement]:             row += f"{val:>10{float_fmt}}"
            row += f"{val:>10{float_fmt}}"
# L226 [Function return]:     return row
    return row
# L227 [Blank separator]: 

# L228 [Blank separator]: 

# L229 [Function definition]: def _format_percent_row(label, values):
def _format_percent_row(label, values):
# L230 [Executable statement]:     row = f"{label:<25}"
    row = f"{label:<25}"
# L231 [Loop over iterable]:     for val in values:
    for val in values:
# L232 [Conditional block]:         if val is None:
        if val is None:
# L233 [Executable statement]:             row += f"{'--':>{PERCENT_COL_WIDTH}}"
            row += f"{'--':>{PERCENT_COL_WIDTH}}"
# L234 [Else branch]:         else:
        else:
# L235 [Executable statement]:             row += f"{f'{val:.2f}%':>{PERCENT_COL_WIDTH}}"
            row += f"{f'{val:.2f}%':>{PERCENT_COL_WIDTH}}"
# L236 [Function return]:     return row
    return row
# L237 [Blank separator]: 

# L238 [Blank separator]: 

# L239 [Function definition]: def _format_cut_header(cut_keys, value_width=10):
def _format_cut_header(cut_keys, value_width=10):
# L240 [Executable statement]:     header = f"{'Process':<25}"
    header = f"{'Process':<25}"
# L241 [Loop over iterable]:     for key in cut_keys:
    for key in cut_keys:
# L242 [Executable statement]:         header += f"{key:>{value_width}}"
        header += f"{key:>{value_width}}"
# L243 [Function return]:     return header
    return header
# L244 [Blank separator]: 

# L245 [Blank separator]: 

# L246 [Function definition]: def writeCutflowText(summary):
def writeCutflowText(summary):
# L247 [Executable statement]:     """Write cutflow table to a plain-text file."""
    """Write cutflow table to a plain-text file."""
# L248 [Blank separator]: 

# L249 [Executable statement]:     os.makedirs(outputDir, exist_ok=True)
    os.makedirs(outputDir, exist_ok=True)
# L250 [Executable statement]:     outpath = os.path.join(outputDir, "cutFlow_cutflow.txt")
    outpath = os.path.join(outputDir, "cutFlow_cutflow.txt")
# L251 [Blank separator]: 

# L252 [Executable statement]:     lines = []
    lines = []
# L253 [Executable statement]:     lines.append("=" * 80)
    lines.append("=" * 80)
# L254 [Executable statement]:     lines.append("CUTFLOW TABLE (normalized to 10.8 ab^-1)")
    lines.append("CUTFLOW TABLE (normalized to 10.8 ab^-1)")
# L255 [Executable statement]:     lines.append("=" * 80)
    lines.append("=" * 80)
# L256 [Blank separator]: 

# L257 [Executable statement]:     header = f"{'Process':<25}"
    header = f"{'Process':<25}"
# L258 [Loop over iterable]:     for lab in summary["cut_labels"]:
    for lab in summary["cut_labels"]:
# L259 [Executable statement]:         header += f"{lab:>10}"
        header += f"{lab:>10}"
# L260 [Executable statement]:     lines.append(header)
    lines.append(header)
# L261 [Executable statement]:     lines.append("-" * 95)
    lines.append("-" * 95)
# L262 [Blank separator]: 

# L263 [Loop over iterable]:     for label, values, isSignal in summary["process_rows"]:
    for label, values, isSignal in summary["process_rows"]:
# L264 [Executable statement]:         lines.append(_format_table_row(label, values, ".0f"))
        lines.append(_format_table_row(label, values, ".0f"))
# L265 [Blank separator]: 

# L266 [Executable statement]:     lines.append("-" * 95)
    lines.append("-" * 95)
# L267 [Executable statement]:     lines.append(_format_table_row("Total Signal", summary["total_sig"], ".1f"))
    lines.append(_format_table_row("Total Signal", summary["total_sig"], ".1f"))
# L268 [Executable statement]:     lines.append(_format_table_row("Total Background", summary["total_bkg"], ".1f"))
    lines.append(_format_table_row("Total Background", summary["total_bkg"], ".1f"))
# L269 [Executable statement]:     lines.append("-" * 95)
    lines.append("-" * 95)
# L270 [Executable statement]:     lines.append(_format_table_row("S/B", summary["s_over_b"], ".4f"))
    lines.append(_format_table_row("S/B", summary["s_over_b"], ".4f"))
# L271 [Executable statement]:     lines.append(_format_table_row("S/sqrt(B)", summary["s_over_sqrt_b"], ".1f"))
    lines.append(_format_table_row("S/sqrt(B)", summary["s_over_sqrt_b"], ".1f"))
# L272 [Executable statement]:     lines.append("=" * 95)
    lines.append("=" * 95)
# L273 [Blank separator]: 

# L274 [Context manager block]:     with open(outpath, "w", encoding="ascii") as f:
    with open(outpath, "w", encoding="ascii") as f:
# L275 [Executable statement]:         f.write("\n".join(lines) + "\n")
        f.write("\n".join(lines) + "\n")
# L276 [Blank separator]: 

# L277 [Blank separator]: 

# L278 [Function definition]: def writeCutflowLatex(summary):
def writeCutflowLatex(summary):
# L279 [Executable statement]:     """Write cutflow table to a LaTeX file."""
    """Write cutflow table to a LaTeX file."""
# L280 [Blank separator]: 

# L281 [Executable statement]:     os.makedirs(outputDir, exist_ok=True)
    os.makedirs(outputDir, exist_ok=True)
# L282 [Executable statement]:     outpath = os.path.join(outputDir, "cutFlow_cutflow.tex")
    outpath = os.path.join(outputDir, "cutFlow_cutflow.tex")
# L283 [Blank separator]: 

# L284 [Executable statement]:     cols = "l" + "r" * len(summary["cut_labels"])
    cols = "l" + "r" * len(summary["cut_labels"])
# L285 [Executable statement]:     lines = [
    lines = [
# L286 [Executable statement]:         r"\begin{tabular}{" + cols + r"}",
        r"\begin{tabular}{" + cols + r"}",
# L287 [Executable statement]:         r"\hline",
        r"\hline",
# L288 [Executable statement]:     ]
    ]
# L289 [Blank separator]: 

# L290 [Executable statement]:     header = ["Process"] + summary["cut_labels"]
    header = ["Process"] + summary["cut_labels"]
# L291 [Executable statement]:     lines.append(" & ".join(header) + r" \\")
    lines.append(" & ".join(header) + r" \\")
# L292 [Executable statement]:     lines.append(r"\hline")
    lines.append(r"\hline")
# L293 [Blank separator]: 

# L294 [Loop over iterable]:     for label, values, isSignal in summary["process_rows"]:
    for label, values, isSignal in summary["process_rows"]:
# L295 [Executable statement]:         row = [label] + [f"{val:.0f}" for val in values]
        row = [label] + [f"{val:.0f}" for val in values]
# L296 [Executable statement]:         lines.append(" & ".join(row) + r" \\")
        lines.append(" & ".join(row) + r" \\")
# L297 [Blank separator]: 

# L298 [Executable statement]:     lines.append(r"\hline")
    lines.append(r"\hline")
# L299 [Executable statement]:     lines.append(" & ".join(["Total Signal"] + [f"{v:.1f}" for v in summary["total_sig"]]) + r" \\")
    lines.append(" & ".join(["Total Signal"] + [f"{v:.1f}" for v in summary["total_sig"]]) + r" \\")
# L300 [Executable statement]:     lines.append(" & ".join(["Total Background"] + [f"{v:.1f}" for v in summary["total_bkg"]]) + r" \\")
    lines.append(" & ".join(["Total Background"] + [f"{v:.1f}" for v in summary["total_bkg"]]) + r" \\")
# L301 [Executable statement]:     lines.append(r"\hline")
    lines.append(r"\hline")
# L302 [Executable statement]:     lines.append(" & ".join(["S/B"] + [("--" if v is None else f"{v:.4f}") for v in summary["s_over_b"]]) + r" \\")
    lines.append(" & ".join(["S/B"] + [("--" if v is None else f"{v:.4f}") for v in summary["s_over_b"]]) + r" \\")
# L303 [Executable statement]:     lines.append(" & ".join(["S/$\\sqrt{B}$"] + [("--" if v is None else f"{v:.1f}") for v in summary["s_over_sqrt_b"]]) + r" \\")
    lines.append(" & ".join(["S/$\\sqrt{B}$"] + [("--" if v is None else f"{v:.1f}") for v in summary["s_over_sqrt_b"]]) + r" \\")
# L304 [Executable statement]:     lines.append(r"\hline")
    lines.append(r"\hline")
# L305 [Executable statement]:     lines.append(r"\end{tabular}")
    lines.append(r"\end{tabular}")
# L306 [Blank separator]: 

# L307 [Context manager block]:     with open(outpath, "w", encoding="ascii") as f:
    with open(outpath, "w", encoding="ascii") as f:
# L308 [Executable statement]:         f.write("\n".join(lines) + "\n")
        f.write("\n".join(lines) + "\n")
# L309 [Blank separator]: 

# L310 [Blank separator]: 

# L311 [Function definition]: def makeCutflowPdf(summary):
def makeCutflowPdf(summary):
# L312 [Executable statement]:     """Render a cutflow table as a PDF, similar to standard FCCAnalysis outputs."""
    """Render a cutflow table as a PDF, similar to standard FCCAnalysis outputs."""
# L313 [Blank separator]: 

# L314 [Executable statement]:     os.makedirs(outputDir, exist_ok=True)
    os.makedirs(outputDir, exist_ok=True)
# L315 [Executable statement]:     outpath = os.path.join(outputDir, "cutFlow_cutflow.pdf")
    outpath = os.path.join(outputDir, "cutFlow_cutflow.pdf")
# L316 [Blank separator]: 

# L317 [Executable statement]:     c = ROOT.TCanvas("cutflow_table", "", 1800, 700)
    c = ROOT.TCanvas("cutflow_table", "", 1800, 700)
# L318 [Executable statement]:     c.cd()
    c.cd()
# L319 [Blank separator]: 

# L320 [Executable statement]:     title = ROOT.TLatex()
    title = ROOT.TLatex()
# L321 [Executable statement]:     title.SetNDC()
    title.SetNDC()
# L322 [Executable statement]:     title.SetTextFont(42)
    title.SetTextFont(42)
# L323 [Executable statement]:     title.SetTextSize(0.035)
    title.SetTextSize(0.035)
# L324 [Executable statement]:     title.DrawLatex(0.03, 0.95, "Cutflow table, normalized to 10.8 ab^{-1}")
    title.DrawLatex(0.03, 0.95, "Cutflow table, normalized to 10.8 ab^{-1}")
# L325 [Blank separator]: 

# L326 [Executable statement]:     latex = ROOT.TLatex()
    latex = ROOT.TLatex()
# L327 [Executable statement]:     latex.SetNDC()
    latex.SetNDC()
# L328 [Executable statement]:     latex.SetTextFont(42)
    latex.SetTextFont(42)
# L329 [Executable statement]:     latex.SetTextSize(0.024)
    latex.SetTextSize(0.024)
# L330 [Blank separator]: 

# L331 [Executable statement]:     x_process = 0.03
    x_process = 0.03
# L332 [Executable statement]:     x_start = 0.32
    x_start = 0.32
# L333 [Executable statement]:     x_end = 0.97
    x_end = 0.97
# L334 [Executable statement]:     ncuts = len(summary["cut_labels"])
    ncuts = len(summary["cut_labels"])
# L335 [Executable statement]:     x_cuts = [x_start + i * (x_end - x_start) / max(1, ncuts - 1) for i in range(ncuts)]
    x_cuts = [x_start + i * (x_end - x_start) / max(1, ncuts - 1) for i in range(ncuts)]
# L336 [Blank separator]: 

# L337 [Executable statement]:     y = 0.88
    y = 0.88
# L338 [Executable statement]:     latex.SetTextAlign(13)
    latex.SetTextAlign(13)
# L339 [Executable statement]:     latex.DrawLatex(x_process, y, "Process")
    latex.DrawLatex(x_process, y, "Process")
# L340 [Executable statement]:     latex.SetTextAlign(23)
    latex.SetTextAlign(23)
# L341 [Loop over iterable]:     for x, label in zip(x_cuts, summary["cut_labels"]):
    for x, label in zip(x_cuts, summary["cut_labels"]):
# L342 [Executable statement]:         latex.DrawLatex(x, y, label)
        latex.DrawLatex(x, y, label)
# L343 [Blank separator]: 

# L344 [Executable statement]:     rows = []
    rows = []
# L345 [Loop over iterable]:     for label, values, isSignal in summary["process_rows"]:
    for label, values, isSignal in summary["process_rows"]:
# L346 [Executable statement]:         rows.append((label, values))
        rows.append((label, values))
# L347 [Executable statement]:     rows.append(("Total Signal", summary["total_sig"]))
    rows.append(("Total Signal", summary["total_sig"]))
# L348 [Executable statement]:     rows.append(("Total Background", summary["total_bkg"]))
    rows.append(("Total Background", summary["total_bkg"]))
# L349 [Executable statement]:     rows.append(("S/B", summary["s_over_b"]))
    rows.append(("S/B", summary["s_over_b"]))
# L350 [Executable statement]:     rows.append(("S/sqrt(B)", summary["s_over_sqrt_b"]))
    rows.append(("S/sqrt(B)", summary["s_over_sqrt_b"]))
# L351 [Blank separator]: 

# L352 [Executable statement]:     y -= 0.07
    y -= 0.07
# L353 [Loop over iterable]:     for label, values in rows:
    for label, values in rows:
# L354 [Executable statement]:         latex.SetTextAlign(13)
        latex.SetTextAlign(13)
# L355 [Executable statement]:         latex.DrawLatex(x_process, y, label)
        latex.DrawLatex(x_process, y, label)
# L356 [Executable statement]:         latex.SetTextAlign(23)
        latex.SetTextAlign(23)
# L357 [Loop over iterable]:         for x, val in zip(x_cuts, values):
        for x, val in zip(x_cuts, values):
# L358 [Conditional block]:             if val is None:
            if val is None:
# L359 [Executable statement]:                 txt = "--"
                txt = "--"
# L360 [Else-if conditional]:             elif label in ("S/B",):
            elif label in ("S/B",):
# L361 [Executable statement]:                 txt = f"{val:.4f}"
                txt = f"{val:.4f}"
# L362 [Else-if conditional]:             elif label in ("S/sqrt(B)",):
            elif label in ("S/sqrt(B)",):
# L363 [Executable statement]:                 txt = f"{val:.1f}"
                txt = f"{val:.1f}"
# L364 [Else-if conditional]:             elif label.startswith("Total"):
            elif label.startswith("Total"):
# L365 [Executable statement]:                 txt = f"{val:.1f}"
                txt = f"{val:.1f}"
# L366 [Else branch]:             else:
            else:
# L367 [Executable statement]:                 txt = f"{val:.0f}"
                txt = f"{val:.0f}"
# L368 [Executable statement]:             latex.DrawLatex(x, y, txt)
            latex.DrawLatex(x, y, txt)
# L369 [Executable statement]:         y -= 0.06
        y -= 0.06
# L370 [Blank separator]: 

# L371 [Executable statement]:     c.SaveAs(outpath)
    c.SaveAs(outpath)
# L372 [Executable statement]:     c.SaveAs(outpath.replace(".pdf", ".png"))
    c.SaveAs(outpath.replace(".pdf", ".png"))
# L373 [Executable statement]:     c.Close()
    c.Close()
# L374 [Blank separator]: 

# L375 [Blank separator]: 

# L376 [Function definition]: def writeCutflowEfficiencyText(summary):
def writeCutflowEfficiencyText(summary):
# L377 [Executable statement]:     """Write cumulative cut efficiencies in percent to a plain-text file."""
    """Write cumulative cut efficiencies in percent to a plain-text file."""
# L378 [Blank separator]: 

# L379 [Executable statement]:     os.makedirs(outputDir, exist_ok=True)
    os.makedirs(outputDir, exist_ok=True)
# L380 [Executable statement]:     outpath = os.path.join(outputDir, "cutFlow_efficiency.txt")
    outpath = os.path.join(outputDir, "cutFlow_efficiency.txt")
# L381 [Blank separator]: 

# L382 [Executable statement]:     rule = "-" * (25 + PERCENT_COL_WIDTH * len(summary["cut_ids"]))
    rule = "-" * (25 + PERCENT_COL_WIDTH * len(summary["cut_ids"]))
# L383 [Executable statement]:     lines = []
    lines = []
# L384 [Executable statement]:     lines.append("=" * 80)
    lines.append("=" * 80)
# L385 [Executable statement]:     lines.append("CUTFLOW EFFICIENCY TABLE [%], cumulative w.r.t. cut0 (All)")
    lines.append("CUTFLOW EFFICIENCY TABLE [%], cumulative w.r.t. cut0 (All)")
# L386 [Executable statement]:     lines.append("=" * 80)
    lines.append("=" * 80)
# L387 [Executable statement]:     lines.append(_format_cut_header(summary["cut_ids"], PERCENT_COL_WIDTH))
    lines.append(_format_cut_header(summary["cut_ids"], PERCENT_COL_WIDTH))
# L388 [Executable statement]:     lines.append(rule)
    lines.append(rule)
# L389 [Blank separator]: 

# L390 [Loop over iterable]:     for label, values, isSignal in summary["process_eff_rows"]:
    for label, values, isSignal in summary["process_eff_rows"]:
# L391 [Executable statement]:         lines.append(_format_percent_row(label, values))
        lines.append(_format_percent_row(label, values))
# L392 [Blank separator]: 

# L393 [Executable statement]:     lines.append(rule)
    lines.append(rule)
# L394 [Executable statement]:     lines.append(_format_percent_row("Total Signal eff", summary["total_sig_eff"]))
    lines.append(_format_percent_row("Total Signal eff", summary["total_sig_eff"]))
# L395 [Executable statement]:     lines.append(_format_percent_row("Total Bkg eff", summary["total_bkg_eff"]))
    lines.append(_format_percent_row("Total Bkg eff", summary["total_bkg_eff"]))
# L396 [Executable statement]:     lines.append("=" * len(rule))
    lines.append("=" * len(rule))
# L397 [Executable statement]:     lines.append("")
    lines.append("")
# L398 [Executable statement]:     lines.append("Cut definitions:")
    lines.append("Cut definitions:")
# L399 [Loop over iterable]:     for cut_id, label in zip(summary["cut_ids"], summary["cut_labels"]):
    for cut_id, label in zip(summary["cut_ids"], summary["cut_labels"]):
# L400 [Executable statement]:         lines.append(f"  {cut_id}: {label}")
        lines.append(f"  {cut_id}: {label}")
# L401 [Blank separator]: 

# L402 [Context manager block]:     with open(outpath, "w", encoding="ascii") as f:
    with open(outpath, "w", encoding="ascii") as f:
# L403 [Executable statement]:         f.write("\n".join(lines) + "\n")
        f.write("\n".join(lines) + "\n")
# L404 [Blank separator]: 

# L405 [Function definition]: def writeCutflowEfficiencyLatex(summary):
def writeCutflowEfficiencyLatex(summary):
# L406 [Executable statement]:     """Write cumulative cut efficiencies in percent to a LaTeX file."""
    """Write cumulative cut efficiencies in percent to a LaTeX file."""
# L407 [Blank separator]: 

# L408 [Executable statement]:     os.makedirs(outputDir, exist_ok=True)
    os.makedirs(outputDir, exist_ok=True)
# L409 [Executable statement]:     outpath = os.path.join(outputDir, "cutFlow_efficiency.tex")
    outpath = os.path.join(outputDir, "cutFlow_efficiency.tex")
# L410 [Blank separator]: 

# L411 [Executable statement]:     cols = "l" + "r" * len(summary["cut_ids"])
    cols = "l" + "r" * len(summary["cut_ids"])
# L412 [Executable statement]:     ncols = len(summary["cut_ids"]) + 1
    ncols = len(summary["cut_ids"]) + 1
# L413 [Executable statement]:     lines = [
    lines = [
# L414 [Executable statement]:         r"\begin{tabular}{" + cols + r"}",
        r"\begin{tabular}{" + cols + r"}",
# L415 [Executable statement]:         r"\hline",
        r"\hline",
# L416 [Executable statement]:     ]
    ]
# L417 [Blank separator]: 

# L418 [Executable statement]:     header = ["Process"] + summary["cut_ids"]
    header = ["Process"] + summary["cut_ids"]
# L419 [Executable statement]:     lines.append(" & ".join(header) + r" \\")
    lines.append(" & ".join(header) + r" \\")
# L420 [Executable statement]:     lines.append(r"\hline")
    lines.append(r"\hline")
# L421 [Blank separator]: 

# L422 [Loop over iterable]:     for label, values, isSignal in summary["process_eff_rows"]:
    for label, values, isSignal in summary["process_eff_rows"]:
# L423 [Executable statement]:         row = [label] + [("--" if v is None else f"{v:.2f}\\%") for v in values]
        row = [label] + [("--" if v is None else f"{v:.2f}\\%") for v in values]
# L424 [Executable statement]:         lines.append(" & ".join(row) + r" \\")
        lines.append(" & ".join(row) + r" \\")
# L425 [Blank separator]: 

# L426 [Executable statement]:     lines.append(r"\hline")
    lines.append(r"\hline")
# L427 [Executable statement]:     lines.append(" & ".join(["Total Signal eff"] + [("--" if v is None else f"{v:.2f}\\%") for v in summary["total_sig_eff"]]) + r" \\")
    lines.append(" & ".join(["Total Signal eff"] + [("--" if v is None else f"{v:.2f}\\%") for v in summary["total_sig_eff"]]) + r" \\")
# L428 [Executable statement]:     lines.append(" & ".join(["Total Bkg eff"] + [("--" if v is None else f"{v:.2f}\\%") for v in summary["total_bkg_eff"]]) + r" \\")
    lines.append(" & ".join(["Total Bkg eff"] + [("--" if v is None else f"{v:.2f}\\%") for v in summary["total_bkg_eff"]]) + r" \\")
# L429 [Executable statement]:     lines.append(r"\hline")
    lines.append(r"\hline")
# L430 [Executable statement]:     lines.append(rf"\multicolumn{{{ncols}}}{{l}}{{Cut definitions:}} \\")
    lines.append(rf"\multicolumn{{{ncols}}}{{l}}{{Cut definitions:}} \\")
# L431 [Loop over iterable]:     for cut_id, label in zip(summary["cut_ids"], summary["cut_labels"]):
    for cut_id, label in zip(summary["cut_ids"], summary["cut_labels"]):
# L432 [Executable statement]:         safe_label = label.replace("_", r"\_").replace("%", r"\%")
        safe_label = label.replace("_", r"\_").replace("%", r"\%")
# L433 [Executable statement]:         lines.append(rf"\multicolumn{{{ncols}}}{{l}}{{{cut_id}: {safe_label}}} \\")
        lines.append(rf"\multicolumn{{{ncols}}}{{l}}{{{cut_id}: {safe_label}}} \\")
# L434 [Executable statement]:     lines.append(r"\hline")
    lines.append(r"\hline")
# L435 [Executable statement]:     lines.append(r"\end{tabular}")
    lines.append(r"\end{tabular}")
# L436 [Blank separator]: 

# L437 [Context manager block]:     with open(outpath, "w", encoding="ascii") as f:
    with open(outpath, "w", encoding="ascii") as f:
# L438 [Executable statement]:         f.write("\n".join(lines) + "\n")
        f.write("\n".join(lines) + "\n")
# L439 [Blank separator]: 

# L440 [Function definition]: def makeCutflowEfficiencyPdf(summary):
def makeCutflowEfficiencyPdf(summary):
# L441 [Executable statement]:     """Render a cumulative cut-efficiency table as a PDF."""
    """Render a cumulative cut-efficiency table as a PDF."""
# L442 [Blank separator]: 

# L443 [Executable statement]:     os.makedirs(outputDir, exist_ok=True)
    os.makedirs(outputDir, exist_ok=True)
# L444 [Executable statement]:     outpath = os.path.join(outputDir, "cutFlow_efficiency.pdf")
    outpath = os.path.join(outputDir, "cutFlow_efficiency.pdf")
# L445 [Blank separator]: 

# L446 [Executable statement]:     c = ROOT.TCanvas("cutflow_eff_table", "", 1800, 850)
    c = ROOT.TCanvas("cutflow_eff_table", "", 1800, 850)
# L447 [Executable statement]:     c.cd()
    c.cd()
# L448 [Blank separator]: 

# L449 [Executable statement]:     title = ROOT.TLatex()
    title = ROOT.TLatex()
# L450 [Executable statement]:     title.SetNDC()
    title.SetNDC()
# L451 [Executable statement]:     title.SetTextFont(42)
    title.SetTextFont(42)
# L452 [Executable statement]:     title.SetTextSize(0.035)
    title.SetTextSize(0.035)
# L453 [Executable statement]:     title.DrawLatex(0.03, 0.95, "Cutflow efficiencies [%], cumulative w.r.t. cut0 (All)")
    title.DrawLatex(0.03, 0.95, "Cutflow efficiencies [%], cumulative w.r.t. cut0 (All)")
# L454 [Blank separator]: 

# L455 [Executable statement]:     latex = ROOT.TLatex()
    latex = ROOT.TLatex()
# L456 [Executable statement]:     latex.SetNDC()
    latex.SetNDC()
# L457 [Executable statement]:     latex.SetTextFont(42)
    latex.SetTextFont(42)
# L458 [Executable statement]:     latex.SetTextSize(0.024)
    latex.SetTextSize(0.024)
# L459 [Blank separator]: 

# L460 [Executable statement]:     x_process = 0.03
    x_process = 0.03
# L461 [Executable statement]:     x_start = 0.32
    x_start = 0.32
# L462 [Executable statement]:     x_end = 0.97
    x_end = 0.97
# L463 [Executable statement]:     ncuts = len(summary["cut_ids"])
    ncuts = len(summary["cut_ids"])
# L464 [Executable statement]:     x_cuts = [x_start + i * (x_end - x_start) / max(1, ncuts - 1) for i in range(ncuts)]
    x_cuts = [x_start + i * (x_end - x_start) / max(1, ncuts - 1) for i in range(ncuts)]
# L465 [Blank separator]: 

# L466 [Executable statement]:     y = 0.88
    y = 0.88
# L467 [Executable statement]:     latex.SetTextAlign(13)
    latex.SetTextAlign(13)
# L468 [Executable statement]:     latex.DrawLatex(x_process, y, "Process")
    latex.DrawLatex(x_process, y, "Process")
# L469 [Executable statement]:     latex.SetTextAlign(23)
    latex.SetTextAlign(23)
# L470 [Loop over iterable]:     for x, label in zip(x_cuts, summary["cut_ids"]):
    for x, label in zip(x_cuts, summary["cut_ids"]):
# L471 [Executable statement]:         latex.DrawLatex(x, y, label)
        latex.DrawLatex(x, y, label)
# L472 [Blank separator]: 

# L473 [Executable statement]:     rows = []
    rows = []
# L474 [Loop over iterable]:     for label, values, isSignal in summary["process_eff_rows"]:
    for label, values, isSignal in summary["process_eff_rows"]:
# L475 [Executable statement]:         rows.append((label, values))
        rows.append((label, values))
# L476 [Executable statement]:     rows.append(("Total Signal eff", summary["total_sig_eff"]))
    rows.append(("Total Signal eff", summary["total_sig_eff"]))
# L477 [Executable statement]:     rows.append(("Total Bkg eff", summary["total_bkg_eff"]))
    rows.append(("Total Bkg eff", summary["total_bkg_eff"]))
# L478 [Blank separator]: 

# L479 [Executable statement]:     y -= 0.07
    y -= 0.07
# L480 [Loop over iterable]:     for label, values in rows:
    for label, values in rows:
# L481 [Executable statement]:         latex.SetTextAlign(13)
        latex.SetTextAlign(13)
# L482 [Executable statement]:         latex.DrawLatex(x_process, y, label)
        latex.DrawLatex(x_process, y, label)
# L483 [Executable statement]:         latex.SetTextAlign(23)
        latex.SetTextAlign(23)
# L484 [Loop over iterable]:         for x, val in zip(x_cuts, values):
        for x, val in zip(x_cuts, values):
# L485 [Executable statement]:             txt = "--" if val is None else f"{val:.2f}%"
            txt = "--" if val is None else f"{val:.2f}%"
# L486 [Executable statement]:             latex.DrawLatex(x, y, txt)
            latex.DrawLatex(x, y, txt)
# L487 [Executable statement]:         y -= 0.06
        y -= 0.06
# L488 [Blank separator]: 

# L489 [Executable statement]:     legend = ROOT.TLatex()
    legend = ROOT.TLatex()
# L490 [Executable statement]:     legend.SetNDC()
    legend.SetNDC()
# L491 [Executable statement]:     legend.SetTextFont(42)
    legend.SetTextFont(42)
# L492 [Executable statement]:     legend.SetTextSize(0.020)
    legend.SetTextSize(0.020)
# L493 [Executable statement]:     legend.SetTextAlign(13)
    legend.SetTextAlign(13)
# L494 [Executable statement]:     legend.DrawLatex(0.03, 0.24, "Cut definitions:")
    legend.DrawLatex(0.03, 0.24, "Cut definitions:")
# L495 [Loop over iterable]:     for idx, (cut_id, label) in enumerate(zip(summary["cut_ids"], summary["cut_labels"])):
    for idx, (cut_id, label) in enumerate(zip(summary["cut_ids"], summary["cut_labels"])):
# L496 [Executable statement]:         x = 0.03 + (idx % 2) * 0.44
        x = 0.03 + (idx % 2) * 0.44
# L497 [Executable statement]:         yy = 0.20 - (idx // 2) * 0.04
        yy = 0.20 - (idx // 2) * 0.04
# L498 [Executable statement]:         legend.DrawLatex(x, yy, f"{cut_id}: {label}")
        legend.DrawLatex(x, yy, f"{cut_id}: {label}")
# L499 [Blank separator]: 

# L500 [Executable statement]:     c.SaveAs(outpath)
    c.SaveAs(outpath)
# L501 [Executable statement]:     c.SaveAs(outpath.replace(".pdf", ".png"))
    c.SaveAs(outpath.replace(".pdf", ".png"))
# L502 [Executable statement]:     c.Close()
    c.Close()
# L503 [Blank separator]: 

# L504 [Function definition]: def makePlot(histname, xtitle, rebin, xmin, xmax, logy):
def makePlot(histname, xtitle, rebin, xmin, xmax, logy):
# L505 [Executable statement]:     """Create a single plot with stacked backgrounds and signal overlay"""
    """Create a single plot with stacked backgrounds and signal overlay"""
# L506 [Blank separator]: 

# L507 [Original comment]:     # Create canvas
    # Create canvas
# L508 [Executable statement]:     c = ROOT.TCanvas("c", "", 800, 700)
    c = ROOT.TCanvas("c", "", 800, 700)
# L509 [Executable statement]:     c.cd()
    c.cd()
# L510 [Blank separator]: 

# L511 [Conditional block]:     if logy:
    if logy:
# L512 [Executable statement]:         c.SetLogy()
        c.SetLogy()
# L513 [Blank separator]: 

# L514 [Original comment]:     # Prepare histograms
    # Prepare histograms
# L515 [Executable statement]:     bkg_hists = []
    bkg_hists = []
# L516 [Executable statement]:     sig_hists = []
    sig_hists = []
# L517 [Blank separator]: 

# L518 [Loop over iterable]:     for fname, label, color, isSignal in processes:
    for fname, label, color, isSignal in processes:
# L519 [Executable statement]:         h = getHist(fname, histname)
        h = getHist(fname, histname)
# L520 [Conditional block]:         if h is None:
        if h is None:
# L521 [Executable statement]:             continue
            continue
# L522 [Blank separator]: 

# L523 [Conditional block]:         if rebin > 1:
        if rebin > 1:
# L524 [Executable statement]:             h.Rebin(rebin)
            h.Rebin(rebin)
# L525 [Blank separator]: 

# L526 [Executable statement]:         h.SetLineColor(color)
        h.SetLineColor(color)
# L527 [Executable statement]:         h.SetLineWidth(2)
        h.SetLineWidth(2)
# L528 [Blank separator]: 

# L529 [Conditional block]:         if isSignal:
        if isSignal:
# L530 [Executable statement]:             h.SetFillStyle(0)
            h.SetFillStyle(0)
# L531 [Executable statement]:             sig_hists.append((h, label, color))
            sig_hists.append((h, label, color))
# L532 [Else branch]:         else:
        else:
# L533 [Executable statement]:             h.SetFillColor(color)
            h.SetFillColor(color)
# L534 [Executable statement]:             h.SetFillStyle(1001)
            h.SetFillStyle(1001)
# L535 [Executable statement]:             bkg_hists.append((h, label, color))
            bkg_hists.append((h, label, color))
# L536 [Blank separator]: 

# L537 [Conditional block]:     if not bkg_hists and not sig_hists:
    if not bkg_hists and not sig_hists:
# L538 [Runtime log output]:         print(f"Warning: No histograms found for {histname}")
        print(f"Warning: No histograms found for {histname}")
# L539 [Return from function]:         return
        return
# L540 [Blank separator]: 

# L541 [Original comment]:     # Create THStack for backgrounds
    # Create THStack for backgrounds
# L542 [Executable statement]:     hs = ROOT.THStack("hs", "")
    hs = ROOT.THStack("hs", "")
# L543 [Loop over iterable]:     for h, label, color in bkg_hists:
    for h, label, color in bkg_hists:
# L544 [Executable statement]:         hs.Add(h)
        hs.Add(h)
# L545 [Blank separator]: 

# L546 [Original comment]:     # Sum signals for combined overlay
    # Sum signals for combined overlay
# L547 [Executable statement]:     h_sig_sum = None
    h_sig_sum = None
# L548 [Loop over iterable]:     for h, label, color in sig_hists:
    for h, label, color in sig_hists:
# L549 [Conditional block]:         if h_sig_sum is None:
        if h_sig_sum is None:
# L550 [Executable statement]:             h_sig_sum = h.Clone("h_sig_sum")
            h_sig_sum = h.Clone("h_sig_sum")
# L551 [Else branch]:         else:
        else:
# L552 [Executable statement]:             h_sig_sum.Add(h)
            h_sig_sum.Add(h)
# L553 [Blank separator]: 

# L554 [Conditional block]:     if h_sig_sum:
    if h_sig_sum:
# L555 [Executable statement]:         h_sig_sum.SetLineColor(ROOT.kRed+1)
        h_sig_sum.SetLineColor(ROOT.kRed+1)
# L556 [Executable statement]:         h_sig_sum.SetLineWidth(3)
        h_sig_sum.SetLineWidth(3)
# L557 [Executable statement]:         h_sig_sum.SetFillStyle(0)
        h_sig_sum.SetFillStyle(0)
# L558 [Blank separator]: 

# L559 [Original comment]:     # Determine y-axis range
    # Determine y-axis range
# L560 [Executable statement]:     ymax = 0
    ymax = 0
# L561 [Conditional block]:     if hs.GetNhists() > 0:
    if hs.GetNhists() > 0:
# L562 [Executable statement]:         ymax = max(ymax, hs.GetMaximum())
        ymax = max(ymax, hs.GetMaximum())
# L563 [Conditional block]:     if h_sig_sum:
    if h_sig_sum:
# L564 [Executable statement]:         ymax = max(ymax, h_sig_sum.GetMaximum())
        ymax = max(ymax, h_sig_sum.GetMaximum())
# L565 [Blank separator]: 

# L566 [Conditional block]:     if logy:
    if logy:
# L567 [Executable statement]:         ymin = 0.1
        ymin = 0.1
# L568 [Executable statement]:         ymax *= 50
        ymax *= 50
# L569 [Else branch]:     else:
    else:
# L570 [Executable statement]:         ymin = 0
        ymin = 0
# L571 [Executable statement]:         ymax *= 1.5
        ymax *= 1.5
# L572 [Blank separator]: 

# L573 [Original comment]:     # Draw
    # Draw
# L574 [Conditional block]:     if hs.GetNhists() > 0:
    if hs.GetNhists() > 0:
# L575 [Executable statement]:         hs.Draw("HIST")
        hs.Draw("HIST")
# L576 [Executable statement]:         hs.GetXaxis().SetTitle(xtitle)
        hs.GetXaxis().SetTitle(xtitle)
# L577 [Executable statement]:         hs.GetYaxis().SetTitle("Events")
        hs.GetYaxis().SetTitle("Events")
# L578 [Executable statement]:         hs.GetXaxis().SetRangeUser(xmin, xmax)
        hs.GetXaxis().SetRangeUser(xmin, xmax)
# L579 [Executable statement]:         hs.SetMinimum(ymin)
        hs.SetMinimum(ymin)
# L580 [Executable statement]:         hs.SetMaximum(ymax)
        hs.SetMaximum(ymax)
# L581 [Executable statement]:         hs.GetXaxis().SetTitleSize(0.045)
        hs.GetXaxis().SetTitleSize(0.045)
# L582 [Executable statement]:         hs.GetYaxis().SetTitleSize(0.045)
        hs.GetYaxis().SetTitleSize(0.045)
# L583 [Executable statement]:         hs.GetXaxis().SetLabelSize(0.04)
        hs.GetXaxis().SetLabelSize(0.04)
# L584 [Executable statement]:         hs.GetYaxis().SetLabelSize(0.04)
        hs.GetYaxis().SetLabelSize(0.04)
# L585 [Executable statement]:         hs.GetYaxis().SetTitleOffset(1.3)
        hs.GetYaxis().SetTitleOffset(1.3)
# L586 [Blank separator]: 

# L587 [Conditional block]:     if h_sig_sum:
    if h_sig_sum:
# L588 [Executable statement]:         h_sig_sum.Draw("HIST SAME")
        h_sig_sum.Draw("HIST SAME")
# L589 [Blank separator]: 

# L590 [Original comment]:     # Legend
    # Legend
# L591 [Executable statement]:     leg = ROOT.TLegend(0.60, 0.65, 0.92, 0.88)
    leg = ROOT.TLegend(0.60, 0.65, 0.92, 0.88)
# L592 [Executable statement]:     leg.SetTextSize(0.032)
    leg.SetTextSize(0.032)
# L593 [Blank separator]: 

# L594 [Conditional block]:     if h_sig_sum:
    if h_sig_sum:
# L595 [Executable statement]:         leg.AddEntry(h_sig_sum, "Signal (ZH, H#rightarrowWW)", "l")
        leg.AddEntry(h_sig_sum, "Signal (ZH, H#rightarrowWW)", "l")
# L596 [Blank separator]: 

# L597 [Original comment]:     # Add backgrounds in reverse order (top to bottom in legend)
    # Add backgrounds in reverse order (top to bottom in legend)
# L598 [Loop over iterable]:     for h, label, color in reversed(bkg_hists):
    for h, label, color in reversed(bkg_hists):
# L599 [Executable statement]:         leg.AddEntry(h, label, "f")
        leg.AddEntry(h, label, "f")
# L600 [Blank separator]: 

# L601 [Executable statement]:     leg.Draw()
    leg.Draw()
# L602 [Blank separator]: 

# L603 [Original comment]:     # CMS-style label
    # CMS-style label
# L604 [Executable statement]:     latex = ROOT.TLatex()
    latex = ROOT.TLatex()
# L605 [Executable statement]:     latex.SetNDC()
    latex.SetNDC()
# L606 [Executable statement]:     latex.SetTextFont(42)
    latex.SetTextFont(42)
# L607 [Executable statement]:     latex.SetTextSize(0.04)
    latex.SetTextSize(0.04)
# L608 [Executable statement]:     latex.DrawLatex(0.14, 0.93, "#bf{FCC-ee} #it{Simulation}")
    latex.DrawLatex(0.14, 0.93, "#bf{FCC-ee} #it{Simulation}")
# L609 [Executable statement]:     latex.SetTextSize(0.035)
    latex.SetTextSize(0.035)
# L610 [Executable statement]:     latex.DrawLatex(0.70, 0.93, "#sqrt{s} = 240 GeV, 10.8 ab^{-1}")
    latex.DrawLatex(0.70, 0.93, "#sqrt{s} = 240 GeV, 10.8 ab^{-1}")
# L611 [Blank separator]: 

# L612 [Executable statement]:     os.makedirs(outputDir, exist_ok=True)
    os.makedirs(outputDir, exist_ok=True)
# L613 [Executable statement]:     c.SaveAs(os.path.join(outputDir, f"{histname}.pdf"))
    c.SaveAs(os.path.join(outputDir, f"{histname}.pdf"))
# L614 [Executable statement]:     c.SaveAs(os.path.join(outputDir, f"{histname}.png"))
    c.SaveAs(os.path.join(outputDir, f"{histname}.png"))
# L615 [Blank separator]: 

# L616 [Executable statement]:     c.Close()
    c.Close()
# L617 [Blank separator]: 

# L618 [Blank separator]: 

# L619 [Function definition]: def makeCutflowTable():
def makeCutflowTable():
# L620 [Executable statement]:     """Print cutflow table and save text/tex/pdf outputs."""
    """Print cutflow table and save text/tex/pdf outputs."""
# L621 [Blank separator]: 

# L622 [Executable statement]:     summary = collectCutflowData()
    summary = collectCutflowData()
# L623 [Blank separator]: 

# L624 [Runtime log output]:     print("\n" + "=" * 80)
    print("\n" + "=" * 80)
# L625 [Runtime log output]:     print("CUTFLOW TABLE (normalized to 10.8 ab^-1)")
    print("CUTFLOW TABLE (normalized to 10.8 ab^-1)")
# L626 [Runtime log output]:     print("=" * 80)
    print("=" * 80)
# L627 [Executable statement]:     header = f"{'Process':<25}"
    header = f"{'Process':<25}"
# L628 [Loop over iterable]:     for lab in summary["cut_labels"]:
    for lab in summary["cut_labels"]:
# L629 [Executable statement]:         header += f"{lab:>10}"
        header += f"{lab:>10}"
# L630 [Runtime log output]:     print(header)
    print(header)
# L631 [Runtime log output]:     print("-" * 95)
    print("-" * 95)
# L632 [Blank separator]: 

# L633 [Loop over iterable]:     for label, values, isSignal in summary["process_rows"]:
    for label, values, isSignal in summary["process_rows"]:
# L634 [Runtime log output]:         print(_format_table_row(label, values, ".0f"))
        print(_format_table_row(label, values, ".0f"))
# L635 [Blank separator]: 

# L636 [Runtime log output]:     print("-" * 95)
    print("-" * 95)
# L637 [Runtime log output]:     print(_format_table_row("Total Signal", summary["total_sig"], ".1f"))
    print(_format_table_row("Total Signal", summary["total_sig"], ".1f"))
# L638 [Runtime log output]:     print(_format_table_row("Total Background", summary["total_bkg"], ".1f"))
    print(_format_table_row("Total Background", summary["total_bkg"], ".1f"))
# L639 [Runtime log output]:     print("-" * 95)
    print("-" * 95)
# L640 [Runtime log output]:     print(_format_table_row("S/B", summary["s_over_b"], ".4f"))
    print(_format_table_row("S/B", summary["s_over_b"], ".4f"))
# L641 [Runtime log output]:     print(_format_table_row("S/sqrt(B)", summary["s_over_sqrt_b"], ".1f"))
    print(_format_table_row("S/sqrt(B)", summary["s_over_sqrt_b"], ".1f"))
# L642 [Runtime log output]:     print("=" * 95 + "\n")
    print("=" * 95 + "\n")
# L643 [Blank separator]: 

# L644 [Runtime log output]:     print("\n" + "=" * 80)
    print("\n" + "=" * 80)
# L645 [Runtime log output]:     print("CUTFLOW EFFICIENCY TABLE [%], cumulative w.r.t. cut0 (All)")
    print("CUTFLOW EFFICIENCY TABLE [%], cumulative w.r.t. cut0 (All)")
# L646 [Runtime log output]:     print("=" * 80)
    print("=" * 80)
# L647 [Executable statement]:     rule = "-" * (25 + PERCENT_COL_WIDTH * len(summary["cut_ids"]))
    rule = "-" * (25 + PERCENT_COL_WIDTH * len(summary["cut_ids"]))
# L648 [Runtime log output]:     print(_format_cut_header(summary["cut_ids"], PERCENT_COL_WIDTH))
    print(_format_cut_header(summary["cut_ids"], PERCENT_COL_WIDTH))
# L649 [Runtime log output]:     print(rule)
    print(rule)
# L650 [Blank separator]: 

# L651 [Loop over iterable]:     for label, values, isSignal in summary["process_eff_rows"]:
    for label, values, isSignal in summary["process_eff_rows"]:
# L652 [Runtime log output]:         print(_format_percent_row(label, values))
        print(_format_percent_row(label, values))
# L653 [Blank separator]: 

# L654 [Runtime log output]:     print(rule)
    print(rule)
# L655 [Runtime log output]:     print(_format_percent_row("Total Signal eff", summary["total_sig_eff"]))
    print(_format_percent_row("Total Signal eff", summary["total_sig_eff"]))
# L656 [Runtime log output]:     print(_format_percent_row("Total Bkg eff", summary["total_bkg_eff"]))
    print(_format_percent_row("Total Bkg eff", summary["total_bkg_eff"]))
# L657 [Runtime log output]:     print("=" * len(rule))
    print("=" * len(rule))
# L658 [Runtime log output]:     print("Cut definitions:")
    print("Cut definitions:")
# L659 [Loop over iterable]:     for cut_id, label in zip(summary["cut_ids"], summary["cut_labels"]):
    for cut_id, label in zip(summary["cut_ids"], summary["cut_labels"]):
# L660 [Runtime log output]:         print(f"  {cut_id}: {label}")
        print(f"  {cut_id}: {label}")
# L661 [Runtime log output]:     print()
    print()
# L662 [Blank separator]: 

# L663 [Executable statement]:     writeCutflowText(summary)
    writeCutflowText(summary)
# L664 [Executable statement]:     writeCutflowLatex(summary)
    writeCutflowLatex(summary)
# L665 [Executable statement]:     makeCutflowPdf(summary)
    makeCutflowPdf(summary)
# L666 [Executable statement]:     writeCutflowEfficiencyText(summary)
    writeCutflowEfficiencyText(summary)
# L667 [Executable statement]:     writeCutflowEfficiencyLatex(summary)
    writeCutflowEfficiencyLatex(summary)
# L668 [Executable statement]:     makeCutflowEfficiencyPdf(summary)
    makeCutflowEfficiencyPdf(summary)
# L669 [Blank separator]: 

# L670 [Blank separator]: 

# L671 [Function definition]: def makeNormalizedPlot(histname, xtitle, rebin, xmin, xmax, logy=False):
def makeNormalizedPlot(histname, xtitle, rebin, xmin, xmax, logy=False):
# L672 [Executable statement]:     """Create normalized stacked plot (signal and background both normalized to unit area)"""
    """Create normalized stacked plot (signal and background both normalized to unit area)"""
# L673 [Blank separator]: 

# L674 [Executable statement]:     c = ROOT.TCanvas("c", "", 800, 700)
    c = ROOT.TCanvas("c", "", 800, 700)
# L675 [Executable statement]:     c.cd()
    c.cd()
# L676 [Conditional block]:     if logy:
    if logy:
# L677 [Executable statement]:         c.SetLogy()
        c.SetLogy()
# L678 [Blank separator]: 

# L679 [Original comment]:     # Prepare histograms
    # Prepare histograms
# L680 [Executable statement]:     bkg_hists = []
    bkg_hists = []
# L681 [Executable statement]:     sig_hists = []
    sig_hists = []
# L682 [Blank separator]: 

# L683 [Loop over iterable]:     for fname, label, color, isSignal in processes:
    for fname, label, color, isSignal in processes:
# L684 [Executable statement]:         h = getHist(fname, histname)
        h = getHist(fname, histname)
# L685 [Conditional block]:         if h is None:
        if h is None:
# L686 [Executable statement]:             continue
            continue
# L687 [Blank separator]: 

# L688 [Conditional block]:         if rebin > 1:
        if rebin > 1:
# L689 [Executable statement]:             h.Rebin(rebin)
            h.Rebin(rebin)
# L690 [Blank separator]: 

# L691 [Executable statement]:         h.SetLineColor(color)
        h.SetLineColor(color)
# L692 [Executable statement]:         h.SetLineWidth(2)
        h.SetLineWidth(2)
# L693 [Blank separator]: 

# L694 [Conditional block]:         if isSignal:
        if isSignal:
# L695 [Executable statement]:             h.SetFillStyle(0)
            h.SetFillStyle(0)
# L696 [Executable statement]:             sig_hists.append((h, label, color))
            sig_hists.append((h, label, color))
# L697 [Else branch]:         else:
        else:
# L698 [Executable statement]:             h.SetFillColor(color)
            h.SetFillColor(color)
# L699 [Executable statement]:             h.SetFillStyle(1001)
            h.SetFillStyle(1001)
# L700 [Executable statement]:             bkg_hists.append((h, label, color))
            bkg_hists.append((h, label, color))
# L701 [Blank separator]: 

# L702 [Conditional block]:     if not bkg_hists and not sig_hists:
    if not bkg_hists and not sig_hists:
# L703 [Runtime log output]:         print(f"Warning: No histograms found for {histname}")
        print(f"Warning: No histograms found for {histname}")
# L704 [Return from function]:         return
        return
# L705 [Blank separator]: 

# L706 [Original comment]:     # Sum all backgrounds
    # Sum all backgrounds
# L707 [Executable statement]:     h_bkg_sum = None
    h_bkg_sum = None
# L708 [Loop over iterable]:     for h, label, color in bkg_hists:
    for h, label, color in bkg_hists:
# L709 [Conditional block]:         if h_bkg_sum is None:
        if h_bkg_sum is None:
# L710 [Executable statement]:             h_bkg_sum = h.Clone("h_bkg_sum")
            h_bkg_sum = h.Clone("h_bkg_sum")
# L711 [Else branch]:         else:
        else:
# L712 [Executable statement]:             h_bkg_sum.Add(h)
            h_bkg_sum.Add(h)
# L713 [Blank separator]: 

# L714 [Original comment]:     # Sum all signals
    # Sum all signals
# L715 [Executable statement]:     h_sig_sum = None
    h_sig_sum = None
# L716 [Loop over iterable]:     for h, label, color in sig_hists:
    for h, label, color in sig_hists:
# L717 [Conditional block]:         if h_sig_sum is None:
        if h_sig_sum is None:
# L718 [Executable statement]:             h_sig_sum = h.Clone("h_sig_sum")
            h_sig_sum = h.Clone("h_sig_sum")
# L719 [Else branch]:         else:
        else:
# L720 [Executable statement]:             h_sig_sum.Add(h)
            h_sig_sum.Add(h)
# L721 [Blank separator]: 

# L722 [Original comment]:     # Normalize both to unit area
    # Normalize both to unit area
# L723 [Conditional block]:     if h_bkg_sum and h_bkg_sum.Integral() > 0:
    if h_bkg_sum and h_bkg_sum.Integral() > 0:
# L724 [Executable statement]:         h_bkg_sum.Scale(1.0 / h_bkg_sum.Integral())
        h_bkg_sum.Scale(1.0 / h_bkg_sum.Integral())
# L725 [Conditional block]:     if h_sig_sum and h_sig_sum.Integral() > 0:
    if h_sig_sum and h_sig_sum.Integral() > 0:
# L726 [Executable statement]:         h_sig_sum.Scale(1.0 / h_sig_sum.Integral())
        h_sig_sum.Scale(1.0 / h_sig_sum.Integral())
# L727 [Blank separator]: 

# L728 [Original comment]:     # Style
    # Style
# L729 [Conditional block]:     if h_bkg_sum:
    if h_bkg_sum:
# L730 [Executable statement]:         h_bkg_sum.SetFillColor(ROOT.kAzure+1)
        h_bkg_sum.SetFillColor(ROOT.kAzure+1)
# L731 [Executable statement]:         h_bkg_sum.SetFillStyle(3004)
        h_bkg_sum.SetFillStyle(3004)
# L732 [Executable statement]:         h_bkg_sum.SetLineColor(ROOT.kAzure+1)
        h_bkg_sum.SetLineColor(ROOT.kAzure+1)
# L733 [Executable statement]:         h_bkg_sum.SetLineWidth(2)
        h_bkg_sum.SetLineWidth(2)
# L734 [Blank separator]: 

# L735 [Conditional block]:     if h_sig_sum:
    if h_sig_sum:
# L736 [Executable statement]:         h_sig_sum.SetLineColor(ROOT.kRed+1)
        h_sig_sum.SetLineColor(ROOT.kRed+1)
# L737 [Executable statement]:         h_sig_sum.SetLineWidth(3)
        h_sig_sum.SetLineWidth(3)
# L738 [Executable statement]:         h_sig_sum.SetFillStyle(0)
        h_sig_sum.SetFillStyle(0)
# L739 [Blank separator]: 

# L740 [Original comment]:     # Determine y-axis range
    # Determine y-axis range
# L741 [Executable statement]:     ymax = 0
    ymax = 0
# L742 [Conditional block]:     if h_bkg_sum:
    if h_bkg_sum:
# L743 [Executable statement]:         ymax = max(ymax, h_bkg_sum.GetMaximum())
        ymax = max(ymax, h_bkg_sum.GetMaximum())
# L744 [Conditional block]:     if h_sig_sum:
    if h_sig_sum:
# L745 [Executable statement]:         ymax = max(ymax, h_sig_sum.GetMaximum())
        ymax = max(ymax, h_sig_sum.GetMaximum())
# L746 [Blank separator]: 

# L747 [Conditional block]:     if logy:
    if logy:
# L748 [Executable statement]:         ymin = 1e-4
        ymin = 1e-4
# L749 [Executable statement]:         ymax *= 10
        ymax *= 10
# L750 [Else branch]:     else:
    else:
# L751 [Executable statement]:         ymin = 0
        ymin = 0
# L752 [Executable statement]:         ymax *= 1.4
        ymax *= 1.4
# L753 [Blank separator]: 

# L754 [Original comment]:     # Draw
    # Draw
# L755 [Executable statement]:     first = True
    first = True
# L756 [Conditional block]:     if h_bkg_sum:
    if h_bkg_sum:
# L757 [Executable statement]:         h_bkg_sum.GetXaxis().SetTitle(xtitle)
        h_bkg_sum.GetXaxis().SetTitle(xtitle)
# L758 [Executable statement]:         h_bkg_sum.GetYaxis().SetTitle("Normalized")
        h_bkg_sum.GetYaxis().SetTitle("Normalized")
# L759 [Executable statement]:         h_bkg_sum.GetXaxis().SetRangeUser(xmin, xmax)
        h_bkg_sum.GetXaxis().SetRangeUser(xmin, xmax)
# L760 [Executable statement]:         h_bkg_sum.SetMinimum(ymin)
        h_bkg_sum.SetMinimum(ymin)
# L761 [Executable statement]:         h_bkg_sum.SetMaximum(ymax)
        h_bkg_sum.SetMaximum(ymax)
# L762 [Executable statement]:         h_bkg_sum.GetXaxis().SetTitleSize(0.045)
        h_bkg_sum.GetXaxis().SetTitleSize(0.045)
# L763 [Executable statement]:         h_bkg_sum.GetYaxis().SetTitleSize(0.045)
        h_bkg_sum.GetYaxis().SetTitleSize(0.045)
# L764 [Executable statement]:         h_bkg_sum.GetXaxis().SetLabelSize(0.04)
        h_bkg_sum.GetXaxis().SetLabelSize(0.04)
# L765 [Executable statement]:         h_bkg_sum.GetYaxis().SetLabelSize(0.04)
        h_bkg_sum.GetYaxis().SetLabelSize(0.04)
# L766 [Executable statement]:         h_bkg_sum.GetYaxis().SetTitleOffset(1.3)
        h_bkg_sum.GetYaxis().SetTitleOffset(1.3)
# L767 [Executable statement]:         h_bkg_sum.Draw("HIST")
        h_bkg_sum.Draw("HIST")
# L768 [Executable statement]:         first = False
        first = False
# L769 [Blank separator]: 

# L770 [Conditional block]:     if h_sig_sum:
    if h_sig_sum:
# L771 [Conditional block]:         if first:
        if first:
# L772 [Executable statement]:             h_sig_sum.GetXaxis().SetTitle(xtitle)
            h_sig_sum.GetXaxis().SetTitle(xtitle)
# L773 [Executable statement]:             h_sig_sum.GetYaxis().SetTitle("Normalized")
            h_sig_sum.GetYaxis().SetTitle("Normalized")
# L774 [Executable statement]:             h_sig_sum.GetXaxis().SetRangeUser(xmin, xmax)
            h_sig_sum.GetXaxis().SetRangeUser(xmin, xmax)
# L775 [Executable statement]:             h_sig_sum.SetMinimum(ymin)
            h_sig_sum.SetMinimum(ymin)
# L776 [Executable statement]:             h_sig_sum.SetMaximum(ymax)
            h_sig_sum.SetMaximum(ymax)
# L777 [Executable statement]:             h_sig_sum.GetXaxis().SetTitleSize(0.045)
            h_sig_sum.GetXaxis().SetTitleSize(0.045)
# L778 [Executable statement]:             h_sig_sum.GetYaxis().SetTitleSize(0.045)
            h_sig_sum.GetYaxis().SetTitleSize(0.045)
# L779 [Executable statement]:             h_sig_sum.GetXaxis().SetLabelSize(0.04)
            h_sig_sum.GetXaxis().SetLabelSize(0.04)
# L780 [Executable statement]:             h_sig_sum.GetYaxis().SetLabelSize(0.04)
            h_sig_sum.GetYaxis().SetLabelSize(0.04)
# L781 [Executable statement]:             h_sig_sum.GetYaxis().SetTitleOffset(1.3)
            h_sig_sum.GetYaxis().SetTitleOffset(1.3)
# L782 [Executable statement]:             h_sig_sum.Draw("HIST")
            h_sig_sum.Draw("HIST")
# L783 [Else branch]:         else:
        else:
# L784 [Executable statement]:             h_sig_sum.Draw("HIST SAME")
            h_sig_sum.Draw("HIST SAME")
# L785 [Blank separator]: 

# L786 [Original comment]:     # Legend
    # Legend
# L787 [Executable statement]:     leg = ROOT.TLegend(0.60, 0.75, 0.92, 0.88)
    leg = ROOT.TLegend(0.60, 0.75, 0.92, 0.88)
# L788 [Executable statement]:     leg.SetTextSize(0.032)
    leg.SetTextSize(0.032)
# L789 [Conditional block]:     if h_sig_sum:
    if h_sig_sum:
# L790 [Executable statement]:         leg.AddEntry(h_sig_sum, "Signal (ZH, H#rightarrowWW)", "l")
        leg.AddEntry(h_sig_sum, "Signal (ZH, H#rightarrowWW)", "l")
# L791 [Conditional block]:     if h_bkg_sum:
    if h_bkg_sum:
# L792 [Executable statement]:         leg.AddEntry(h_bkg_sum, "Background (all)", "f")
        leg.AddEntry(h_bkg_sum, "Background (all)", "f")
# L793 [Executable statement]:     leg.Draw()
    leg.Draw()
# L794 [Blank separator]: 

# L795 [Original comment]:     # CMS-style label
    # CMS-style label
# L796 [Executable statement]:     latex = ROOT.TLatex()
    latex = ROOT.TLatex()
# L797 [Executable statement]:     latex.SetNDC()
    latex.SetNDC()
# L798 [Executable statement]:     latex.SetTextFont(42)
    latex.SetTextFont(42)
# L799 [Executable statement]:     latex.SetTextSize(0.04)
    latex.SetTextSize(0.04)
# L800 [Executable statement]:     latex.DrawLatex(0.14, 0.93, "#bf{FCC-ee} #it{Simulation} (normalized)")
    latex.DrawLatex(0.14, 0.93, "#bf{FCC-ee} #it{Simulation} (normalized)")
# L801 [Executable statement]:     latex.SetTextSize(0.035)
    latex.SetTextSize(0.035)
# L802 [Executable statement]:     latex.DrawLatex(0.70, 0.93, "#sqrt{s} = 240 GeV")
    latex.DrawLatex(0.70, 0.93, "#sqrt{s} = 240 GeV")
# L803 [Blank separator]: 

# L804 [Executable statement]:     os.makedirs(outputDir, exist_ok=True)
    os.makedirs(outputDir, exist_ok=True)
# L805 [Executable statement]:     c.SaveAs(os.path.join(outputDir, f"{histname}_norm.pdf"))
    c.SaveAs(os.path.join(outputDir, f"{histname}_norm.pdf"))
# L806 [Executable statement]:     c.SaveAs(os.path.join(outputDir, f"{histname}_norm.png"))
    c.SaveAs(os.path.join(outputDir, f"{histname}_norm.png"))
# L807 [Blank separator]: 

# L808 [Executable statement]:     c.Close()
    c.Close()
# L809 [Blank separator]: 

# L810 [Blank separator]: 

# L811 [Function definition]: def makeComparisonPlot(histname, xtitle, rebin, xmin, xmax):
def makeComparisonPlot(histname, xtitle, rebin, xmin, xmax):
# L812 [Executable statement]:     """Create shape comparison plot (normalized to unit area)"""
    """Create shape comparison plot (normalized to unit area)"""
# L813 [Blank separator]: 

# L814 [Executable statement]:     c = ROOT.TCanvas("c", "", 800, 600)
    c = ROOT.TCanvas("c", "", 800, 600)
# L815 [Executable statement]:     c.cd()
    c.cd()
# L816 [Blank separator]: 

# L817 [Original comment]:     # Only compare signal vs main backgrounds
    # Only compare signal vs main backgrounds
# L818 [Executable statement]:     compare = [
    compare = [
# L819 [Executable statement]:         ("wzp6_ee_hadZH_HWW_ecm240", "Signal (ZH, H#rightarrowWW)", ROOT.kRed+1),
        ("wzp6_ee_hadZH_HWW_ecm240", "Signal (ZH, H#rightarrowWW)", ROOT.kRed+1),
# L820 [Executable statement]:         ("p8_ee_WW_ecm240", "WW bkg", ROOT.kOrange-3),
        ("p8_ee_WW_ecm240", "WW bkg", ROOT.kOrange-3),
# L821 [Executable statement]:         ("p8_ee_ZZ_ecm240", "ZZ bkg", ROOT.kAzure+1),
        ("p8_ee_ZZ_ecm240", "ZZ bkg", ROOT.kAzure+1),
# L822 [Executable statement]:     ]
    ]
# L823 [Blank separator]: 

# L824 [Executable statement]:     hists = []
    hists = []
# L825 [Loop over iterable]:     for fname, label, color in compare:
    for fname, label, color in compare:
# L826 [Executable statement]:         h = getHist(fname, histname)
        h = getHist(fname, histname)
# L827 [Conditional block]:         if h is None:
        if h is None:
# L828 [Executable statement]:             continue
            continue
# L829 [Blank separator]: 

# L830 [Conditional block]:         if rebin > 1:
        if rebin > 1:
# L831 [Executable statement]:             h.Rebin(rebin)
            h.Rebin(rebin)
# L832 [Blank separator]: 

# L833 [Original comment]:         # Normalize to unit area
        # Normalize to unit area
# L834 [Conditional block]:         if h.Integral() > 0:
        if h.Integral() > 0:
# L835 [Executable statement]:             h.Scale(1.0 / h.Integral())
            h.Scale(1.0 / h.Integral())
# L836 [Blank separator]: 

# L837 [Executable statement]:         h.SetLineColor(color)
        h.SetLineColor(color)
# L838 [Executable statement]:         h.SetLineWidth(3)
        h.SetLineWidth(3)
# L839 [Executable statement]:         h.SetFillStyle(0)
        h.SetFillStyle(0)
# L840 [Executable statement]:         hists.append((h, label))
        hists.append((h, label))
# L841 [Blank separator]: 

# L842 [Conditional block]:     if not hists:
    if not hists:
# L843 [Return from function]:         return
        return
# L844 [Blank separator]: 

# L845 [Original comment]:     # Find y-axis range
    # Find y-axis range
# L846 [Executable statement]:     ymax = max(h.GetMaximum() for h, _ in hists) * 1.4
    ymax = max(h.GetMaximum() for h, _ in hists) * 1.4
# L847 [Blank separator]: 

# L848 [Original comment]:     # Draw
    # Draw
# L849 [Loop over iterable]:     for i, (h, label) in enumerate(hists):
    for i, (h, label) in enumerate(hists):
# L850 [Executable statement]:         h.GetXaxis().SetTitle(xtitle)
        h.GetXaxis().SetTitle(xtitle)
# L851 [Executable statement]:         h.GetYaxis().SetTitle("Normalized")
        h.GetYaxis().SetTitle("Normalized")
# L852 [Executable statement]:         h.GetXaxis().SetRangeUser(xmin, xmax)
        h.GetXaxis().SetRangeUser(xmin, xmax)
# L853 [Executable statement]:         h.SetMaximum(ymax)
        h.SetMaximum(ymax)
# L854 [Executable statement]:         h.SetMinimum(0)
        h.SetMinimum(0)
# L855 [Conditional block]:         if i == 0:
        if i == 0:
# L856 [Executable statement]:             h.Draw("HIST")
            h.Draw("HIST")
# L857 [Else branch]:         else:
        else:
# L858 [Executable statement]:             h.Draw("HIST SAME")
            h.Draw("HIST SAME")
# L859 [Blank separator]: 

# L860 [Original comment]:     # Legend
    # Legend
# L861 [Executable statement]:     leg = ROOT.TLegend(0.60, 0.70, 0.92, 0.88)
    leg = ROOT.TLegend(0.60, 0.70, 0.92, 0.88)
# L862 [Loop over iterable]:     for h, label in hists:
    for h, label in hists:
# L863 [Executable statement]:         leg.AddEntry(h, label, "l")
        leg.AddEntry(h, label, "l")
# L864 [Executable statement]:     leg.Draw()
    leg.Draw()
# L865 [Blank separator]: 

# L866 [Original comment]:     # Label
    # Label
# L867 [Executable statement]:     latex = ROOT.TLatex()
    latex = ROOT.TLatex()
# L868 [Executable statement]:     latex.SetNDC()
    latex.SetNDC()
# L869 [Executable statement]:     latex.SetTextFont(42)
    latex.SetTextFont(42)
# L870 [Executable statement]:     latex.SetTextSize(0.04)
    latex.SetTextSize(0.04)
# L871 [Executable statement]:     latex.DrawLatex(0.14, 0.93, "#bf{FCC-ee} #it{Simulation} (shape comparison)")
    latex.DrawLatex(0.14, 0.93, "#bf{FCC-ee} #it{Simulation} (shape comparison)")
# L872 [Blank separator]: 

# L873 [Executable statement]:     os.makedirs(outputDir, exist_ok=True)
    os.makedirs(outputDir, exist_ok=True)
# L874 [Executable statement]:     c.SaveAs(os.path.join(outputDir, f"{histname}_shape.pdf"))
    c.SaveAs(os.path.join(outputDir, f"{histname}_shape.pdf"))
# L875 [Executable statement]:     c.SaveAs(os.path.join(outputDir, f"{histname}_shape.png"))
    c.SaveAs(os.path.join(outputDir, f"{histname}_shape.png"))
# L876 [Blank separator]: 

# L877 [Executable statement]:     c.Close()
    c.Close()
# L878 [Blank separator]: 

# L879 [Blank separator]: 

# L880 [Original comment]: # ============================================================
# ============================================================
# L881 [Original comment]: # Main
# Main
# L882 [Original comment]: # ============================================================
# ============================================================
# L883 [Blank separator]: 

# L884 [Conditional block]: if __name__ == "__main__":
if __name__ == "__main__":
# L885 [Blank separator]: 

# L886 [Executable statement]:     setStyle()
    setStyle()
# L887 [Blank separator]: 

# L888 [Runtime log output]:     print("=" * 60)
    print("=" * 60)
# L889 [Runtime log output]:     print("H->WW->lvqq Analysis Plotting Script")
    print("H->WW->lvqq Analysis Plotting Script")
# L890 [Runtime log output]:     print("=" * 60)
    print("=" * 60)
# L891 [Runtime log output]:     print(f"Input directory:  {inputDir}")
    print(f"Input directory:  {inputDir}")
# L892 [Runtime log output]:     print(f"Output directory: {outputDir}")
    print(f"Output directory: {outputDir}")
# L893 [Runtime log output]:     print(f"Luminosity:       {intLumi/1e6:.1f} ab^-1")
    print(f"Luminosity:       {intLumi/1e6:.1f} ab^-1")
# L894 [Runtime log output]:     print("=" * 60)
    print("=" * 60)
# L895 [Blank separator]: 

# L896 [Original comment]:     # Check input directory
    # Check input directory
# L897 [Conditional block]:     if not os.path.exists(inputDir):
    if not os.path.exists(inputDir):
# L898 [Runtime log output]:         print(f"ERROR: Input directory {inputDir} does not exist!")
        print(f"ERROR: Input directory {inputDir} does not exist!")
# L899 [Runtime log output]:         print("Please run the analysis first with:")
        print("Please run the analysis first with:")
# L900 [Runtime log output]:         print("  fccanalysis run h_hww_lvqq.py")
        print("  fccanalysis run h_hww_lvqq.py")
# L901 [Executable statement]:         sys.exit(1)
        sys.exit(1)
# L902 [Blank separator]: 

# L903 [Original comment]:     # Make all stacked plots (unnormalized)
    # Make all stacked plots (unnormalized)
# L904 [Runtime log output]:     print("\nGenerating stacked plots (unnormalized)...")
    print("\nGenerating stacked plots (unnormalized)...")
# L905 [Loop over iterable]:     for hname, xtitle, rebin, xmin, xmax, logy in histograms:
    for hname, xtitle, rebin, xmin, xmax, logy in histograms:
# L906 [Runtime log output]:         print(f"  {hname}...")
        print(f"  {hname}...")
# L907 [Executable statement]:         makePlot(hname, xtitle, rebin, xmin, xmax, logy)
        makePlot(hname, xtitle, rebin, xmin, xmax, logy)
# L908 [Blank separator]: 

# L909 [Original comment]:     # Make normalized plots (signal vs background, both normalized to unit area)
    # Make normalized plots (signal vs background, both normalized to unit area)
# L910 [Runtime log output]:     print("\nGenerating normalized plots...")
    print("\nGenerating normalized plots...")
# L911 [Executable statement]:     norm_hists = [
    norm_hists = [
# L912 [Executable statement]:         ("lepton_p", "Lepton momentum [GeV]", 4, 0, 150),
        ("lepton_p", "Lepton momentum [GeV]", 4, 0, 150),
# L913 [Executable statement]:         ("lepton_iso", "Lepton isolation", 2, 0, 1),
        ("lepton_iso", "Lepton isolation", 2, 0, 1),
# L914 [Executable statement]:         ("missingEnergy_e", "Missing energy [GeV]", 4, 0, 150),
        ("missingEnergy_e", "Missing energy [GeV]", 4, 0, 150),
# L915 [Executable statement]:         ("missingEnergy_p", "Missing momentum [GeV]", 4, 0, 150),
        ("missingEnergy_p", "Missing momentum [GeV]", 4, 0, 150),
# L916 [Executable statement]:         ("missingMass", "Missing mass [GeV]", 4, 0, 240),
        ("missingMass", "Missing mass [GeV]", 4, 0, 240),
# L917 [Executable statement]:         ("cosTheta_miss", "|cos(#theta_{miss})|", 1, 0, 1),
        ("cosTheta_miss", "|cos(#theta_{miss})|", 1, 0, 1),
# L918 [Executable statement]:         ("visibleEnergy", "Visible energy (no lepton) [GeV]", 4, 0, 250),
        ("visibleEnergy", "Visible energy (no lepton) [GeV]", 4, 0, 250),
# L919 [Executable statement]:         ("jet0_p", "Jet 0 momentum [GeV]", 4, 0, 120),
        ("jet0_p", "Jet 0 momentum [GeV]", 4, 0, 120),
# L920 [Executable statement]:         ("jet1_p", "Jet 1 momentum [GeV]", 4, 0, 120),
        ("jet1_p", "Jet 1 momentum [GeV]", 4, 0, 120),
# L921 [Executable statement]:         ("jet2_p", "Jet 2 momentum [GeV]", 4, 0, 120),
        ("jet2_p", "Jet 2 momentum [GeV]", 4, 0, 120),
# L922 [Executable statement]:         ("jet3_p", "Jet 3 momentum [GeV]", 4, 0, 120),
        ("jet3_p", "Jet 3 momentum [GeV]", 4, 0, 120),
# L923 [Executable statement]:         ("Zcand_m", "m_{Z cand} [GeV]", 4, 0, 200),
        ("Zcand_m", "m_{Z cand} [GeV]", 4, 0, 200),
# L924 [Executable statement]:         ("Wstar_m", "m_{W*} [GeV]", 4, 0, 150),
        ("Wstar_m", "m_{W*} [GeV]", 4, 0, 150),
# L925 [Executable statement]:         ("Wlep_m", "m_{W_{lep}} [GeV]", 4, 0, 200),
        ("Wlep_m", "m_{W_{lep}} [GeV]", 4, 0, 200),
# L926 [Executable statement]:         ("Hcand_m", "m_{H cand} [GeV]", 4, 50, 250),
        ("Hcand_m", "m_{H cand} [GeV]", 4, 50, 250),
# L927 [Executable statement]:         ("Hcand_m_afterZ", "m_{H cand} (after Z cut) [GeV]", 4, 50, 250),
        ("Hcand_m_afterZ", "m_{H cand} (after Z cut) [GeV]", 4, 50, 250),
# L928 [Executable statement]:         ("Hcand_m_final", "m_{H cand} (final) [GeV]", 4, 50, 250),
        ("Hcand_m_final", "m_{H cand} (final) [GeV]", 4, 50, 250),
# L929 [Executable statement]:         ("recoil_m", "Recoil mass [GeV]", 4, 50, 200),
        ("recoil_m", "Recoil mass [GeV]", 4, 50, 200),
# L930 [Executable statement]:         ("recoil_m_afterZ", "Recoil mass (after Z cut) [GeV]", 4, 50, 200),
        ("recoil_m_afterZ", "Recoil mass (after Z cut) [GeV]", 4, 50, 200),
# L931 [Executable statement]:         ("deltaZ", "|m_{jj} - m_{Z}| [GeV]", 4, 0, 50),
        ("deltaZ", "|m_{jj} - m_{Z}| [GeV]", 4, 0, 50),
# L932 [Executable statement]:     ]
    ]
# L933 [Loop over iterable]:     for hname, xtitle, rebin, xmin, xmax in norm_hists:
    for hname, xtitle, rebin, xmin, xmax in norm_hists:
# L934 [Runtime log output]:         print(f"  {hname}_norm...")
        print(f"  {hname}_norm...")
# L935 [Executable statement]:         makeNormalizedPlot(hname, xtitle, rebin, xmin, xmax)
        makeNormalizedPlot(hname, xtitle, rebin, xmin, xmax)
# L936 [Blank separator]: 

# L937 [Original comment]:     # Make shape comparison plots (signal vs WW vs ZZ separately)
    # Make shape comparison plots (signal vs WW vs ZZ separately)
# L938 [Runtime log output]:     print("\nGenerating shape comparison plots...")
    print("\nGenerating shape comparison plots...")
# L939 [Executable statement]:     shape_hists = [
    shape_hists = [
# L940 [Executable statement]:         ("Zcand_m", "m_{Z cand} [GeV]", 4, 0, 200),
        ("Zcand_m", "m_{Z cand} [GeV]", 4, 0, 200),
# L941 [Executable statement]:         ("Wstar_m", "m_{W*} [GeV]", 4, 0, 150),
        ("Wstar_m", "m_{W*} [GeV]", 4, 0, 150),
# L942 [Executable statement]:         ("Hcand_m", "m_{H cand} [GeV]", 4, 50, 250),
        ("Hcand_m", "m_{H cand} [GeV]", 4, 50, 250),
# L943 [Executable statement]:         ("recoil_m", "Recoil mass [GeV]", 4, 50, 200),
        ("recoil_m", "Recoil mass [GeV]", 4, 50, 200),
# L944 [Executable statement]:         ("deltaZ", "|m_{jj} - m_{Z}| [GeV]", 4, 0, 50),
        ("deltaZ", "|m_{jj} - m_{Z}| [GeV]", 4, 0, 50),
# L945 [Executable statement]:         ("lepton_p", "Lepton momentum [GeV]", 4, 0, 150),
        ("lepton_p", "Lepton momentum [GeV]", 4, 0, 150),
# L946 [Executable statement]:         ("lepton_iso", "Lepton isolation", 2, 0, 1),
        ("lepton_iso", "Lepton isolation", 2, 0, 1),
# L947 [Executable statement]:         ("missingEnergy_e", "Missing energy [GeV]", 4, 0, 150),
        ("missingEnergy_e", "Missing energy [GeV]", 4, 0, 150),
# L948 [Executable statement]:         ("missingEnergy_p", "Missing momentum [GeV]", 4, 0, 150),
        ("missingEnergy_p", "Missing momentum [GeV]", 4, 0, 150),
# L949 [Executable statement]:         ("missingMass", "Missing mass [GeV]", 4, 0, 240),
        ("missingMass", "Missing mass [GeV]", 4, 0, 240),
# L950 [Executable statement]:         ("cosTheta_miss", "|cos(#theta_{miss})|", 1, 0, 1),
        ("cosTheta_miss", "|cos(#theta_{miss})|", 1, 0, 1),
# L951 [Executable statement]:         ("visibleEnergy", "Visible energy (no lepton) [GeV]", 4, 0, 250),
        ("visibleEnergy", "Visible energy (no lepton) [GeV]", 4, 0, 250),
# L952 [Executable statement]:         ("jet0_p", "Jet 0 momentum [GeV]", 4, 0, 120),
        ("jet0_p", "Jet 0 momentum [GeV]", 4, 0, 120),
# L953 [Executable statement]:         ("jet1_p", "Jet 1 momentum [GeV]", 4, 0, 120),
        ("jet1_p", "Jet 1 momentum [GeV]", 4, 0, 120),
# L954 [Executable statement]:         ("jet2_p", "Jet 2 momentum [GeV]", 4, 0, 120),
        ("jet2_p", "Jet 2 momentum [GeV]", 4, 0, 120),
# L955 [Executable statement]:         ("jet3_p", "Jet 3 momentum [GeV]", 4, 0, 120),
        ("jet3_p", "Jet 3 momentum [GeV]", 4, 0, 120),
# L956 [Executable statement]:     ]
    ]
# L957 [Loop over iterable]:     for hname, xtitle, rebin, xmin, xmax in shape_hists:
    for hname, xtitle, rebin, xmin, xmax in shape_hists:
# L958 [Runtime log output]:         print(f"  {hname}_shape...")
        print(f"  {hname}_shape...")
# L959 [Executable statement]:         makeComparisonPlot(hname, xtitle, rebin, xmin, xmax)
        makeComparisonPlot(hname, xtitle, rebin, xmin, xmax)
# L960 [Blank separator]: 

# L961 [Original comment]:     # Print cutflow table
    # Print cutflow table
# L962 [Executable statement]:     makeCutflowTable()
    makeCutflowTable()
# L963 [Blank separator]: 

# L964 [Runtime log output]:     print(f"All plots saved to: {outputDir}")
    print(f"All plots saved to: {outputDir}")
# L965 [Runtime log output]:     print("Done!")
    print("Done!")
