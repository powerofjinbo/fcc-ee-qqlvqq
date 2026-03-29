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

from ml_config import DEFAULT_MODEL_DIR, SIGNAL_SAMPLES


HIST_DIR = ANALYSIS_DIR / "output" / "h_hww_lvqq" / "histmaker" / "ecm240"
PLOT_DIR = ANALYSIS_DIR / DEFAULT_MODEL_DIR / "plots"


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


def draw_straight_line(ax, x1: float, y1: float, x2: float, y2: float, **kwargs) -> None:
    ax.plot([x1, x2], [y1, y2], solid_capstyle="round", **kwargs)


def draw_fermion(ax, x1: float, y1: float, x2: float, y2: float, forward: bool = True, **kwargs) -> None:
    line_kwargs = {"color": "black", "linewidth": 2.9}
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
            "mutation_scale": 17,
            "lw": line_kwargs["linewidth"],
            "color": line_kwargs["color"],
            "shrinkA": 13,
            "shrinkB": 13,
        },
    )


def draw_boson(ax, x1: float, y1: float, x2: float, y2: float, dashed: bool = False, **kwargs) -> None:
    style = {"color": "black", "linewidth": 2.5}
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
    phase = np.linspace(0.0, 2.0 * np.pi * 7.0, npts)
    amp = 0.012
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


def make_feynman_diagram() -> None:
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.axis("off")

    v0 = (0.28, 0.50)
    v1 = (0.48, 0.50)
    vz = (0.66, 0.74)
    vh = (0.66, 0.26)
    vw1 = (0.82, 0.38)
    vw2 = (0.82, 0.16)

    draw_fermion(ax, 0.04, 0.76, *v0, forward=False)
    draw_fermion(ax, 0.04, 0.24, *v0, forward=True)
    draw_boson(ax, *v0, *v1)
    draw_boson(ax, *v1, *vz)
    draw_straight_line(ax, *v1, *vh, color="black", linewidth=2.7, linestyle=(0, (5, 3)))
    draw_fermion(ax, *vz, 0.95, 0.88, forward=True)
    draw_fermion(ax, *vz, 0.95, 0.60, forward=False)
    draw_boson(ax, *vh, *vw1)
    draw_boson(ax, *vh, *vw2, dashed=True)
    draw_fermion(ax, *vw1, 0.95, 0.48, forward=True)
    draw_fermion(ax, *vw1, 0.95, 0.30, forward=False)
    draw_fermion(ax, *vw2, 0.95, 0.20, forward=True)
    draw_fermion(ax, *vw2, 0.95, 0.06, forward=False)

    ax.scatter(
        [v0[0], v1[0], vz[0], vh[0], vw1[0], vw2[0]],
        [v0[1], v1[1], vz[1], vh[1], vw1[1], vw2[1]],
        s=30,
        color="black",
        zorder=5,
    )

    add_label(ax, 0.02, 0.78, r"$e^+$", ha="left")
    add_label(ax, 0.02, 0.22, r"$e^-$", ha="left")
    add_label(ax, 0.38, 0.56, r"$Z^*$")
    add_label(ax, 0.58, 0.80, r"$Z$")
    add_label(ax, 0.58, 0.20, r"$H$")
    add_label(ax, 0.84, 0.42, r"$W$")
    add_label(ax, 0.84, 0.12, r"$W^*$")
    add_label(ax, 0.97, 0.90, r"$q$")
    add_label(ax, 0.97, 0.58, r"$\bar{q}$")
    add_label(ax, 0.97, 0.50, r"$\ell$")
    add_label(ax, 0.97, 0.28, r"$\nu$")
    add_label(ax, 0.97, 0.22, r"$q$")
    add_label(ax, 0.97, 0.04, r"$\bar{q}'$")

    fig.tight_layout()
    fig.savefig(PLOT_DIR / "feynman_diagram.pdf")
    fig.savefig(PLOT_DIR / "feynman_diagram.png", dpi=180)
    plt.close(fig)


def main() -> None:
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    make_pairing_validation()
    make_feynman_diagram()
    print(f"Generated supporting figures in {PLOT_DIR}")


if __name__ == "__main__":
    main()
