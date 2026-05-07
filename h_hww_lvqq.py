import os

import ROOT

from ml_config import (
    BACKGROUND_SAMPLES,
    BACKGROUND_FRACTIONS,
    CUT_SCAN_BRANCHES,
    DEFAULT_HISTMAKER_DIR,
    DEFAULT_SCANMAKER_DIR,
    DEFAULT_TREEMAKER_DIR,
    ML_FEATURES,
    ML_SPECTATORS,
    SAMPLE_PROCESSING_FRACTIONS,
    SIGNAL_FRACTION,
    SIGNAL_SAMPLES,
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
Z_MASS_MIN = 85.0
Z_MASS_MAX = 95.0
ZCAND_P_MIN = 40.0
ZCAND_P_MAX = 60.0
HCAND_M_MIN = 120.0
HCAND_M_MAX = 135.0
RECOIL_M_MIN = 120.0
RECOIL_M_MAX = 135.0


def build_graph_lvqq(df, dataset):
    hists = []

    df = df.Define("ecm", str(ecm))
    df = df.Define("weight", "1.0")
    weightsum = df.Sum("weight")

    for i in range(0, 11):
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
    hists.append(df.Histo1D(("n_extra_iso_leptons_p20_after_cut1", "", *bins_nlep), "n_extra_iso_leptons_p20"))
    df = df.Filter(f"lepton_iso < {LEPTON_ISO_MAX}")
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut2"))

    # cut3: veto events with an additional hard isolated lepton.
    # This keeps signal leptons in the 10-20 GeV range while rejecting
    # multi-lepton backgrounds with an extra isolated lepton above 20 GeV.
    hists.append(df.Histo1D(("n_iso_leptons_p10", "", *bins_nlep), "n_iso_leptons_p10"))
    hists.append(df.Histo1D(("n_iso_leptons_p10_after_cut2", "", *bins_nlep), "n_iso_leptons_p10"))
    hists.append(df.Histo1D(("n_extra_iso_leptons_p20", "", *bins_nlep), "n_extra_iso_leptons_p20"))

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
    df = df.Define("paired_ZWstar", "FCCAnalyses::pairing_Zpriority_4jets(jets_tlv, 91.19)")
    df = df.Define("deltaZ", "FCCAnalyses::pairing_Zpriority_deltaZ(jets_tlv, 91.19)")
    df = df.Define("deltaR_Wstar", "FCCAnalyses::pairing_Zpriority_deltaR_Wstar(jets_tlv, 91.19)")
    df = df.Define("angle_Wstar_jj", "FCCAnalyses::pairing_Zpriority_angle_Wstar(jets_tlv, 91.19)")

    df = df.Define("Zcand", "paired_ZWstar[0]")
    df = df.Define("Wstar", "paired_ZWstar[1]")
    df = df.Define("Zcand_m", "Zcand.M()")
    df = df.Define("Zcand_p", "Zcand.P()")
    df = df.Define("Zcand_dm", "abs(Zcand_m - 91.19)")
    df = df.Define("Wstar_m", "Wstar.M()")

    hists.append(df.Histo1D(("Zcand_m", "", *bins_m), "Zcand_m"))
    hists.append(df.Histo1D(("Zcand_p", "", *bins_p), "Zcand_p"))
    hists.append(df.Histo1D(("Wstar_m", "", *bins_m), "Wstar_m"))
    hists.append(df.Histo1D(("deltaZ", "", *bins_chi2), "deltaZ"))
    hists.append(df.Histo1D(("deltaR_Wstar", "", *bins_delta_r), "deltaR_Wstar"))
    hists.append(df.Histo1D(("angle_Wstar_jj", "", *bins_angle), "angle_Wstar_jj"))

    df = df.Define("totalJetMass", "FCCAnalyses::totalJetMass(jets_tlv)")
    df = df.Define("thrust", "FCCAnalyses::computeThrust(rps_no_leptons)")
    df = df.Define("angleLepMiss", "FCCAnalyses::angleLeptonMiss(selected_lepton, missingEnergy_rp)")

    df = df.Define("init_tlv", "TLorentzVector ret; ret.SetPxPyPzE(0,0,0,ecm); return ret;")
    df = df.Define("recoil_tlv", "init_tlv - Zcand")
    df = df.Define("recoil_m", "recoil_tlv.M()")
    df = df.Define("recoil_dmH", "abs(recoil_m - 125.0)")
    hists.append(df.Histo1D(("recoil_m", "", *bins_recoil), "recoil_m"))

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
    hists.append(df.Histo1D(("Wlep_m", "", *bins_m), "Wlep_m"))

    df = df.Define("Hcand", "Wlep + Wstar")
    df = df.Define("Hcand_m", "Hcand.M()")
    hists.append(df.Histo1D(("Hcand_m", "", *bins_m), "Hcand_m"))

    # cut7: optimized Z-candidate mass window
    df = df.Filter(f"Zcand_m > {Z_MASS_MIN} && Zcand_m < {Z_MASS_MAX}")
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut7"))
    hists.append(df.Histo1D(("Zcand_p_afterZ", "", *bins_p), "Zcand_p"))

    # cut8: production-Z recoil kinematics
    df = df.Filter(f"Zcand_p > {ZCAND_P_MIN} && Zcand_p < {ZCAND_P_MAX}")
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut8"))
    hists.append(df.Histo1D(("Hcand_m_afterZp", "", *bins_m), "Hcand_m"))
    hists.append(df.Histo1D(("recoil_m_afterZp", "", *bins_recoil), "recoil_m"))

    # cut9: reconstructed Higgs-candidate mass window
    df = df.Filter(f"Hcand_m > {HCAND_M_MIN} && Hcand_m < {HCAND_M_MAX}")
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut9"))
    hists.append(df.Histo1D(("Hcand_m_afterH", "", *bins_m), "Hcand_m"))
    hists.append(df.Histo1D(("recoil_m_afterH", "", *bins_recoil), "recoil_m"))

    # cut10: optimized recoil-mass window
    df = df.Filter(f"recoil_m > {RECOIL_M_MIN} && recoil_m < {RECOIL_M_MAX}")
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut10"))
    hists.append(df.Histo1D(("Hcand_m_final", "", *bins_m), "Hcand_m"))

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
    df = df.Define("paired_ZWstar", "FCCAnalyses::pairing_Zpriority_4jets(jets_tlv, 91.19)")
    df = df.Define("deltaR_Wstar", "FCCAnalyses::pairing_Zpriority_deltaR_Wstar(jets_tlv, 91.19)")
    df = df.Define("angle_Wstar_jj", "FCCAnalyses::pairing_Zpriority_angle_Wstar(jets_tlv, 91.19)")
    df = df.Define("Zcand", "paired_ZWstar[0]")
    df = df.Define("Wstar", "paired_ZWstar[1]")
    df = df.Define("Zcand_m", "Zcand.M()")
    df = df.Define("Zcand_p", "Zcand.P()")
    df = df.Define("Zcand_dm", "abs(Zcand_m - 91.19)")
    df = df.Define("Wstar_m", "Wstar.M()")

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
    df = df.Define("Hcand", "Wlep + Wstar")
    df = df.Define("Hcand_m", "Hcand.M()")
    df = df.Define("deltaW_onShell", "abs(Wlep_m - 80.379) - abs(Wstar_m - 80.379)")
    df = df.Define(
        "pass_baseline",
        f"n_leptons_p10_p60 >= 1 && lepton_iso < {LEPTON_ISO_MAX} && n_extra_iso_leptons_p20 == 0 && "
        f"missingEnergy_e > {MISSING_E_MIN} && missingEnergy_e < {MISSING_E_MAX} && "
        f"sqrt_d34 > {SQRT_D34_MIN} && "
        f"min_jet_nconst > {MIN_JET_NCONST_MIN} && "
        f"Zcand_m > {Z_MASS_MIN} && Zcand_m < {Z_MASS_MAX} && "
        f"Zcand_p > {ZCAND_P_MIN} && Zcand_p < {ZCAND_P_MAX} && "
        f"Hcand_m > {HCAND_M_MIN} && Hcand_m < {HCAND_M_MAX} && "
        f"recoil_m > {RECOIL_M_MIN} && recoil_m < {RECOIL_M_MAX}",
    )

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
            return ML_SPECTATORS + ML_FEATURES
else:
    def build_graph(df, dataset):
        hists, weightsum, df = build_graph_lvqq(df, dataset)
        return hists, weightsum
