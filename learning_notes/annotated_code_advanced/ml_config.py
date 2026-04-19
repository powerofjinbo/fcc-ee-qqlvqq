# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
"""Shared configuration for the lvqq XGBoost BDT workflow."""

# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
import os


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def _parse_fraction_value(raw_value: str, env_name: str) -> float:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    try:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        fraction = float(raw_value)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    except ValueError as exc:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        raise RuntimeError(
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            f"Invalid {env_name}={raw_value!r}; expected a float in (0, 1]."
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ) from exc
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if not (0.0 < fraction <= 1.0):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        raise RuntimeError(
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            f"Invalid {env_name}={raw_value!r}; expected a float in (0, 1]."
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        )
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    return fraction


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def _default_background_fractions() -> dict[str, float]:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    return {"ww": 1.0, "zz": 1.0, "qq": 1.0, "tautau": 1.0}


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def _parse_background_fractions() -> dict[str, float]:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    fractions = _default_background_fractions()

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    global_override = os.environ.get("LVQQ_BACKGROUND_FRACTION")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if global_override is not None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        parsed = _parse_fraction_value(global_override, "LVQQ_BACKGROUND_FRACTION")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        fractions = {key: parsed for key in fractions}

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for key, env_name in {
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "ww": "LVQQ_WW_FRACTION",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "zz": "LVQQ_ZZ_FRACTION",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "qq": "LVQQ_QQ_FRACTION",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "tautau": "LVQQ_TAUTAU_FRACTION",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    }.items():
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        raw_value = os.environ.get(env_name)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        if raw_value is not None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            fractions[key] = _parse_fraction_value(raw_value, env_name)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    return fractions

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
ML_SPECTATORS = [
# [Physics] Event weight setup: maps generated events to expected yields using cross section and integrated luminosity, with sample processing fraction correction.
    "weight",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "njets",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
]

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
ML_FEATURES = [
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    "lepton_p",
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    "lepton_iso",
    # "missingEnergy_e",  # redundant with missingEnergy_p (massless neutrino)
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    "missingEnergy_p",
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    "missingMass",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "cosTheta_miss",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "visibleEnergy",
    # "visibleEnergy_norm",  # redundant: = visibleEnergy / 240 (constant)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "jet0_p",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "jet1_p",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "jet2_p",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "jet3_p",
    # "jet_p_sum",  # redundant: = visibleEnergy (same particle collection)
    # "Zcand_m",  # redundant with Zcand_dm (= |Zcand_m - 91.19|)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "Zcand_dm",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "Wstar_m",
    # "deltaZ",  # redundant: = Zcand_dm (numerically identical)
    # "recoil_m",  # redundant with recoil_dmH (= |recoil_m - 125|)
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    "recoil_dmH",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "Wlep_m",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "Hcand_m",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "totalJetMass",
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    "thrust",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "angleLepMiss",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "d_23",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    "d_34",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
]

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
SIGNAL_SAMPLES = [
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_qqH_HWW_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_bbH_HWW_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_ccH_HWW_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_ssH_HWW_ecm240",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
]

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
BACKGROUND_FRACTIONS = _parse_background_fractions()

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
ZH_OTHER_SAMPLES = [
    # Hadronic-Z irreducible ZH backgrounds included in the lvqq fit.
    # The original setup only kept the qqH subset; the full hadronic-Z set
    # is needed for a complete background model.
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_qqH_Hbb_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_qqH_Htautau_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_qqH_Hgg_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_qqH_Hcc_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_qqH_HZZ_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_bbH_Hbb_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_bbH_Htautau_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_bbH_Hgg_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_bbH_Hcc_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_bbH_HZZ_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_ccH_Hbb_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_ccH_Htautau_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_ccH_Hgg_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_ccH_Hcc_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_ccH_HZZ_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_ssH_Hbb_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_ssH_Htautau_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_ssH_Hgg_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_ssH_Hcc_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wzp6_ee_ssH_HZZ_ecm240",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
]

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
LARGE_BACKGROUND_SAMPLES = [
    # Diboson
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "p8_ee_WW_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "p8_ee_ZZ_ecm240",
    # 2-fermion (qq, tautau)
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wz3p6_ee_uu_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wz3p6_ee_dd_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wz3p6_ee_cc_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wz3p6_ee_ss_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wz3p6_ee_bb_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wz3p6_ee_tautau_ecm240",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
]

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
FULL_BACKGROUND_SAMPLES = [
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    *LARGE_BACKGROUND_SAMPLES,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    *ZH_OTHER_SAMPLES,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
]

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
BACKGROUND_SAMPLES = FULL_BACKGROUND_SAMPLES

# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
WW_SAMPLES = ["p8_ee_WW_ecm240"]
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
ZZ_SAMPLES = ["p8_ee_ZZ_ecm240"]
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
QQ_SAMPLES = [
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wz3p6_ee_uu_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wz3p6_ee_dd_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wz3p6_ee_cc_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wz3p6_ee_ss_ecm240",
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    "wz3p6_ee_bb_ecm240",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
]
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
TAUTAU_SAMPLES = ["wz3p6_ee_tautau_ecm240"]

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
SAMPLE_PROCESSING_FRACTIONS = {
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    **{sample: 1.0 for sample in SIGNAL_SAMPLES},
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    **{sample: BACKGROUND_FRACTIONS["ww"] for sample in WW_SAMPLES},
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    **{sample: BACKGROUND_FRACTIONS["zz"] for sample in ZZ_SAMPLES},
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    **{sample: BACKGROUND_FRACTIONS["qq"] for sample in QQ_SAMPLES},
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    **{sample: BACKGROUND_FRACTIONS["tautau"] for sample in TAUTAU_SAMPLES},
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    **{sample: 1.0 for sample in ZH_OTHER_SAMPLES},
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
}

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
DEFAULT_TREE_NAME = "events"
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
DEFAULT_TREEMAKER_DIR = "output/h_hww_lvqq/treemaker/ecm240"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
DEFAULT_MODEL_DIR = "ml/models/xgboost_bdt_v6"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
DEFAULT_SCORE_BRANCH = "bdt_score"
