# Annotated rewrite generated for: h_hww_lvqq.py
# L1 [Import statement]: import os
import os
# L2 [Blank separator]: 

# L3 [Import statement]: import ROOT
import ROOT
# L4 [Blank separator]: 

# L5 [Import statement]: from ml_config import (
from ml_config import (
# L6 [Executable statement]:     BACKGROUND_SAMPLES,
    BACKGROUND_SAMPLES,
# L7 [Executable statement]:     BACKGROUND_FRACTIONS,
    BACKGROUND_FRACTIONS,
# L8 [Executable statement]:     ML_FEATURES,
    ML_FEATURES,
# L9 [Executable statement]:     ML_SPECTATORS,
    ML_SPECTATORS,
# L10 [Executable statement]:     SAMPLE_PROCESSING_FRACTIONS,
    SAMPLE_PROCESSING_FRACTIONS,
# L11 [Executable statement]:     SIGNAL_SAMPLES,
    SIGNAL_SAMPLES,
# L12 [Executable statement]: )
)
# L13 [Blank separator]: 

# L14 [Executable statement]: ROOT.TH1.SetDefaultSumw2(ROOT.kTRUE)
ROOT.TH1.SetDefaultSumw2(ROOT.kTRUE)
# L15 [Blank separator]: 

# L16 [Original comment]: # ============================================================
# ============================================================
# L17 [Original comment]: # FCC-ee analysis: e+e- -> Z(qq) H(WW -> l nu qq)
# FCC-ee analysis: e+e- -> Z(qq) H(WW -> l nu qq)
# L18 [Original comment]: # Final state: 4 jets + 1 lepton (e/mu) + MET
# Final state: 4 jets + 1 lepton (e/mu) + MET
# L19 [Original comment]: # ============================================================
# ============================================================
# L20 [Blank separator]: 

# L21 [Executable statement]: ecm = 240
ecm = 240
# L22 [Executable statement]: mode = os.environ.get("LVQQ_MODE", "histmaker").strip().lower()
mode = os.environ.get("LVQQ_MODE", "histmaker").strip().lower()
# L23 [Conditional block]: if mode not in {"histmaker", "treemaker"}:
if mode not in {"histmaker", "treemaker"}:
# L24 [Executable statement]:     raise RuntimeError(f"Unsupported LVQQ_MODE={mode!r}; use 'histmaker' or 'treemaker'")
    raise RuntimeError(f"Unsupported LVQQ_MODE={mode!r}; use 'histmaker' or 'treemaker'")
# L25 [Blank separator]: 

# L26 [Executable statement]: treemaker = mode == "treemaker"
treemaker = mode == "treemaker"
# L27 [Blank separator]: 

# L28 [Blank separator]: 

# L29 [Function definition]: def _get_worker_cpus() -> int:
def _get_worker_cpus() -> int:
# L30 [Executable statement]:     raw_value = os.environ.get("LVQQ_CPUS", os.environ.get("SLURM_CPUS_PER_TASK", "32"))
    raw_value = os.environ.get("LVQQ_CPUS", os.environ.get("SLURM_CPUS_PER_TASK", "32"))
# L31 [Exception handling start]:     try:
    try:
# L32 [Executable statement]:         cpus = int(raw_value)
        cpus = int(raw_value)
# L33 [Exception handler]:     except ValueError as exc:
    except ValueError as exc:
# L34 [Executable statement]:         raise RuntimeError(f"Invalid CPU setting {raw_value!r}; expected a positive integer") from exc
        raise RuntimeError(f"Invalid CPU setting {raw_value!r}; expected a positive integer") from exc
# L35 [Conditional block]:     if cpus < 1:
    if cpus < 1:
# L36 [Executable statement]:         raise RuntimeError(f"Invalid CPU setting {raw_value!r}; expected a positive integer")
        raise RuntimeError(f"Invalid CPU setting {raw_value!r}; expected a positive integer")
# L37 [Function return]:     return cpus
    return cpus
# L38 [Blank separator]: 

# L39 [Executable statement]: processList = {
processList = {
# L40 [Original comment]:     # Signal: ZH -> Z(qq) H(WW* -> lvqq)
    # Signal: ZH -> Z(qq) H(WW* -> lvqq)
# L41 [Executable statement]:     **{sample: {"fraction": SAMPLE_PROCESSING_FRACTIONS[sample]} for sample in SIGNAL_SAMPLES},
    **{sample: {"fraction": SAMPLE_PROCESSING_FRACTIONS[sample]} for sample in SIGNAL_SAMPLES},
# L42 [Original comment]:     # Full background model with mixed processing fractions.
    # Full background model with mixed processing fractions.
# L43 [Executable statement]:     **{sample: {"fraction": SAMPLE_PROCESSING_FRACTIONS[sample]} for sample in BACKGROUND_SAMPLES},
    **{sample: {"fraction": SAMPLE_PROCESSING_FRACTIONS[sample]} for sample in BACKGROUND_SAMPLES},
# L44 [Executable statement]: }
}
# L45 [Blank separator]: 

# L46 [Executable statement]: inputDir = "/ceph/submit/data/group/fcc/ee/generation/DelphesEvents/winter2023/IDEA/"
inputDir = "/ceph/submit/data/group/fcc/ee/generation/DelphesEvents/winter2023/IDEA/"
# L47 [Executable statement]: procDict = "/ceph/submit/data/group/fcc/ee/generation/DelphesEvents/winter2023/IDEA/samplesDict.json"
procDict = "/ceph/submit/data/group/fcc/ee/generation/DelphesEvents/winter2023/IDEA/samplesDict.json"
# L48 [Executable statement]: includePaths = ["../functions/functions.h", "../functions/functions_gen.h", "utils.h"]
includePaths = ["../functions/functions.h", "../functions/functions_gen.h", "utils.h"]
# L49 [Blank separator]: 

# L50 [Conditional block]: if treemaker:
if treemaker:
# L51 [Executable statement]:     outputDir = f"output/h_hww_lvqq/treemaker/ecm{ecm}/"
    outputDir = f"output/h_hww_lvqq/treemaker/ecm{ecm}/"
# L52 [Else branch]: else:
else:
# L53 [Executable statement]:     outputDir = f"output/h_hww_lvqq/histmaker/ecm{ecm}/"
    outputDir = f"output/h_hww_lvqq/histmaker/ecm{ecm}/"
# L54 [Blank separator]: 

# L55 [Executable statement]: nCPUS = _get_worker_cpus()
nCPUS = _get_worker_cpus()
# L56 [Executable statement]: ROOT.EnableImplicitMT(nCPUS)
ROOT.EnableImplicitMT(nCPUS)
# L57 [Runtime log output]: print(f"[lvqq] active backgrounds: {len(BACKGROUND_SAMPLES)}")
print(f"[lvqq] active backgrounds: {len(BACKGROUND_SAMPLES)}")
# L58 [Runtime log output]: print(
print(
# L59 [Executable statement]:     "[lvqq] fractions:"
    "[lvqq] fractions:"
# L60 [Executable statement]:     f" WW={BACKGROUND_FRACTIONS['ww']:.6g},"
    f" WW={BACKGROUND_FRACTIONS['ww']:.6g},"
# L61 [Executable statement]:     f" ZZ={BACKGROUND_FRACTIONS['zz']:.6g},"
    f" ZZ={BACKGROUND_FRACTIONS['zz']:.6g},"
# L62 [Executable statement]:     f" qq={BACKGROUND_FRACTIONS['qq']:.6g},"
    f" qq={BACKGROUND_FRACTIONS['qq']:.6g},"
# L63 [Executable statement]:     f" tautau={BACKGROUND_FRACTIONS['tautau']:.6g}"
    f" tautau={BACKGROUND_FRACTIONS['tautau']:.6g}"
# L64 [Executable statement]: )
)
# L65 [Blank separator]: 

# L66 [Executable statement]: doScale = True
doScale = True
# L67 [Executable statement]: intLumi = 10.8e6 if ecm == 240 else 3e6
intLumi = 10.8e6 if ecm == 240 else 3e6
# L68 [Blank separator]: 

# L69 [Executable statement]: bins_count = (50, 0, 50)
bins_count = (50, 0, 50)
# L70 [Executable statement]: bins_p = (200, 0, 200)
bins_p = (200, 0, 200)
# L71 [Executable statement]: bins_m = (400, 0, 400)
bins_m = (400, 0, 400)
# L72 [Executable statement]: bins_met = (200, 0, 200)
bins_met = (200, 0, 200)
# L73 [Executable statement]: bins_chi2 = (200, 0, 50)
bins_chi2 = (200, 0, 50)
# L74 [Executable statement]: bins_recoil = (400, 0, 200)
bins_recoil = (400, 0, 200)
# L75 [Executable statement]: bins_cos = (100, 0, 1)
bins_cos = (100, 0, 1)
# L76 [Executable statement]: bins_iso = (100, 0, 1)
bins_iso = (100, 0, 1)
# L77 [Blank separator]: 

# L78 [Blank separator]: 

# L79 [Function definition]: def build_graph_lvqq(df, dataset):
def build_graph_lvqq(df, dataset):
# L80 [Executable statement]:     hists = []
    hists = []
# L81 [Blank separator]: 

# L82 [Executable statement]:     df = df.Define("ecm", str(ecm))
    df = df.Define("ecm", str(ecm))
# L83 [Executable statement]:     df = df.Define("weight", "1.0")
    df = df.Define("weight", "1.0")
# L84 [Executable statement]:     weightsum = df.Sum("weight")
    weightsum = df.Sum("weight")
# L85 [Blank separator]: 

# L86 [Loop over iterable]:     for i in range(0, 12):
    for i in range(0, 12):
# L87 [Executable statement]:         df = df.Define(f"cut{i}", str(i))
        df = df.Define(f"cut{i}", str(i))
# L88 [Blank separator]: 

# L89 [Executable statement]:     hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut0"))
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut0"))
# L90 [Blank separator]: 

# L91 [Executable statement]:     df = df.Alias("Muon0", "Muon#0.index")
    df = df.Alias("Muon0", "Muon#0.index")
# L92 [Executable statement]:     df = df.Alias("Electron0", "Electron#0.index")
    df = df.Alias("Electron0", "Electron#0.index")
# L93 [Blank separator]: 

# L94 [Executable statement]:     df = df.Define("muons_all", "FCCAnalyses::ReconstructedParticle::get(Muon0, ReconstructedParticles)")
    df = df.Define("muons_all", "FCCAnalyses::ReconstructedParticle::get(Muon0, ReconstructedParticles)")
# L95 [Executable statement]:     df = df.Define("electrons_all", "FCCAnalyses::ReconstructedParticle::get(Electron0, ReconstructedParticles)")
    df = df.Define("electrons_all", "FCCAnalyses::ReconstructedParticle::get(Electron0, ReconstructedParticles)")
# L96 [Blank separator]: 

# L97 [Original comment]:     # cut1: exactly one high-momentum lepton
    # cut1: exactly one high-momentum lepton
# L98 [Executable statement]:     df = df.Define("muons_p20", "FCCAnalyses::ReconstructedParticle::sel_p(20)(muons_all)")
    df = df.Define("muons_p20", "FCCAnalyses::ReconstructedParticle::sel_p(20)(muons_all)")
# L99 [Executable statement]:     df = df.Define("electrons_p20", "FCCAnalyses::ReconstructedParticle::sel_p(20)(electrons_all)")
    df = df.Define("electrons_p20", "FCCAnalyses::ReconstructedParticle::sel_p(20)(electrons_all)")
# L100 [Executable statement]:     df = df.Define("leptons_p20", "FCCAnalyses::ReconstructedParticle::merge(muons_p20, electrons_p20)")
    df = df.Define("leptons_p20", "FCCAnalyses::ReconstructedParticle::merge(muons_p20, electrons_p20)")
# L101 [Executable statement]:     df = df.Define("n_leptons_p20", "FCCAnalyses::ReconstructedParticle::get_n(leptons_p20)")
    df = df.Define("n_leptons_p20", "FCCAnalyses::ReconstructedParticle::get_n(leptons_p20)")
# L102 [Executable statement]:     df = df.Filter("n_leptons_p20 == 1")
    df = df.Filter("n_leptons_p20 == 1")
# L103 [Executable statement]:     hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut1"))
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut1"))
# L104 [Blank separator]: 

# L105 [Executable statement]:     df = df.Define("lepton_p", "FCCAnalyses::ReconstructedParticle::get_p(leptons_p20)[0]")
    df = df.Define("lepton_p", "FCCAnalyses::ReconstructedParticle::get_p(leptons_p20)[0]")
# L106 [Executable statement]:     hists.append(df.Histo1D(("lepton_p", "", *bins_p), "lepton_p"))
    hists.append(df.Histo1D(("lepton_p", "", *bins_p), "lepton_p"))
# L107 [Blank separator]: 

# L108 [Original comment]:     # cut2: isolated prompt lepton
    # cut2: isolated prompt lepton
# L109 [Executable statement]:     df = df.Define("lepton_iso_v", "FCCAnalyses::coneIsolation(0.01, 0.30)(leptons_p20, ReconstructedParticles)")
    df = df.Define("lepton_iso_v", "FCCAnalyses::coneIsolation(0.01, 0.30)(leptons_p20, ReconstructedParticles)")
# L110 [Executable statement]:     df = df.Define("lepton_iso", "lepton_iso_v[0]")
    df = df.Define("lepton_iso", "lepton_iso_v[0]")
# L111 [Executable statement]:     hists.append(df.Histo1D(("lepton_iso", "", *bins_iso), "lepton_iso"))
    hists.append(df.Histo1D(("lepton_iso", "", *bins_iso), "lepton_iso"))
# L112 [Executable statement]:     df = df.Filter("lepton_iso < 0.15")
    df = df.Filter("lepton_iso < 0.15")
# L113 [Executable statement]:     hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut2"))
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut2"))
# L114 [Blank separator]: 

# L115 [Original comment]:     # cut3: veto extra leptons above 5 GeV
    # cut3: veto extra leptons above 5 GeV
# L116 [Executable statement]:     df = df.Define("muons_p5", "FCCAnalyses::ReconstructedParticle::sel_p(5)(muons_all)")
    df = df.Define("muons_p5", "FCCAnalyses::ReconstructedParticle::sel_p(5)(muons_all)")
# L117 [Executable statement]:     df = df.Define("electrons_p5", "FCCAnalyses::ReconstructedParticle::sel_p(5)(electrons_all)")
    df = df.Define("electrons_p5", "FCCAnalyses::ReconstructedParticle::sel_p(5)(electrons_all)")
# L118 [Executable statement]:     df = df.Define("leptons_p5", "FCCAnalyses::ReconstructedParticle::merge(muons_p5, electrons_p5)")
    df = df.Define("leptons_p5", "FCCAnalyses::ReconstructedParticle::merge(muons_p5, electrons_p5)")
# L119 [Executable statement]:     df = df.Define("n_leptons_p5", "FCCAnalyses::ReconstructedParticle::get_n(leptons_p5)")
    df = df.Define("n_leptons_p5", "FCCAnalyses::ReconstructedParticle::get_n(leptons_p5)")
# L120 [Executable statement]:     df = df.Filter("n_leptons_p5 == 1")
    df = df.Filter("n_leptons_p5 == 1")
# L121 [Executable statement]:     hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut3"))
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut3"))
# L122 [Blank separator]: 

# L123 [Original comment]:     # cut4: missing-energy selection
    # cut4: missing-energy selection
# L124 [Executable statement]:     df = df.Define("missingEnergy_rp", "FCCAnalyses::missingEnergy(ecm, ReconstructedParticles)")
    df = df.Define("missingEnergy_rp", "FCCAnalyses::missingEnergy(ecm, ReconstructedParticles)")
# L125 [Executable statement]:     df = df.Define("missingEnergy_e", "missingEnergy_rp[0].energy")
    df = df.Define("missingEnergy_e", "missingEnergy_rp[0].energy")
# L126 [Executable statement]:     df = df.Define("missingEnergy_p", "FCCAnalyses::ReconstructedParticle::get_p(missingEnergy_rp)[0]")
    df = df.Define("missingEnergy_p", "FCCAnalyses::ReconstructedParticle::get_p(missingEnergy_rp)[0]")
# L127 [Executable statement]:     df = df.Define("missingMass", "FCCAnalyses::missingMass(ecm, ReconstructedParticles)")
    df = df.Define("missingMass", "FCCAnalyses::missingMass(ecm, ReconstructedParticles)")
# L128 [Executable statement]:     df = df.Define("cosTheta_miss", "FCCAnalyses::get_cosTheta_miss(missingEnergy_rp)")
    df = df.Define("cosTheta_miss", "FCCAnalyses::get_cosTheta_miss(missingEnergy_rp)")
# L129 [Executable statement]:     hists.append(df.Histo1D(("missingEnergy_e", "", *bins_met), "missingEnergy_e"))
    hists.append(df.Histo1D(("missingEnergy_e", "", *bins_met), "missingEnergy_e"))
# L130 [Executable statement]:     hists.append(df.Histo1D(("missingEnergy_p", "", *bins_met), "missingEnergy_p"))
    hists.append(df.Histo1D(("missingEnergy_p", "", *bins_met), "missingEnergy_p"))
# L131 [Executable statement]:     hists.append(df.Histo1D(("missingMass", "", *bins_m), "missingMass"))
    hists.append(df.Histo1D(("missingMass", "", *bins_m), "missingMass"))
# L132 [Executable statement]:     hists.append(df.Histo1D(("cosTheta_miss", "", *bins_cos), "cosTheta_miss"))
    hists.append(df.Histo1D(("cosTheta_miss", "", *bins_cos), "cosTheta_miss"))
# L133 [Executable statement]:     df = df.Filter("missingEnergy_e > 20")
    df = df.Filter("missingEnergy_e > 20")
# L134 [Executable statement]:     hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut4"))
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut4"))
# L135 [Blank separator]: 

# L136 [Original comment]:     # cut5: remove the selected lepton and cluster the rest into 4 jets
    # cut5: remove the selected lepton and cluster the rest into 4 jets
# L137 [Executable statement]:     df = df.Define("rps_no_leptons", "FCCAnalyses::ReconstructedParticle::remove(ReconstructedParticles, leptons_p5)")
    df = df.Define("rps_no_leptons", "FCCAnalyses::ReconstructedParticle::remove(ReconstructedParticles, leptons_p5)")
# L138 [Executable statement]:     df = df.Alias("rps_sel", "rps_no_leptons")
    df = df.Alias("rps_sel", "rps_no_leptons")
# L139 [Blank separator]: 

# L140 [Executable statement]:     df = df.Define("visibleEnergy", "FCCAnalyses::visibleEnergy(rps_sel)")
    df = df.Define("visibleEnergy", "FCCAnalyses::visibleEnergy(rps_sel)")
# L141 [Executable statement]:     df = df.Define("visibleEnergy_norm", "visibleEnergy / ecm")
    df = df.Define("visibleEnergy_norm", "visibleEnergy / ecm")
# L142 [Executable statement]:     hists.append(df.Histo1D(("visibleEnergy", "", *bins_p), "visibleEnergy"))
    hists.append(df.Histo1D(("visibleEnergy", "", *bins_p), "visibleEnergy"))
# L143 [Blank separator]: 

# L144 [Executable statement]:     df = df.Define("RP_px", "FCCAnalyses::ReconstructedParticle::get_px(rps_sel)")
    df = df.Define("RP_px", "FCCAnalyses::ReconstructedParticle::get_px(rps_sel)")
# L145 [Executable statement]:     df = df.Define("RP_py", "FCCAnalyses::ReconstructedParticle::get_py(rps_sel)")
    df = df.Define("RP_py", "FCCAnalyses::ReconstructedParticle::get_py(rps_sel)")
# L146 [Executable statement]:     df = df.Define("RP_pz", "FCCAnalyses::ReconstructedParticle::get_pz(rps_sel)")
    df = df.Define("RP_pz", "FCCAnalyses::ReconstructedParticle::get_pz(rps_sel)")
# L147 [Executable statement]:     df = df.Define("RP_e", "FCCAnalyses::ReconstructedParticle::get_e(rps_sel)")
    df = df.Define("RP_e", "FCCAnalyses::ReconstructedParticle::get_e(rps_sel)")
# L148 [Blank separator]: 

# L149 [Executable statement]:     df = df.Define("pseudo_jets", "FCCAnalyses::JetClusteringUtils::set_pseudoJets(RP_px, RP_py, RP_pz, RP_e)")
    df = df.Define("pseudo_jets", "FCCAnalyses::JetClusteringUtils::set_pseudoJets(RP_px, RP_py, RP_pz, RP_e)")
# L150 [Executable statement]:     df = df.Define("clustered_jets", "JetClustering::clustering_ee_kt(2, 4, 0, 10)(pseudo_jets)")
    df = df.Define("clustered_jets", "JetClustering::clustering_ee_kt(2, 4, 0, 10)(pseudo_jets)")
# L151 [Executable statement]:     df = df.Define("jets", "FCCAnalyses::JetClusteringUtils::get_pseudoJets(clustered_jets)")
    df = df.Define("jets", "FCCAnalyses::JetClusteringUtils::get_pseudoJets(clustered_jets)")
# L152 [Executable statement]:     df = df.Define("njets", "jets.size()")
    df = df.Define("njets", "jets.size()")
# L153 [Executable statement]:     hists.append(df.Histo1D(("njets", "", *bins_count), "njets"))
    hists.append(df.Histo1D(("njets", "", *bins_count), "njets"))
# L154 [Executable statement]:     df = df.Filter("njets == 4")
    df = df.Filter("njets == 4")
# L155 [Executable statement]:     hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut5"))
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut5"))
# L156 [Blank separator]: 

# L157 [Executable statement]:     df = df.Define("jet0_p", "sqrt(jets[0].px()*jets[0].px() + jets[0].py()*jets[0].py() + jets[0].pz()*jets[0].pz())")
    df = df.Define("jet0_p", "sqrt(jets[0].px()*jets[0].px() + jets[0].py()*jets[0].py() + jets[0].pz()*jets[0].pz())")
# L158 [Executable statement]:     df = df.Define("jet1_p", "sqrt(jets[1].px()*jets[1].px() + jets[1].py()*jets[1].py() + jets[1].pz()*jets[1].pz())")
    df = df.Define("jet1_p", "sqrt(jets[1].px()*jets[1].px() + jets[1].py()*jets[1].py() + jets[1].pz()*jets[1].pz())")
# L159 [Executable statement]:     df = df.Define("jet2_p", "sqrt(jets[2].px()*jets[2].px() + jets[2].py()*jets[2].py() + jets[2].pz()*jets[2].pz())")
    df = df.Define("jet2_p", "sqrt(jets[2].px()*jets[2].px() + jets[2].py()*jets[2].py() + jets[2].pz()*jets[2].pz())")
# L160 [Executable statement]:     df = df.Define("jet3_p", "sqrt(jets[3].px()*jets[3].px() + jets[3].py()*jets[3].py() + jets[3].pz()*jets[3].pz())")
    df = df.Define("jet3_p", "sqrt(jets[3].px()*jets[3].px() + jets[3].py()*jets[3].py() + jets[3].pz()*jets[3].pz())")
# L161 [Executable statement]:     df = df.Define("jet_p_sum", "jet0_p + jet1_p + jet2_p + jet3_p")
    df = df.Define("jet_p_sum", "jet0_p + jet1_p + jet2_p + jet3_p")
# L162 [Executable statement]:     hists.append(df.Histo1D(("jet0_p", "", *bins_p), "jet0_p"))
    hists.append(df.Histo1D(("jet0_p", "", *bins_p), "jet0_p"))
# L163 [Executable statement]:     hists.append(df.Histo1D(("jet1_p", "", *bins_p), "jet1_p"))
    hists.append(df.Histo1D(("jet1_p", "", *bins_p), "jet1_p"))
# L164 [Executable statement]:     hists.append(df.Histo1D(("jet2_p", "", *bins_p), "jet2_p"))
    hists.append(df.Histo1D(("jet2_p", "", *bins_p), "jet2_p"))
# L165 [Executable statement]:     hists.append(df.Histo1D(("jet3_p", "", *bins_p), "jet3_p"))
    hists.append(df.Histo1D(("jet3_p", "", *bins_p), "jet3_p"))
# L166 [Blank separator]: 

# L167 [Original comment]:     # Pair jets with a Z-priority strategy for H -> WW*
    # Pair jets with a Z-priority strategy for H -> WW*
# L168 [Executable statement]:     df = df.Define("jets_e", "FCCAnalyses::JetClusteringUtils::get_e(jets)")
    df = df.Define("jets_e", "FCCAnalyses::JetClusteringUtils::get_e(jets)")
# L169 [Executable statement]:     df = df.Define("jets_px", "FCCAnalyses::JetClusteringUtils::get_px(jets)")
    df = df.Define("jets_px", "FCCAnalyses::JetClusteringUtils::get_px(jets)")
# L170 [Executable statement]:     df = df.Define("jets_py", "FCCAnalyses::JetClusteringUtils::get_py(jets)")
    df = df.Define("jets_py", "FCCAnalyses::JetClusteringUtils::get_py(jets)")
# L171 [Executable statement]:     df = df.Define("jets_pz", "FCCAnalyses::JetClusteringUtils::get_pz(jets)")
    df = df.Define("jets_pz", "FCCAnalyses::JetClusteringUtils::get_pz(jets)")
# L172 [Executable statement]:     df = df.Define("jets_tlv", "FCCAnalyses::makeLorentzVectors(jets_px, jets_py, jets_pz, jets_e)")
    df = df.Define("jets_tlv", "FCCAnalyses::makeLorentzVectors(jets_px, jets_py, jets_pz, jets_e)")
# L173 [Executable statement]:     df = df.Define("paired_ZWstar", "FCCAnalyses::pairing_Zpriority_4jets(jets_tlv, 91.19)")
    df = df.Define("paired_ZWstar", "FCCAnalyses::pairing_Zpriority_4jets(jets_tlv, 91.19)")
# L174 [Executable statement]:     df = df.Define("deltaZ", "FCCAnalyses::pairing_Zpriority_deltaZ(jets_tlv, 91.19)")
    df = df.Define("deltaZ", "FCCAnalyses::pairing_Zpriority_deltaZ(jets_tlv, 91.19)")
# L175 [Blank separator]: 

# L176 [Executable statement]:     df = df.Define("Zcand", "paired_ZWstar[0]")
    df = df.Define("Zcand", "paired_ZWstar[0]")
# L177 [Executable statement]:     df = df.Define("Wstar", "paired_ZWstar[1]")
    df = df.Define("Wstar", "paired_ZWstar[1]")
# L178 [Executable statement]:     df = df.Define("Zcand_m", "Zcand.M()")
    df = df.Define("Zcand_m", "Zcand.M()")
# L179 [Executable statement]:     df = df.Define("Zcand_dm", "abs(Zcand_m - 91.19)")
    df = df.Define("Zcand_dm", "abs(Zcand_m - 91.19)")
# L180 [Executable statement]:     df = df.Define("Wstar_m", "Wstar.M()")
    df = df.Define("Wstar_m", "Wstar.M()")
# L181 [Blank separator]: 

# L182 [Executable statement]:     hists.append(df.Histo1D(("Zcand_m", "", *bins_m), "Zcand_m"))
    hists.append(df.Histo1D(("Zcand_m", "", *bins_m), "Zcand_m"))
# L183 [Executable statement]:     hists.append(df.Histo1D(("Wstar_m", "", *bins_m), "Wstar_m"))
    hists.append(df.Histo1D(("Wstar_m", "", *bins_m), "Wstar_m"))
# L184 [Executable statement]:     hists.append(df.Histo1D(("deltaZ", "", *bins_chi2), "deltaZ"))
    hists.append(df.Histo1D(("deltaZ", "", *bins_chi2), "deltaZ"))
# L185 [Blank separator]: 

# L186 [Original comment]:     # New features from autonomous exploration
    # New features from autonomous exploration
# L187 [Original comment]:     # Jet merging variables (Durham kT distance when going from n+1 to n jets)
    # Jet merging variables (Durham kT distance when going from n+1 to n jets)
# L188 [Executable statement]:     df = df.Define("d_23", "FCCAnalyses::JetClusteringUtils::get_exclusive_dmerge(clustered_jets, 2)")
    df = df.Define("d_23", "FCCAnalyses::JetClusteringUtils::get_exclusive_dmerge(clustered_jets, 2)")
# L189 [Executable statement]:     df = df.Define("d_34", "FCCAnalyses::JetClusteringUtils::get_exclusive_dmerge(clustered_jets, 3)")
    df = df.Define("d_34", "FCCAnalyses::JetClusteringUtils::get_exclusive_dmerge(clustered_jets, 3)")
# L190 [Blank separator]: 

# L191 [Executable statement]:     df = df.Define("totalJetMass", "FCCAnalyses::totalJetMass(jets_tlv)")
    df = df.Define("totalJetMass", "FCCAnalyses::totalJetMass(jets_tlv)")
# L192 [Executable statement]:     df = df.Define("thrust", "FCCAnalyses::computeThrust(rps_no_leptons)")
    df = df.Define("thrust", "FCCAnalyses::computeThrust(rps_no_leptons)")
# L193 [Executable statement]:     df = df.Define("angleLepMiss", "FCCAnalyses::angleLeptonMiss(leptons_p20, missingEnergy_rp)")
    df = df.Define("angleLepMiss", "FCCAnalyses::angleLeptonMiss(leptons_p20, missingEnergy_rp)")
# L194 [Blank separator]: 

# L195 [Executable statement]:     df = df.Define("init_tlv", "TLorentzVector ret; ret.SetPxPyPzE(0,0,0,ecm); return ret;")
    df = df.Define("init_tlv", "TLorentzVector ret; ret.SetPxPyPzE(0,0,0,ecm); return ret;")
# L196 [Executable statement]:     df = df.Define("recoil_tlv", "init_tlv - Zcand")
    df = df.Define("recoil_tlv", "init_tlv - Zcand")
# L197 [Executable statement]:     df = df.Define("recoil_m", "recoil_tlv.M()")
    df = df.Define("recoil_m", "recoil_tlv.M()")
# L198 [Executable statement]:     df = df.Define("recoil_dmH", "abs(recoil_m - 125.0)")
    df = df.Define("recoil_dmH", "abs(recoil_m - 125.0)")
# L199 [Executable statement]:     hists.append(df.Histo1D(("recoil_m", "", *bins_recoil), "recoil_m"))
    hists.append(df.Histo1D(("recoil_m", "", *bins_recoil), "recoil_m"))
# L200 [Blank separator]: 

# L201 [Executable statement]:     df = df.Define(
    df = df.Define(
# L202 [Executable statement]:         "lepton_tlv",
        "lepton_tlv",
# L203 [Executable statement]:         "TLorentzVector v; v.SetPxPyPzE(leptons_p20[0].momentum.x, leptons_p20[0].momentum.y, leptons_p20[0].momentum.z, leptons_p20[0].energy); return v;",
        "TLorentzVector v; v.SetPxPyPzE(leptons_p20[0].momentum.x, leptons_p20[0].momentum.y, leptons_p20[0].momentum.z, leptons_p20[0].energy); return v;",
# L204 [Executable statement]:     )
    )
# L205 [Executable statement]:     df = df.Define(
    df = df.Define(
# L206 [Executable statement]:         "nu_tlv",
        "nu_tlv",
# L207 [Executable statement]:         "TLorentzVector v; v.SetPxPyPzE(missingEnergy_rp[0].momentum.x, missingEnergy_rp[0].momentum.y, missingEnergy_rp[0].momentum.z, missingEnergy_rp[0].energy); return v;",
        "TLorentzVector v; v.SetPxPyPzE(missingEnergy_rp[0].momentum.x, missingEnergy_rp[0].momentum.y, missingEnergy_rp[0].momentum.z, missingEnergy_rp[0].energy); return v;",
# L208 [Executable statement]:     )
    )
# L209 [Executable statement]:     df = df.Define("Wlep", "lepton_tlv + nu_tlv")
    df = df.Define("Wlep", "lepton_tlv + nu_tlv")
# L210 [Executable statement]:     df = df.Define("Wlep_m", "Wlep.M()")
    df = df.Define("Wlep_m", "Wlep.M()")
# L211 [Executable statement]:     hists.append(df.Histo1D(("Wlep_m", "", *bins_m), "Wlep_m"))
    hists.append(df.Histo1D(("Wlep_m", "", *bins_m), "Wlep_m"))
# L212 [Blank separator]: 

# L213 [Executable statement]:     df = df.Define("Hcand", "Wlep + Wstar")
    df = df.Define("Hcand", "Wlep + Wstar")
# L214 [Executable statement]:     df = df.Define("Hcand_m", "Hcand.M()")
    df = df.Define("Hcand_m", "Hcand.M()")
# L215 [Executable statement]:     hists.append(df.Histo1D(("Hcand_m", "", *bins_m), "Hcand_m"))
    hists.append(df.Histo1D(("Hcand_m", "", *bins_m), "Hcand_m"))
# L216 [Blank separator]: 

# L217 [Original comment]:     # cut6: Z mass window
    # cut6: Z mass window
# L218 [Executable statement]:     df = df.Filter("abs(Zcand_m - 91.19) < 15")
    df = df.Filter("abs(Zcand_m - 91.19) < 15")
# L219 [Executable statement]:     hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut6"))
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut6"))
# L220 [Executable statement]:     hists.append(df.Histo1D(("Hcand_m_afterZ", "", *bins_m), "Hcand_m"))
    hists.append(df.Histo1D(("Hcand_m_afterZ", "", *bins_m), "Hcand_m"))
# L221 [Executable statement]:     hists.append(df.Histo1D(("recoil_m_afterZ", "", *bins_recoil), "recoil_m"))
    hists.append(df.Histo1D(("recoil_m_afterZ", "", *bins_recoil), "recoil_m"))
# L222 [Blank separator]: 

# L223 [Original comment]:     # cut7: recoil window
    # cut7: recoil window
# L224 [Executable statement]:     df = df.Filter("abs(recoil_m - 125) < 20")
    df = df.Filter("abs(recoil_m - 125) < 20")
# L225 [Executable statement]:     hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut7"))
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut7"))
# L226 [Executable statement]:     hists.append(df.Histo1D(("Hcand_m_final", "", *bins_m), "Hcand_m"))
    hists.append(df.Histo1D(("Hcand_m_final", "", *bins_m), "Hcand_m"))
# L227 [Blank separator]: 

# L228 [Function return]:     return hists, weightsum, df
    return hists, weightsum, df
# L229 [Blank separator]: 

# L230 [Blank separator]: 

# L231 [Conditional block]: if treemaker:
if treemaker:
# L232 [Class definition]:     class RDFanalysis:
    class RDFanalysis:
# L233 [Executable statement]:         @staticmethod
        @staticmethod
# L234 [Function definition]:         def analysers(df):
        def analysers(df):
# L235 [Executable statement]:             hists, weightsum, df = build_graph_lvqq(df, "")
            hists, weightsum, df = build_graph_lvqq(df, "")
# L236 [Function return]:             return df
            return df
# L237 [Blank separator]: 

# L238 [Executable statement]:         @staticmethod
        @staticmethod
# L239 [Function definition]:         def output():
        def output():
# L240 [Function return]:             return ML_SPECTATORS + ML_FEATURES
            return ML_SPECTATORS + ML_FEATURES
# L241 [Else branch]: else:
else:
# L242 [Function definition]:     def build_graph(df, dataset):
    def build_graph(df, dataset):
# L243 [Executable statement]:         hists, weightsum, df = build_graph_lvqq(df, dataset)
        hists, weightsum, df = build_graph_lvqq(df, dataset)
# L244 [Function return]:         return hists, weightsum
        return hists, weightsum
