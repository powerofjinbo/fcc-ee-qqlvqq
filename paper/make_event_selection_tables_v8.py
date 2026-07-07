#!/usr/bin/env python3
"""Draw a paper-style event-selection and cutflow summary figure."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import uproot

REPO_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_DIR))

from ml_config import SIGNAL_SAMPLES, ZH_OTHER_SAMPLES  # noqa: E402


TAG = "cut_sig100_bkg100_v10_split_local"
INPUT_DIR = REPO_DIR / f"output/h_hww_lvqq_{TAG}/histmaker/ecm240"
OUT_DIR = REPO_DIR / "paper/figs"

CUT_LABELS = [
    "All",
    "1 lep",
    "Iso",
    "Veto",
    "MET",
    "4 jets",
    "Nconst",
    "Z win",
    r"$p_Z$",
]

SELECTION_ROWS = [
    ("1", r"$\geq 1$ lepton with $10 < p_\ell < 60$ GeV", "Multi-jet, lepton tails"),
    ("2", r"Selected lepton isolation $I_\ell < 0.20$", "Non-prompt leptons"),
    ("3", r"Veto additional leptons with $p > 20$ GeV", r"$ZZ\to\ell\ell qq$, multi-lepton"),
    ("4", r"$10 < E_{\rm miss} < 55$ GeV", "Fully hadronic and high-MET tails"),
    ("5", r"Exactly 4 jets and $\sqrt{d_{34}} > 14$ GeV", "Low-multiplicity / continuum"),
    ("6", r"$\min(N_{\rm const}^{\rm jet}) > 8$", "Sparse fake jets"),
    ("7", r"$85 < m_{Z,\rm cand} < 95$ GeV", "Combinatorial jet pairing"),
    ("8", r"$40 < p_{Z,\rm cand} < 60$ GeV", "Non-$ZH$ recoil kinematics"),
]

GROUPS = [
    ("Signal", list(SIGNAL_SAMPLES)),
    (r"$WW$", ["p8_ee_WW_ecm240"]),
    (r"$ZZ$", ["p8_ee_ZZ_ecm240"]),
    (r"$q\bar{q}$", [
        "wz3p6_ee_uu_ecm240",
        "wz3p6_ee_dd_ecm240",
        "wz3p6_ee_cc_ecm240",
        "wz3p6_ee_ss_ecm240",
        "wz3p6_ee_bb_ecm240",
    ]),
    (r"$\tau\tau$", ["wz3p6_ee_tautau_ecm240"]),
    ("ZH(other)", list(ZH_OTHER_SAMPLES)),
]


def read_cutflow(sample: str, ncuts: int) -> list[float]:
    path = INPUT_DIR / f"{sample}.root"
    if not path.exists():
        raise FileNotFoundError(path)
    with uproot.open(path) as handle:
        values = handle["cutFlow"].to_numpy(flow=False)[0]
    if len(values) > ncuts and abs(float(values[ncuts])) > 1e-9:
        raise RuntimeError(
            f"{path} has a nonzero cutFlow bin beyond the configured 8-cut "
            "sequence. Rerun histmaker before regenerating this table."
        )
    if abs(float(values[ncuts - 1])) < 1e-9 and abs(float(values[ncuts - 2])) > 1e-9:
        raise RuntimeError(
            f"{path} cutFlow drops to zero exactly at the last of the {ncuts} labels in "
            "this frozen v8/v9/v10 table script (e.g. a v_fable tag, which has "
            "no Z-mass window). Use a table script matching "
            "ml_config.CUTFLOW_STAGES instead."
        )
    return [float(v) for v in values[:ncuts]]


def grouped_yields() -> dict[str, list[float]]:
    ncuts = len(CUT_LABELS)
    output: dict[str, list[float]] = {}
    for label, samples in GROUPS:
        total = [0.0] * ncuts
        for sample in samples:
            values = read_cutflow(sample, ncuts)
            total = [a + b for a, b in zip(total, values)]
        output[label] = total
    return output


def format_yield(value: float) -> str:
    if abs(value) < 0.5:
        return "0"
    if abs(value) < 1000:
        return f"{value:.0f}"
    exponent = int(math.floor(math.log10(abs(value))))
    mantissa = value / (10 ** exponent)
    if mantissa >= 9.95:
        mantissa /= 10.0
        exponent += 1
    return rf"${mantissa:.2g}\!\cdot\!10^{{{exponent}}}$"


def format_eff(value: float) -> str:
    if math.isnan(value):
        return "-"
    if abs(value - 100.0) < 0.05:
        return "100"
    if value >= 10:
        return f"{value:.1f}"
    if value >= 1:
        return f"{value:.2f}"
    if value >= 0.01:
        return f"{value:.3f}"
    if value > 0:
        return f"{value:.4f}"
    return "0"


def draw_selection_table(ax) -> None:
    left, right = 0.18, 0.82
    x_cut, x_req, x_target = 0.215, 0.285, 0.61
    y_title, y_top, y_header, y_mid, y_bottom = 0.975, 0.94, 0.907, 0.875, 0.585

    ax.text(0.5, y_title, "Table 2: Event selection criteria.",
            ha="center", va="top", fontsize=18)
    ax.plot([left, right], [y_top, y_top], color="black", lw=1.4)
    ax.plot([left, right], [y_mid, y_mid], color="black", lw=0.9)
    ax.plot([left, right], [y_bottom, y_bottom], color="black", lw=1.4)

    ax.text(x_cut, y_header, "Cut", ha="center", va="center", fontsize=15)
    ax.text(x_req, y_header, "Requirement", ha="left", va="center", fontsize=15)
    ax.text(x_target, y_header, "Targeted background", ha="left", va="center", fontsize=15)

    row_step = (y_mid - y_bottom) / len(SELECTION_ROWS)
    for i, (cut, req, target) in enumerate(SELECTION_ROWS):
        y = y_mid - (i + 0.65) * row_step
        ax.text(x_cut, y, cut, ha="center", va="center", fontsize=14)
        ax.text(x_req, y, req, ha="left", va="center", fontsize=14)
        ax.text(x_target, y, target, ha="left", va="center", fontsize=14)


def draw_cutflow_table(ax, yields: dict[str, list[float]]) -> None:
    left, right = 0.022, 0.978
    y_title, y_top, y_group, y_sub, y_header_line = 0.51, 0.475, 0.445, 0.407, 0.378
    y_bottom = 0.055

    ax.text(
        0.5,
        y_title,
        r"Table 3: Cutflow: expected yields and cumulative efficiencies [%] "
        r"at $\mathcal{L}=10.8\,\mathrm{ab}^{-1}$.",
        ha="center",
        va="center",
        fontsize=17,
    )

    ax.plot([left, right], [y_top, y_top], color="black", lw=1.4)
    ax.plot([left, right], [y_header_line, y_header_line], color="black", lw=0.9)
    ax.plot([left, right], [y_bottom, y_bottom], color="black", lw=1.4)

    cut_w = 0.095
    group_w = (right - left - cut_w) / len(GROUPS)
    y_line_group = y_group - 0.027
    for i, (group, _) in enumerate(GROUPS):
        g_left = left + cut_w + i * group_w
        g_right = g_left + group_w
        g_center = (g_left + g_right) / 2
        ax.text(g_center, y_group, group, ha="center", va="center", fontsize=14)
        ax.plot([g_left + 0.008, g_right - 0.008], [y_line_group, y_line_group], color="black", lw=0.6)
        ax.text(g_left + group_w * 0.34, y_sub, "Yield", ha="center", va="center", fontsize=13)
        ax.text(g_left + group_w * 0.80, y_sub, "[%]", ha="center", va="center", fontsize=13)

    ax.text(left + cut_w * 0.38, y_sub, "Cut", ha="center", va="center", fontsize=13)

    row_area_top = y_header_line - 0.025
    row_step = (row_area_top - y_bottom) / len(CUT_LABELS)
    for row_idx, cut_label in enumerate(CUT_LABELS):
        y = row_area_top - row_idx * row_step
        ax.text(left + cut_w * 0.28, y, cut_label, ha="left", va="center", fontsize=12.5)
        for i, (group, _) in enumerate(GROUPS):
            vals = yields[group]
            value = vals[row_idx]
            eff = 100.0 * value / vals[0] if vals[0] else float("nan")
            g_left = left + cut_w + i * group_w
            ax.text(g_left + group_w * 0.34, y, format_yield(value),
                    ha="center", va="center", fontsize=11.5)
            ax.text(g_left + group_w * 0.80, y, format_eff(eff),
                    ha="center", va="center", fontsize=11.5)

    ax.text(
        0.5,
        0.022,
        r"Nominal baseline ends at Cut8. $m_{H,\rm cand}$ and recoil mass are kept as diagnostic/BDT-shape variables, not hard filters.",
        ha="center",
        va="center",
        fontsize=10.5,
        color="#333333",
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", default=TAG)
    parser.add_argument("--version", default="v10")
    args = parser.parse_args(argv)

    global INPUT_DIR
    INPUT_DIR = REPO_DIR / f"output/h_hww_lvqq_{args.tag}/histmaker/ecm240"

    if not INPUT_DIR.exists():
        raise SystemExit(f"Missing histmaker directory: {INPUT_DIR}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    yields = grouped_yields()

    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["DejaVu Serif", "Times New Roman", "Times"],
        "mathtext.fontset": "dejavuserif",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })

    fig, ax = plt.subplots(figsize=(16.5, 10.5))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    draw_selection_table(ax)
    draw_cutflow_table(ax, yields)

    pdf = OUT_DIR / f"event_selection_tables_{args.version}.pdf"
    png = OUT_DIR / f"event_selection_tables_{args.version}.png"
    fig.savefig(pdf, bbox_inches="tight")
    fig.savefig(png, dpi=220, bbox_inches="tight")
    plt.close(fig)

    print(f"Using tag: {args.tag}")
    print(f"Wrote {pdf}")
    print(f"Wrote {png}")


if __name__ == "__main__":
    main()
