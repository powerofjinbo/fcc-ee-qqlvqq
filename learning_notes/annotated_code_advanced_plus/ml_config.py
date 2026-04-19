# ML/physics contract for the lvqq chain:
# cross sections, sample maps, cutflow fractions, and BDT feature contracts.
#
# This file is the "single source of truth" for reproducibility:
# - every module imports the same signal/background/sample naming,
# - all fractions are resolved consistently via env overrides,
# - features passed to ML are explicitly curated and annotated with exclusions.
# The executable logic is unchanged; only explanatory comments are enriched.

"""Shared configuration for the lvqq XGBoost BDT workflow."""

# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import os


# [Workflow] ml_config.py function _parse_fraction_value: modularize one operation for deterministic pipeline control.
def _parse_fraction_value(raw_value: str, env_name: str) -> float:
# [Context] Supporting line for the active lvqq analysis stage.
    try:
# [Context] Supporting line for the active lvqq analysis stage.
        fraction = float(raw_value)
# [Context] Supporting line for the active lvqq analysis stage.
    except ValueError as exc:
# [Context] Supporting line for the active lvqq analysis stage.
        raise RuntimeError(
# [Context] Supporting line for the active lvqq analysis stage.
            f"Invalid {env_name}={raw_value!r}; expected a float in (0, 1]."
# [Context] Supporting line for the active lvqq analysis stage.
        ) from exc
# [Context] Supporting line for the active lvqq analysis stage.
    if not (0.0 < fraction <= 1.0):
# [Context] Supporting line for the active lvqq analysis stage.
        raise RuntimeError(
# [Context] Supporting line for the active lvqq analysis stage.
            f"Invalid {env_name}={raw_value!r}; expected a float in (0, 1]."
# [Context] Supporting line for the active lvqq analysis stage.
        )
# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return fraction


# [Workflow] ml_config.py function _default_background_fractions: modularize one operation for deterministic pipeline control.
def _default_background_fractions() -> dict[str, float]:
# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return {"ww": 1.0, "zz": 1.0, "qq": 1.0, "tautau": 1.0}


# [Workflow] ml_config.py function _parse_background_fractions: modularize one operation for deterministic pipeline control.
def _parse_background_fractions() -> dict[str, float]:
# [Context] Supporting line for the active lvqq analysis stage.
    fractions = _default_background_fractions()

# [Context] Supporting line for the active lvqq analysis stage.
    global_override = os.environ.get("LVQQ_BACKGROUND_FRACTION")
# [Context] Supporting line for the active lvqq analysis stage.
    if global_override is not None:
# [Context] Supporting line for the active lvqq analysis stage.
        parsed = _parse_fraction_value(global_override, "LVQQ_BACKGROUND_FRACTION")
# [Context] Supporting line for the active lvqq analysis stage.
        fractions = {key: parsed for key in fractions}

# [Context] Supporting line for the active lvqq analysis stage.
    for key, env_name in {
# [Context] Supporting line for the active lvqq analysis stage.
        "ww": "LVQQ_WW_FRACTION",
# [Context] Supporting line for the active lvqq analysis stage.
        "zz": "LVQQ_ZZ_FRACTION",
# [Context] Supporting line for the active lvqq analysis stage.
        "qq": "LVQQ_QQ_FRACTION",
# [Context] Supporting line for the active lvqq analysis stage.
        "tautau": "LVQQ_TAUTAU_FRACTION",
# [Context] Supporting line for the active lvqq analysis stage.
    }.items():
# [Context] Supporting line for the active lvqq analysis stage.
        raw_value = os.environ.get(env_name)
# [Context] Supporting line for the active lvqq analysis stage.
        if raw_value is not None:
# [Context] Supporting line for the active lvqq analysis stage.
            fractions[key] = _parse_fraction_value(raw_value, env_name)

# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return fractions

# [Workflow] Configuration binding; this line defines a stable contract across modules.
ML_SPECTATORS = [
# [Context] Supporting line for the active lvqq analysis stage.
    "weight",
# [Context] Supporting line for the active lvqq analysis stage.
    "njets",
# [Context] Supporting line for the active lvqq analysis stage.
]

# [Physics/ML] Columns explicitly used by the BDT as learning features.
# "spectators" are written for bookkeeping but are not inputs to tree split decisions.
ML_FEATURES = [
# [Physics] Feature-level intent:
# - kinematics: jet/lepton momentum and directions,
# - topology: resonance consistency variables (Z/W/H candidates),
# - global event-shape handles soft-radiation / reconstruction quality effects.
    "lepton_p",
# [Context] Supporting line for the active lvqq analysis stage.
    "lepton_iso",
    # "missingEnergy_e",  # redundant with missingEnergy_p (massless neutrino)
# [Context] Supporting line for the active lvqq analysis stage.
    "missingEnergy_p",
# [Context] Supporting line for the active lvqq analysis stage.
    "missingMass",
# [Context] Supporting line for the active lvqq analysis stage.
    "cosTheta_miss",
# [Context] Supporting line for the active lvqq analysis stage.
    "visibleEnergy",
    # "visibleEnergy_norm",  # redundant: = visibleEnergy / 240 (constant)
# [Context] Supporting line for the active lvqq analysis stage.
    "jet0_p",
# [Context] Supporting line for the active lvqq analysis stage.
    "jet1_p",
# [Context] Supporting line for the active lvqq analysis stage.
    "jet2_p",
# [Context] Supporting line for the active lvqq analysis stage.
    "jet3_p",
    # "jet_p_sum",  # redundant: = visibleEnergy (same particle collection)
    # "Zcand_m",  # redundant with Zcand_dm (= |Zcand_m - 91.19|)
# [Context] Supporting line for the active lvqq analysis stage.
    "Zcand_dm",
# [Context] Supporting line for the active lvqq analysis stage.
    "Wstar_m",
    # "deltaZ",  # redundant: = Zcand_dm (numerically identical)
    # "recoil_m",  # redundant with recoil_dmH (= |recoil_m - 125|)
# [Context] Supporting line for the active lvqq analysis stage.
    "recoil_dmH",
# [Context] Supporting line for the active lvqq analysis stage.
    "Wlep_m",
# [Context] Supporting line for the active lvqq analysis stage.
    "Hcand_m",
# [Context] Supporting line for the active lvqq analysis stage.
    "totalJetMass",
# [Context] Supporting line for the active lvqq analysis stage.
    "thrust",
# [Context] Supporting line for the active lvqq analysis stage.
    "angleLepMiss",
# [Context] Supporting line for the active lvqq analysis stage.
    "d_23",
# [Context] Supporting line for the active lvqq analysis stage.
    "d_34",
# [Context] Supporting line for the active lvqq analysis stage.
]

# [Workflow] Configuration binding; this line defines a stable contract across modules.
SIGNAL_SAMPLES = [
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_qqH_HWW_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_bbH_HWW_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_ccH_HWW_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_ssH_HWW_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
]

# [Workflow] Configuration binding; this line defines a stable contract across modules.
BACKGROUND_FRACTIONS = _parse_background_fractions()

# [Workflow] Configuration binding; this line defines a stable contract across modules.
ZH_OTHER_SAMPLES = [
    # Hadronic-Z irreducible ZH backgrounds included in the lvqq fit.
    # The original setup only kept the qqH subset; the full hadronic-Z set
    # is needed for a complete background model.
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_qqH_Hbb_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_qqH_Htautau_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_qqH_Hgg_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_qqH_Hcc_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_qqH_HZZ_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_bbH_Hbb_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_bbH_Htautau_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_bbH_Hgg_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_bbH_Hcc_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_bbH_HZZ_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_ccH_Hbb_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_ccH_Htautau_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_ccH_Hgg_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_ccH_Hcc_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_ccH_HZZ_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_ssH_Hbb_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_ssH_Htautau_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_ssH_Hgg_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_ssH_Hcc_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_ssH_HZZ_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
]

# [Workflow] Configuration binding; this line defines a stable contract across modules.
LARGE_BACKGROUND_SAMPLES = [
    # Diboson
# [Context] Supporting line for the active lvqq analysis stage.
    "p8_ee_WW_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "p8_ee_ZZ_ecm240",
    # 2-fermion (qq, tautau)
# [Context] Supporting line for the active lvqq analysis stage.
    "wz3p6_ee_uu_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wz3p6_ee_dd_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wz3p6_ee_cc_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wz3p6_ee_ss_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wz3p6_ee_bb_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wz3p6_ee_tautau_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
]

# [Workflow] Configuration binding; this line defines a stable contract across modules.
FULL_BACKGROUND_SAMPLES = [
# [Context] Supporting line for the active lvqq analysis stage.
    *LARGE_BACKGROUND_SAMPLES,
# [Context] Supporting line for the active lvqq analysis stage.
    *ZH_OTHER_SAMPLES,
# [Context] Supporting line for the active lvqq analysis stage.
]

# [Workflow] Configuration binding; this line defines a stable contract across modules.
BACKGROUND_SAMPLES = FULL_BACKGROUND_SAMPLES

# [Workflow] Configuration binding; this line defines a stable contract across modules.
WW_SAMPLES = ["p8_ee_WW_ecm240"]
# [Workflow] Configuration binding; this line defines a stable contract across modules.
ZZ_SAMPLES = ["p8_ee_ZZ_ecm240"]
# [Workflow] Configuration binding; this line defines a stable contract across modules.
QQ_SAMPLES = [
# [Context] Supporting line for the active lvqq analysis stage.
    "wz3p6_ee_uu_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wz3p6_ee_dd_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wz3p6_ee_cc_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wz3p6_ee_ss_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
    "wz3p6_ee_bb_ecm240",
# [Context] Supporting line for the active lvqq analysis stage.
]
# [Workflow] Configuration binding; this line defines a stable contract across modules.
TAUTAU_SAMPLES = ["wz3p6_ee_tautau_ecm240"]

# [Workflow] Configuration binding; this line defines a stable contract across modules.
SAMPLE_PROCESSING_FRACTIONS = {
# [Context] Supporting line for the active lvqq analysis stage.
    **{sample: 1.0 for sample in SIGNAL_SAMPLES},
# [Context] Supporting line for the active lvqq analysis stage.
    **{sample: BACKGROUND_FRACTIONS["ww"] for sample in WW_SAMPLES},
# [Context] Supporting line for the active lvqq analysis stage.
    **{sample: BACKGROUND_FRACTIONS["zz"] for sample in ZZ_SAMPLES},
# [Context] Supporting line for the active lvqq analysis stage.
    **{sample: BACKGROUND_FRACTIONS["qq"] for sample in QQ_SAMPLES},
# [Context] Supporting line for the active lvqq analysis stage.
    **{sample: BACKGROUND_FRACTIONS["tautau"] for sample in TAUTAU_SAMPLES},
# [Context] Supporting line for the active lvqq analysis stage.
    **{sample: 1.0 for sample in ZH_OTHER_SAMPLES},
# [Context] Supporting line for the active lvqq analysis stage.
}

# [Workflow] Configuration binding; this line defines a stable contract across modules.
DEFAULT_TREE_NAME = "events"
# [Workflow] Configuration binding; this line defines a stable contract across modules.
DEFAULT_TREEMAKER_DIR = "output/h_hww_lvqq/treemaker/ecm240"
# [Workflow] Configuration binding; this line defines a stable contract across modules.
DEFAULT_MODEL_DIR = "ml/models/xgboost_bdt_v6"
# [Workflow] Configuration binding; this line defines a stable contract across modules.
DEFAULT_SCORE_BRANCH = "bdt_score"
