#!/usr/bin/env python3
"""Fast cut scans from the loose lvqq scanmaker ntuples.

The scanmaker output keeps events after the nominal Cut1 lepton candidate and
successful exclusive 4-jet reconstruction.  The scans below use the current
cut-based baseline through the Z-candidate momentum requirement.  The Higgs
candidate and recoil masses are retained as diagnostic/fit-shape variables, but
they are not part of the nominal hard-cut baseline.
"""

from __future__ import annotations

import argparse
import math
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import uproot

THIS_DIR = Path(__file__).resolve().parent
ANALYSIS_DIR = THIS_DIR.parent
sys.path.insert(0, str(ANALYSIS_DIR))

from ml_config import (  # noqa: E402
    BACKGROUND_SAMPLES,
    CUT_SCAN_BRANCHES,
    DEFAULT_SCANMAKER_DIR,
    DEFAULT_TREE_NAME,
    QQ_SAMPLES,
    SIGNAL_SAMPLES,
    TAUTAU_SAMPLES,
    WW_SAMPLES,
    ZH_OTHER_SAMPLES,
    ZZ_SAMPLES,
)
from ml.train_xgboost_bdt import INT_LUMI, SAMPLE_INFO, get_tree_status  # noqa: E402


YIELD_GROUPS = ("signal", "ww", "zz", "qq", "tautau", "zh_other")

LEPTON_THRESHOLDS = tuple(range(2, 21)) + (25, 30)
LEPTON_COUNT_BRANCH = {threshold: f"n_leptons_p{threshold}" for threshold in LEPTON_THRESHOLDS}
ISO_LEPTON_COUNT_BRANCH = {threshold: f"n_iso_leptons_p{threshold}" for threshold in LEPTON_THRESHOLDS}

LEPTON_ISO_MAX = 0.20
MISSING_E_MIN = 10.0
MISSING_E_MAX = 55.0
ZCAND_P_MIN = 40.0
ZCAND_P_MAX = 60.0
SQRT_D34_BASELINE = 14.0
MIN_JET_NCONST_BASELINE = 8.0
DEFAULT_OUTPUT_DIR = "cut_scans_v_fable_baseline"


def sample_group(sample: str, label: int) -> str:
    if label == 1:
        return "signal"
    if sample in WW_SAMPLES:
        return "ww"
    if sample in ZZ_SAMPLES:
        return "zz"
    if sample in QQ_SAMPLES:
        return "qq"
    if sample in TAUTAU_SAMPLES:
        return "tautau"
    if sample in ZH_OTHER_SAMPLES:
        return "zh_other"
    return "other"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", default=DEFAULT_SCANMAKER_DIR)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--tree-name", default=DEFAULT_TREE_NAME)
    parser.add_argument("--signal-samples", nargs="*", default=SIGNAL_SAMPLES)
    parser.add_argument("--background-samples", nargs="*", default=BACKGROUND_SAMPLES)
    parser.add_argument("--step-size", default="100 MB")
    parser.add_argument("--no-plots", action="store_true")
    parser.add_argument(
        "--plots-from-csv",
        action="store_true",
        help="Only regenerate cut-scan plots from existing CSV files; do not reread ROOT ntuples.",
    )
    return parser.parse_args()


def physics_weight(sample: str, events_processed: int | None = None) -> float:
    info = SAMPLE_INFO.get(sample)
    if info is None:
        print(f"[warn] no cross-section metadata for {sample}; using unit weight")
        return 1.0
    if events_processed is not None and events_processed > 0:
        return INT_LUMI * info["xsec"] / events_processed
    return INT_LUMI * info["xsec"] / (info["ngen"] * info.get("fraction", 1.0))


def iter_chunks(input_dir: Path, tree_name: str, samples: list[str], label: int, branches: list[str], step_size: str):
    for sample in samples:
        path = input_dir / f"{sample}.root"
        if not path.exists():
            print(f"[warn] missing input: {path}")
            continue

        with uproot.open(path) as root_file:
            status = get_tree_status(root_file, tree_name)
            if not status["has_tree"]:
                print(f"[warn] {path} has no tree {tree_name!r}; skipping")
                continue

            tree = root_file[tree_name]
            available = set(tree.keys())
            missing = [branch for branch in branches if branch not in available]
            if missing:
                raise RuntimeError(f"{path} is missing scan branches: {missing}")

            events_processed = None
            if "eventsProcessed" in root_file:
                events_processed = int(root_file["eventsProcessed"].member("fVal"))
            weight = physics_weight(sample, events_processed)
            group = sample_group(sample, label)
            for chunk in tree.iterate(branches, library="pd", step_size=step_size):
                chunk["phys_weight"] = weight
                chunk["label"] = label
                chunk["sample"] = sample
                chunk["group"] = group
                yield chunk


def update_yield(accumulator, key, mask, groups, weights) -> None:
    if mask.size == 0:
        return
    yields = accumulator[key]
    for group in YIELD_GROUPS:
        yields[group] += float(weights[mask & (groups == group)].sum())


def rows_from_accumulator(accumulator, kind: str, param_names: list[str]) -> pd.DataFrame:
    rows = []
    for key, yields in accumulator.items():
        params = dict(zip(param_names, key))
        signal = yields.get("signal", 0.0)
        background = sum(yields.get(group, 0.0) for group in YIELD_GROUPS if group != "signal")
        total = signal + background
        rel_unc = math.sqrt(total) / signal if signal > 0 else math.inf
        s_over_sqrt_sb = signal / math.sqrt(total) if total > 0 else 0.0
        s_over_b = signal / background if background > 0 else math.inf
        rows.append({
            "scan": kind,
            **params,
            "signal": signal,
            "background": background,
            "ww": yields.get("ww", 0.0),
            "zz": yields.get("zz", 0.0),
            "qq": yields.get("qq", 0.0),
            "tautau": yields.get("tautau", 0.0),
            "zh_other": yields.get("zh_other", 0.0),
            "s_over_b": s_over_b,
            "s_over_sqrt_sb": s_over_sqrt_sb,
            "rel_uncertainty": rel_unc,
            "rel_uncertainty_pct": 100.0 * rel_unc,
        })
    return pd.DataFrame(rows).sort_values("rel_uncertainty").reset_index(drop=True)


def baseline_masks(frame: pd.DataFrame) -> dict[str, np.ndarray]:
    cut1 = frame["n_leptons_p10_p60"].to_numpy() >= 1
    if "n_extra_iso_leptons_p20" in frame:
        cut3 = frame["n_extra_iso_leptons_p20"].to_numpy() == 0
    else:
        cut3 = frame["n_iso_leptons_p10"].to_numpy() == 1
    iso = frame["lepton_iso"].to_numpy() < LEPTON_ISO_MAX
    met_e = frame["missingEnergy_e"].to_numpy()
    met = (met_e > MISSING_E_MIN) & (met_e < MISSING_E_MAX)
    sqrt_d34 = frame["sqrt_d34"].to_numpy()
    topology = sqrt_d34 > SQRT_D34_BASELINE
    min_jet_nconst = frame["min_jet_nconst"].to_numpy()
    nconst = min_jet_nconst > MIN_JET_NCONST_BASELINE
    zcand_dm = frame["Zcand_dm"].to_numpy()
    # v_fable baseline has NO hard mZ window (Zcand_dm is a BDT input). Keep an
    # all-pass mask so the z-window scan still measures what ADDING a window
    # would do relative to the nominal baseline.
    z = np.ones(len(zcand_dm), dtype=bool)
    zcand_p = frame["Zcand_p"].to_numpy()
    # v_fable baseline has NO hard pZ window either (BDT input); all-pass mask
    # keeps the pZ/recoil scans meaningful as add-a-window studies.
    z_p = np.ones(len(zcand_p), dtype=bool)
    preselection = cut1 & iso & cut3 & met
    return {
        "lepton": cut1 & cut3,
        "iso": iso,
        "met": met,
        "topology": topology,
        "nconst": nconst,
        "z": z,
        "z_p": z_p,
        "preselection": preselection,
        "baseline": preselection & topology & nconst & z & z_p,
    }


def veto_thresholds_for_pmin(pmin: int) -> tuple[int, ...]:
    candidates = {5, 7, 10, 12, 15, pmin, pmin - 2, pmin - 5}
    return tuple(sorted(threshold for threshold in candidates if 2 <= threshold <= pmin))


def accumulate_scans(frame: pd.DataFrame, accumulators: dict[str, dict]) -> None:
    labels = frame["label"].to_numpy()
    groups = frame["group"].to_numpy()
    weights = frame["phys_weight"].to_numpy()
    masks = baseline_masks(frame)

    lepton_p = frame["lepton_p"].to_numpy()
    lepton_iso = frame["lepton_iso"].to_numpy()
    met_e = frame["missingEnergy_e"].to_numpy()
    missing_mass = frame["missingMass"].to_numpy()
    cos_miss = frame["cosTheta_miss"].to_numpy()
    sqrt_d34 = frame["sqrt_d34"].to_numpy()
    min_jet_p = frame["min_jet_p"].to_numpy()
    wstar_m = frame["Wstar_m"].to_numpy()
    deltaR_wstar = frame["deltaR_Wstar"].to_numpy()
    recoil_m = frame["recoil_m"].to_numpy()
    zcand_dm = frame["Zcand_dm"].to_numpy()

    other_for_lepton = masks["iso"] & masks["met"] & masks["topology"] & masks["nconst"] & masks["z"] & masks["z_p"]
    for pmin in (10, 15, 20, 25, 30):
        for pmax in (50, 60, 70, 80, 100, math.inf):
            if pmax <= pmin:
                continue
            window = (lepton_p > pmin) & (lepton_p < pmax)
            for veto in (*sorted({2, 3, 5, 7, 10, 15, pmin}), "none"):
                if veto == "none":
                    mask = other_for_lepton & window
                    update_yield(accumulators["lepton"], (pmin, pmax, veto), mask, groups, weights)
                    continue
                if veto > pmin:
                    continue
                n_branch = frame[LEPTON_COUNT_BRANCH[veto]].to_numpy() == 1
                mask = other_for_lepton & window & n_branch
                update_yield(accumulators["lepton"], (pmin, pmax, veto), mask, groups, weights)

    for pmin in (5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20):
        for pmax in (45, 50, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70, 75, 80):
            if pmax <= pmin + 20:
                continue
            window = (lepton_p > pmin) & (lepton_p < pmax)

            mask = other_for_lepton & window
            update_yield(accumulators["lepton_fine"], (pmin, pmax, "none", "none"), mask, groups, weights)

            for veto in veto_thresholds_for_pmin(pmin):
                n_any = frame[LEPTON_COUNT_BRANCH[veto]].to_numpy() == 1
                mask = other_for_lepton & window & n_any
                update_yield(accumulators["lepton_fine"], (pmin, pmax, "any", veto), mask, groups, weights)

                n_iso = frame[ISO_LEPTON_COUNT_BRANCH[veto]].to_numpy() == 1
                mask = other_for_lepton & window & n_iso
                update_yield(accumulators["lepton_fine"], (pmin, pmax, "isolated", veto), mask, groups, weights)

    other_for_iso = masks["lepton"] & masks["met"] & masks["topology"] & masks["nconst"] & masks["z"] & masks["z_p"]
    for iso_max in (0.05, 0.10, 0.15, 0.20, 0.30, 0.50, 1.00):
        mask = other_for_iso & (lepton_iso < iso_max)
        update_yield(accumulators["iso"], (iso_max,), mask, groups, weights)

    other_for_met = masks["lepton"] & masks["iso"] & masks["topology"] & masks["nconst"] & masks["z"] & masks["z_p"]
    for met_min in (0, 5, 10, 15, 20):
        for cos_max in (0.95, 0.98, 0.99, 1.00):
            mask = other_for_met & (met_e > met_min) & (cos_miss < cos_max)
            update_yield(accumulators["met_costheta"], (met_min, cos_max), mask, groups, weights)

    cut4_options = {
        "A_no_cut4": np.ones_like(met_e, dtype=bool),
        "B_cos_lt_0p98": cos_miss < 0.98,
        "C_met_gt_10": met_e > 10.0,
        "D_10_lt_met_lt_60": (met_e > 10.0) & (met_e < 60.0),
        "E_10_lt_met_lt_80": (met_e > 10.0) & (met_e < 80.0),
        "F_10_lt_met_lt_90": (met_e > 10.0) & (met_e < 90.0),
        "G_mmiss_lt_80": missing_mass < 80.0,
        "H_mmiss_lt_80_cos_lt_0p98": (missing_mass < 80.0) & (cos_miss < 0.98),
        "I_10_lt_met_lt_80_cos_lt_0p98": (met_e > 10.0) & (met_e < 80.0) & (cos_miss < 0.98),
    }
    for option, option_mask in cut4_options.items():
        update_yield(accumulators["cut4_options"], (option,), other_for_met & option_mask, groups, weights)

    for mmiss_max in (40, 50, 60, 70, 80, 100, 120):
        update_yield(
            accumulators["missing_mass"],
            (mmiss_max,),
            other_for_met & (missing_mass < mmiss_max),
            groups,
            weights,
        )

    # Cut5 candidates are compared after fixed Cut1-4 plus downstream Z
    # kinematics, so the scan answers only the topology-quality question.
    other_for_topology = masks["preselection"] & masks["nconst"] & masks["z"] & masks["z_p"]
    for threshold in (0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30):
        mask = other_for_topology & (sqrt_d34 > threshold)
        update_yield(accumulators["sqrt_d34"], (threshold,), mask, groups, weights)

    for threshold in (0, 2, 3, 5, 7, 10, 12, 15):
        mask = other_for_topology & (min_jet_p > threshold)
        update_yield(accumulators["min_jet_p"], (threshold,), mask, groups, weights)

    for threshold in (0, 10, 15, 20, 25, 30):
        mask = other_for_topology & (wstar_m > threshold)
        update_yield(accumulators["wstar_mass"], (threshold,), mask, groups, weights)

    for threshold in (0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0):
        mask = other_for_topology & (deltaR_wstar > threshold)
        update_yield(accumulators["deltaR_wstar"], (threshold,), mask, groups, weights)

    topology_options = {
        "A_no_topology_cut": np.ones_like(sqrt_d34, dtype=bool),
        "B_sqrt_d34_gt_10": sqrt_d34 > 10.0,
        "C_sqrt_d34_gt_12": sqrt_d34 > 12.0,
        "D_sqrt_d34_gt_15": sqrt_d34 > 15.0,
        "E_min_jet_p_gt_5": min_jet_p > 5.0,
        "F_Wstar_m_gt_15": wstar_m > 15.0,
        "G_deltaR_Wstar_gt_0p4": deltaR_wstar > 0.4,
        "H_d34_gt_12_Wstar_gt_15": (sqrt_d34 > 12.0) & (wstar_m > 15.0),
        "I_d34_gt_12_min_jet_p_gt_5": (sqrt_d34 > 12.0) & (min_jet_p > 5.0),
        "J_d34_gt_12_Wstar_gt_15_deltaR_gt_0p4": (sqrt_d34 > 12.0) & (wstar_m > 15.0) & (deltaR_wstar > 0.4),
    }
    for option, option_mask in topology_options.items():
        update_yield(accumulators["cut5_topology_options"], (option,), other_for_topology & option_mask, groups, weights)

    other_for_z = masks["lepton"] & masks["iso"] & masks["met"] & masks["topology"] & masks["nconst"] & masks["z_p"]
    for z_window in (5, 8, 10, 12, 15, 18, 20, 25):
        mask = other_for_z & (zcand_dm < z_window)
        update_yield(accumulators["z_window"], (z_window,), mask, groups, weights)

    other_for_recoil = masks["baseline"]
    for left in (5, 10, 15, 20, 25, 30, 35, 40):
        for right in (5, 10, 15, 20, 25, 30, 35, 40):
            mask = other_for_recoil & (recoil_m > 125.0 - left) & (recoil_m < 125.0 + right)
            update_yield(accumulators["recoil"], (left, right), mask, groups, weights)


def accumulate_validation_hists(frame: pd.DataFrame, hists: dict) -> None:
    masks = baseline_masks(frame)
    labels = frame["label"].to_numpy()
    weights = frame["phys_weight"].to_numpy()
    validation_mask = masks["baseline"]

    sig_mask = validation_mask & (labels == 1)
    bkg_mask = validation_mask & (labels == 0)

    wlep = frame["Wlep_m"].to_numpy()
    wstar = frame["Wstar_m"].to_numpy()
    delta = frame["deltaW_onShell"].to_numpy()

    h2, _, _ = np.histogram2d(
        wlep[sig_mask],
        wstar[sig_mask],
        bins=hists["w2_bins"],
        weights=weights[sig_mask],
    )
    hists["w2_signal"] += h2

    sig_delta, _ = np.histogram(delta[sig_mask], bins=hists["delta_bins"], weights=weights[sig_mask])
    bkg_delta, _ = np.histogram(delta[bkg_mask], bins=hists["delta_bins"], weights=weights[bkg_mask])
    hists["delta_signal"] += sig_delta
    hists["delta_background"] += bkg_delta


METRIC = "rel_uncertainty_pct"
METRIC_LABEL = r"Counting proxy $\delta\mu/\mu$ [%]"


def _format_tick(value) -> str:
    if isinstance(value, str):
        return value
    if np.isinf(value):
        return "inf"
    return f"{value:g}"


def _axis_position(values, target):
    for index, value in enumerate(values):
        if isinstance(value, str) or isinstance(target, str):
            if str(value) == str(target):
                return index
            continue
        if np.isinf(value) and np.isinf(target):
            return index
        if np.isclose(float(value), float(target)):
            return index
    return None


def save_heatmap(
    df: pd.DataFrame,
    x: str,
    y: str,
    value: str,
    path: Path,
    title: str,
    *,
    baseline: tuple | None = None,
) -> None:
    if df.empty:
        return
    pivot = df.pivot_table(index=y, columns=x, values=value, aggfunc="min")
    fig, ax = plt.subplots(figsize=(7.0, 5.2))
    image = ax.imshow(pivot.values, origin="lower", aspect="auto", cmap="viridis_r")
    ax.set_xticks(np.arange(len(pivot.columns)))
    ax.set_xticklabels([_format_tick(v) for v in pivot.columns], rotation=45, ha="right")
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_yticklabels([_format_tick(v) for v in pivot.index])
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_title(title)

    values = pivot.values.astype(float)
    if np.isfinite(values).any():
        best_flat = np.nanargmin(values)
        best_y, best_x = np.unravel_index(best_flat, values.shape)
        ax.scatter(best_x, best_y, marker="*", s=160, c="black", edgecolors="white", linewidths=0.8, label="best")

    if baseline is not None:
        base_x = _axis_position(pivot.columns, baseline[0])
        base_y = _axis_position(pivot.index, baseline[1])
        if base_x is not None and base_y is not None:
            ax.scatter(base_x, base_y, marker="x", s=90, c="#d62728", linewidths=2.0, label="baseline")

    if ax.get_legend_handles_labels()[0]:
        ax.legend(loc="best", frameon=True, fontsize=8)

    cbar = fig.colorbar(image, ax=ax)
    cbar.set_label(METRIC_LABEL if value == METRIC else value)
    fig.tight_layout()
    fig.savefig(path.with_suffix(".pdf"))
    fig.savefig(path.with_suffix(".png"), dpi=160)
    plt.close(fig)


def save_line(
    df: pd.DataFrame,
    x: str,
    y: str,
    path: Path,
    title: str,
    *,
    baseline_x=None,
) -> None:
    if df.empty:
        return
    df = df.sort_values(x)
    fig, ax = plt.subplots(figsize=(6.6, 4.6))
    ax.plot(df[x], df[y], marker="o", linewidth=1.8)
    best = df.loc[df[y].idxmin()]
    ax.scatter(best[x], best[y], marker="*", s=160, c="black", edgecolors="white", linewidths=0.8, zorder=5, label="best")
    if baseline_x is not None:
        baseline_rows = df[np.isclose(df[x].astype(float), float(baseline_x))]
        if not baseline_rows.empty:
            baseline = baseline_rows.iloc[0]
            ax.scatter(
                baseline[x],
                baseline[y],
                marker="x",
                s=90,
                c="#d62728",
                linewidths=2.0,
                zorder=5,
                label="baseline",
            )
    ax.set_xlabel(x)
    ax.set_ylabel(METRIC_LABEL if y == METRIC else y)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend(frameon=True, fontsize=8)
    fig.tight_layout()
    fig.savefig(path.with_suffix(".pdf"))
    fig.savefig(path.with_suffix(".png"), dpi=160)
    plt.close(fig)


def save_multi_line(
    df: pd.DataFrame,
    x: str,
    series: str,
    y: str,
    path: Path,
    title: str,
    *,
    baseline: tuple | None = None,
    legend_title: str | None = None,
) -> None:
    if df.empty:
        return

    def sort_key(value):
        if isinstance(value, str):
            return float("inf") if value == "none" else value
        if np.isinf(value):
            return float("inf")
        return float(value)

    fig, ax = plt.subplots(figsize=(7.4, 4.9))
    best = df.loc[df[y].idxmin()]
    baseline_drawn = False

    for series_value, subdf in sorted(df.groupby(series), key=lambda item: sort_key(item[0])):
        subdf = subdf.sort_values(x, key=lambda s: s.map(sort_key))
        ax.plot(
            subdf[x],
            subdf[y],
            marker="o",
            linewidth=1.6,
            markersize=4.5,
            label=f"{series}={_format_tick(series_value)}",
        )

        best_match = subdf.index == best.name
        if best_match.any():
            best_row = subdf.loc[best_match].iloc[0]
            ax.scatter(
                best_row[x],
                best_row[y],
                marker="*",
                s=180,
                c="black",
                edgecolors="white",
                linewidths=0.8,
                zorder=6,
                label="best",
            )

        if baseline is not None and not baseline_drawn:
            base_x, base_series = baseline
            matching = subdf[
                np.isclose(subdf[x].astype(float), float(base_x))
                & np.isclose(subdf[series].astype(float), float(base_series))
            ]
            if not matching.empty:
                base = matching.iloc[0]
                ax.scatter(
                    base[x],
                    base[y],
                    marker="x",
                    s=95,
                    c="#d62728",
                    linewidths=2.2,
                    zorder=7,
                    label="baseline",
                )
                baseline_drawn = True

    ax.set_xlabel(x)
    ax.set_ylabel(METRIC_LABEL if y == METRIC else y)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend(title=legend_title, frameon=True, fontsize=8, title_fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(path.with_suffix(".pdf"))
    fig.savefig(path.with_suffix(".png"), dpi=160)
    plt.close(fig)


def save_categorical_line(
    df: pd.DataFrame,
    x: str,
    y: str,
    path: Path,
    title: str,
    *,
    baseline_x=None,
) -> None:
    if df.empty:
        return
    working = df.copy()

    def sort_key(value):
        if str(value) == "none":
            return 1e9
        return float(value)

    working = working.sort_values(x, key=lambda s: s.map(sort_key))
    labels = [_format_tick(v) for v in working[x]]
    xpos = np.arange(len(working))
    fig, ax = plt.subplots(figsize=(6.6, 4.6))
    ax.plot(xpos, working[y], marker="o", linewidth=1.8)

    best_pos = int(np.argmin(working[y].to_numpy()))
    ax.scatter(best_pos, working.iloc[best_pos][y], marker="*", s=160, c="black", edgecolors="white", linewidths=0.8, zorder=5, label="best")
    if baseline_x is not None:
        for index, value in enumerate(working[x]):
            if str(value) == str(baseline_x):
                ax.scatter(index, working.iloc[index][y], marker="x", s=90, c="#d62728", linewidths=2.0, zorder=5, label="baseline")
                break

    ax.set_xticks(xpos)
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_xlabel(x)
    ax.set_ylabel(METRIC_LABEL if y == METRIC else y)
    ax.set_title(title)
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend(frameon=True, fontsize=8)
    fig.tight_layout()
    fig.savefig(path.with_suffix(".pdf"))
    fig.savefig(path.with_suffix(".png"), dpi=160)
    plt.close(fig)


def save_validation_plots(hists: dict | None, output_dir: Path) -> None:
    if hists is None:
        return
    x_edges, y_edges = hists["w2_bins"]
    w2 = hists["w2_signal"]
    if w2.sum() > 0:
        fig, ax = plt.subplots(figsize=(6.2, 5.3))
        mesh = ax.pcolormesh(x_edges, y_edges, w2.T, cmap="magma")
        ax.axvline(80.379, color="white", linestyle="--", linewidth=1.2)
        ax.axhline(80.379, color="white", linestyle="--", linewidth=1.2)
        ax.set_xlabel(r"$m_{\ell\nu}$ [GeV]")
        ax.set_ylabel(r"$m_{qq}^{W^*}$ [GeV]")
        ax.set_title("Signal on-shell-W validation")
        cbar = fig.colorbar(mesh, ax=ax)
        cbar.set_label("weighted events")
        fig.tight_layout()
        fig.savefig(output_dir / "wlep_vs_wstar_signal.pdf")
        fig.savefig(output_dir / "wlep_vs_wstar_signal.png", dpi=160)
        plt.close(fig)

    delta_edges = hists["delta_bins"]
    centers = 0.5 * (delta_edges[:-1] + delta_edges[1:])
    width = np.diff(delta_edges)
    sig = hists["delta_signal"]
    bkg = hists["delta_background"]
    if sig.sum() > 0 or bkg.sum() > 0:
        fig, ax = plt.subplots(figsize=(6.8, 4.8))
        if bkg.sum() > 0:
            ax.step(centers, bkg / bkg.sum(), where="mid", label="background", color="#4c78a8")
        if sig.sum() > 0:
            ax.step(centers, sig / sig.sum(), where="mid", label="signal", color="#e45756")
        ax.axvline(0.0, color="black", linestyle="--", linewidth=1.1)
        ax.set_xlabel(r"$|m_{\ell\nu}-m_W| - |m_{qq}^{W^*}-m_W|$ [GeV]")
        ax.set_ylabel("unit area")
        ax.set_title("Leptonic-side on-shell check")
        ax.legend(frameon=False)
        ax.grid(True, alpha=0.25)
        ax.set_xlim(delta_edges[0], delta_edges[-1])
        fig.tight_layout()
        fig.savefig(output_dir / "deltaW_onShell.pdf")
        fig.savefig(output_dir / "deltaW_onShell.png", dpi=160)
        plt.close(fig)


def save_plots(outputs: dict[str, pd.DataFrame], hists: dict | None, output_dir: Path) -> None:
    lepton = outputs["lepton"]
    if not lepton.empty:
        best_veto = lepton.groupby(["pmin", "pmax"], as_index=False)["rel_uncertainty_pct"].min()
        save_multi_line(
            best_veto,
            "pmin",
            "pmax",
            METRIC,
            output_dir / "cut1_lepton_window_scan",
            "Cut 1: selected-lepton momentum window, best veto per point",
            baseline=(10, 60),
            legend_title=r"$p_\ell^{max}$",
        )

        cut3 = lepton[(lepton["pmin"] == 10) & np.isclose(lepton["pmax"].astype(float), 60.0)]
        if not cut3.empty:
            save_categorical_line(
                cut3,
                "veto",
                METRIC,
                output_dir / "cut3_extra_lepton_veto_scan",
                "Cut 3: extra-lepton veto threshold at baseline lepton window",
                baseline_x="20",
            )

    lepton_fine = outputs.get("lepton_fine", pd.DataFrame())
    if not lepton_fine.empty:
        best_veto = lepton_fine.groupby(["pmin", "pmax"], as_index=False)[METRIC].min()
        save_multi_line(
            best_veto,
            "pmin",
            "pmax",
            METRIC,
            output_dir / "cut1_fine_lepton_window_scan",
            "Cut 1 fine scan, best veto per point",
            baseline=(10, 60),
            legend_title=r"$p_\ell^{max}$",
        )

        for pmin, pmax in ((10, 60), (20, 60)):
            candidate = lepton_fine[(lepton_fine["pmin"] == pmin) & (lepton_fine["pmax"] == pmax)].copy()
            if candidate.empty:
                continue
            candidate["veto_label"] = candidate.apply(
                lambda row: "none" if row["veto_kind"] == "none" else f"{row['veto_kind']} > {row['veto']}",
                axis=1,
            )
            candidate = candidate.sort_values(METRIC).head(18).sort_values(METRIC, ascending=False)
            fig, ax = plt.subplots(figsize=(8.0, 5.2))
            colors = candidate["veto_kind"].map({"none": "#4c78a8", "any": "#f58518", "isolated": "#54a24b"}).fillna("#777777")
            ax.barh(candidate["veto_label"], candidate[METRIC], color=colors)
            best = candidate.loc[candidate[METRIC].idxmin()]
            ax.scatter(best[METRIC], best["veto_label"], marker="*", s=180, c="black", edgecolors="white", linewidths=0.8, zorder=5)
            ax.set_xlabel(METRIC_LABEL)
            ax.set_ylabel("extra-lepton veto")
            ax.set_title(fr"Cut 3 fine veto scan for ${pmin}<p_\ell<{pmax}$ GeV")
            ax.grid(True, axis="x", alpha=0.3)
            fig.tight_layout()
            fig.savefig(output_dir / f"cut3_fine_veto_for_p{pmin}_{pmax}.pdf")
            fig.savefig(output_dir / f"cut3_fine_veto_for_p{pmin}_{pmax}.png", dpi=160)
            plt.close(fig)

    save_line(outputs["iso"], "iso_max", METRIC, output_dir / "cut2_isolation_scan", "Cut 2: lepton isolation threshold", baseline_x=0.20)
    save_multi_line(
        outputs["met_costheta"],
        "met_min",
        "cos_max",
        METRIC,
        output_dir / "cut4_met_costheta_scan",
        "Cut 4: missing-energy and missing-direction scan",
        baseline=(0, 0.98),
        legend_title=r"$|\cos\theta_{miss}|_{max}$",
    )
    cut4_options = outputs.get("cut4_options", pd.DataFrame())
    if not cut4_options.empty:
        working = cut4_options.sort_values(METRIC, ascending=False)
        fig, ax = plt.subplots(figsize=(8.2, 5.0))
        colors = ["#4c78a8" if option != "B_cos_lt_0p98" else "#54a24b" for option in working["option"]]
        ax.barh(working["option"], working[METRIC], color=colors)
        best = working.loc[working[METRIC].idxmin()]
        ax.scatter(best[METRIC], best["option"], marker="*", s=180, c="black", edgecolors="white", linewidths=0.8, zorder=5)
        ax.set_xlabel(METRIC_LABEL)
        ax.set_ylabel("Cut4 candidate")
        ax.set_title("Cut 4: missing-system candidate comparison")
        ax.grid(True, axis="x", alpha=0.3)
        fig.tight_layout()
        fig.savefig(output_dir / "cut4_missing_system_options.pdf")
        fig.savefig(output_dir / "cut4_missing_system_options.png", dpi=160)
        plt.close(fig)

    if "missing_mass" in outputs:
        save_line(
            outputs["missing_mass"],
            "mmiss_max",
            METRIC,
            output_dir / "cut4_missing_mass_scan",
            "Cut 4: missing-mass upper cut scan",
            baseline_x=80,
        )

    save_line(
        outputs["sqrt_d34"],
        "sqrt_d34_min",
        METRIC,
        output_dir / "cut5_sqrt_d34_scan",
        r"Cut 5 after fixed Z-candidate kinematics: $\sqrt{d_{34}}$ scan",
        baseline_x=SQRT_D34_BASELINE,
    )
    save_line(
        outputs["min_jet_p"],
        "min_jet_p_min",
        METRIC,
        output_dir / "cut5_min_jet_p_scan",
        "Cut 5 after fixed Z-candidate kinematics: minimum jet momentum scan",
        baseline_x=0,
    )
    save_line(
        outputs["wstar_mass"],
        "wstar_m_min",
        METRIC,
        output_dir / "cut5_wstar_mass_scan",
        r"Cut 5 after fixed Z-candidate kinematics: $m_{W^*}$ lower-cut scan",
        baseline_x=0,
    )
    save_line(
        outputs["deltaR_wstar"],
        "deltaR_wstar_min",
        METRIC,
        output_dir / "cut5_deltaR_wstar_scan",
        r"Cut 5 after fixed Z-candidate kinematics: $\Delta R_{jj}^{W^*}$ scan",
        baseline_x=0,
    )
    cut5_options = outputs.get("cut5_topology_options", pd.DataFrame())
    if not cut5_options.empty:
        working = cut5_options.sort_values(METRIC, ascending=False)
        fig, ax = plt.subplots(figsize=(8.4, 5.2))
        ax.barh(working["option"], working[METRIC], color="#4c78a8")
        best = working.loc[working[METRIC].idxmin()]
        ax.scatter(best[METRIC], best["option"], marker="*", s=180, c="black", edgecolors="white", linewidths=0.8, zorder=5)
        ax.set_xlabel(METRIC_LABEL)
        ax.set_ylabel("Cut5 topology candidate")
        ax.set_title("Cut 5: topology-quality candidate comparison")
        ax.grid(True, axis="x", alpha=0.3)
        fig.tight_layout()
        fig.savefig(output_dir / "cut5_topology_options.pdf")
        fig.savefig(output_dir / "cut5_topology_options.png", dpi=160)
        plt.close(fig)

    save_line(
        outputs["z_window"],
        "z_window",
        METRIC,
        output_dir / "optional_z_window_scan",
        "Optional diagnostic: Z mass-window ADDED on top of the no-window baseline",
        baseline_x=None,
    )
    save_multi_line(
        outputs["recoil"],
        "right",
        "left",
        METRIC,
        output_dir / "optional_recoil_asymmetric_scan",
        "Optional diagnostic: asymmetric recoil-window scan",
        baseline=None,
        legend_title="left",
    )
    save_validation_plots(hists, output_dir)


def load_outputs_from_csv(output_dir: Path) -> dict[str, pd.DataFrame]:
    files = {
        "lepton": "lepton_scan.csv",
        "lepton_fine": "lepton_fine_scan.csv",
        "iso": "iso_scan.csv",
        "met_costheta": "met_costheta_scan.csv",
        "cut4_options": "cut4_options_scan.csv",
        "missing_mass": "missing_mass_scan.csv",
        "sqrt_d34": "sqrt_d34_scan.csv",
        "min_jet_p": "min_jet_p_scan.csv",
        "wstar_mass": "wstar_mass_scan.csv",
        "deltaR_wstar": "deltaR_wstar_scan.csv",
        "cut5_topology_options": "cut5_topology_options_scan.csv",
        "z_window": "z_window_scan.csv",
        "recoil": "recoil_scan.csv",
    }
    outputs = {}
    for key, filename in files.items():
        path = output_dir / filename
        if not path.exists():
            if key in {
                "lepton_fine",
                "cut4_options",
                "missing_mass",
                "min_jet_p",
                "wstar_mass",
                "deltaR_wstar",
                "cut5_topology_options",
            }:
                outputs[key] = pd.DataFrame()
                continue
            raise FileNotFoundError(f"Missing CSV for plot-only mode: {path}")
        outputs[key] = pd.read_csv(path)
    return outputs


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.plots_from_csv:
        outputs = load_outputs_from_csv(output_dir)
        save_plots(outputs, None, output_dir)
        print(f"\nRegenerated cut-scan plots from CSV files in {output_dir}")
        return

    branches = [branch for branch in CUT_SCAN_BRANCHES if branch != "weight"]
    empty_yields = lambda: {group: 0.0 for group in YIELD_GROUPS}
    accumulators = {
        "lepton": defaultdict(empty_yields),
        "lepton_fine": defaultdict(empty_yields),
        "iso": defaultdict(empty_yields),
        "met_costheta": defaultdict(empty_yields),
        "cut4_options": defaultdict(empty_yields),
        "missing_mass": defaultdict(empty_yields),
        "sqrt_d34": defaultdict(empty_yields),
        "min_jet_p": defaultdict(empty_yields),
        "wstar_mass": defaultdict(empty_yields),
        "deltaR_wstar": defaultdict(empty_yields),
        "cut5_topology_options": defaultdict(empty_yields),
        "z_window": defaultdict(empty_yields),
        "recoil": defaultdict(empty_yields),
    }
    hists = {
        "w2_bins": (np.linspace(0, 160, 81), np.linspace(0, 160, 81)),
        "w2_signal": np.zeros((80, 80), dtype=float),
        "delta_bins": np.linspace(-100, 100, 81),
        "delta_signal": np.zeros(80, dtype=float),
        "delta_background": np.zeros(80, dtype=float),
    }

    samples = [(args.signal_samples, 1), (args.background_samples, 0)]
    for sample_names, label in samples:
        for frame in iter_chunks(input_dir, args.tree_name, sample_names, label, branches, args.step_size):
            accumulate_scans(frame, accumulators)
            accumulate_validation_hists(frame, hists)

    outputs = {
        "lepton": rows_from_accumulator(accumulators["lepton"], "lepton", ["pmin", "pmax", "veto"]),
        "lepton_fine": rows_from_accumulator(
            accumulators["lepton_fine"],
            "lepton_fine",
            ["pmin", "pmax", "veto_kind", "veto"],
        ),
        "iso": rows_from_accumulator(accumulators["iso"], "iso", ["iso_max"]),
        "met_costheta": rows_from_accumulator(accumulators["met_costheta"], "met_costheta", ["met_min", "cos_max"]),
        "cut4_options": rows_from_accumulator(accumulators["cut4_options"], "cut4_options", ["option"]),
        "missing_mass": rows_from_accumulator(accumulators["missing_mass"], "missing_mass", ["mmiss_max"]),
        "sqrt_d34": rows_from_accumulator(accumulators["sqrt_d34"], "sqrt_d34", ["sqrt_d34_min"]),
        "min_jet_p": rows_from_accumulator(accumulators["min_jet_p"], "min_jet_p", ["min_jet_p_min"]),
        "wstar_mass": rows_from_accumulator(accumulators["wstar_mass"], "wstar_mass", ["wstar_m_min"]),
        "deltaR_wstar": rows_from_accumulator(accumulators["deltaR_wstar"], "deltaR_wstar", ["deltaR_wstar_min"]),
        "cut5_topology_options": rows_from_accumulator(accumulators["cut5_topology_options"], "cut5_topology_options", ["option"]),
        "z_window": rows_from_accumulator(accumulators["z_window"], "z_window", ["z_window"]),
        "recoil": rows_from_accumulator(accumulators["recoil"], "recoil", ["left", "right"]),
    }

    combined = []
    for name, frame in outputs.items():
        frame.to_csv(output_dir / f"{name}_scan.csv", index=False)
        if not frame.empty:
            combined.append(frame.head(20))
            print(f"\n==> best {name} configurations")
            print(frame.head(10).to_string(index=False))

    if combined:
        pd.concat(combined, ignore_index=True).to_csv(output_dir / "best_scan_configs.csv", index=False)

    if not args.no_plots:
        save_plots(outputs, hists, output_dir)

    print(f"\nWrote cut-scan outputs to {output_dir}")


if __name__ == "__main__":
    main()
