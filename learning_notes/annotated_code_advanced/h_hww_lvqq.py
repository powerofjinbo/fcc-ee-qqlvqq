# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
import os

# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
import ROOT

# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
from ml_config import (
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    BACKGROUND_SAMPLES,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    BACKGROUND_FRACTIONS,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ML_FEATURES,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ML_SPECTATORS,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    SAMPLE_PROCESSING_FRACTIONS,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    SIGNAL_SAMPLES,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
ROOT.TH1.SetDefaultSumw2(ROOT.kTRUE)

# ============================================================
# FCC-ee analysis: e+e- -> Z(qq) H(WW -> l nu qq)
# Final state: 4 jets + 1 lepton (e/mu) + MET
# ============================================================

# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
ecm = 240
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
mode = os.environ.get("LVQQ_MODE", "histmaker").strip().lower()
# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
if mode not in {"histmaker", "treemaker"}:
# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
    raise RuntimeError(f"Unsupported LVQQ_MODE={mode!r}; use 'histmaker' or 'treemaker'")

# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
treemaker = mode == "treemaker"


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def _get_worker_cpus() -> int:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    raw_value = os.environ.get("LVQQ_CPUS", os.environ.get("SLURM_CPUS_PER_TASK", "32"))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    try:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        cpus = int(raw_value)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    except ValueError as exc:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        raise RuntimeError(f"Invalid CPU setting {raw_value!r}; expected a positive integer") from exc
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if cpus < 1:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        raise RuntimeError(f"Invalid CPU setting {raw_value!r}; expected a positive integer")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    return cpus

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
processList = {
    # Signal: ZH -> Z(qq) H(WW* -> lvqq)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    **{sample: {"fraction": SAMPLE_PROCESSING_FRACTIONS[sample]} for sample in SIGNAL_SAMPLES},
    # Full background model with mixed processing fractions.
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    **{sample: {"fraction": SAMPLE_PROCESSING_FRACTIONS[sample]} for sample in BACKGROUND_SAMPLES},
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
}

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
inputDir = "/ceph/submit/data/group/fcc/ee/generation/DelphesEvents/winter2023/IDEA/"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
procDict = "/ceph/submit/data/group/fcc/ee/generation/DelphesEvents/winter2023/IDEA/samplesDict.json"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
includePaths = ["../functions/functions.h", "../functions/functions_gen.h", "utils.h"]

# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
if treemaker:
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    outputDir = f"output/h_hww_lvqq/treemaker/ecm{ecm}/"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
else:
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    outputDir = f"output/h_hww_lvqq/histmaker/ecm{ecm}/"

# [Performance] Parallel event processing setup to keep large ntuple loops efficient and deterministic at analysis scale.
nCPUS = _get_worker_cpus()
# [Performance] Parallel event processing setup to keep large ntuple loops efficient and deterministic at analysis scale.
ROOT.EnableImplicitMT(nCPUS)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
print(f"[lvqq] active backgrounds: {len(BACKGROUND_SAMPLES)}")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
print(
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "[lvqq] fractions:"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    f" WW={BACKGROUND_FRACTIONS['ww']:.6g},"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    f" ZZ={BACKGROUND_FRACTIONS['zz']:.6g},"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    f" qq={BACKGROUND_FRACTIONS['qq']:.6g},"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    f" tautau={BACKGROUND_FRACTIONS['tautau']:.6g}"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
doScale = True
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
intLumi = 10.8e6 if ecm == 240 else 3e6

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
bins_count = (50, 0, 50)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
bins_p = (200, 0, 200)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
bins_m = (400, 0, 400)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
bins_met = (200, 0, 200)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
bins_chi2 = (200, 0, 50)
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
bins_recoil = (400, 0, 200)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
bins_cos = (100, 0, 1)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
bins_iso = (100, 0, 1)


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def build_graph_lvqq(df, dataset):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    hists = []

# [Physics] Derived branch definition in ROOT DataFrame: transforms raw detector objects into compact physics features for downstream fit/ML.
    df = df.Define("ecm", str(ecm))
# [Physics] Derived branch definition in ROOT DataFrame: transforms raw detector objects into compact physics features for downstream fit/ML.
    df = df.Define("weight", "1.0")
# [Physics] Event weight setup: maps generated events to expected yields using cross section and integrated luminosity, with sample processing fraction correction.
    weightsum = df.Sum("weight")

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for i in range(0, 12):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        df = df.Define(f"cut{i}", str(i))

# [Physics] This is one line in the cut-flow chain; index names map to staged selection requirements used later for cutflow and optimization.
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut0"))

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    df = df.Alias("Muon0", "Muon#0.index")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    df = df.Alias("Electron0", "Electron#0.index")

# [Physics] Derived branch definition in ROOT DataFrame: transforms raw detector objects into compact physics features for downstream fit/ML.
    df = df.Define("muons_all", "FCCAnalyses::ReconstructedParticle::get(Muon0, ReconstructedParticles)")
# [Physics] Derived branch definition in ROOT DataFrame: transforms raw detector objects into compact physics features for downstream fit/ML.
    df = df.Define("electrons_all", "FCCAnalyses::ReconstructedParticle::get(Electron0, ReconstructedParticles)")

    # cut1: exactly one high-momentum lepton
# [Physics] Derived branch definition in ROOT DataFrame: transforms raw detector objects into compact physics features for downstream fit/ML.
    df = df.Define("muons_p20", "FCCAnalyses::ReconstructedParticle::sel_p(20)(muons_all)")
# [Physics] Derived branch definition in ROOT DataFrame: transforms raw detector objects into compact physics features for downstream fit/ML.
    df = df.Define("electrons_p20", "FCCAnalyses::ReconstructedParticle::sel_p(20)(electrons_all)")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("leptons_p20", "FCCAnalyses::ReconstructedParticle::merge(muons_p20, electrons_p20)")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("n_leptons_p20", "FCCAnalyses::ReconstructedParticle::get_n(leptons_p20)")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Filter("n_leptons_p20 == 1")
# [Physics] This is one line in the cut-flow chain; index names map to staged selection requirements used later for cutflow and optimization.
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut1"))

# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("lepton_p", "FCCAnalyses::ReconstructedParticle::get_p(leptons_p20)[0]")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    hists.append(df.Histo1D(("lepton_p", "", *bins_p), "lepton_p"))

    # cut2: isolated prompt lepton
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("lepton_iso_v", "FCCAnalyses::coneIsolation(0.01, 0.30)(leptons_p20, ReconstructedParticles)")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("lepton_iso", "lepton_iso_v[0]")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    hists.append(df.Histo1D(("lepton_iso", "", *bins_iso), "lepton_iso"))
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Filter("lepton_iso < 0.15")
# [Physics] This is one line in the cut-flow chain; index names map to staged selection requirements used later for cutflow and optimization.
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut2"))

    # cut3: veto extra leptons above 5 GeV
# [Physics] Derived branch definition in ROOT DataFrame: transforms raw detector objects into compact physics features for downstream fit/ML.
    df = df.Define("muons_p5", "FCCAnalyses::ReconstructedParticle::sel_p(5)(muons_all)")
# [Physics] Derived branch definition in ROOT DataFrame: transforms raw detector objects into compact physics features for downstream fit/ML.
    df = df.Define("electrons_p5", "FCCAnalyses::ReconstructedParticle::sel_p(5)(electrons_all)")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("leptons_p5", "FCCAnalyses::ReconstructedParticle::merge(muons_p5, electrons_p5)")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("n_leptons_p5", "FCCAnalyses::ReconstructedParticle::get_n(leptons_p5)")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Filter("n_leptons_p5 == 1")
# [Physics] This is one line in the cut-flow chain; index names map to staged selection requirements used later for cutflow and optimization.
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut3"))

    # cut4: missing-energy selection
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("missingEnergy_rp", "FCCAnalyses::missingEnergy(ecm, ReconstructedParticles)")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("missingEnergy_e", "missingEnergy_rp[0].energy")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("missingEnergy_p", "FCCAnalyses::ReconstructedParticle::get_p(missingEnergy_rp)[0]")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("missingMass", "FCCAnalyses::missingMass(ecm, ReconstructedParticles)")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("cosTheta_miss", "FCCAnalyses::get_cosTheta_miss(missingEnergy_rp)")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    hists.append(df.Histo1D(("missingEnergy_e", "", *bins_met), "missingEnergy_e"))
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    hists.append(df.Histo1D(("missingEnergy_p", "", *bins_met), "missingEnergy_p"))
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    hists.append(df.Histo1D(("missingMass", "", *bins_m), "missingMass"))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    hists.append(df.Histo1D(("cosTheta_miss", "", *bins_cos), "cosTheta_miss"))
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Filter("missingEnergy_e > 20")
# [Physics] This is one line in the cut-flow chain; index names map to staged selection requirements used later for cutflow and optimization.
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut4"))

    # cut5: remove the selected lepton and cluster the rest into 4 jets
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("rps_no_leptons", "FCCAnalyses::ReconstructedParticle::remove(ReconstructedParticles, leptons_p5)")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Alias("rps_sel", "rps_no_leptons")

# [Physics] Derived branch definition in ROOT DataFrame: transforms raw detector objects into compact physics features for downstream fit/ML.
    df = df.Define("visibleEnergy", "FCCAnalyses::visibleEnergy(rps_sel)")
# [Physics] Derived branch definition in ROOT DataFrame: transforms raw detector objects into compact physics features for downstream fit/ML.
    df = df.Define("visibleEnergy_norm", "visibleEnergy / ecm")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    hists.append(df.Histo1D(("visibleEnergy", "", *bins_p), "visibleEnergy"))

# [Physics] Derived branch definition in ROOT DataFrame: transforms raw detector objects into compact physics features for downstream fit/ML.
    df = df.Define("RP_px", "FCCAnalyses::ReconstructedParticle::get_px(rps_sel)")
# [Physics] Derived branch definition in ROOT DataFrame: transforms raw detector objects into compact physics features for downstream fit/ML.
    df = df.Define("RP_py", "FCCAnalyses::ReconstructedParticle::get_py(rps_sel)")
# [Physics] Derived branch definition in ROOT DataFrame: transforms raw detector objects into compact physics features for downstream fit/ML.
    df = df.Define("RP_pz", "FCCAnalyses::ReconstructedParticle::get_pz(rps_sel)")
# [Physics] Derived branch definition in ROOT DataFrame: transforms raw detector objects into compact physics features for downstream fit/ML.
    df = df.Define("RP_e", "FCCAnalyses::ReconstructedParticle::get_e(rps_sel)")

# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("pseudo_jets", "FCCAnalyses::JetClusteringUtils::set_pseudoJets(RP_px, RP_py, RP_pz, RP_e)")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("clustered_jets", "JetClustering::clustering_ee_kt(2, 4, 0, 10)(pseudo_jets)")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("jets", "FCCAnalyses::JetClusteringUtils::get_pseudoJets(clustered_jets)")
# [Physics] Derived branch definition in ROOT DataFrame: transforms raw detector objects into compact physics features for downstream fit/ML.
    df = df.Define("njets", "jets.size()")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    hists.append(df.Histo1D(("njets", "", *bins_count), "njets"))
# [Physics] Explicit event selection cut. Cuts tighten event topology to match lvqq reconstruction assumptions and control background topology before ML modeling.
    df = df.Filter("njets == 4")
# [Physics] This is one line in the cut-flow chain; index names map to staged selection requirements used later for cutflow and optimization.
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut5"))

# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("jet0_p", "sqrt(jets[0].px()*jets[0].px() + jets[0].py()*jets[0].py() + jets[0].pz()*jets[0].pz())")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("jet1_p", "sqrt(jets[1].px()*jets[1].px() + jets[1].py()*jets[1].py() + jets[1].pz()*jets[1].pz())")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("jet2_p", "sqrt(jets[2].px()*jets[2].px() + jets[2].py()*jets[2].py() + jets[2].pz()*jets[2].pz())")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("jet3_p", "sqrt(jets[3].px()*jets[3].px() + jets[3].py()*jets[3].py() + jets[3].pz()*jets[3].pz())")
# [Physics] Derived branch definition in ROOT DataFrame: transforms raw detector objects into compact physics features for downstream fit/ML.
    df = df.Define("jet_p_sum", "jet0_p + jet1_p + jet2_p + jet3_p")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    hists.append(df.Histo1D(("jet0_p", "", *bins_p), "jet0_p"))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    hists.append(df.Histo1D(("jet1_p", "", *bins_p), "jet1_p"))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    hists.append(df.Histo1D(("jet2_p", "", *bins_p), "jet2_p"))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    hists.append(df.Histo1D(("jet3_p", "", *bins_p), "jet3_p"))

    # Pair jets with a Z-priority strategy for H -> WW*
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("jets_e", "FCCAnalyses::JetClusteringUtils::get_e(jets)")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("jets_px", "FCCAnalyses::JetClusteringUtils::get_px(jets)")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("jets_py", "FCCAnalyses::JetClusteringUtils::get_py(jets)")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("jets_pz", "FCCAnalyses::JetClusteringUtils::get_pz(jets)")
# [Physics] Derived branch definition in ROOT DataFrame: transforms raw detector objects into compact physics features for downstream fit/ML.
    df = df.Define("jets_tlv", "FCCAnalyses::makeLorentzVectors(jets_px, jets_py, jets_pz, jets_e)")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("paired_ZWstar", "FCCAnalyses::pairing_Zpriority_4jets(jets_tlv, 91.19)")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("deltaZ", "FCCAnalyses::pairing_Zpriority_deltaZ(jets_tlv, 91.19)")

# [Physics] Derived branch definition in ROOT DataFrame: transforms raw detector objects into compact physics features for downstream fit/ML.
    df = df.Define("Zcand", "paired_ZWstar[0]")
# [Physics] Derived branch definition in ROOT DataFrame: transforms raw detector objects into compact physics features for downstream fit/ML.
    df = df.Define("Wstar", "paired_ZWstar[1]")
# [Physics] Derived branch definition in ROOT DataFrame: transforms raw detector objects into compact physics features for downstream fit/ML.
    df = df.Define("Zcand_m", "Zcand.M()")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("Zcand_dm", "abs(Zcand_m - 91.19)")
# [Physics] Derived branch definition in ROOT DataFrame: transforms raw detector objects into compact physics features for downstream fit/ML.
    df = df.Define("Wstar_m", "Wstar.M()")

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    hists.append(df.Histo1D(("Zcand_m", "", *bins_m), "Zcand_m"))
# [Physics] Mass-like observables encode event-level consistency; they become strong discriminants for separating H->WW* from diboson and qq backgrounds.
    hists.append(df.Histo1D(("Wstar_m", "", *bins_m), "Wstar_m"))
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    hists.append(df.Histo1D(("deltaZ", "", *bins_chi2), "deltaZ"))

    # New features from autonomous exploration
    # Jet merging variables (Durham kT distance when going from n+1 to n jets)
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("d_23", "FCCAnalyses::JetClusteringUtils::get_exclusive_dmerge(clustered_jets, 2)")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("d_34", "FCCAnalyses::JetClusteringUtils::get_exclusive_dmerge(clustered_jets, 3)")

# [Physics] Derived branch definition in ROOT DataFrame: transforms raw detector objects into compact physics features for downstream fit/ML.
    df = df.Define("totalJetMass", "FCCAnalyses::totalJetMass(jets_tlv)")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("thrust", "FCCAnalyses::computeThrust(rps_no_leptons)")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("angleLepMiss", "FCCAnalyses::angleLeptonMiss(leptons_p20, missingEnergy_rp)")

# [Physics] Derived branch definition in ROOT DataFrame: transforms raw detector objects into compact physics features for downstream fit/ML.
    df = df.Define("init_tlv", "TLorentzVector ret; ret.SetPxPyPzE(0,0,0,ecm); return ret;")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("recoil_tlv", "init_tlv - Zcand")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("recoil_m", "recoil_tlv.M()")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("recoil_dmH", "abs(recoil_m - 125.0)")
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    hists.append(df.Histo1D(("recoil_m", "", *bins_recoil), "recoil_m"))

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    df = df.Define(
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        "lepton_tlv",
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        "TLorentzVector v; v.SetPxPyPzE(leptons_p20[0].momentum.x, leptons_p20[0].momentum.y, leptons_p20[0].momentum.z, leptons_p20[0].energy); return v;",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    )
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    df = df.Define(
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "nu_tlv",
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        "TLorentzVector v; v.SetPxPyPzE(missingEnergy_rp[0].momentum.x, missingEnergy_rp[0].momentum.y, missingEnergy_rp[0].momentum.z, missingEnergy_rp[0].energy); return v;",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    )
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Define("Wlep", "lepton_tlv + nu_tlv")
# [Physics] Derived branch definition in ROOT DataFrame: transforms raw detector objects into compact physics features for downstream fit/ML.
    df = df.Define("Wlep_m", "Wlep.M()")
# [Physics] Mass-like observables encode event-level consistency; they become strong discriminants for separating H->WW* from diboson and qq backgrounds.
    hists.append(df.Histo1D(("Wlep_m", "", *bins_m), "Wlep_m"))

# [Physics] Derived branch definition in ROOT DataFrame: transforms raw detector objects into compact physics features for downstream fit/ML.
    df = df.Define("Hcand", "Wlep + Wstar")
# [Physics] Derived branch definition in ROOT DataFrame: transforms raw detector objects into compact physics features for downstream fit/ML.
    df = df.Define("Hcand_m", "Hcand.M()")
# [Physics] Mass-like observables encode event-level consistency; they become strong discriminants for separating H->WW* from diboson and qq backgrounds.
    hists.append(df.Histo1D(("Hcand_m", "", *bins_m), "Hcand_m"))

    # cut6: Z mass window
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Filter("abs(Zcand_m - 91.19) < 15")
# [Physics] This is one line in the cut-flow chain; index names map to staged selection requirements used later for cutflow and optimization.
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut6"))
# [Physics] Mass-like observables encode event-level consistency; they become strong discriminants for separating H->WW* from diboson and qq backgrounds.
    hists.append(df.Histo1D(("Hcand_m_afterZ", "", *bins_m), "Hcand_m"))
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    hists.append(df.Histo1D(("recoil_m_afterZ", "", *bins_recoil), "recoil_m"))

    # cut7: recoil window
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    df = df.Filter("abs(recoil_m - 125) < 20")
# [Physics] This is one line in the cut-flow chain; index names map to staged selection requirements used later for cutflow and optimization.
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut7"))
# [Physics] Mass-like observables encode event-level consistency; they become strong discriminants for separating H->WW* from diboson and qq backgrounds.
    hists.append(df.Histo1D(("Hcand_m_final", "", *bins_m), "Hcand_m"))

# [Physics] Event weight setup: maps generated events to expected yields using cross section and integrated luminosity, with sample processing fraction correction.
    return hists, weightsum, df


# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
if treemaker:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    class RDFanalysis:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        @staticmethod
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        def analysers(df):
# [Physics] Event weight setup: maps generated events to expected yields using cross section and integrated luminosity, with sample processing fraction correction.
            hists, weightsum, df = build_graph_lvqq(df, "")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            return df

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        @staticmethod
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        def output():
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            return ML_SPECTATORS + ML_FEATURES
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
else:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    def build_graph(df, dataset):
# [Physics] Event weight setup: maps generated events to expected yields using cross section and integrated luminosity, with sample processing fraction correction.
        hists, weightsum, df = build_graph_lvqq(df, dataset)
# [Physics] Event weight setup: maps generated events to expected yields using cross section and integrated luminosity, with sample processing fraction correction.
        return hists, weightsum
