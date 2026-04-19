import os

import ROOT

from ml_config import (
    BACKGROUND_SAMPLES,
    BACKGROUND_FRACTIONS,
    ML_FEATURES,
    ML_SPECTATORS,
    SAMPLE_PROCESSING_FRACTIONS,
    SIGNAL_SAMPLES,
)

ROOT.TH1.SetDefaultSumw2(ROOT.kTRUE)

# ============================================================
# FCC-ee analysis: e+e- -> Z(qq) H(WW -> l nu qq)
# Final state: 4 jets + 1 lepton (e/mu) + MET
# ============================================================

ecm = 240
mode = os.environ.get("LVQQ_MODE", "histmaker").strip().lower()
if mode not in {"histmaker", "treemaker"}:
    raise RuntimeError(f"Unsupported LVQQ_MODE={mode!r}; use 'histmaker' or 'treemaker'")

treemaker = mode == "treemaker"


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

inputDir = "/ceph/submit/data/group/fcc/ee/generation/DelphesEvents/winter2023/IDEA/"
procDict = "/ceph/submit/data/group/fcc/ee/generation/DelphesEvents/winter2023/IDEA/samplesDict.json"
includePaths = ["../functions/functions.h", "../functions/functions_gen.h", "utils.h"]

if treemaker:
    outputDir = f"output/h_hww_lvqq/treemaker/ecm{ecm}/"
else:
    outputDir = f"output/h_hww_lvqq/histmaker/ecm{ecm}/"

nCPUS = _get_worker_cpus()
ROOT.EnableImplicitMT(nCPUS)
print(f"[lvqq] active backgrounds: {len(BACKGROUND_SAMPLES)}")
print(
    "[lvqq] fractions:"
    f" WW={BACKGROUND_FRACTIONS['ww']:.6g},"
    f" ZZ={BACKGROUND_FRACTIONS['zz']:.6g},"
    f" qq={BACKGROUND_FRACTIONS['qq']:.6g},"
    f" tautau={BACKGROUND_FRACTIONS['tautau']:.6g}"
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


def build_graph_lvqq(df, dataset):
    hists = []

    df = df.Define("ecm", str(ecm))
    df = df.Define("weight", "1.0")
    weightsum = df.Sum("weight")

    for i in range(0, 12):
        df = df.Define(f"cut{i}", str(i))

    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut0"))

    df = df.Alias("Muon0", "Muon#0.index")
    df = df.Alias("Electron0", "Electron#0.index")

    df = df.Define("muons_all", "FCCAnalyses::ReconstructedParticle::get(Muon0, ReconstructedParticles)")
    df = df.Define("electrons_all", "FCCAnalyses::ReconstructedParticle::get(Electron0, ReconstructedParticles)")

    # cut1: exactly one high-momentum lepton
    df = df.Define("muons_p20", "FCCAnalyses::ReconstructedParticle::sel_p(20)(muons_all)")
    df = df.Define("electrons_p20", "FCCAnalyses::ReconstructedParticle::sel_p(20)(electrons_all)")
    df = df.Define("leptons_p20", "FCCAnalyses::ReconstructedParticle::merge(muons_p20, electrons_p20)")
    df = df.Define("n_leptons_p20", "FCCAnalyses::ReconstructedParticle::get_n(leptons_p20)")
    hists.append(df.Histo1D(("n_leptons_p20", "", *bins_nlep), "n_leptons_p20"))
    df = df.Filter("n_leptons_p20 == 1")
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut1"))

    df = df.Define("lepton_p", "FCCAnalyses::ReconstructedParticle::get_p(leptons_p20)[0]")
    hists.append(df.Histo1D(("lepton_p", "", *bins_p), "lepton_p"))

    # cut2: isolated prompt lepton
    df = df.Define("lepton_iso_v", "FCCAnalyses::coneIsolation(0.01, 0.30)(leptons_p20, ReconstructedParticles)")
    df = df.Define("lepton_iso", "lepton_iso_v[0]")
    hists.append(df.Histo1D(("lepton_iso", "", *bins_iso), "lepton_iso"))
    df = df.Filter("lepton_iso < 0.15")
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut2"))

    # cut3: veto extra leptons above 5 GeV
    df = df.Define("muons_p5", "FCCAnalyses::ReconstructedParticle::sel_p(5)(muons_all)")
    df = df.Define("electrons_p5", "FCCAnalyses::ReconstructedParticle::sel_p(5)(electrons_all)")
    df = df.Define("leptons_p5", "FCCAnalyses::ReconstructedParticle::merge(muons_p5, electrons_p5)")
    df = df.Define("n_leptons_p5", "FCCAnalyses::ReconstructedParticle::get_n(leptons_p5)")
    hists.append(df.Histo1D(("n_leptons_p5", "", *bins_nlep), "n_leptons_p5"))
    df = df.Filter("n_leptons_p5 == 1")
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut3"))

    # cut4: missing-energy selection
    df = df.Define("missingEnergy_rp", "FCCAnalyses::missingEnergy(ecm, ReconstructedParticles)")
    df = df.Define("missingEnergy_e", "missingEnergy_rp[0].energy")
    df = df.Define("missingEnergy_p", "FCCAnalyses::ReconstructedParticle::get_p(missingEnergy_rp)[0]")
    df = df.Define("missingMass", "FCCAnalyses::missingMass(ecm, ReconstructedParticles)")
    df = df.Define("cosTheta_miss", "FCCAnalyses::get_cosTheta_miss(missingEnergy_rp)")
    hists.append(df.Histo1D(("missingEnergy_e", "", *bins_met), "missingEnergy_e"))
    hists.append(df.Histo1D(("missingEnergy_p", "", *bins_met), "missingEnergy_p"))
    hists.append(df.Histo1D(("missingMass", "", *bins_m), "missingMass"))
    hists.append(df.Histo1D(("cosTheta_miss", "", *bins_cos), "cosTheta_miss"))
    df = df.Filter("missingEnergy_e > 20")
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut4"))

    # cut5: remove the selected lepton and cluster the rest into 4 jets
    df = df.Define("rps_no_leptons", "FCCAnalyses::ReconstructedParticle::remove(ReconstructedParticles, leptons_p5)")
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
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut5"))

    df = df.Define("jet0_p", "sqrt(jets[0].px()*jets[0].px() + jets[0].py()*jets[0].py() + jets[0].pz()*jets[0].pz())")
    df = df.Define("jet1_p", "sqrt(jets[1].px()*jets[1].px() + jets[1].py()*jets[1].py() + jets[1].pz()*jets[1].pz())")
    df = df.Define("jet2_p", "sqrt(jets[2].px()*jets[2].px() + jets[2].py()*jets[2].py() + jets[2].pz()*jets[2].pz())")
    df = df.Define("jet3_p", "sqrt(jets[3].px()*jets[3].px() + jets[3].py()*jets[3].py() + jets[3].pz()*jets[3].pz())")
    df = df.Define("jet_p_sum", "jet0_p + jet1_p + jet2_p + jet3_p")
    hists.append(df.Histo1D(("jet0_p", "", *bins_p), "jet0_p"))
    hists.append(df.Histo1D(("jet1_p", "", *bins_p), "jet1_p"))
    hists.append(df.Histo1D(("jet2_p", "", *bins_p), "jet2_p"))
    hists.append(df.Histo1D(("jet3_p", "", *bins_p), "jet3_p"))

    # Pair jets with a Z-priority strategy for H -> WW*
    df = df.Define("jets_e", "FCCAnalyses::JetClusteringUtils::get_e(jets)")
    df = df.Define("jets_px", "FCCAnalyses::JetClusteringUtils::get_px(jets)")
    df = df.Define("jets_py", "FCCAnalyses::JetClusteringUtils::get_py(jets)")
    df = df.Define("jets_pz", "FCCAnalyses::JetClusteringUtils::get_pz(jets)")
    df = df.Define("jets_tlv", "FCCAnalyses::makeLorentzVectors(jets_px, jets_py, jets_pz, jets_e)")
    df = df.Define("paired_ZWstar", "FCCAnalyses::pairing_Zpriority_4jets(jets_tlv, 91.19)")
    df = df.Define("deltaZ", "FCCAnalyses::pairing_Zpriority_deltaZ(jets_tlv, 91.19)")

    df = df.Define("Zcand", "paired_ZWstar[0]")
    df = df.Define("Wstar", "paired_ZWstar[1]")
    df = df.Define("Zcand_m", "Zcand.M()")
    df = df.Define("Zcand_dm", "abs(Zcand_m - 91.19)")
    df = df.Define("Wstar_m", "Wstar.M()")

    hists.append(df.Histo1D(("Zcand_m", "", *bins_m), "Zcand_m"))
    hists.append(df.Histo1D(("Wstar_m", "", *bins_m), "Wstar_m"))
    hists.append(df.Histo1D(("deltaZ", "", *bins_chi2), "deltaZ"))

    # New features from autonomous exploration
    # Jet merging variables (Durham kT distance when going from n+1 to n jets)
    df = df.Define("d_23", "FCCAnalyses::JetClusteringUtils::get_exclusive_dmerge(clustered_jets, 2)")
    df = df.Define("d_34", "FCCAnalyses::JetClusteringUtils::get_exclusive_dmerge(clustered_jets, 3)")

    df = df.Define("totalJetMass", "FCCAnalyses::totalJetMass(jets_tlv)")
    df = df.Define("thrust", "FCCAnalyses::computeThrust(rps_no_leptons)")
    df = df.Define("angleLepMiss", "FCCAnalyses::angleLeptonMiss(leptons_p20, missingEnergy_rp)")

    df = df.Define("init_tlv", "TLorentzVector ret; ret.SetPxPyPzE(0,0,0,ecm); return ret;")
    df = df.Define("recoil_tlv", "init_tlv - Zcand")
    df = df.Define("recoil_m", "recoil_tlv.M()")
    df = df.Define("recoil_dmH", "abs(recoil_m - 125.0)")
    hists.append(df.Histo1D(("recoil_m", "", *bins_recoil), "recoil_m"))

    df = df.Define(
        "lepton_tlv",
        "TLorentzVector v; v.SetPxPyPzE(leptons_p20[0].momentum.x, leptons_p20[0].momentum.y, leptons_p20[0].momentum.z, leptons_p20[0].energy); return v;",
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

    # cut6: Z mass window
    df = df.Filter("abs(Zcand_m - 91.19) < 15")
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut6"))
    hists.append(df.Histo1D(("Hcand_m_afterZ", "", *bins_m), "Hcand_m"))
    hists.append(df.Histo1D(("recoil_m_afterZ", "", *bins_recoil), "recoil_m"))

    # cut7: recoil window
    df = df.Filter("abs(recoil_m - 125) < 20")
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut7"))
    hists.append(df.Histo1D(("Hcand_m_final", "", *bins_m), "Hcand_m"))

    return hists, weightsum, df


if treemaker:
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
