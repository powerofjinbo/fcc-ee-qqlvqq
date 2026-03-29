"""Shared configuration for the lvqq XGBoost BDT workflow."""

import os


def _parse_fraction_value(raw_value: str, env_name: str) -> float:
    try:
        fraction = float(raw_value)
    except ValueError as exc:
        raise RuntimeError(
            f"Invalid {env_name}={raw_value!r}; expected a float in (0, 1]."
        ) from exc
    if not (0.0 < fraction <= 1.0):
        raise RuntimeError(
            f"Invalid {env_name}={raw_value!r}; expected a float in (0, 1]."
        )
    return fraction


def _default_background_fractions() -> dict[str, float]:
    return {"ww": 0.10, "zz": 0.10, "qq": 0.05, "tautau": 0.10}


def _parse_background_fractions() -> dict[str, float]:
    fractions = _default_background_fractions()

    global_override = os.environ.get("LVQQ_BACKGROUND_FRACTION")
    if global_override is not None:
        parsed = _parse_fraction_value(global_override, "LVQQ_BACKGROUND_FRACTION")
        fractions = {key: parsed for key in fractions}

    for key, env_name in {
        "ww": "LVQQ_WW_FRACTION",
        "zz": "LVQQ_ZZ_FRACTION",
        "qq": "LVQQ_QQ_FRACTION",
        "tautau": "LVQQ_TAUTAU_FRACTION",
    }.items():
        raw_value = os.environ.get(env_name)
        if raw_value is not None:
            fractions[key] = _parse_fraction_value(raw_value, env_name)

    return fractions

ML_SPECTATORS = [
    "weight",
    "njets",
]

ML_FEATURES = [
    "lepton_p",
    "lepton_iso",
    # "missingEnergy_e",  # redundant with missingEnergy_p (massless neutrino)
    "missingEnergy_p",
    "missingMass",
    "cosTheta_miss",
    "visibleEnergy",
    # "visibleEnergy_norm",  # redundant: = visibleEnergy / 240 (constant)
    "jet0_p",
    "jet1_p",
    "jet2_p",
    "jet3_p",
    # "jet_p_sum",  # redundant: = visibleEnergy (same particle collection)
    # "Zcand_m",  # redundant with Zcand_dm (= |Zcand_m - 91.19|)
    "Zcand_dm",
    "Wstar_m",
    # "deltaZ",  # redundant: = Zcand_dm (numerically identical)
    # "recoil_m",  # redundant with recoil_dmH (= |recoil_m - 125|)
    "recoil_dmH",
    "Wlep_m",
    "Hcand_m",
    "totalJetMass",
    "thrust",
    "angleLepMiss",
    "d_23",
    "d_34",
]

SIGNAL_SAMPLES = [
    "wzp6_ee_qqH_HWW_ecm240",
    "wzp6_ee_bbH_HWW_ecm240",
    "wzp6_ee_ccH_HWW_ecm240",
    "wzp6_ee_ssH_HWW_ecm240",
]

BACKGROUND_FRACTIONS = _parse_background_fractions()

ZH_OTHER_SAMPLES = [
    # Hadronic-Z irreducible ZH backgrounds included in the lvqq fit.
    # The original setup only kept the qqH subset; the full hadronic-Z set
    # is needed for a complete background model.
    "wzp6_ee_qqH_Hbb_ecm240",
    "wzp6_ee_qqH_Htautau_ecm240",
    "wzp6_ee_qqH_Hgg_ecm240",
    "wzp6_ee_qqH_Hcc_ecm240",
    "wzp6_ee_qqH_HZZ_ecm240",
    "wzp6_ee_bbH_Hbb_ecm240",
    "wzp6_ee_bbH_Htautau_ecm240",
    "wzp6_ee_bbH_Hgg_ecm240",
    "wzp6_ee_bbH_Hcc_ecm240",
    "wzp6_ee_bbH_HZZ_ecm240",
    "wzp6_ee_ccH_Hbb_ecm240",
    "wzp6_ee_ccH_Htautau_ecm240",
    "wzp6_ee_ccH_Hgg_ecm240",
    "wzp6_ee_ccH_Hcc_ecm240",
    "wzp6_ee_ccH_HZZ_ecm240",
    "wzp6_ee_ssH_Hbb_ecm240",
    "wzp6_ee_ssH_Htautau_ecm240",
    "wzp6_ee_ssH_Hgg_ecm240",
    "wzp6_ee_ssH_Hcc_ecm240",
    "wzp6_ee_ssH_HZZ_ecm240",
]

LARGE_BACKGROUND_SAMPLES = [
    # Diboson
    "p8_ee_WW_ecm240",
    "p8_ee_ZZ_ecm240",
    # 2-fermion (qq, tautau)
    "wz3p6_ee_uu_ecm240",
    "wz3p6_ee_dd_ecm240",
    "wz3p6_ee_cc_ecm240",
    "wz3p6_ee_ss_ecm240",
    "wz3p6_ee_bb_ecm240",
    "wz3p6_ee_tautau_ecm240",
]

FULL_BACKGROUND_SAMPLES = [
    *LARGE_BACKGROUND_SAMPLES,
    *ZH_OTHER_SAMPLES,
]

BACKGROUND_SAMPLES = FULL_BACKGROUND_SAMPLES

WW_SAMPLES = ["p8_ee_WW_ecm240"]
ZZ_SAMPLES = ["p8_ee_ZZ_ecm240"]
QQ_SAMPLES = [
    "wz3p6_ee_uu_ecm240",
    "wz3p6_ee_dd_ecm240",
    "wz3p6_ee_cc_ecm240",
    "wz3p6_ee_ss_ecm240",
    "wz3p6_ee_bb_ecm240",
]
TAUTAU_SAMPLES = ["wz3p6_ee_tautau_ecm240"]

SAMPLE_PROCESSING_FRACTIONS = {
    **{sample: 1.0 for sample in SIGNAL_SAMPLES},
    **{sample: BACKGROUND_FRACTIONS["ww"] for sample in WW_SAMPLES},
    **{sample: BACKGROUND_FRACTIONS["zz"] for sample in ZZ_SAMPLES},
    **{sample: BACKGROUND_FRACTIONS["qq"] for sample in QQ_SAMPLES},
    **{sample: BACKGROUND_FRACTIONS["tautau"] for sample in TAUTAU_SAMPLES},
    **{sample: 1.0 for sample in ZH_OTHER_SAMPLES},
}

DEFAULT_TREE_NAME = "events"
DEFAULT_TREEMAKER_DIR = "output/h_hww_lvqq/treemaker/ecm240"
DEFAULT_MODEL_DIR = "ml/models/xgboost_bdt_v6"
DEFAULT_SCORE_BRANCH = "bdt_score"
