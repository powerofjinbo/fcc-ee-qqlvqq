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
        ("Zcand_m", r"$m_{Z,\mathrm{cand}}$ [GeV]", 91.1876),
        ("Wstar_m", r"$m_{W^*}$ [GeV]", 38.0),
        ("Wlep_m", r"$m_{W,\mathrm{lep}}$ [GeV]", 80.379),
        ("Hcand_m_final", r"$m_{H,\mathrm{cand}}$ [GeV]", 125.0),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(9.5, 7.0))
    axes = axes.flatten()

    for ax, (hist_name, xlabel, ref_mass) in zip(axes, figure_specs):
        sig_values, edges = load_merged_hist(SIGNAL_SAMPLES, hist_name)
        ww_values, _ = load_merged_hist(["p8_ee_WW_ecm240"], hist_name)
        centers = 0.5 * (edges[:-1] + edges[1:])

        ax.step(
            centers,
            normalize(sig_values),
            where="mid",
            color="#d62728",
            linewidth=2.0,
            label=r"Signal: ZH, H$\rightarrow$WW$^*$",
        )
        ax.step(
            centers,
            normalize(ww_values),
            where="mid",
            color="#1f77b4",
            linewidth=1.8,
            label=r"Background: WW",
        )
        ax.axvline(ref_mass, color="black", linestyle="--", linewidth=1.0)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Normalized events")
        ax.grid(alpha=0.25)

    axes[0].legend(frameon=False, fontsize=9, loc="upper right")
    fig.suptitle("Pairing validation after the analysis selection", fontsize=13)
    fig.tight_layout()
    fig.savefig(PLOT_DIR / "pairing_validation.pdf")
    fig.savefig(PLOT_DIR / "pairing_validation.png", dpi=180)
    plt.close(fig)


def draw_line(ax, x1: float, y1: float, x2: float, y2: float, **kwargs) -> None:
    ax.plot([x1, x2], [y1, y2], solid_capstyle="round", **kwargs)


def add_label(ax, x: float, y: float, text: str, **kwargs) -> None:
    defaults = {"fontsize": 11, "ha": "center", "va": "center"}
    defaults.update(kwargs)
    ax.text(x, y, text, **defaults)


def make_feynman_diagram() -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.axis("off")

    style = {"color": "black", "linewidth": 2.0}
    dashed = {"color": "black", "linewidth": 1.6, "linestyle": "--"}

    v0 = (0.28, 0.50)
    v1 = (0.48, 0.50)
    vz = (0.66, 0.74)
    vh = (0.66, 0.26)
    vw1 = (0.82, 0.38)
    vw2 = (0.82, 0.16)

    draw_line(ax, 0.04, 0.76, *v0, **style)
    draw_line(ax, 0.04, 0.24, *v0, **style)
    draw_line(ax, *v0, *v1, **style)
    draw_line(ax, *v1, *vz, **style)
    draw_line(ax, *v1, *vh, **style)
    draw_line(ax, *vz, 0.95, 0.88, **style)
    draw_line(ax, *vz, 0.95, 0.60, **style)
    draw_line(ax, *vh, *vw1, **style)
    draw_line(ax, *vh, *vw2, **dashed)
    draw_line(ax, *vw1, 0.95, 0.48, **style)
    draw_line(ax, *vw1, 0.95, 0.30, **style)
    draw_line(ax, *vw2, 0.95, 0.20, **style)
    draw_line(ax, *vw2, 0.95, 0.06, **style)

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
