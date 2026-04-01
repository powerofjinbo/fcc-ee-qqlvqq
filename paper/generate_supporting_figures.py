#!/usr/bin/env python3
"""Generate paper support figures from existing analysis outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import sys
import uproot


THIS_DIR = Path(__file__).resolve().parent
ANALYSIS_DIR = THIS_DIR.parent
sys.path.insert(0, str(ANALYSIS_DIR))

from ml_config import (
    DEFAULT_MODEL_DIR,
    QQ_SAMPLES,
    SAMPLE_PROCESSING_FRACTIONS,
    SIGNAL_SAMPLES,
    WW_SAMPLES,
    ZZ_SAMPLES,
)


HIST_DIR = ANALYSIS_DIR / "output" / "h_hww_lvqq" / "histmaker" / "ecm240"
TREE_DIR = ANALYSIS_DIR / "output" / "h_hww_lvqq" / "treemaker" / "ecm240"
PLOT_DIR = ANALYSIS_DIR / DEFAULT_MODEL_DIR / "plots"
INT_LUMI = 10.8e6  # pb^-1

# Minimal physics metadata needed for support-figure weighting.
SAMPLE_INFO = {
    "wzp6_ee_qqH_HWW_ecm240": {"xsec": 0.01140, "ngen": 1100000},
    "wzp6_ee_bbH_HWW_ecm240": {"xsec": 0.006350, "ngen": 1000000},
    "wzp6_ee_ccH_HWW_ecm240": {"xsec": 0.004988, "ngen": 1200000},
    "wzp6_ee_ssH_HWW_ecm240": {"xsec": 0.006403, "ngen": 1200000},
    "p8_ee_WW_ecm240": {"xsec": 16.4385, "ngen": 373375386},
    "p8_ee_ZZ_ecm240": {"xsec": 1.35899, "ngen": 209700000},
    "wz3p6_ee_uu_ecm240": {"xsec": 11.9447, "ngen": 100790000},
    "wz3p6_ee_dd_ecm240": {"xsec": 10.8037, "ngen": 100910000},
    "wz3p6_ee_cc_ecm240": {"xsec": 11.0595, "ngen": 101290000},
    "wz3p6_ee_ss_ecm240": {"xsec": 10.7725, "ngen": 102348636},
    "wz3p6_ee_bb_ecm240": {"xsec": 10.4299, "ngen": 99490000},
}


def load_merged_hist(samples: list[str], hist_name: str) -> tuple[np.ndarray, np.ndarray]:
    values = None
    edges = None
    for sample in samples:
        path = HIST_DIR / f"{sample}.root"
        with uproot.open(path) as root_file:
            hist = root_file[hist_name]
            sample_values, sample_edges = hist.to_numpy()
        if values is None:
            values = sample_values.astype(float)
            edges = sample_edges.astype(float)
        else:
            values += sample_values
    if values is None or edges is None:
        raise RuntimeError(f"Could not load histogram {hist_name!r} from {samples!r}")
    return values, edges


def normalize(values: np.ndarray) -> np.ndarray:
    total = float(np.sum(values))
    return values / total if total > 0.0 else values.copy()


def sample_phys_weight(sample: str) -> float:
    info = SAMPLE_INFO[sample]
    frac = SAMPLE_PROCESSING_FRACTIONS.get(sample, 1.0)
    return INT_LUMI * info["xsec"] / (info["ngen"] * frac)


def load_weighted_branch(samples: list[str], branch_name: str) -> tuple[np.ndarray, np.ndarray]:
    values_list: list[np.ndarray] = []
    weights_list: list[np.ndarray] = []

    for sample in samples:
        path = TREE_DIR / f"{sample}.root"
        with uproot.open(path) as root_file:
            if "events" not in root_file:
                continue
            tree = root_file["events"]
            if branch_name not in tree:
                continue
            sample_values = np.asarray(tree[branch_name].array(library="np"), dtype=float)

        if sample_values.size == 0:
            continue

        sample_weight = sample_phys_weight(sample)
        values_list.append(sample_values)
        weights_list.append(np.full(sample_values.shape, sample_weight, dtype=float))

    if not values_list:
        raise RuntimeError(f"Could not load branch {branch_name!r} from {samples!r}")

    return np.concatenate(values_list), np.concatenate(weights_list)


def make_pairing_validation() -> None:
    figure_specs = [
        ("Zcand_m", r"$m_{Z,\mathrm{cand}}$ [GeV]", 91.1876, (40.0, 140.0), r"$Z$ candidate"),
        ("Wstar_m", r"$m_{W^*}$ [GeV]", None, (0.0, 95.0), r"Hadronic $W^*$ candidate"),
        ("Wlep_m", r"$m_{W,\mathrm{lep}}$ [GeV]", 80.379, (30.0, 150.0), r"Leptonic $W$ candidate"),
        ("Hcand_m_final", r"$m_{H,\mathrm{cand}}$ [GeV]", 125.0, (95.0, 155.0), r"Higgs candidate"),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(9.2, 6.8))
    axes = axes.flatten()

    for ax, (hist_name, xlabel, ref_mass, xlim, title) in zip(axes, figure_specs):
        sig_values, edges = load_merged_hist(SIGNAL_SAMPLES, hist_name)
        ww_values, _ = load_merged_hist(["p8_ee_WW_ecm240"], hist_name)
        centers = 0.5 * (edges[:-1] + edges[1:])
        sig_norm = normalize(sig_values)
        ww_norm = normalize(ww_values)

        ax.fill_between(
            centers,
            ww_norm,
            step="mid",
            color="#4C78A8",
            alpha=0.22,
        )
        ax.step(
            centers,
            ww_norm,
            where="mid",
            color="#4C78A8",
            linewidth=1.8,
            label=r"Background: WW",
        )
        ax.step(
            centers,
            sig_norm,
            where="mid",
            color="#D64F4F",
            linewidth=2.2,
            label=r"Signal: ZH, H$\rightarrow$WW$^*$",
        )
        ref_handle = None
        if ref_mass is not None:
            ref_handle = ax.axvline(
                ref_mass,
                color="#222222",
                linestyle="--",
                linewidth=1.3,
                label="Reference mass",
            )
        ax.set_title(title, fontsize=11)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Normalized yield")
        ax.set_xlim(*xlim)
        ax.grid(axis="y", alpha=0.25)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.legend(frameon=False, fontsize=8.3, loc="upper right")

    fig.tight_layout()
    fig.savefig(PLOT_DIR / "pairing_validation.pdf")
    fig.savefig(PLOT_DIR / "pairing_validation.png", dpi=180)
    plt.close(fig)


def make_d34_distribution() -> None:
    group_specs = [
        (r"Signal: ZH, H$\rightarrow$WW$^*$", SIGNAL_SAMPLES, "#D64F4F", 2.3),
        ("Background: WW", WW_SAMPLES, "#E68613", 2.0),
        ("Background: ZZ", ZZ_SAMPLES, "#4C78A8", 1.8),
        (r"Background: $q\bar{q}$", QQ_SAMPLES, "#54A24B", 1.8),
    ]

    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    bins = np.linspace(0.0, 60.0, 31)

    for label, samples, color, linewidth in group_specs:
        values, weights = load_weighted_branch(samples, "d_34")
        x = np.sqrt(np.clip(values, 0.0, None))
        total = float(np.sum(weights))
        norm_weights = weights / total if total > 0.0 else weights
        ax.hist(
            x,
            bins=bins,
            weights=norm_weights,
            histtype="step",
            linewidth=linewidth,
            color=color,
            label=label,
        )

    ax.set_xlim(0.0, 60.0)
    ax.set_xlabel(r"$\sqrt{d_{34}}$ [GeV]")
    ax.set_ylabel("Normalized yield")
    ax.grid(axis="y", alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False, fontsize=8.5, loc="upper right")
    fig.tight_layout()
    fig.savefig(PLOT_DIR / "d34_distribution.pdf")
    fig.savefig(PLOT_DIR / "d34_distribution.png", dpi=180)
    plt.close(fig)


def draw_straight_line(ax, x1: float, y1: float, x2: float, y2: float, **kwargs) -> None:
    ax.plot([x1, x2], [y1, y2], solid_capstyle="round", **kwargs)


def draw_fermion(ax, x1: float, y1: float, x2: float, y2: float, forward: bool = True, **kwargs) -> None:
    line_kwargs = {"color": "black", "linewidth": 2.5}
    line_kwargs.update(kwargs)
    draw_straight_line(ax, x1, y1, x2, y2, **line_kwargs)
    start = (x1, y1) if forward else (x2, y2)
    end = (x2, y2) if forward else (x1, y1)
    ax.annotate(
        "",
        xy=end,
        xytext=start,
        arrowprops={
            "arrowstyle": "-|>",
            "mutation_scale": 15,
            "lw": line_kwargs["linewidth"],
            "color": line_kwargs["color"],
            "shrinkA": 10,
            "shrinkB": 10,
        },
    )


def draw_boson(ax, x1: float, y1: float, x2: float, y2: float, dashed: bool = False, **kwargs) -> None:
    style = {"color": "black", "linewidth": 2.2}
    style.update(kwargs)
    npts = 200
    x = np.linspace(x1, x2, npts)
    y = np.linspace(y1, y2, npts)
    dx = x2 - x1
    dy = y2 - y1
    length = np.hypot(dx, dy)
    if length == 0:
        return
    nx = -dy / length
    ny = dx / length
    n_waves = max(5.5, 8.0 * length)
    phase = np.linspace(0.0, 2.0 * np.pi * n_waves, npts)
    amp = 0.010
    x_wavy = x + amp * np.sin(phase) * nx
    y_wavy = y + amp * np.sin(phase) * ny
    if dashed:
        ax.plot(x_wavy, y_wavy, linestyle=(0, (4, 3)), solid_capstyle="round", **style)
    else:
        ax.plot(x_wavy, y_wavy, solid_capstyle="round", **style)


def add_label(ax, x: float, y: float, text: str, **kwargs) -> None:
    defaults = {"fontsize": 11, "ha": "center", "va": "center"}
    defaults.update(kwargs)
    ax.text(x, y, text, **defaults)


def label_on_segment(
    ax,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    text: str,
    *,
    t: float = 0.5,
    offset: float = 0.035,
    side: float = 1.0,
    **kwargs,
) -> None:
    dx = x2 - x1
    dy = y2 - y1
    length = np.hypot(dx, dy)
    if length == 0:
        add_label(ax, x1, y1, text, **kwargs)
        return

    nx = -dy / length
    ny = dx / length
    x = x1 + t * dx + side * offset * nx
    y = y1 + t * dy + side * offset * ny
    defaults = {"fontsize": 11, "ha": "center", "va": "center"}
    defaults.update(kwargs)
    ax.text(x, y, text, **defaults)


def make_feynman_diagram() -> None:
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.set_aspect("equal")
    ax.axis("off")

    v0 = (0.24, 0.50)
    v1 = (0.44, 0.50)
    vz = (0.62, 0.73)
    vh = (0.62, 0.27)
    vw1 = (0.79, 0.39)
    vw2 = (0.79, 0.15)

    eplus = (0.05, 0.76)
    eminus = (0.05, 0.24)
    zq = (0.94, 0.86)
    zqbar = (0.94, 0.60)
    wl = (0.94, 0.49)
    wnu = (0.94, 0.29)
    wq = (0.94, 0.20)
    wqbar = (0.94, 0.04)

    draw_fermion(ax, *eplus, *v0, forward=False)
    draw_fermion(ax, *eminus, *v0, forward=True)
    draw_boson(ax, *v0, *v1)
    draw_boson(ax, *v1, *vz)
    draw_straight_line(ax, *v1, *vh, color="black", linewidth=2.3, linestyle=(0, (5, 3)))
    draw_fermion(ax, *vz, *zq, forward=True)
    draw_fermion(ax, *vz, *zqbar, forward=False)
    draw_boson(ax, *vh, *vw1)
    draw_boson(ax, *vh, *vw2, dashed=True)
    draw_fermion(ax, *vw1, *wl, forward=True)
    draw_fermion(ax, *vw1, *wnu, forward=False)
    draw_fermion(ax, *vw2, *wq, forward=True)
    draw_fermion(ax, *vw2, *wqbar, forward=False)

    ax.scatter(
        [v0[0], v1[0], vz[0], vh[0], vw1[0], vw2[0]],
        [v0[1], v1[1], vz[1], vh[1], vw1[1], vw2[1]],
        s=26,
        color="black",
        zorder=5,
    )

    label_on_segment(ax, *v0, *v1, r"$Z^*$", offset=0.045, side=1.0)
    label_on_segment(ax, *v1, *vz, r"$Z$", offset=0.04, side=1.0)
    label_on_segment(ax, *v1, *vh, r"$H$", offset=0.045, side=-1.0)
    label_on_segment(ax, *vh, *vw1, r"$W$", offset=0.04, side=1.0)
    label_on_segment(ax, *vh, *vw2, r"$W^*$", offset=0.04, side=-1.0)

    add_label(ax, 0.025, 0.78, r"$e^+$", ha="left")
    add_label(ax, 0.025, 0.22, r"$e^-$", ha="left")
    add_label(ax, 0.965, 0.88, r"$q$", ha="left")
    add_label(ax, 0.965, 0.58, r"$\bar{q}$", ha="left")
    add_label(ax, 0.965, 0.51, r"$\ell$", ha="left")
    add_label(ax, 0.965, 0.27, r"$\nu$", ha="left")
    add_label(ax, 0.965, 0.21, r"$q$", ha="left")
    add_label(ax, 0.965, 0.03, r"$\bar{q}'$", ha="left")

    fig.tight_layout(pad=0.15)
    fig.savefig(PLOT_DIR / "feynman_diagram.pdf")
    fig.savefig(PLOT_DIR / "feynman_diagram.png", dpi=180)
    plt.close(fig)


def main() -> None:
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    make_pairing_validation()
    make_feynman_diagram()
    make_d34_distribution()
    print(f"Generated supporting figures in {PLOT_DIR}")


if __name__ == "__main__":
    main()
