"""Shared configuration for the lvqq XGBoost BDT workflow."""

import os

# 让输入的fraction范围在0-1之间
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

# 设定默认fraction的值
def _default_background_fractions() -> dict[str, float]:
    return {"ww": 1.0, "zz": 1.0, "qq": 1.0, "tautau": 1.0}

# 精细化独立覆盖
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

# ML中的辅助信息，并不参与ML模型学习过程
ML_SPECTATORS = [
    "weight",
    "njets",
]

# ML模型学习的所有特征
ML_FEATURES = [
    "lepton_p",            # isolated lepton的动量，来自在壳W boson的衰变
    "lepton_iso",          # isolated lepton的隔离度，是lepton周围一定范围内其他粒子的动量总和
    "missingEnergy_p",     # missing momentum的动量，即中微子动量
    "missingMass",         # 校验是否一个中微子，因为一个中微子的质量应该是约为0，用m = sqrt(E**2 - p**2)来算
    "cosTheta_miss",       # 中微子方向与对撞机z轴夹角的余弦值，如果缺失能量的方向太靠近束流轴，可能是因为某个粒子跑丢了导致的‘假账’，而不是产生了真正的中微子
    "visibleEnergy",       # 所有能量的特征，接近240的是背景，反之是信号（因为中微子带走了能量）
    "jet0_p",              # 动量最大的那个喷注
    "jet1_p",              # 动量第二大的喷注
    "jet2_p",              # 动量第三大的喷注
    "jet3_p",              # 动量最小的那个喷注
    "Zcand_dm",            # 重建出的Z boson的mass与其实际物理质量91.19之间的绝对差值，重建是由两个qq重建的，因为在壳，正常来说这个值会趋于0
    "Wstar_m",             # 由qq重建出离壳的W boson，正常信号在20-40GeV
    "recoil_dmH",          # 通过算Z boson反冲质量与 Higgs 实际质量125GeV之间的绝对差值，m**2 = (240 - E_z)**2 - (p_z)**2
    "Wlep_m",              # lepton + 中微子重建出来的W boson质量，这个W是on shell的，分布应该在80GeV左右
    "Hcand_m",             # 它是将重建出的两个W boson（即 Wlep_m 和 Wstar_m）的四动量直接相加得到的不变质量。
    "totalJetMass",        # 4个jets合成的总质量，对于信号来说，这个4 jets 理论上应该接近（Z质量 + W质量）
    "thrust",              # 所有粒子动量分布的各向异性（各向异性的程度），所有粒子动量分布的各向异性（各向异性的程度）
    "angleLepMiss",        # isolated lepton 与中微子之间的夹角。
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
