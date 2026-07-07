import os

import ROOT

from ml_config import (
    BACKGROUND_SAMPLES,
    BACKGROUND_FRACTIONS,
    CUT_SCAN_BRANCHES,
    DEFAULT_HISTMAKER_DIR,
    DEFAULT_SCANMAKER_DIR,
    DEFAULT_TREEMAKER_DIR,
    SAMPLE_PROCESSING_FRACTIONS,
    SIGNAL_FRACTION,
    SIGNAL_SAMPLES,
    TREEMAKER_BRANCHES,
)

ROOT.TH1.SetDefaultSumw2(ROOT.kTRUE)

# ============================================================
# FCC-ee analysis: e+e- -> Z(qq) H(WW -> l nu qq)
# Final state: 4 jets + 1 lepton (e/mu) + MET
# ============================================================

ecm = 240
mode = os.environ.get("LVQQ_MODE", "histmaker").strip().lower()
if mode not in {"histmaker", "treemaker", "scanmaker"}:
    raise RuntimeError(f"Unsupported LVQQ_MODE={mode!r}; use 'histmaker', 'treemaker', or 'scanmaker'")

treemaker = mode == "treemaker"
scanmaker = mode == "scanmaker"


def _get_worker_cpus() -> int:
    raw_value = os.environ.get("LVQQ_CPUS", os.environ.get("SLURM_CPUS_PER_TASK", "32"))
    try:
        cpus = int(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"Invalid CPU setting {raw_value!r}; expected a positive integer") from exc
    if cpus < 1:
        raise RuntimeError(f"Invalid CPU setting {raw_value!r}; expected a positive integer")
    return cpus


processList = {
    # Signal: ZH -> Z(qq) H(WW* -> lvqq)
    **{sample: {"fraction": SAMPLE_PROCESSING_FRACTIONS[sample]} for sample in SIGNAL_SAMPLES},
    # Full background model with mixed processing fractions.
    **{sample: {"fraction": SAMPLE_PROCESSING_FRACTIONS[sample]} for sample in BACKGROUND_SAMPLES},
}

DEFAULT_INPUT_DIR = "/ceph/submit/data/group/fcc/ee/generation/DelphesEvents/winter2023/IDEA"
inputDir = os.environ.get("LVQQ_INPUT_DIR", DEFAULT_INPUT_DIR)
procDict = os.environ.get("LVQQ_PROC_DICT", f"{DEFAULT_INPUT_DIR}/samplesDict.json")
includePaths = ["../functions/functions.h", "../functions/functions_gen.h", "utils.h"]

if scanmaker:
    outputDir = f"{DEFAULT_SCANMAKER_DIR}/"
elif treemaker:
    outputDir = f"{DEFAULT_TREEMAKER_DIR}/"
else:
    outputDir = f"{DEFAULT_HISTMAKER_DIR}/"

nCPUS = _get_worker_cpus()
# Let the FCCAnalyses driver configure ROOT threading from nCPUS/--ncpus.
# Enabling ImplicitMT while using --nevents breaks ROOT::RDataFrame::Range(),
# which is our fastest smoke-test path for debugging the selection.
print(f"[lvqq] active backgrounds: {len(BACKGROUND_SAMPLES)}")
print(f"[lvqq] signal fraction: {SIGNAL_FRACTION:.6g}")
print(
    "[lvqq] fractions:"
    f" WW={BACKGROUND_FRACTIONS['ww']:.6g},"
    f" ZZ={BACKGROUND_FRACTIONS['zz']:.6g},"
    f" qq={BACKGROUND_FRACTIONS['qq']:.6g},"
    f" tautau={BACKGROUND_FRACTIONS['tautau']:.6g},"
    f" ZH(other)={BACKGROUND_FRACTIONS['zh_other']:.6g}"
)

doScale = True
intLumi = 10.8e6 if ecm == 240 else 3e6

bins_count = (50, 0, 50)
bins_nlep = (10, -0.5, 9.5)
bins_p = (200, 0, 200)
bins_m = (400, 0, 400)
bins_met = (200, 0, 200)
bins_chi2 = (200, 0, 50)
bins_recoil = (400, 0, 200)
bins_cos = (100, 0, 1)
bins_iso = (100, 0, 1)
bins_sqrt_d = (480, 0, 120)
bins_nconst = (80, 0, 80)
bins_delta_r = (100, 0, 5)
bins_angle = (100, 0, 3.2)
bins_delta_w = (240, -120, 120)
bins_binary = (2, -0.5, 1.5)

LEPTON_P_MIN = 10.0
LEPTON_P_MAX = 60.0
LEPTON_ISO_MAX = 0.20
EXTRA_ISO_LEPTON_P_MIN = 20.0
MISSING_E_MIN = 10.0
MISSING_E_MAX = 55.0
SQRT_D34_MIN = 14.0
MIN_JET_NCONST_MIN = 8.0
MEAN_JET_NCONST_MIN = 16.0
MEAN_JET_NCONST_MAX = 30.0
Z_MASS = 91.19
W_MASS = 80.379
# v_fable: no hard Z-candidate mass or momentum window. Zcand_m/Zcand_dm and
# Zcand_p are BDT inputs. Full profile-likelihood window scans
# (ml/scan_zcand_windows.py) showed every candidate window on either variable
# degrades the 20-bin shape-fit precision relative to no window.
#
# Optional study knob: LVQQ_ZCAND_P_WINDOW="lo,hi" reinstates a hard Zcand_p
# window (applied as a plain filter; it does NOT get its own cutFlow stage).
_zcand_p_raw = os.environ.get("LVQQ_ZCAND_P_WINDOW", "none").strip().lower()
if _zcand_p_raw in ("none", "off", ""):
    APPLY_ZCAND_P_CUT = False
    ZCAND_P_MIN = ZCAND_P_MAX = None
else:
    APPLY_ZCAND_P_CUT = True
    try:
        ZCAND_P_MIN, ZCAND_P_MAX = (float(x) for x in _zcand_p_raw.split(","))
    except ValueError as exc:
        raise RuntimeError(
            f"Invalid LVQQ_ZCAND_P_WINDOW={_zcand_p_raw!r}; use 'lo,hi' or 'none'"
        ) from exc
    print(f"[lvqq] study override: Zcand_p window {ZCAND_P_MIN}-{ZCAND_P_MAX} GeV")

def build_graph_lvqq(df, dataset):
    hists = []

    df = df.Define("ecm", str(ecm))
    df = df.Define("weight", "1.0")
    weightsum = df.Sum("weight")

    for i in range(0, 10):
        df = df.Define(f"cut{i}", str(i))

    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut0"))

    df = df.Alias("Muon0", "Muon#0.index")
    df = df.Alias("Electron0", "Electron#0.index")

    df = df.Define("muons_all", "FCCAnalyses::ReconstructedParticle::get(Muon0, ReconstructedParticles)")
    df = df.Define("electrons_all", "FCCAnalyses::ReconstructedParticle::get(Electron0, ReconstructedParticles)")

    df = df.Define("leptons_all", "FCCAnalyses::ReconstructedParticle::merge(muons_all, electrons_all)")

    # cut1: require a lepton candidate in the optimized signal-lepton momentum window
    df = df.Define("leptons_p10_p60", f"FCCAnalyses::selectPWindow(leptons_all, {LEPTON_P_MIN}, {LEPTON_P_MAX})")
    df = df.Define("n_leptons_p10_p60", "FCCAnalyses::ReconstructedParticle::get_n(leptons_p10_p60)")
    hists.append(df.Histo1D(("n_leptons_p10_p60", "", *bins_nlep), "n_leptons_p10_p60"))
    df = df.Filter("n_leptons_p10_p60 >= 1")
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut1"))

    # cut2: selected prompt isolated lepton
    df = df.Define("selected_lepton", "FCCAnalyses::leadingByP(leptons_p10_p60)")
    df = df.Define("lepton_p", "FCCAnalyses::ReconstructedParticle::get_p(selected_lepton)[0]")
    hists.append(df.Histo1D(("lepton_p", "", *bins_p), "lepton_p"))
    hists.append(df.Histo1D(("lepton_p_after_cut1", "", *bins_p), "lepton_p"))

    df = df.Define("lepton_iso_v", "FCCAnalyses::coneIsolation(0.01, 0.30)(selected_lepton, ReconstructedParticles)")
    df = df.Define("lepton_iso", "lepton_iso_v[0]")
    df = df.Define("lepton_iso_all_v", "FCCAnalyses::coneIsolation(0.01, 0.30)(leptons_all, ReconstructedParticles)")
    df = df.Define("n_iso_leptons_p10", f"FCCAnalyses::countAbovePAndIso(leptons_all, lepton_iso_all_v, 10.0, {LEPTON_ISO_MAX})")
    df = df.Define(
        "isolated_leptons_p10",
        f"FCCAnalyses::selectAbovePAndIso(leptons_all, lepton_iso_all_v, {LEPTON_P_MIN}, {LEPTON_ISO_MAX})",
    )
    df = df.Define(
        "isolated_leptons_p10_p60",
        f"FCCAnalyses::selectPWindow(isolated_leptons_p10, {LEPTON_P_MIN}, {LEPTON_P_MAX})",
    )
    df = df.Define(
        "n_iso_leptons_p10_p60",
        "FCCAnalyses::ReconstructedParticle::get_n(isolated_leptons_p10_p60)",
    )
    df = df.Define(
        "n_iso_leptons_p20",
        f"FCCAnalyses::countAbovePAndIso(leptons_all, lepton_iso_all_v, {EXTRA_ISO_LEPTON_P_MIN}, {LEPTON_ISO_MAX})",
    )
    df = df.Define(
        "selected_lepton_counts_p20",
        f"(lepton_p > {EXTRA_ISO_LEPTON_P_MIN} && lepton_iso < {LEPTON_ISO_MAX}) ? 1 : 0",
    )
    df = df.Define(
        "n_extra_iso_leptons_p20",
        "std::max(0, n_iso_leptons_p20 - selected_lepton_counts_p20)",
    )
    hists.append(df.Histo1D(("lepton_iso", "", *bins_iso), "lepton_iso"))
    hists.append(df.Histo1D(("lepton_iso_after_cut1", "", *bins_iso), "lepton_iso"))
    hists.append(df.Histo1D(("n_iso_leptons_p10_after_cut1", "", *bins_nlep), "n_iso_leptons_p10"))
    hists.append(df.Histo1D(("n_iso_leptons_p10_p60_after_cut1", "", *bins_nlep), "n_iso_leptons_p10_p60"))
    hists.append(df.Histo1D(("n_extra_iso_leptons_p20_after_cut1", "", *bins_nlep), "n_extra_iso_leptons_p20"))
    df = df.Filter(f"lepton_iso < {LEPTON_ISO_MAX}")
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut2"))

    # cut3: veto events with an additional hard lepton candidate.
    # The internal counter uses the same isolation definition as the selected
    # lepton, but the cut is presented as an extra-lepton veto.
    hists.append(df.Histo1D(("n_iso_leptons_p10", "", *bins_nlep), "n_iso_leptons_p10"))
    hists.append(df.Histo1D(("n_iso_leptons_p10_after_cut2", "", *bins_nlep), "n_iso_leptons_p10"))
    hists.append(df.Histo1D(("n_extra_iso_leptons_p20", "", *bins_nlep), "n_extra_iso_leptons_p20"))
    df = df.Define(
        "extra_iso_lepton_p_after_cut2",
        f"FCCAnalyses::extraLeptonMomenta(leptons_all, lepton_iso_all_v, selected_lepton, {LEPTON_P_MIN}, {LEPTON_ISO_MAX})",
    )
    hists.append(df.Histo1D(("extra_iso_lepton_p_after_cut2", "", *bins_p), "extra_iso_lepton_p_after_cut2"))

    df = df.Define("missingEnergy_rp", "FCCAnalyses::missingEnergy(ecm, ReconstructedParticles)")
    df = df.Define("missingEnergy_e", "missingEnergy_rp[0].energy")
    df = df.Define("missingEnergy_p", "FCCAnalyses::ReconstructedParticle::get_p(missingEnergy_rp)[0]")
    df = df.Define("missingMass", "FCCAnalyses::missingMass(ecm, ReconstructedParticles)")
    df = df.Define("cosTheta_miss", "FCCAnalyses::get_cosTheta_miss(missingEnergy_rp)")
    hists.append(df.Histo1D(("missingEnergy_e_after_cut2", "", *bins_met), "missingEnergy_e"))
    hists.append(df.Histo1D(("missingEnergy_p_after_cut2", "", *bins_met), "missingEnergy_p"))
    hists.append(df.Histo1D(("missingMass_after_cut2", "", *bins_m), "missingMass"))
    hists.append(df.Histo1D(("cosTheta_miss_after_cut2", "", *bins_cos), "cosTheta_miss"))

    df = df.Filter("n_extra_iso_leptons_p20 == 0")
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut3"))

    # cut4: optimized missing-energy window
    hists.append(df.Histo1D(("missingEnergy_e", "", *bins_met), "missingEnergy_e"))
    hists.append(df.Histo1D(("missingEnergy_e_after_cut3", "", *bins_met), "missingEnergy_e"))
    hists.append(df.Histo1D(("missingEnergy_p", "", *bins_met), "missingEnergy_p"))
    hists.append(df.Histo1D(("missingEnergy_p_after_cut3", "", *bins_met), "missingEnergy_p"))
    hists.append(df.Histo1D(("missingMass", "", *bins_m), "missingMass"))
    hists.append(df.Histo1D(("missingMass_after_cut3", "", *bins_m), "missingMass"))
    hists.append(df.Histo1D(("cosTheta_miss", "", *bins_cos), "cosTheta_miss"))
    hists.append(df.Histo1D(("cosTheta_miss_after_cut3", "", *bins_cos), "cosTheta_miss"))
    df = df.Filter(f"missingEnergy_e > {MISSING_E_MIN} && missingEnergy_e < {MISSING_E_MAX}")
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut4"))

    # Cut5 is treated as a reconstruction step: remove the selected lepton,
    # then force the remaining particles into exclusive N=4 Durham jets.
    # The njets==4 filter is a sanity guard before indexing the jet collection.
    df = df.Define("rps_no_leptons", "FCCAnalyses::ReconstructedParticle::remove(ReconstructedParticles, selected_lepton)")
    df = df.Alias("rps_sel", "rps_no_leptons")

    df = df.Define("visibleEnergy", "FCCAnalyses::visibleEnergy(rps_sel)")
    df = df.Define("visibleEnergy_norm", "visibleEnergy / ecm")
    hists.append(df.Histo1D(("visibleEnergy", "", *bins_p), "visibleEnergy"))

    df = df.Define("RP_px", "FCCAnalyses::ReconstructedParticle::get_px(rps_sel)")
    df = df.Define("RP_py", "FCCAnalyses::ReconstructedParticle::get_py(rps_sel)")
    df = df.Define("RP_pz", "FCCAnalyses::ReconstructedParticle::get_pz(rps_sel)")
    df = df.Define("RP_e", "FCCAnalyses::ReconstructedParticle::get_e(rps_sel)")

    df = df.Define("pseudo_jets", "FCCAnalyses::JetClusteringUtils::set_pseudoJets(RP_px, RP_py, RP_pz, RP_e)")
    df = df.Define("clustered_jets", "JetClustering::clustering_ee_kt(2, 4, 0, 10)(pseudo_jets)")
    df = df.Define("jets", "FCCAnalyses::JetClusteringUtils::get_pseudoJets(clustered_jets)")
    df = df.Define("njets", "jets.size()")
    hists.append(df.Histo1D(("njets", "", *bins_count), "njets"))
    df = df.Filter("njets == 4")
    df = df.Define("jetconstituents", "FCCAnalyses::JetClusteringUtils::get_constituents(clustered_jets)")
    df = df.Define("jet_nconst", "FCCAnalyses::jetConstituentCounts(jetconstituents)")
    df = df.Define("jet0_nconst", "jet_nconst[0]")
    df = df.Define("jet1_nconst", "jet_nconst[1]")
    df = df.Define("jet2_nconst", "jet_nconst[2]")
    df = df.Define("jet3_nconst", "jet_nconst[3]")
    df = df.Define("min_jet_nconst", "FCCAnalyses::minJetConstituentCount(jetconstituents)")
    df = df.Define("mean_jet_nconst", "FCCAnalyses::meanJetConstituentCount(jetconstituents)")
    hists.append(df.Histo1D(("jet0_nconst", "", *bins_nconst), "jet0_nconst"))
    hists.append(df.Histo1D(("jet1_nconst", "", *bins_nconst), "jet1_nconst"))
    hists.append(df.Histo1D(("jet2_nconst", "", *bins_nconst), "jet2_nconst"))
    hists.append(df.Histo1D(("jet3_nconst", "", *bins_nconst), "jet3_nconst"))
    hists.append(df.Histo1D(("min_jet_nconst", "", *bins_nconst), "min_jet_nconst"))
    hists.append(df.Histo1D(("mean_jet_nconst", "", *bins_nconst), "mean_jet_nconst"))

    # Four-prong topology quality.  The exclusive N=4 clustering always tries
    # to return four pseudo-jets, so sqrt(d34) tests whether the fourth jet is
    # genuinely resolved rather than a forced soft split.
    df = df.Define("d_23", "FCCAnalyses::JetClusteringUtils::get_exclusive_dmerge(clustered_jets, 2)")
    df = df.Define("d_34", "FCCAnalyses::JetClusteringUtils::get_exclusive_dmerge(clustered_jets, 3)")
    df = df.Define("sqrt_d23", "d_23 > 0 ? sqrt(d_23) : 0.0")
    df = df.Define("sqrt_d34", "d_34 > 0 ? sqrt(d_34) : 0.0")
    hists.append(df.Histo1D(("sqrt_d23", "", *bins_sqrt_d), "sqrt_d23"))
    hists.append(df.Histo1D(("sqrt_d34", "", *bins_sqrt_d), "sqrt_d34"))
    df = df.Filter(f"sqrt_d34 > {SQRT_D34_MIN}")
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut5"))

    # cut6: reject forced/tau-like four-jet reconstructions where at least one
    # pseudo-jet has very low constituent multiplicity.
    hists.append(df.Histo1D(("min_jet_nconst_after_cut5", "", *bins_nconst), "min_jet_nconst"))
    df = df.Filter(f"min_jet_nconst > {MIN_JET_NCONST_MIN}")
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut6"))

    # Keep the mean jet multiplicity as a topology diagnostic only.  After the
    # min-constituent cut it is strongly correlated with Cut6 and is not used
    # as an additional hard cut.
    hists.append(df.Histo1D(("mean_jet_nconst_after_cut6", "", *bins_nconst), "mean_jet_nconst"))

    df = df.Define("jet0_p", "sqrt(jets[0].px()*jets[0].px() + jets[0].py()*jets[0].py() + jets[0].pz()*jets[0].pz())")
    df = df.Define("jet1_p", "sqrt(jets[1].px()*jets[1].px() + jets[1].py()*jets[1].py() + jets[1].pz()*jets[1].pz())")
    df = df.Define("jet2_p", "sqrt(jets[2].px()*jets[2].px() + jets[2].py()*jets[2].py() + jets[2].pz()*jets[2].pz())")
    df = df.Define("jet3_p", "sqrt(jets[3].px()*jets[3].px() + jets[3].py()*jets[3].py() + jets[3].pz()*jets[3].pz())")
    df = df.Define("jet_p_sum", "jet0_p + jet1_p + jet2_p + jet3_p")
    df = df.Define("min_jet_p", "std::min(std::min(jet0_p, jet1_p), std::min(jet2_p, jet3_p))")
    hists.append(df.Histo1D(("jet0_p", "", *bins_p), "jet0_p"))
    hists.append(df.Histo1D(("jet1_p", "", *bins_p), "jet1_p"))
    hists.append(df.Histo1D(("jet2_p", "", *bins_p), "jet2_p"))
    hists.append(df.Histo1D(("jet3_p", "", *bins_p), "jet3_p"))
    hists.append(df.Histo1D(("min_jet_p", "", *bins_p), "min_jet_p"))

    # Pair jets with a Z-priority strategy for H -> WW*
    df = df.Define("jets_e", "FCCAnalyses::JetClusteringUtils::get_e(jets)")
    df = df.Define("jets_px", "FCCAnalyses::JetClusteringUtils::get_px(jets)")
    df = df.Define("jets_py", "FCCAnalyses::JetClusteringUtils::get_py(jets)")
    df = df.Define("jets_pz", "FCCAnalyses::JetClusteringUtils::get_pz(jets)")
    df = df.Define("jets_tlv", "FCCAnalyses::makeLorentzVectors(jets_px, jets_py, jets_pz, jets_e)")
    df = df.Define("paired_ZWstar", f"FCCAnalyses::pairing_Zpriority_4jets(jets_tlv, {Z_MASS})")
    df = df.Define("paired_ZWchi2", f"FCCAnalyses::pairing_ZWchi2_4jets(jets_tlv, {Z_MASS}, {W_MASS}, 10.0, 15.0)")
    df = df.Define("deltaZ", f"FCCAnalyses::pairing_Zpriority_deltaZ(jets_tlv, {Z_MASS})")
    df = df.Define("chi2_ZWpair", f"FCCAnalyses::pairing_ZWchi2_score(jets_tlv, {Z_MASS}, {W_MASS}, 10.0, 15.0)")
    df = df.Define("deltaR_Wstar", f"FCCAnalyses::pairing_Zpriority_deltaR_Wstar(jets_tlv, {Z_MASS})")
    df = df.Define("angle_Wstar_jj", f"FCCAnalyses::pairing_Zpriority_angle_Wstar(jets_tlv, {Z_MASS})")

    df = df.Define("Zcand", "paired_ZWstar[0]")
    df = df.Define("Wstar", "paired_ZWstar[1]")
    df = df.Define("Whad", "Wstar")
    df = df.Define("Zcand_m", "Zcand.M()")
    df = df.Define("Zcand_p", "Zcand.P()")
    df = df.Define("Zcand_dm", f"abs(Zcand_m - {Z_MASS})")
    df = df.Define("Wstar_m", "Wstar.M()")
    df = df.Define("Whad_m", "Whad.M()")
    df = df.Define("Whad_p", "Whad.P()")

    df = df.Define("Zcand_ZWchi2", "paired_ZWchi2[0]")
    df = df.Define("Whad_ZWchi2", "paired_ZWchi2[1]")
    df = df.Define("Zcand_m_ZWchi2", "Zcand_ZWchi2.M()")
    df = df.Define("Zcand_p_ZWchi2", "Zcand_ZWchi2.P()")
    df = df.Define("Zcand_dm_ZWchi2", f"abs(Zcand_m_ZWchi2 - {Z_MASS})")
    df = df.Define("Whad_m_ZWchi2", "Whad_ZWchi2.M()")
    df = df.Define("Whad_p_ZWchi2", "Whad_ZWchi2.P()")
    df = df.Define("delta_pairing_Zcand_m", "abs(Zcand_m - Zcand_m_ZWchi2)")
    df = df.Define("delta_pairing_Whad_m", "abs(Whad_m - Whad_m_ZWchi2)")

    hists.append(df.Histo1D(("Zcand_m", "", *bins_m), "Zcand_m"))
    hists.append(df.Histo1D(("Zcand_p", "", *bins_p), "Zcand_p"))
    hists.append(df.Histo1D(("Wstar_m", "", *bins_m), "Wstar_m"))
    hists.append(df.Histo1D(("Whad_m", "", *bins_m), "Whad_m"))
    hists.append(df.Histo1D(("Whad_p", "", *bins_p), "Whad_p"))
    hists.append(df.Histo1D(("deltaZ", "", *bins_chi2), "deltaZ"))
    hists.append(df.Histo1D(("chi2_ZWpair", "", *bins_chi2), "chi2_ZWpair"))
    hists.append(df.Histo1D(("Zcand_m_ZWchi2", "", *bins_m), "Zcand_m_ZWchi2"))
    hists.append(df.Histo1D(("Zcand_p_ZWchi2", "", *bins_p), "Zcand_p_ZWchi2"))
    hists.append(df.Histo1D(("Whad_m_ZWchi2", "", *bins_m), "Whad_m_ZWchi2"))
    hists.append(df.Histo1D(("Whad_p_ZWchi2", "", *bins_p), "Whad_p_ZWchi2"))
    hists.append(df.Histo1D(("delta_pairing_Zcand_m", "", *bins_m), "delta_pairing_Zcand_m"))
    hists.append(df.Histo1D(("delta_pairing_Whad_m", "", *bins_m), "delta_pairing_Whad_m"))
    hists.append(df.Histo1D(("deltaR_Wstar", "", *bins_delta_r), "deltaR_Wstar"))
    hists.append(df.Histo1D(("angle_Wstar_jj", "", *bins_angle), "angle_Wstar_jj"))

    df = df.Define("totalJetMass", "FCCAnalyses::totalJetMass(jets_tlv)")
    df = df.Define("thrust", "FCCAnalyses::computeThrust(rps_no_leptons)")
    df = df.Define("angleLepMiss", "FCCAnalyses::angleLeptonMiss(selected_lepton, missingEnergy_rp)")

    df = df.Define("init_tlv", "TLorentzVector ret; ret.SetPxPyPzE(0,0,0,ecm); return ret;")
    df = df.Define("recoil_tlv", "init_tlv - Zcand")
    df = df.Define("recoil_m", "recoil_tlv.M()")
    df = df.Define("recoil_dmH", "abs(recoil_m - 125.0)")
    df = df.Define("recoil_tlv_ZWchi2", "init_tlv - Zcand_ZWchi2")
    df = df.Define("recoil_m_ZWchi2", "recoil_tlv_ZWchi2.M()")
    df = df.Define("recoil_dmH_ZWchi2", "abs(recoil_m_ZWchi2 - 125.0)")
    hists.append(df.Histo1D(("recoil_m", "", *bins_recoil), "recoil_m"))
    hists.append(df.Histo1D(("recoil_m_ZWchi2", "", *bins_recoil), "recoil_m_ZWchi2"))

    df = df.Define(
        "lepton_tlv",
        "TLorentzVector v; v.SetPxPyPzE(selected_lepton[0].momentum.x, selected_lepton[0].momentum.y, selected_lepton[0].momentum.z, selected_lepton[0].energy); return v;",
    )
    df = df.Define(
        "nu_tlv",
        "TLorentzVector v; v.SetPxPyPzE(missingEnergy_rp[0].momentum.x, missingEnergy_rp[0].momentum.y, missingEnergy_rp[0].momentum.z, missingEnergy_rp[0].energy); return v;",
    )
    df = df.Define("Wlep", "lepton_tlv + nu_tlv")
    df = df.Define("Wlep_m", "Wlep.M()")
    df = df.Define("Wlep_p", "Wlep.P()")
    df = df.Define("abs_Wlep_mW", f"abs(Wlep_m - {W_MASS})")
    df = df.Define("abs_Whad_mW", f"abs(Whad_m - {W_MASS})")
    df = df.Define("abs_Whad_ZWchi2_mW", f"abs(Whad_m_ZWchi2 - {W_MASS})")
    df = df.Define("deltaW_onShell", "abs_Wlep_mW - abs_Whad_mW")
    df = df.Define("deltaW_onShell_ZWchi2", "abs_Wlep_mW - abs_Whad_ZWchi2_mW")
    df = df.Define("lepW_offshell_like", "deltaW_onShell > 0 ? 1.0 : 0.0")
    df = df.Define("lepW_onshell_like", "deltaW_onShell < 0 ? 1.0 : 0.0")
    df = df.Define("hadW_onshell_like", "deltaW_onShell > 0 ? 1.0 : 0.0")
    df = df.Define("w_topology_category", "deltaW_onShell < 0 ? 0.0 : 1.0")
    df = df.Define("mW_min", "std::min(Wlep_m, Whad_m)")
    df = df.Define("mW_max", "std::max(Wlep_m, Whad_m)")
    hists.append(df.Histo1D(("Wlep_m", "", *bins_m), "Wlep_m"))
    hists.append(df.Histo1D(("Wlep_p", "", *bins_p), "Wlep_p"))
    hists.append(df.Histo1D(("abs_Wlep_mW", "", *bins_m), "abs_Wlep_mW"))
    hists.append(df.Histo1D(("abs_Whad_mW", "", *bins_m), "abs_Whad_mW"))
    hists.append(df.Histo1D(("deltaW_onShell", "", *bins_delta_w), "deltaW_onShell"))
    hists.append(df.Histo1D(("deltaW_onShell_ZWchi2", "", *bins_delta_w), "deltaW_onShell_ZWchi2"))
    hists.append(df.Histo1D(("lepW_offshell_like", "", *bins_binary), "lepW_offshell_like"))
    hists.append(df.Histo1D(("lepW_onshell_like", "", *bins_binary), "lepW_onshell_like"))
    hists.append(df.Histo1D(("hadW_onshell_like", "", *bins_binary), "hadW_onshell_like"))
    hists.append(df.Histo1D(("w_topology_category", "", *bins_binary), "w_topology_category"))
    hists.append(df.Histo1D(("mW_min", "", *bins_m), "mW_min"))
    hists.append(df.Histo1D(("mW_max", "", *bins_m), "mW_max"))

    df = df.Define("Hcand", "Wlep + Wstar")
    df = df.Define("Hcand_m", "Hcand.M()")
    df = df.Define("Hcand_ZWchi2", "Wlep + Whad_ZWchi2")
    df = df.Define("Hcand_m_ZWchi2", "Hcand_ZWchi2.M()")
    hists.append(df.Histo1D(("Hcand_m", "", *bins_m), "Hcand_m"))
    hists.append(df.Histo1D(("Hcand_m_ZWchi2", "", *bins_m), "Hcand_m_ZWchi2"))

    # The baseline selection ends at cut6. Zcand_p/Zcand_m are BDT inputs;
    # the optional study window below is a plain filter without a cutFlow stage.
    if APPLY_ZCAND_P_CUT:
        df = df.Filter(f"Zcand_p > {ZCAND_P_MIN} && Zcand_p < {ZCAND_P_MAX}")

    return hists, weightsum, df


def build_graph_scanmaker(df, dataset):
    df = df.Define("ecm", str(ecm))
    df = df.Define("weight", "1.0")

    df = df.Alias("Muon0", "Muon#0.index")
    df = df.Alias("Electron0", "Electron#0.index")

    df = df.Define("muons_all", "FCCAnalyses::ReconstructedParticle::get(Muon0, ReconstructedParticles)")
    df = df.Define("electrons_all", "FCCAnalyses::ReconstructedParticle::get(Electron0, ReconstructedParticles)")
    df = df.Define("leptons_all", "FCCAnalyses::ReconstructedParticle::merge(muons_all, electrons_all)")

    for threshold in (*range(2, 21), 25, 30):
        df = df.Define(f"n_leptons_p{threshold}", f"FCCAnalyses::countAboveP(leptons_all, {threshold}.0)")
    df = df.Define("leptons_p10_p60", f"FCCAnalyses::selectPWindow(leptons_all, {LEPTON_P_MIN}, {LEPTON_P_MAX})")
    df = df.Define("n_leptons_p10_p60", "FCCAnalyses::ReconstructedParticle::get_n(leptons_p10_p60)")

    df = df.Define("lepton_iso_all_v", "FCCAnalyses::coneIsolation(0.01, 0.30)(leptons_all, ReconstructedParticles)")
    for threshold in (*range(2, 21), 25, 30):
        df = df.Define(
            f"n_iso_leptons_p{threshold}",
            f"FCCAnalyses::countAbovePAndIso(leptons_all, lepton_iso_all_v, {threshold}.0, {LEPTON_ISO_MAX})",
        )
    df = df.Define(
        "isolated_leptons_p10",
        f"FCCAnalyses::selectAbovePAndIso(leptons_all, lepton_iso_all_v, 10.0, {LEPTON_ISO_MAX})",
    )
    df = df.Define("isolated_leptons_p10_p60", "FCCAnalyses::selectPWindow(isolated_leptons_p10, 10.0, 60.0)")
    df = df.Define("n_iso_leptons_p10_p60", "FCCAnalyses::ReconstructedParticle::get_n(isolated_leptons_p10_p60)")

    # Keep the loose scan ntuple aligned with the nominal Cut1 lepton definition.
    # This makes the lepton removed before jet clustering identical in histmaker
    # and scanmaker, which is essential for Cut5 topology scans.
    df = df.Filter("n_leptons_p10_p60 >= 1")
    df = df.Define("selected_lepton", "FCCAnalyses::leadingByP(leptons_p10_p60)")
    df = df.Define("lepton_p", "FCCAnalyses::ReconstructedParticle::get_p(selected_lepton)[0]")
    df = df.Define("lepton_iso_v", "FCCAnalyses::coneIsolation(0.01, 0.30)(selected_lepton, ReconstructedParticles)")
    df = df.Define("lepton_iso", "lepton_iso_v[0]")
    df = df.Define(
        "selected_lepton_counts_p20",
        f"(lepton_p > {EXTRA_ISO_LEPTON_P_MIN} && lepton_iso < {LEPTON_ISO_MAX}) ? 1 : 0",
    )
    df = df.Define(
        "n_extra_iso_leptons_p20",
        "std::max(0, n_iso_leptons_p20 - selected_lepton_counts_p20)",
    )
    df = df.Define(
        "extra_iso_lepton_p_after_cut2",
        f"FCCAnalyses::extraLeptonMomenta(leptons_all, lepton_iso_all_v, selected_lepton, {LEPTON_P_MIN}, {LEPTON_ISO_MAX})",
    )

    df = df.Define("missingEnergy_rp", "FCCAnalyses::missingEnergy(ecm, ReconstructedParticles)")
    df = df.Define("missingEnergy_e", "missingEnergy_rp[0].energy")
    df = df.Define("missingEnergy_p", "FCCAnalyses::ReconstructedParticle::get_p(missingEnergy_rp)[0]")
    df = df.Define("missingMass", "FCCAnalyses::missingMass(ecm, ReconstructedParticles)")
    df = df.Define("cosTheta_miss", "FCCAnalyses::get_cosTheta_miss(missingEnergy_rp)")

    df = df.Define("rps_no_leptons", "FCCAnalyses::ReconstructedParticle::remove(ReconstructedParticles, selected_lepton)")
    df = df.Define("visibleEnergy", "FCCAnalyses::visibleEnergy(rps_no_leptons)")
    df = df.Define("visibleEnergy_norm", "visibleEnergy / ecm")

    df = df.Define("RP_px", "FCCAnalyses::ReconstructedParticle::get_px(rps_no_leptons)")
    df = df.Define("RP_py", "FCCAnalyses::ReconstructedParticle::get_py(rps_no_leptons)")
    df = df.Define("RP_pz", "FCCAnalyses::ReconstructedParticle::get_pz(rps_no_leptons)")
    df = df.Define("RP_e", "FCCAnalyses::ReconstructedParticle::get_e(rps_no_leptons)")

    df = df.Define("pseudo_jets", "FCCAnalyses::JetClusteringUtils::set_pseudoJets(RP_px, RP_py, RP_pz, RP_e)")
    df = df.Define("clustered_jets", "JetClustering::clustering_ee_kt(2, 4, 0, 10)(pseudo_jets)")
    df = df.Define("jets", "FCCAnalyses::JetClusteringUtils::get_pseudoJets(clustered_jets)")
    df = df.Define("njets", "jets.size()")
    df = df.Filter("njets == 4")
    df = df.Define("jetconstituents", "FCCAnalyses::JetClusteringUtils::get_constituents(clustered_jets)")
    df = df.Define("jet_nconst", "FCCAnalyses::jetConstituentCounts(jetconstituents)")
    df = df.Define("jet0_nconst", "jet_nconst[0]")
    df = df.Define("jet1_nconst", "jet_nconst[1]")
    df = df.Define("jet2_nconst", "jet_nconst[2]")
    df = df.Define("jet3_nconst", "jet_nconst[3]")
    df = df.Define("min_jet_nconst", "FCCAnalyses::minJetConstituentCount(jetconstituents)")
    df = df.Define("mean_jet_nconst", "FCCAnalyses::meanJetConstituentCount(jetconstituents)")

    df = df.Define("jet0_p", "sqrt(jets[0].px()*jets[0].px() + jets[0].py()*jets[0].py() + jets[0].pz()*jets[0].pz())")
    df = df.Define("jet1_p", "sqrt(jets[1].px()*jets[1].px() + jets[1].py()*jets[1].py() + jets[1].pz()*jets[1].pz())")
    df = df.Define("jet2_p", "sqrt(jets[2].px()*jets[2].px() + jets[2].py()*jets[2].py() + jets[2].pz()*jets[2].pz())")
    df = df.Define("jet3_p", "sqrt(jets[3].px()*jets[3].px() + jets[3].py()*jets[3].py() + jets[3].pz()*jets[3].pz())")
    df = df.Define("min_jet_p", "std::min(std::min(jet0_p, jet1_p), std::min(jet2_p, jet3_p))")

    df = df.Define("jets_e", "FCCAnalyses::JetClusteringUtils::get_e(jets)")
    df = df.Define("jets_px", "FCCAnalyses::JetClusteringUtils::get_px(jets)")
    df = df.Define("jets_py", "FCCAnalyses::JetClusteringUtils::get_py(jets)")
    df = df.Define("jets_pz", "FCCAnalyses::JetClusteringUtils::get_pz(jets)")
    df = df.Define("jets_tlv", "FCCAnalyses::makeLorentzVectors(jets_px, jets_py, jets_pz, jets_e)")
    df = df.Define("paired_ZWstar", f"FCCAnalyses::pairing_Zpriority_4jets(jets_tlv, {Z_MASS})")
    df = df.Define("paired_ZWchi2", f"FCCAnalyses::pairing_ZWchi2_4jets(jets_tlv, {Z_MASS}, {W_MASS}, 10.0, 15.0)")
    df = df.Define("deltaR_Wstar", f"FCCAnalyses::pairing_Zpriority_deltaR_Wstar(jets_tlv, {Z_MASS})")
    df = df.Define("angle_Wstar_jj", f"FCCAnalyses::pairing_Zpriority_angle_Wstar(jets_tlv, {Z_MASS})")
    df = df.Define("chi2_ZWpair", f"FCCAnalyses::pairing_ZWchi2_score(jets_tlv, {Z_MASS}, {W_MASS}, 10.0, 15.0)")
    df = df.Define("Zcand", "paired_ZWstar[0]")
    df = df.Define("Wstar", "paired_ZWstar[1]")
    df = df.Define("Whad", "Wstar")
    df = df.Define("Zcand_m", "Zcand.M()")
    df = df.Define("Zcand_p", "Zcand.P()")
    df = df.Define("Zcand_dm", f"abs(Zcand_m - {Z_MASS})")
    df = df.Define("Wstar_m", "Wstar.M()")
    df = df.Define("Whad_m", "Whad.M()")
    df = df.Define("Whad_p", "Whad.P()")

    df = df.Define("Zcand_ZWchi2", "paired_ZWchi2[0]")
    df = df.Define("Whad_ZWchi2", "paired_ZWchi2[1]")
    df = df.Define("Zcand_m_ZWchi2", "Zcand_ZWchi2.M()")
    df = df.Define("Zcand_p_ZWchi2", "Zcand_ZWchi2.P()")
    df = df.Define("Zcand_dm_ZWchi2", f"abs(Zcand_m_ZWchi2 - {Z_MASS})")
    df = df.Define("Whad_m_ZWchi2", "Whad_ZWchi2.M()")
    df = df.Define("Whad_p_ZWchi2", "Whad_ZWchi2.P()")
    df = df.Define("delta_pairing_Zcand_m", "abs(Zcand_m - Zcand_m_ZWchi2)")
    df = df.Define("delta_pairing_Whad_m", "abs(Whad_m - Whad_m_ZWchi2)")

    df = df.Define("d_23", "FCCAnalyses::JetClusteringUtils::get_exclusive_dmerge(clustered_jets, 2)")
    df = df.Define("d_34", "FCCAnalyses::JetClusteringUtils::get_exclusive_dmerge(clustered_jets, 3)")
    df = df.Define("sqrt_d23", "d_23 > 0 ? sqrt(d_23) : 0.0")
    df = df.Define("sqrt_d34", "d_34 > 0 ? sqrt(d_34) : 0.0")
    df = df.Define("totalJetMass", "FCCAnalyses::totalJetMass(jets_tlv)")
    df = df.Define("thrust", "FCCAnalyses::computeThrust(rps_no_leptons)")
    df = df.Define("angleLepMiss", "FCCAnalyses::angleLeptonMiss(selected_lepton, missingEnergy_rp)")

    df = df.Define("init_tlv", "TLorentzVector ret; ret.SetPxPyPzE(0,0,0,ecm); return ret;")
    df = df.Define("recoil_tlv", "init_tlv - Zcand")
    df = df.Define("recoil_m", "recoil_tlv.M()")
    df = df.Define("recoil_dmH", "abs(recoil_m - 125.0)")
    df = df.Define("recoil_tlv_ZWchi2", "init_tlv - Zcand_ZWchi2")
    df = df.Define("recoil_m_ZWchi2", "recoil_tlv_ZWchi2.M()")
    df = df.Define("recoil_dmH_ZWchi2", "abs(recoil_m_ZWchi2 - 125.0)")
    df = df.Define(
        "lepton_tlv",
        "TLorentzVector v; v.SetPxPyPzE(selected_lepton[0].momentum.x, selected_lepton[0].momentum.y, selected_lepton[0].momentum.z, selected_lepton[0].energy); return v;",
    )
    df = df.Define(
        "nu_tlv",
        "TLorentzVector v; v.SetPxPyPzE(missingEnergy_rp[0].momentum.x, missingEnergy_rp[0].momentum.y, missingEnergy_rp[0].momentum.z, missingEnergy_rp[0].energy); return v;",
    )
    df = df.Define("Wlep", "lepton_tlv + nu_tlv")
    df = df.Define("Wlep_m", "Wlep.M()")
    df = df.Define("Wlep_p", "Wlep.P()")
    df = df.Define("abs_Wlep_mW", f"abs(Wlep_m - {W_MASS})")
    df = df.Define("abs_Whad_mW", f"abs(Whad_m - {W_MASS})")
    df = df.Define("abs_Whad_ZWchi2_mW", f"abs(Whad_m_ZWchi2 - {W_MASS})")
    df = df.Define("Hcand", "Wlep + Wstar")
    df = df.Define("Hcand_m", "Hcand.M()")
    df = df.Define("Hcand_ZWchi2", "Wlep + Whad_ZWchi2")
    df = df.Define("Hcand_m_ZWchi2", "Hcand_ZWchi2.M()")
    df = df.Define("deltaW_onShell", "abs_Wlep_mW - abs_Whad_mW")
    df = df.Define("deltaW_onShell_ZWchi2", "abs_Wlep_mW - abs_Whad_ZWchi2_mW")
    df = df.Define("lepW_offshell_like", "deltaW_onShell > 0 ? 1.0 : 0.0")
    df = df.Define("lepW_onshell_like", "deltaW_onShell < 0 ? 1.0 : 0.0")
    df = df.Define("hadW_onshell_like", "deltaW_onShell > 0 ? 1.0 : 0.0")
    df = df.Define("w_topology_category", "deltaW_onShell < 0 ? 0.0 : 1.0")
    df = df.Define("mW_min", "std::min(Wlep_m, Whad_m)")
    df = df.Define("mW_max", "std::max(Wlep_m, Whad_m)")
    baseline_expr = (
        f"n_leptons_p10_p60 >= 1 && lepton_iso < {LEPTON_ISO_MAX} && n_extra_iso_leptons_p20 == 0 && "
        f"missingEnergy_e > {MISSING_E_MIN} && missingEnergy_e < {MISSING_E_MAX} && "
        f"sqrt_d34 > {SQRT_D34_MIN} && "
        f"min_jet_nconst > {MIN_JET_NCONST_MIN}"
    )
    if APPLY_ZCAND_P_CUT:
        baseline_expr += f" && Zcand_p > {ZCAND_P_MIN} && Zcand_p < {ZCAND_P_MAX}"
    df = df.Define("pass_baseline", baseline_expr)

    return df


if scanmaker:
    class RDFanalysis:
        @staticmethod
        def analysers(df):
            return build_graph_scanmaker(df, "")

        @staticmethod
        def output():
            return CUT_SCAN_BRANCHES

elif treemaker:
    class RDFanalysis:
        @staticmethod
        def analysers(df):
            hists, weightsum, df = build_graph_lvqq(df, "")
            return df

        @staticmethod
        def output():
            return TREEMAKER_BRANCHES
else:
    def build_graph(df, dataset):
        hists, weightsum, df = build_graph_lvqq(df, dataset)
        return hists, weightsum
