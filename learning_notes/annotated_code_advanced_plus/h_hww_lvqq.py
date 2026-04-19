# Physics reconstruction graph for e+e- -> Z(qq)H(WW*→ℓνqq): one isolated lepton + four jets + recoil consistency.
#
# This is an advanced educational copy of the reconstruction chain.
# The executable logic is unchanged, only explanatory content was enriched.
#
# Design target:
# - keep exactly the lvqq topology in each event that reaches training,
# - make each selection reproducible and auditable in cutFlow,
# - provide interpretable observables for both ML scoring and physics diagnostics.

# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import os

# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import ROOT

# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
from ml_config import (
# [Context] Supporting line for the active lvqq analysis stage.
    BACKGROUND_SAMPLES,
# [Context] Supporting line for the active lvqq analysis stage.
    BACKGROUND_FRACTIONS,
# [Context] Supporting line for the active lvqq analysis stage.
    ML_FEATURES,
# [Context] Supporting line for the active lvqq analysis stage.
    ML_SPECTATORS,
# [Context] Supporting line for the active lvqq analysis stage.
    SAMPLE_PROCESSING_FRACTIONS,
# [Context] Supporting line for the active lvqq analysis stage.
    SIGNAL_SAMPLES,
# [Context] Supporting line for the active lvqq analysis stage.
)

# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
ROOT.TH1.SetDefaultSumw2(ROOT.kTRUE)

# ============================================================
# FCC-ee analysis: e+e- -> Z(qq) H(WW -> l nu qq)
# Final state: 4 jets + 1 lepton (e/mu) + MET
# ============================================================

# [Context] Supporting line for the active lvqq analysis stage.
ecm = 240
# [Context] Supporting line for the active lvqq analysis stage.
mode = os.environ.get("LVQQ_MODE", "histmaker").strip().lower()
# [Context] Supporting line for the active lvqq analysis stage.
if mode not in {"histmaker", "treemaker"}:
# [Context] Supporting line for the active lvqq analysis stage.
    raise RuntimeError(f"Unsupported LVQQ_MODE={mode!r}; use 'histmaker' or 'treemaker'")

# [Context] Supporting line for the active lvqq analysis stage.
treemaker = mode == "treemaker"


# [Workflow] Read CPU budget from scheduler/env and fail fast if misconfigured.
def _get_worker_cpus() -> int:
# [Context] Supporting line for the active lvqq analysis stage.
    raw_value = os.environ.get("LVQQ_CPUS", os.environ.get("SLURM_CPUS_PER_TASK", "32"))
# [Context] Supporting line for the active lvqq analysis stage.
    try:
# [Context] Supporting line for the active lvqq analysis stage.
        cpus = int(raw_value)
# [Context] Supporting line for the active lvqq analysis stage.
    except ValueError as exc:
# [Context] Supporting line for the active lvqq analysis stage.
        raise RuntimeError(f"Invalid CPU setting {raw_value!r}; expected a positive integer") from exc
# [Context] Supporting line for the active lvqq analysis stage.
    if cpus < 1:
# [Context] Supporting line for the active lvqq analysis stage.
        raise RuntimeError(f"Invalid CPU setting {raw_value!r}; expected a positive integer")
# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return cpus

# [Context] Supporting line for the active lvqq analysis stage.
processList = {
    # Signal: ZH -> Z(qq) H(WW* -> lvqq)
# [Context] Supporting line for the active lvqq analysis stage.
    **{sample: {"fraction": SAMPLE_PROCESSING_FRACTIONS[sample]} for sample in SIGNAL_SAMPLES},
    # Full background model with mixed processing fractions.
# [Context] Supporting line for the active lvqq analysis stage.
    **{sample: {"fraction": SAMPLE_PROCESSING_FRACTIONS[sample]} for sample in BACKGROUND_SAMPLES},
# [Context] Supporting line for the active lvqq analysis stage.
}

# [Context] Supporting line for the active lvqq analysis stage.
inputDir = "/ceph/submit/data/group/fcc/ee/generation/DelphesEvents/winter2023/IDEA/"
# [Context] Supporting line for the active lvqq analysis stage.
procDict = "/ceph/submit/data/group/fcc/ee/generation/DelphesEvents/winter2023/IDEA/samplesDict.json"
# [Context] Supporting line for the active lvqq analysis stage.
includePaths = ["../functions/functions.h", "../functions/functions_gen.h", "utils.h"]

# [Context] Supporting line for the active lvqq analysis stage.
if treemaker:
# [Context] Supporting line for the active lvqq analysis stage.
    outputDir = f"output/h_hww_lvqq/treemaker/ecm{ecm}/"
# [Context] Supporting line for the active lvqq analysis stage.
else:
# [Context] Supporting line for the active lvqq analysis stage.
    outputDir = f"output/h_hww_lvqq/histmaker/ecm{ecm}/"

# [Context] Supporting line for the active lvqq analysis stage.
nCPUS = _get_worker_cpus()
# [Physics] ROOT-style plotting/histogram objects used in detector-level diagnostics.
ROOT.EnableImplicitMT(nCPUS)
# [Context] Supporting line for the active lvqq analysis stage.
print(f"[lvqq] active backgrounds: {len(BACKGROUND_SAMPLES)}")
# [Context] Supporting line for the active lvqq analysis stage.
print(
# [Context] Supporting line for the active lvqq analysis stage.
    "[lvqq] fractions:"
# [Context] Supporting line for the active lvqq analysis stage.
    f" WW={BACKGROUND_FRACTIONS['ww']:.6g},"
# [Context] Supporting line for the active lvqq analysis stage.
    f" ZZ={BACKGROUND_FRACTIONS['zz']:.6g},"
# [Context] Supporting line for the active lvqq analysis stage.
    f" qq={BACKGROUND_FRACTIONS['qq']:.6g},"
# [Context] Supporting line for the active lvqq analysis stage.
    f" tautau={BACKGROUND_FRACTIONS['tautau']:.6g}"
# [Context] Supporting line for the active lvqq analysis stage.
)

# [Context] Supporting line for the active lvqq analysis stage.
doScale = True
# [Context] Supporting line for the active lvqq analysis stage.
intLumi = 10.8e6 if ecm == 240 else 3e6

# [Context] Supporting line for the active lvqq analysis stage.
bins_count = (50, 0, 50)
# [Context] Supporting line for the active lvqq analysis stage.
bins_p = (200, 0, 200)
# [Context] Supporting line for the active lvqq analysis stage.
bins_m = (400, 0, 400)
# [Context] Supporting line for the active lvqq analysis stage.
bins_met = (200, 0, 200)
# [Context] Supporting line for the active lvqq analysis stage.
bins_chi2 = (200, 0, 50)
# [Context] Supporting line for the active lvqq analysis stage.
bins_recoil = (400, 0, 200)
# [Context] Supporting line for the active lvqq analysis stage.
bins_cos = (100, 0, 1)
# [Context] Supporting line for the active lvqq analysis stage.
bins_iso = (100, 0, 1)


# [Physics] Core staged reconstruction + event selection graph.
# Every step is explicitly ordered because final MVAs are sensitive to object definition drift.
# Definitions create new branches (observables), filters discard events from the downstream sample.
def build_graph_lvqq(df, dataset):
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    hists = []

# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("ecm", str(ecm))
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("weight", "1.0")
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    weightsum = df.Sum("weight")

# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    for i in range(0, 12):
# [Physics] Derived branch definition maps detector collections to physics observables.
        df = df.Define(f"cut{i}", str(i))

# [Cutflow] Stage-tracking variable for acceptance and efficiency accounting.
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut0"))

# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    df = df.Alias("Muon0", "Muon#0.index")
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    df = df.Alias("Electron0", "Electron#0.index")

# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("muons_all", "FCCAnalyses::ReconstructedParticle::get(Muon0, ReconstructedParticles)")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("electrons_all", "FCCAnalyses::ReconstructedParticle::get(Electron0, ReconstructedParticles)")

    # cut1: exactly one high-momentum lepton
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("muons_p20", "FCCAnalyses::ReconstructedParticle::sel_p(20)(muons_all)")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("electrons_p20", "FCCAnalyses::ReconstructedParticle::sel_p(20)(electrons_all)")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("leptons_p20", "FCCAnalyses::ReconstructedParticle::merge(muons_p20, electrons_p20)")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("n_leptons_p20", "FCCAnalyses::ReconstructedParticle::get_n(leptons_p20)")
# [Physics] Selection filter defines the reconstructed event topology at each analysis stage.
    # [Filter] Keep only events with exactly one high-pT lepton; this enforces the semi-leptonic (lvqq) final state by construction and removes dileptonic/topologies.
    df = df.Filter("n_leptons_p20 == 1")
# [Cutflow] Stage-tracking variable for acceptance and efficiency accounting.
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut1"))

# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("lepton_p", "FCCAnalyses::ReconstructedParticle::get_p(leptons_p20)[0]")
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    hists.append(df.Histo1D(("lepton_p", "", *bins_p), "lepton_p"))

    # cut2: isolated prompt lepton
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("lepton_iso_v", "FCCAnalyses::coneIsolation(0.01, 0.30)(leptons_p20, ReconstructedParticles)")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("lepton_iso", "lepton_iso_v[0]")
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    hists.append(df.Histo1D(("lepton_iso", "", *bins_iso), "lepton_iso"))
# [Physics] Selection filter defines the reconstructed event topology at each analysis stage.
    # [Filter] Require a tight isolation value to suppress leptons from heavy-flavor decays and fake leptons; this improves signal purity before jet reconstruction.
    df = df.Filter("lepton_iso < 0.15")
# [Cutflow] Stage-tracking variable for acceptance and efficiency accounting.
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut2"))

    # cut3: veto extra leptons above 5 GeV
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("muons_p5", "FCCAnalyses::ReconstructedParticle::sel_p(5)(muons_all)")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("electrons_p5", "FCCAnalyses::ReconstructedParticle::sel_p(5)(electrons_all)")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("leptons_p5", "FCCAnalyses::ReconstructedParticle::merge(muons_p5, electrons_p5)")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("n_leptons_p5", "FCCAnalyses::ReconstructedParticle::get_n(leptons_p5)")
# [Physics] Selection filter defines the reconstructed event topology at each analysis stage.
    # [Filter] Veto additional leptons above 5 GeV, so hadronic activity is interpreted consistently as exactly one prompt lepton channel.
    df = df.Filter("n_leptons_p5 == 1")
# [Cutflow] Stage-tracking variable for acceptance and efficiency accounting.
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut3"))

    # cut4: missing-energy selection
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("missingEnergy_rp", "FCCAnalyses::missingEnergy(ecm, ReconstructedParticles)")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("missingEnergy_e", "missingEnergy_rp[0].energy")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("missingEnergy_p", "FCCAnalyses::ReconstructedParticle::get_p(missingEnergy_rp)[0]")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("missingMass", "FCCAnalyses::missingMass(ecm, ReconstructedParticles)")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("cosTheta_miss", "FCCAnalyses::get_cosTheta_miss(missingEnergy_rp)")
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    hists.append(df.Histo1D(("missingEnergy_e", "", *bins_met), "missingEnergy_e"))
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    hists.append(df.Histo1D(("missingEnergy_p", "", *bins_met), "missingEnergy_p"))
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    hists.append(df.Histo1D(("missingMass", "", *bins_m), "missingMass"))
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    hists.append(df.Histo1D(("cosTheta_miss", "", *bins_cos), "cosTheta_miss"))
# [Physics] Selection filter defines the reconstructed event topology at each analysis stage.
    # [Filter] Minimum missing-energy cut removes events with no neutrino-like recoil; this is a physics-motivated pre-filter for WW*→ℓνqq where one neutrino is expected.
    df = df.Filter("missingEnergy_e > 20")
# [Cutflow] Stage-tracking variable for acceptance and efficiency accounting.
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut4"))

    # [Filter] cut5: remove selected lepton, cluster the remaining objects into jets, and keep only 4-jet events.
    # - This is an event-level filter (selection), not a feature derivation.
    # - Physics intent:
    #   lvqq should contain 4 visible hadrons/jets after removing the reconstructed prompt lepton and neutrino system (roughly 4 quarks from Z + W*).
    #   If njets != 4, downstream feature variables tied to ordered jets become ill-defined or unstable.
    # - ML intent:
    #   Enforces a fixed event structure so the final classifier uses one consistent feature tensor per event (no ragged inputs, stable training).
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("rps_no_leptons", "FCCAnalyses::ReconstructedParticle::remove(ReconstructedParticles, leptons_p5)")
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    df = df.Alias("rps_sel", "rps_no_leptons")

# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("visibleEnergy", "FCCAnalyses::visibleEnergy(rps_sel)")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("visibleEnergy_norm", "visibleEnergy / ecm")
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    hists.append(df.Histo1D(("visibleEnergy", "", *bins_p), "visibleEnergy"))

# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("RP_px", "FCCAnalyses::ReconstructedParticle::get_px(rps_sel)")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("RP_py", "FCCAnalyses::ReconstructedParticle::get_py(rps_sel)")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("RP_pz", "FCCAnalyses::ReconstructedParticle::get_pz(rps_sel)")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("RP_e", "FCCAnalyses::ReconstructedParticle::get_e(rps_sel)")

# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("pseudo_jets", "FCCAnalyses::JetClusteringUtils::set_pseudoJets(RP_px, RP_py, RP_pz, RP_e)")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("clustered_jets", "JetClustering::clustering_ee_kt(2, 4, 0, 10)(pseudo_jets)")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("jets", "FCCAnalyses::JetClusteringUtils::get_pseudoJets(clustered_jets)")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("njets", "jets.size()")
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    hists.append(df.Histo1D(("njets", "", *bins_count), "njets"))
# [Physics] Selection filter defines the reconstructed event topology at each analysis stage.
    # [Filter] Keep only events that still have exactly 4 reconstructed jets after clean clustering.
    # Protects against pathological reconstructions (split/merge failures, fake extra jets, or non-converged clustering seeds).
    # This is why Jan asked "filter": cut5 is a hard topology cut and directly changes the dataset, not just input variable values.
    df = df.Filter("njets == 4")
# [Cutflow] Stage-tracking variable for acceptance and efficiency accounting.
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut5"))

# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("jet0_p", "sqrt(jets[0].px()*jets[0].px() + jets[0].py()*jets[0].py() + jets[0].pz()*jets[0].pz())")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("jet1_p", "sqrt(jets[1].px()*jets[1].px() + jets[1].py()*jets[1].py() + jets[1].pz()*jets[1].pz())")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("jet2_p", "sqrt(jets[2].px()*jets[2].px() + jets[2].py()*jets[2].py() + jets[2].pz()*jets[2].pz())")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("jet3_p", "sqrt(jets[3].px()*jets[3].px() + jets[3].py()*jets[3].py() + jets[3].pz()*jets[3].pz())")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("jet_p_sum", "jet0_p + jet1_p + jet2_p + jet3_p")
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    hists.append(df.Histo1D(("jet0_p", "", *bins_p), "jet0_p"))
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    hists.append(df.Histo1D(("jet1_p", "", *bins_p), "jet1_p"))
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    hists.append(df.Histo1D(("jet2_p", "", *bins_p), "jet2_p"))
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    hists.append(df.Histo1D(("jet3_p", "", *bins_p), "jet3_p"))

    # Pair jets with a Z-priority strategy for H -> WW*
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("jets_e", "FCCAnalyses::JetClusteringUtils::get_e(jets)")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("jets_px", "FCCAnalyses::JetClusteringUtils::get_px(jets)")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("jets_py", "FCCAnalyses::JetClusteringUtils::get_py(jets)")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("jets_pz", "FCCAnalyses::JetClusteringUtils::get_pz(jets)")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("jets_tlv", "FCCAnalyses::makeLorentzVectors(jets_px, jets_py, jets_pz, jets_e)")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("paired_ZWstar", "FCCAnalyses::pairing_Zpriority_4jets(jets_tlv, 91.19)")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("deltaZ", "FCCAnalyses::pairing_Zpriority_deltaZ(jets_tlv, 91.19)")

# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("Zcand", "paired_ZWstar[0]")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("Wstar", "paired_ZWstar[1]")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("Zcand_m", "Zcand.M()")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("Zcand_dm", "abs(Zcand_m - 91.19)")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("Wstar_m", "Wstar.M()")

# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    hists.append(df.Histo1D(("Zcand_m", "", *bins_m), "Zcand_m"))
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    hists.append(df.Histo1D(("Wstar_m", "", *bins_m), "Wstar_m"))
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    hists.append(df.Histo1D(("deltaZ", "", *bins_chi2), "deltaZ"))

    # New features from autonomous exploration
    # Jet merging variables (Durham kT distance when going from n+1 to n jets)
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("d_23", "FCCAnalyses::JetClusteringUtils::get_exclusive_dmerge(clustered_jets, 2)")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("d_34", "FCCAnalyses::JetClusteringUtils::get_exclusive_dmerge(clustered_jets, 3)")

# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("totalJetMass", "FCCAnalyses::totalJetMass(jets_tlv)")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("thrust", "FCCAnalyses::computeThrust(rps_no_leptons)")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("angleLepMiss", "FCCAnalyses::angleLeptonMiss(leptons_p20, missingEnergy_rp)")

# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("init_tlv", "TLorentzVector ret; ret.SetPxPyPzE(0,0,0,ecm); return ret;")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("recoil_tlv", "init_tlv - Zcand")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("recoil_m", "recoil_tlv.M()")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("recoil_dmH", "abs(recoil_m - 125.0)")
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    hists.append(df.Histo1D(("recoil_m", "", *bins_recoil), "recoil_m"))

# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define(
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
        "lepton_tlv",
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
        "TLorentzVector v; v.SetPxPyPzE(leptons_p20[0].momentum.x, leptons_p20[0].momentum.y, leptons_p20[0].momentum.z, leptons_p20[0].energy); return v;",
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    )
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define(
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
        "nu_tlv",
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
        "TLorentzVector v; v.SetPxPyPzE(missingEnergy_rp[0].momentum.x, missingEnergy_rp[0].momentum.y, missingEnergy_rp[0].momentum.z, missingEnergy_rp[0].energy); return v;",
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    )
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("Wlep", "lepton_tlv + nu_tlv")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("Wlep_m", "Wlep.M()")
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    hists.append(df.Histo1D(("Wlep_m", "", *bins_m), "Wlep_m"))

# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("Hcand", "Wlep + Wstar")
# [Physics] Derived branch definition maps detector collections to physics observables.
    df = df.Define("Hcand_m", "Hcand.M()")
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    hists.append(df.Histo1D(("Hcand_m", "", *bins_m), "Hcand_m"))

    # cut6: Z mass window
# [Physics] Selection filter defines the reconstructed event topology at each analysis stage.
    # [Filter] Physics mass-window filter for the hadronic Z candidate. Keeps only events consistent with Z→qq topology; this is the first explicit signal-like resonance constraint.
    df = df.Filter("abs(Zcand_m - 91.19) < 15")
# [Cutflow] Stage-tracking variable for acceptance and efficiency accounting.
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut6"))
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    hists.append(df.Histo1D(("Hcand_m_afterZ", "", *bins_m), "Hcand_m"))
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    hists.append(df.Histo1D(("recoil_m_afterZ", "", *bins_recoil), "recoil_m"))

    # cut7: recoil window
# [Physics] Selection filter defines the reconstructed event topology at each analysis stage.
    # [Filter] Recoil-mass filter around 125 GeV approximates Higgs mass constraints in a variable where the Higgs recoil is reconstructed without using all decay products directly.
    df = df.Filter("abs(recoil_m - 125) < 20")
# [Cutflow] Stage-tracking variable for acceptance and efficiency accounting.
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut7"))
# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    hists.append(df.Histo1D(("Hcand_m_final", "", *bins_m), "Hcand_m"))

# [Physics] Build-step line inside reconstruction graph for e+e- lvqq topology.
    return hists, weightsum, df


# [Context] Supporting line for the active lvqq analysis stage.
if treemaker:
# [Context] Supporting line for the active lvqq analysis stage.
    class RDFanalysis:
# [Context] Supporting line for the active lvqq analysis stage.
        @staticmethod
# [Workflow] h_hww_lvqq.py function analysers: modularize one operation for deterministic pipeline control.
        def analysers(df):
# [Context] Supporting line for the active lvqq analysis stage.
            hists, weightsum, df = build_graph_lvqq(df, "")
# [Workflow] Return value hands the constructed object/metric to the next module stage.
            return df

# [Context] Supporting line for the active lvqq analysis stage.
        @staticmethod
# [Workflow] h_hww_lvqq.py function output: modularize one operation for deterministic pipeline control.
        def output():
# [Workflow] Return value hands the constructed object/metric to the next module stage.
            return ML_SPECTATORS + ML_FEATURES
# [Context] Supporting line for the active lvqq analysis stage.
else:
# [Workflow] h_hww_lvqq.py function build_graph: modularize one operation for deterministic pipeline control.
    def build_graph(df, dataset):
# [Context] Supporting line for the active lvqq analysis stage.
        hists, weightsum, df = build_graph_lvqq(df, dataset)
# [Workflow] Return value hands the constructed object/metric to the next module stage.
        return hists, weightsum
