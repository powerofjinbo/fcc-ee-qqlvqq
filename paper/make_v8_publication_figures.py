#!/usr/bin/env python3
"""Generate publication-style figures/tables for the v8 qqlvqq note.

The script intentionally reads the frozen v8 outputs instead of rerunning the
full FCCAnalyses workflow.  It regenerates only paper-level visual products
from the already produced out-of-fold BDT scores and fit summary.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# Keep the /home/submit path instead of resolving the /work symlink.  The
# managed sandbox allows writes under /home/submit/jinboz1, while the resolved
# /work path can be read-only from Codex's point of view.
REPO = Path("/home/submit/jinboz1/work/Z(qq)WW(lvqq)")
TAG = "cut_sig100_bkg100_v8_split_local"
MODEL_DIR = REPO / "ml" / "models" / f"xgboost_bdt_v6_{TAG}"
NOTE_DIR = REPO / "plots_lvqq_cut_sig100_bkg100_v8_split_local" / "FCC_ee_HWW_qqlvqq_polished_source (1)"
FIG_DIR = NOTE_DIR / "figs"


COLORS = {
    "qq": "#4C78A8",
    "WW": "#F58518",
    "ZZ": "#54A24B",
    "ZH_other": "#B279A2",
    "Signal": "#D62728",
}


FEATURE_LABELS = {
    "angleLepMiss": r"$\angle(\ell,\vec{p}_{\rm miss})$",
    "lepton_iso": r"$I_\ell$",
    "cosTheta_miss": r"$|\cos\theta_{\rm miss}|$",
    "missingEnergy_p": r"$|\vec{p}_{\rm miss}|$",
    "missingMass": r"$m_{\rm miss}$",
    "totalJetMass": r"$m_{4j}$",
    "Wstar_m": r"$m_{W^\ast\to jj}$",
    "lepton_p": r"$p_\ell$",
    "Wlep_m": r"$m_{\ell\nu}$",
    "visibleEnergy": r"$E_{\rm vis}$",
    "recoil_dmH": r"$|m_{\rm recoil}-m_H|$",
    "Zcand_p": r"$p_{Z,\rm cand}$",
    "sqrt_d34": r"$\sqrt{d_{34}}$",
    "sqrt_d23": r"$\sqrt{d_{23}}$",
    "min_jet_p": r"$\min p_{\rm jet}$",
    "angle_Wstar_jj": r"$\angle(W^\ast,jj)$",
    "Hcand_m": r"$m_{H,\rm cand}$",
    "thrust": "thrust",
    "deltaR_Wstar": r"$\Delta R(W^\ast)$",
    "jet0_p": r"$p_{j_1}$",
    "jet1_p": r"$p_{j_2}$",
    "jet2_p": r"$p_{j_3}$",
    "jet3_p": r"$p_{j_4}$",
    "Zcand_dm": r"$|m_{Z,\rm cand}-m_Z|$",
    "min_jet_nconst": r"$\min N_{\rm const}^{\rm jet}$",
    "mean_jet_nconst": r"$\langle N_{\rm const}^{\rm jet}\rangle$",
}


def configure_style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 140,
            "savefig.dpi": 300,
            "font.family": "serif",
            "font.serif": ["DejaVu Serif", "Times New Roman", "Times"],
            "mathtext.fontset": "dejavuserif",
            "axes.labelsize": 11,
            "axes.titlesize": 12,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "axes.linewidth": 0.9,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.top": True,
            "ytick.right": True,
        }
    )


def group_sample(sample_name: str, y_true: int) -> str:
    if int(y_true) == 1:
        return "Signal"
    if sample_name.startswith("p8_ee_WW"):
        return "WW"
    if sample_name.startswith("p8_ee_ZZ"):
        return "ZZ"
    if sample_name.startswith("wz3p6_ee_"):
        return "qq"
    return "ZH_other"


def save_both(fig: plt.Figure, stem: str) -> None:
    for ext in ("pdf", "png"):
        fig.savefig(FIG_DIR / f"{stem}.{ext}", bbox_inches="tight")


def make_feature_importance() -> None:
    df = pd.read_csv(MODEL_DIR / "feature_importance.csv", index_col=0)
    df = df.rename(columns={df.columns[0]: "importance"}).sort_values("importance", ascending=False)
    df["importance_pct"] = 100.0 * df["importance"] / df["importance"].sum()
    top = df.iloc[::-1]

    labels = [FEATURE_LABELS.get(name, name.replace("_", r"\_")) for name in top.index]
    y = np.arange(len(top))

    fig, ax = plt.subplots(figsize=(7.0, 8.4))
    ax.barh(y, top["importance_pct"], color="#2F6F73", edgecolor="black", linewidth=0.35)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Relative gain importance [%]")
    ax.set_title("BDT feature importance")
    ax.grid(axis="x", color="0.86", linewidth=0.7)
    ax.set_axisbelow(True)
    ax.text(
        0.99,
        0.03,
        "FCC-ee IDEA fast simulation\n$\\sqrt{s}=240$ GeV, $\\mathcal{L}=10.8\\,\\mathrm{ab}^{-1}$",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=8.5,
    )
    fig.tight_layout()
    save_both(fig, "feature_importance_pub")
    plt.close(fig)


def normalized_hist(values: pd.Series, weights: pd.Series, bins: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    counts, _ = np.histogram(values, bins=bins, weights=weights)
    err2, _ = np.histogram(values, bins=bins, weights=weights**2)
    width = np.diff(bins)
    total = counts.sum()
    if total <= 0:
        return counts, np.sqrt(err2)
    return counts / (total * width), np.sqrt(err2) / (total * width)


def make_bdt_score_distributions() -> None:
    """Draw normalized BDT score shapes used to validate final templates."""

    bins = np.linspace(0.0, 1.0, 26)
    centers = 0.5 * (bins[:-1] + bins[1:])
    oof = pd.read_csv(MODEL_DIR / "kfold_scores.csv")
    test = pd.read_csv(MODEL_DIR / "test_scores.csv")

    fig, ax = plt.subplots(figsize=(6.8, 4.8))

    styles = {
        1: {"label": "Signal", "color": "#D62728"},
        0: {"label": "Background", "color": "#3B6AA0"},
    }

    for y_true, style in styles.items():
        sub = oof[oof["y_true"] == y_true]
        h, _ = normalized_hist(sub["bdt_score"], sub["phys_weight"], bins)
        ax.stairs(
            h,
            bins,
            color=style["color"],
            linewidth=2.0,
            label=f"{style['label']} out-of-fold",
            fill=False,
        )
        ax.fill_between(
            bins,
            np.r_[h, h[-1]],
            step="post",
            color=style["color"],
            alpha=0.14,
            linewidth=0,
        )

        tsub = test[test["y_true"] == y_true]
        th, te = normalized_hist(tsub["bdt_score"], tsub["phys_weight"], bins)
        ax.errorbar(
            centers,
            th,
            yerr=te,
            fmt="o",
            markersize=3.4,
            color=style["color"],
            markerfacecolor="white",
            markeredgewidth=1.0,
            linewidth=0.8,
            capsize=1.5,
            label=f"{style['label']} held-out test",
        )

    ax.set_yscale("log")
    ax.set_xlim(0, 1)
    ax.set_ylim(3e-2, 40)
    ax.set_xlabel("BDT score")
    ax.set_ylabel("Normalised density")
    ax.set_title("BDT score shape validation")
    ax.grid(axis="y", which="major", color="0.88", linewidth=0.7)
    ax.legend(loc="upper center", ncol=2, frameon=False, fontsize=8.2)
    fig.tight_layout()
    save_both(fig, "bdt_score_distributions_pub")
    plt.close(fig)


def make_fit_templates() -> None:
    scores = pd.read_csv(MODEL_DIR / "kfold_scores.csv")
    scores["group"] = [group_sample(s, y) for s, y in zip(scores["sample_name"], scores["y_true"])]

    bins = np.linspace(0.0, 1.0, 21)
    centers = 0.5 * (bins[:-1] + bins[1:])
    widths = np.diff(bins)
    stack_order = ["qq", "WW", "ZZ", "ZH_other"]

    hist = {}
    err2 = {}
    for group in stack_order + ["Signal"]:
        sub = scores[scores["group"] == group]
        h, _ = np.histogram(sub["bdt_score"], bins=bins, weights=sub["phys_weight"])
        e2, _ = np.histogram(sub["bdt_score"], bins=bins, weights=sub["phys_weight"] ** 2)
        hist[group] = h
        err2[group] = e2

    bkg_total = sum(hist[g] for g in stack_order)
    sig = hist["Signal"]
    purity = np.divide(sig, sig + bkg_total, out=np.zeros_like(sig), where=(sig + bkg_total) > 0)

    fig, (ax, rax) = plt.subplots(
        2,
        1,
        figsize=(7.0, 5.4),
        sharex=True,
        gridspec_kw={"height_ratios": [3.1, 1.0], "hspace": 0.05},
    )

    bottom = np.zeros_like(centers)
    for group in stack_order:
        ax.bar(
            centers,
            hist[group],
            width=widths,
            bottom=bottom,
            color=COLORS[group],
            edgecolor="black",
            linewidth=0.35,
            label={"qq": r"$q\bar{q}$", "WW": r"$WW$", "ZZ": r"$ZZ$", "ZH_other": r"$ZH({\rm other})$"}[group],
        )
        bottom += hist[group]

    ax.step(bins, np.r_[sig, sig[-1]], where="post", color=COLORS["Signal"], linewidth=2.0, label=r"$ZH, H\to WW^\ast$")
    ax.errorbar(
        centers,
        bkg_total,
        yerr=np.sqrt(sum(err2[g] for g in stack_order)),
        fmt="none",
        ecolor="black",
        elinewidth=0.8,
        capsize=1.5,
        label="MC stat. unc.",
    )

    ax.set_yscale("log")
    ax.set_ylim(0.5, max((bkg_total + sig).max() * 7.5, 10.0))
    ax.set_ylabel("Expected events / 0.05")
    ax.grid(axis="y", which="major", color="0.88", linewidth=0.7)
    ax.legend(loc="upper left", ncol=2, frameon=False)
    ax.text(
        0.98,
        0.95,
        "$\\sqrt{s}=240$ GeV, $\\mathcal{L}=10.8\\,\\mathrm{ab}^{-1}$\n"
        "$\\mu=1\\pm0.00941$",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=9,
    )

    rax.bar(centers, purity, width=widths, color="#666666", edgecolor="black", linewidth=0.25)
    rax.set_ylim(0, 1.05)
    rax.set_ylabel(r"$S/(S+B)$")
    rax.set_xlabel("BDT score")
    rax.grid(axis="y", color="0.88", linewidth=0.7)
    rax.set_yticks([0, 0.5, 1.0])
    rax.set_xlim(0, 1)

    fig.tight_layout()
    save_both(fig, "fit_templates_pub")
    plt.close(fig)


def make_overall_cutflow() -> None:
    """Draw the v8 cutflow with explicit cut-stage labels on the x axis."""

    cut_labels = [
        "All events",
        r"Cut 1: $\geq1\,\ell$" + "\n" + r"$10<p_\ell<60$",
        r"Cut 2: iso." + "\n" + r"$I_\ell<0.20$",
        r"Cut 3: veto" + "\n" + r"extra $\ell$",
        r"Cut 4: $E_{\rm miss}$" + "\n" + r"$10<E_{\rm miss}<55$",
        r"Cut 5: 4 jets" + "\n" + r"$\sqrt{d_{34}}>14$",
        r"Cut 6: jets" + "\n" + r"$\min N_{\rm const}>8$",
        r"Cut 7: $Z$ mass" + "\n" + r"$85<m_Z<95$",
        r"Cut 8: $Z$ recoil" + "\n" + r"$40<p_Z<60$",
    ]

    x = np.arange(len(cut_labels))
    signal = np.array([314722.8, 129895.2, 106384.5, 98406.2, 61634.2, 48421.1, 38408.6, 24466.2, 16680.8])
    ww = np.array([177535800, 35356620, 29585829, 24443720, 987530, 145064, 22133, 7608, 2481], dtype=float)
    zz = np.array([14677092, 3940124, 2727421, 704601, 161893, 46769, 21703, 12319, 2469], dtype=float)
    qq = np.array([594113065, 40727412, 2316084, 2313401, 371048, 56299, 18405, 7156, 1984], dtype=float)
    tautau = np.array([50416483, 17490231, 16962811, 15118177, 529600, 217, 0, 0, 0], dtype=float)
    zh_other = np.array(
        [
            38569 + 42575 + 120571 + 92362 + 857628,
            8573 + 6013 + 7284 + 42584 + 231776,
            5432 + 204 + 603 + 37636 + 14142,
            3121 + 204 + 602 + 34908 + 14127,
            908 + 128 + 338 + 9419 + 9522,
            781 + 107 + 309 + 2028 + 8182,
            554 + 98 + 297 + 239 + 7451,
            327 + 40 + 137 + 65 + 4313,
            154 + 15 + 43 + 23 + 2300,
        ],
        dtype=float,
    )

    backgrounds = [
        (tautau, r"$\tau\tau$", "#9E9E9E"),
        (zh_other, r"$ZH({\rm other})$", "#5ADBE1"),
        (qq, r"$q\bar q$", "#00A72A"),
        (zz, r"$ZZ$", "#3A95FF"),
        (ww, r"$WW$", "#FF9900"),
    ]

    fig, ax = plt.subplots(figsize=(8.2, 5.6))
    bottom = np.zeros_like(x, dtype=float)
    for values, label, color in backgrounds:
        ax.bar(x, values, bottom=bottom, width=0.82, color=color, edgecolor="black", linewidth=0.25, label=label)
        bottom += values

    ax.step(
        x,
        signal * 100.0,
        where="mid",
        color=COLORS["Signal"],
        linewidth=2.0,
        label=r"$ZH,H\to WW^\ast$ $\times100$",
        zorder=5,
    )

    ax.set_yscale("log")
    ax.set_ylim(0.6, 2.5e11)
    ax.set_ylabel("Expected events")
    ax.set_xlim(-0.55, len(cut_labels) - 0.45)
    ax.set_xticks(x)
    ax.set_xticklabels(cut_labels, rotation=36, ha="right", rotation_mode="anchor")
    ax.tick_params(axis="x", which="major", pad=6)
    ax.grid(axis="y", which="major", color="0.88", linewidth=0.7)
    ax.set_axisbelow(True)
    ax.legend(loc="upper right", frameon=False, ncol=2, fontsize=8.4)
    ax.text(
        0.02,
        0.96,
        "FCC-ee IDEA fast simulation",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=10,
        fontweight="bold",
    )
    ax.text(
        0.02,
        0.90,
        r"$\sqrt{s}=240$ GeV, $\mathcal{L}=10.8\,\mathrm{ab}^{-1}$",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=9.5,
    )
    fig.subplots_adjust(left=0.12, right=0.98, top=0.94, bottom=0.32)
    save_both(fig, "overall_cutflow_pub")
    plt.close(fig)


def make_uncertainty_breakdown() -> None:
    fit = json.loads((MODEL_DIR / "fit_results.json").read_text())
    s_cut = 16680.81934718182
    b_cut = 9468.5012591095
    cut_proxy = 100.0 * math.sqrt(s_cut + b_cut) / s_cut
    nominal = fit["relative_uncertainty_pct"]
    no_mcstat = fit["physics_only_rel_uncertainty_pct"]
    mcstat_quad = math.sqrt(max(0.0, nominal**2 - no_mcstat**2))

    rows = [
        {
            "entry": "Post-selection counting proxy",
            "treatment": "Reference only; sqrt(S+B)/S after baseline cuts",
            "relative_uncertainty_percent": f"{cut_proxy:.3f}",
            "included_in_nominal_fit": "No",
        },
        {
            "entry": "20-bin BDT shape fit, no template MC-stat nuisances",
            "treatment": "1% background-normalisation constraints retained; Barlow-Beeston terms disabled",
            "relative_uncertainty_percent": f"{no_mcstat:.3f}",
            "included_in_nominal_fit": "Diagnostic",
        },
        {
            "entry": "Template MC statistical uncertainty",
            "treatment": "Quadrature contribution inferred from nominal and no-MC-stat fits",
            "relative_uncertainty_percent": f"{mcstat_quad:.3f}",
            "included_in_nominal_fit": "Yes",
        },
        {
            "entry": "Nominal current template fit",
            "treatment": "20-bin BDT fit with 1% background normalisation and bin-by-bin MC-stat nuisances",
            "relative_uncertainty_percent": f"{nominal:.3f}",
            "included_in_nominal_fit": "Yes",
        },
        {
            "entry": "Detector/theory/modelling systematics",
            "treatment": "JES/JER, lepton efficiency, MET modelling, flavour tagging, theory and shape systematics",
            "relative_uncertainty_percent": "TBD",
            "included_in_nominal_fit": "No",
        },
    ]

    out = NOTE_DIR / "uncertainty_breakdown_v8.csv"
    with out.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    configure_style()
    make_overall_cutflow()
    make_feature_importance()
    make_bdt_score_distributions()
    make_fit_templates()
    make_uncertainty_breakdown()
    print(f"Wrote publication figures to {FIG_DIR}")
    print(f"Wrote uncertainty CSV to {NOTE_DIR / 'uncertainty_breakdown_v8.csv'}")


if __name__ == "__main__":
    main()
