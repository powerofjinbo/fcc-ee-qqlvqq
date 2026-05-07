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
    return {"ww": 1.0, "zz": 1.0, "qq": 1.0, "tautau": 1.0, "zh_other": 1.0}


def _parse_signal_fraction() -> float:
    raw_value = os.environ.get("LVQQ_SIGNAL_FRACTION", "1.0")
    return _parse_fraction_value(raw_value, "LVQQ_SIGNAL_FRACTION")


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
        "zh_other": "LVQQ_ZH_OTHER_FRACTION",
    }.items():
        raw_value = os.environ.get(env_name)
        if raw_value is not None:
            fractions[key] = _parse_fraction_value(raw_value, env_name)

    return fractions


def _parse_sample_groups() -> tuple[str, ...]:
    raw_value = os.environ.get("LVQQ_SAMPLE_GROUPS", "").strip()
    if not raw_value or raw_value.lower() == "all":
        return ("all",)

    groups = tuple(group.strip().lower() for group in raw_value.split(",") if group.strip())
    allowed = {"signal", "ww", "zz", "qq", "tautau", "zh_other"}
    invalid = [group for group in groups if group not in allowed]
    if invalid:
        raise RuntimeError(
            "Invalid LVQQ_SAMPLE_GROUPS="
            f"{raw_value!r}; expected comma-separated groups from {sorted(allowed)} or 'all'."
        )
    return groups


def _parse_only_samples() -> tuple[str, ...]:
    raw_value = os.environ.get("LVQQ_ONLY_SAMPLES", "").strip()
    if not raw_value:
        return ()
    return tuple(sample.strip() for sample in raw_value.split(",") if sample.strip())

ML_SPECTATORS = [
    "weight",
    "njets",
]

ML_FEATURES = [
    # Lepton and missing-momentum handles.
    "lepton_p",
    "lepton_iso",
    "missingEnergy_p",
    "missingMass",
    "cosTheta_miss",
    # Visible and jet kinematics.
    "visibleEnergy",
    "jet0_p",
    "jet1_p",
    "jet2_p",
    "jet3_p",
    "min_jet_p",
    # Four-jet topology quality.
    "min_jet_nconst",
    "mean_jet_nconst",
    "sqrt_d23",
    "sqrt_d34",
    # Z/W/H reconstruction.
    "Zcand_dm",
    "Zcand_p",
    "Wstar_m",
    "deltaR_Wstar",
    "angle_Wstar_jj",
    "Wlep_m",
    "Hcand_m",
    "recoil_dmH",
    # Global event shape.
    "totalJetMass",
    "thrust",
    "angleLepMiss",
]

CUT_SCAN_BRANCHES = [
    "weight",
    *[f"n_leptons_p{threshold}" for threshold in range(2, 21)],
    "n_leptons_p25",
    "n_leptons_p30",
    "n_leptons_p10_p60",
    *[f"n_iso_leptons_p{threshold}" for threshold in range(2, 21)],
    "n_iso_leptons_p25",
    "n_iso_leptons_p30",
    "n_iso_leptons_p10_p60",
    "n_extra_iso_leptons_p20",
    "lepton_p",
    "lepton_iso",
    "missingEnergy_e",
    "missingEnergy_p",
    "missingMass",
    "cosTheta_miss",
    "visibleEnergy",
    "visibleEnergy_norm",
    "njets",
    "jet0_p",
    "jet1_p",
    "jet2_p",
    "jet3_p",
    "min_jet_p",
    "jet0_nconst",
    "jet1_nconst",
    "jet2_nconst",
    "jet3_nconst",
    "min_jet_nconst",
    "mean_jet_nconst",
    "Zcand_m",
    "Zcand_p",
    "Zcand_dm",
    "Wstar_m",
    "deltaR_Wstar",
    "angle_Wstar_jj",
    "recoil_m",
    "recoil_dmH",
    "Wlep_m",
    "Hcand_m",
    "deltaW_onShell",
    "d_23",
    "d_34",
    "sqrt_d23",
    "sqrt_d34",
    "totalJetMass",
    "thrust",
    "angleLepMiss",
    "pass_baseline",
]

SIGNAL_SAMPLES = [
    "wzp6_ee_qqH_HWW_ecm240",
    "wzp6_ee_bbH_HWW_ecm240",
    "wzp6_ee_ccH_HWW_ecm240",
    "wzp6_ee_ssH_HWW_ecm240",
]

SIGNAL_FRACTION = _parse_signal_fraction()
BACKGROUND_FRACTIONS = _parse_background_fractions()
OUTPUT_TAG = os.environ.get("LVQQ_OUTPUT_TAG", "").strip()

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

ACTIVE_SAMPLE_GROUPS = _parse_sample_groups()
ONLY_SAMPLES = _parse_only_samples()
if ACTIVE_SAMPLE_GROUPS != ("all",):
    selected = set()
    group_to_samples = {
        "signal": SIGNAL_SAMPLES,
        "ww": WW_SAMPLES,
        "zz": ZZ_SAMPLES,
        "qq": QQ_SAMPLES,
        "tautau": TAUTAU_SAMPLES,
        "zh_other": ZH_OTHER_SAMPLES,
    }
    for group in ACTIVE_SAMPLE_GROUPS:
        selected.update(group_to_samples[group])

    SIGNAL_SAMPLES = [sample for sample in SIGNAL_SAMPLES if sample in selected]
    WW_SAMPLES = [sample for sample in WW_SAMPLES if sample in selected]
    ZZ_SAMPLES = [sample for sample in ZZ_SAMPLES if sample in selected]
    QQ_SAMPLES = [sample for sample in QQ_SAMPLES if sample in selected]
    TAUTAU_SAMPLES = [sample for sample in TAUTAU_SAMPLES if sample in selected]
    ZH_OTHER_SAMPLES = [sample for sample in ZH_OTHER_SAMPLES if sample in selected]
    BACKGROUND_SAMPLES = [
        *WW_SAMPLES,
        *ZZ_SAMPLES,
        *QQ_SAMPLES,
        *TAUTAU_SAMPLES,
        *ZH_OTHER_SAMPLES,
    ]
if ONLY_SAMPLES:
    known_samples = {
        *SIGNAL_SAMPLES,
        *WW_SAMPLES,
        *ZZ_SAMPLES,
        *QQ_SAMPLES,
        *TAUTAU_SAMPLES,
        *ZH_OTHER_SAMPLES,
    }
    invalid = [sample for sample in ONLY_SAMPLES if sample not in known_samples]
    if invalid:
        raise RuntimeError(f"Invalid LVQQ_ONLY_SAMPLES entries after group filtering: {invalid}")

    selected = set(ONLY_SAMPLES)
    SIGNAL_SAMPLES = [sample for sample in SIGNAL_SAMPLES if sample in selected]
    WW_SAMPLES = [sample for sample in WW_SAMPLES if sample in selected]
    ZZ_SAMPLES = [sample for sample in ZZ_SAMPLES if sample in selected]
    QQ_SAMPLES = [sample for sample in QQ_SAMPLES if sample in selected]
    TAUTAU_SAMPLES = [sample for sample in TAUTAU_SAMPLES if sample in selected]
    ZH_OTHER_SAMPLES = [sample for sample in ZH_OTHER_SAMPLES if sample in selected]
    BACKGROUND_SAMPLES = [
        *WW_SAMPLES,
        *ZZ_SAMPLES,
        *QQ_SAMPLES,
        *TAUTAU_SAMPLES,
        *ZH_OTHER_SAMPLES,
    ]

SAMPLE_PROCESSING_FRACTIONS = {
    **{sample: SIGNAL_FRACTION for sample in SIGNAL_SAMPLES},
    **{sample: BACKGROUND_FRACTIONS["ww"] for sample in WW_SAMPLES},
    **{sample: BACKGROUND_FRACTIONS["zz"] for sample in ZZ_SAMPLES},
    **{sample: BACKGROUND_FRACTIONS["qq"] for sample in QQ_SAMPLES},
    **{sample: BACKGROUND_FRACTIONS["tautau"] for sample in TAUTAU_SAMPLES},
    **{sample: BACKGROUND_FRACTIONS["zh_other"] for sample in ZH_OTHER_SAMPLES},
}

DEFAULT_TREE_NAME = "events"
OUTPUT_STEM = "h_hww_lvqq" if not OUTPUT_TAG else f"h_hww_lvqq_{OUTPUT_TAG}"
MODEL_STEM = "xgboost_bdt_v6" if not OUTPUT_TAG else f"xgboost_bdt_v6_{OUTPUT_TAG}"
PLOTS_STEM = "plots_lvqq" if not OUTPUT_TAG else f"plots_lvqq_{OUTPUT_TAG}"

DEFAULT_HISTMAKER_DIR = f"output/{OUTPUT_STEM}/histmaker/ecm240"
DEFAULT_TREEMAKER_DIR = f"output/{OUTPUT_STEM}/treemaker/ecm240"
DEFAULT_SCANMAKER_DIR = f"output/{OUTPUT_STEM}/scanmaker/ecm240"
DEFAULT_BDT_SCORED_DIR = f"output/{OUTPUT_STEM}/bdt_scored/ecm240"
DEFAULT_MODEL_DIR = f"ml/models/{MODEL_STEM}"
DEFAULT_PLOTS_DIR = PLOTS_STEM
DEFAULT_SCORE_BRANCH = "bdt_score"
