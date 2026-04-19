#!/usr/bin/env python3
# Physics validation figure generator for supporting plots used in write-up and review.
#
# This is a line-by-line annotated rewrite for learning and review.
# The executable logic remains unchanged; only explanatory comments were added.

"""Generate paper support figures from existing analysis outputs."""

# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
from __future__ import annotations

# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
from pathlib import Path

# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import matplotlib

# [Workflow] Save inspection plots immediately after generation for review history.
matplotlib.use("Agg")
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import matplotlib.pyplot as plt
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import numpy as np
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import sys
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import uproot


# [Workflow] Configuration binding; this line defines a stable contract across modules.
THIS_DIR = Path(__file__).resolve().parent
# [Workflow] Configuration binding; this line defines a stable contract across modules.
ANALYSIS_DIR = THIS_DIR.parent
# [Context] Supporting line for the active lvqq analysis stage.
sys.path.insert(0, str(ANALYSIS_DIR))

# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
from ml_config import (
# [Context] Supporting line for the active lvqq analysis stage.
    DEFAULT_MODEL_DIR,
# [Context] Supporting line for the active lvqq analysis stage.
    QQ_SAMPLES,
# [Context] Supporting line for the active lvqq analysis stage.
    SAMPLE_PROCESSING_FRACTIONS,
# [Context] Supporting line for the active lvqq analysis stage.
    SIGNAL_SAMPLES,
# [Context] Supporting line for the active lvqq analysis stage.
    WW_SAMPLES,
# [Context] Supporting line for the active lvqq analysis stage.
    ZZ_SAMPLES,
# [Context] Supporting line for the active lvqq analysis stage.
)


# [Workflow] Configuration binding; this line defines a stable contract across modules.
HIST_DIR = ANALYSIS_DIR / "output" / "h_hww_lvqq" / "histmaker" / "ecm240"
# [Workflow] Configuration binding; this line defines a stable contract across modules.
TREE_DIR = ANALYSIS_DIR / "output" / "h_hww_lvqq" / "treemaker" / "ecm240"
# [Workflow] Configuration binding; this line defines a stable contract across modules.
PLOT_DIR = ANALYSIS_DIR / DEFAULT_MODEL_DIR / "plots"
# [Workflow] Configuration binding; this line defines a stable contract across modules.
INT_LUMI = 10.8e6  # pb^-1

# Minimal physics metadata needed for support-figure weighting.
# [Workflow] Configuration binding; this line defines a stable contract across modules.
SAMPLE_INFO = {
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_qqH_HWW_ecm240": {"xsec": 0.01140, "ngen": 1100000},
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_bbH_HWW_ecm240": {"xsec": 0.006350, "ngen": 1000000},
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_ccH_HWW_ecm240": {"xsec": 0.004988, "ngen": 1200000},
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_ssH_HWW_ecm240": {"xsec": 0.006403, "ngen": 1200000},
# [Context] Supporting line for the active lvqq analysis stage.
    "p8_ee_WW_ecm240": {"xsec": 16.4385, "ngen": 373375386},
# [Context] Supporting line for the active lvqq analysis stage.
    "p8_ee_ZZ_ecm240": {"xsec": 1.35899, "ngen": 209700000},
# [Context] Supporting line for the active lvqq analysis stage.
    "wz3p6_ee_uu_ecm240": {"xsec": 11.9447, "ngen": 100790000},
# [Context] Supporting line for the active lvqq analysis stage.
    "wz3p6_ee_dd_ecm240": {"xsec": 10.8037, "ngen": 100910000},
# [Context] Supporting line for the active lvqq analysis stage.
    "wz3p6_ee_cc_ecm240": {"xsec": 11.0595, "ngen": 101290000},
# [Context] Supporting line for the active lvqq analysis stage.
    "wz3p6_ee_ss_ecm240": {"xsec": 10.7725, "ngen": 102348636},
# [Context] Supporting line for the active lvqq analysis stage.
    "wz3p6_ee_bb_ecm240": {"xsec": 10.4299, "ngen": 99490000},
# [Context] Supporting line for the active lvqq analysis stage.
}


# [Physics] Merge related samples before overlaying distributions.
def load_merged_hist(samples: list[str], hist_name: str) -> tuple[np.ndarray, np.ndarray]:
# [Context] Supporting line for the active lvqq analysis stage.
    values = None
# [Context] Supporting line for the active lvqq analysis stage.
    edges = None
# [Context] Supporting line for the active lvqq analysis stage.
    for sample in samples:
# [Context] Supporting line for the active lvqq analysis stage.
        path = HIST_DIR / f"{sample}.root"
# [I/O] Open/write ROOT containers for high-throughput HEP data exchange.
        with uproot.open(path) as root_file:
# [Context] Supporting line for the active lvqq analysis stage.
            hist = root_file[hist_name]
# [Context] Supporting line for the active lvqq analysis stage.
            sample_values, sample_edges = hist.to_numpy()
# [Context] Supporting line for the active lvqq analysis stage.
        if values is None:
# [Context] Supporting line for the active lvqq analysis stage.
            values = sample_values.astype(float)
# [Context] Supporting line for the active lvqq analysis stage.
            edges = sample_edges.astype(float)
# [Context] Supporting line for the active lvqq analysis stage.
        else:
# [Context] Supporting line for the active lvqq analysis stage.
            values += sample_values
# [Context] Supporting line for the active lvqq analysis stage.
    if values is None or edges is None:
# [Context] Supporting line for the active lvqq analysis stage.
        raise RuntimeError(f"Could not load histogram {hist_name!r} from {samples!r}")
# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return values, edges


# [Stats] Unit-normalize shapes so comparisons reflect variable shape, not normalization.
def normalize(values: np.ndarray) -> np.ndarray:
# [Context] Supporting line for the active lvqq analysis stage.
    total = float(np.sum(values))
# [Workflow] Copy exactly the curated deliverables to paper directories.
    return values / total if total > 0.0 else values.copy()


# [Physics] Convert xsec and generated counts into per-sample luminosity scale factors.
def sample_phys_weight(sample: str) -> float:
# [Context] Supporting line for the active lvqq analysis stage.
    info = SAMPLE_INFO[sample]
# [Context] Supporting line for the active lvqq analysis stage.
    frac = SAMPLE_PROCESSING_FRACTIONS.get(sample, 1.0)
# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return INT_LUMI * info["xsec"] / (info["ngen"] * frac)


# [I/O] Load branches and attach per-event physics weights from cross-section assumptions.
def load_weighted_branch(samples: list[str], branch_name: str) -> tuple[np.ndarray, np.ndarray]:
# [Context] Supporting line for the active lvqq analysis stage.
    values_list: list[np.ndarray] = []
# [Context] Supporting line for the active lvqq analysis stage.
    weights_list: list[np.ndarray] = []

# [Context] Supporting line for the active lvqq analysis stage.
    for sample in samples:
# [Context] Supporting line for the active lvqq analysis stage.
        path = TREE_DIR / f"{sample}.root"
# [I/O] Open/write ROOT containers for high-throughput HEP data exchange.
        with uproot.open(path) as root_file:
# [Context] Supporting line for the active lvqq analysis stage.
            if "events" not in root_file:
# [Context] Supporting line for the active lvqq analysis stage.
                continue
# [Context] Supporting line for the active lvqq analysis stage.
            tree = root_file["events"]
# [Context] Supporting line for the active lvqq analysis stage.
            if branch_name not in tree:
# [Context] Supporting line for the active lvqq analysis stage.
                continue
# [Context] Supporting line for the active lvqq analysis stage.
            sample_values = np.asarray(tree[branch_name].array(library="np"), dtype=float)

# [Context] Supporting line for the active lvqq analysis stage.
        if sample_values.size == 0:
# [Context] Supporting line for the active lvqq analysis stage.
            continue

# [Context] Supporting line for the active lvqq analysis stage.
        sample_weight = sample_phys_weight(sample)
# [Context] Supporting line for the active lvqq analysis stage.
        values_list.append(sample_values)
# [Context] Supporting line for the active lvqq analysis stage.
        weights_list.append(np.full(sample_values.shape, sample_weight, dtype=float))

# [Context] Supporting line for the active lvqq analysis stage.
    if not values_list:
# [Context] Supporting line for the active lvqq analysis stage.
        raise RuntimeError(f"Could not load branch {branch_name!r} from {samples!r}")

# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return np.concatenate(values_list), np.concatenate(weights_list)


# [Physics] Validate key reconstructed mass variables with signal-background overlays.
def make_pairing_validation() -> None:
# [Context] Supporting line for the active lvqq analysis stage.
    figure_specs = [
# [Context] Supporting line for the active lvqq analysis stage.
        ("Zcand_m", r"$m_{Z,\mathrm{cand}}$ [GeV]", 91.1876, (40.0, 140.0), r"$Z$ candidate"),
# [Context] Supporting line for the active lvqq analysis stage.
        ("Wstar_m", r"$m_{W^*}$ [GeV]", None, (0.0, 95.0), r"Hadronic $W^*$ candidate"),
# [Context] Supporting line for the active lvqq analysis stage.
        ("Wlep_m", r"$m_{W,\mathrm{lep}}$ [GeV]", 80.379, (30.0, 150.0), r"Leptonic $W$ candidate"),
# [Context] Supporting line for the active lvqq analysis stage.
        ("Hcand_m_final", r"$m_{H,\mathrm{cand}}$ [GeV]", 125.0, (95.0, 155.0), r"Higgs candidate"),
# [Context] Supporting line for the active lvqq analysis stage.
    ]

# [Context] Supporting line for the active lvqq analysis stage.
    fig, axes = plt.subplots(2, 2, figsize=(9.2, 6.8))
# [Context] Supporting line for the active lvqq analysis stage.
    axes = axes.flatten()

# [Context] Supporting line for the active lvqq analysis stage.
    for ax, (hist_name, xlabel, ref_mass, xlim, title) in zip(axes, figure_specs):
# [Context] Supporting line for the active lvqq analysis stage.
        sig_values, edges = load_merged_hist(SIGNAL_SAMPLES, hist_name)
# [Context] Supporting line for the active lvqq analysis stage.
        ww_values, _ = load_merged_hist(["p8_ee_WW_ecm240"], hist_name)
# [Context] Supporting line for the active lvqq analysis stage.
        centers = 0.5 * (edges[:-1] + edges[1:])
# [Context] Supporting line for the active lvqq analysis stage.
        sig_norm = normalize(sig_values)
# [Context] Supporting line for the active lvqq analysis stage.
        ww_norm = normalize(ww_values)

# [Context] Supporting line for the active lvqq analysis stage.
        ax.fill_between(
# [Context] Supporting line for the active lvqq analysis stage.
            centers,
# [Context] Supporting line for the active lvqq analysis stage.
            ww_norm,
# [Context] Supporting line for the active lvqq analysis stage.
            step="mid",
# [Context] Supporting line for the active lvqq analysis stage.
            color="#4C78A8",
# [Context] Supporting line for the active lvqq analysis stage.
            alpha=0.22,
# [Context] Supporting line for the active lvqq analysis stage.
        )
# [Context] Supporting line for the active lvqq analysis stage.
        ax.step(
# [Context] Supporting line for the active lvqq analysis stage.
            centers,
# [Context] Supporting line for the active lvqq analysis stage.
            ww_norm,
# [Context] Supporting line for the active lvqq analysis stage.
            where="mid",
# [Context] Supporting line for the active lvqq analysis stage.
            color="#4C78A8",
# [Context] Supporting line for the active lvqq analysis stage.
            linewidth=1.8,
# [Context] Supporting line for the active lvqq analysis stage.
            label=r"Background: WW",
# [Context] Supporting line for the active lvqq analysis stage.
        )
# [Context] Supporting line for the active lvqq analysis stage.
        ax.step(
# [Context] Supporting line for the active lvqq analysis stage.
            centers,
# [Context] Supporting line for the active lvqq analysis stage.
            sig_norm,
# [Context] Supporting line for the active lvqq analysis stage.
            where="mid",
# [Context] Supporting line for the active lvqq analysis stage.
            color="#D64F4F",
# [Context] Supporting line for the active lvqq analysis stage.
            linewidth=2.2,
# [Context] Supporting line for the active lvqq analysis stage.
            label=r"Signal: ZH, H$\rightarrow$WW$^*$",
# [Context] Supporting line for the active lvqq analysis stage.
        )
# [Context] Supporting line for the active lvqq analysis stage.
        ref_handle = None
# [Context] Supporting line for the active lvqq analysis stage.
        if ref_mass is not None:
# [Context] Supporting line for the active lvqq analysis stage.
            ref_handle = ax.axvline(
# [Context] Supporting line for the active lvqq analysis stage.
                ref_mass,
# [Context] Supporting line for the active lvqq analysis stage.
                color="#222222",
# [Context] Supporting line for the active lvqq analysis stage.
                linestyle="--",
# [Context] Supporting line for the active lvqq analysis stage.
                linewidth=1.3,
# [Context] Supporting line for the active lvqq analysis stage.
                label="Reference mass",
# [Context] Supporting line for the active lvqq analysis stage.
            )
# [Context] Supporting line for the active lvqq analysis stage.
        ax.set_title(title, fontsize=11)
# [Context] Supporting line for the active lvqq analysis stage.
        ax.set_xlabel(xlabel)
# [Context] Supporting line for the active lvqq analysis stage.
        ax.set_ylabel("Normalized yield")
# [Context] Supporting line for the active lvqq analysis stage.
        ax.set_xlim(*xlim)
# [Context] Supporting line for the active lvqq analysis stage.
        ax.grid(axis="y", alpha=0.25)
# [Context] Supporting line for the active lvqq analysis stage.
        ax.spines["top"].set_visible(False)
# [Context] Supporting line for the active lvqq analysis stage.
        ax.spines["right"].set_visible(False)
# [Context] Supporting line for the active lvqq analysis stage.
        ax.legend(frameon=False, fontsize=8.3, loc="upper right")

# [Context] Supporting line for the active lvqq analysis stage.
    fig.tight_layout()
# [Workflow] Save inspection plots immediately after generation for review history.
    fig.savefig(PLOT_DIR / "pairing_validation.pdf")
# [Workflow] Save inspection plots immediately after generation for review history.
    fig.savefig(PLOT_DIR / "pairing_validation.png", dpi=180)
# [Context] Supporting line for the active lvqq analysis stage.
    plt.close(fig)


# [Physics] Inspect jet-geometry variable response for topology separation.
def make_d34_distribution() -> None:
# [Context] Supporting line for the active lvqq analysis stage.
    group_specs = [
# [Context] Supporting line for the active lvqq analysis stage.
        (r"Signal: ZH, H$\rightarrow$WW$^*$", SIGNAL_SAMPLES, "#D64F4F", 2.3),
# [Context] Supporting line for the active lvqq analysis stage.
        ("Background: WW", WW_SAMPLES, "#E68613", 2.0),
# [Context] Supporting line for the active lvqq analysis stage.
        ("Background: ZZ", ZZ_SAMPLES, "#4C78A8", 1.8),
# [Context] Supporting line for the active lvqq analysis stage.
        (r"Background: $q\bar{q}$", QQ_SAMPLES, "#54A24B", 1.8),
# [Context] Supporting line for the active lvqq analysis stage.
    ]

# [Context] Supporting line for the active lvqq analysis stage.
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
# [Context] Supporting line for the active lvqq analysis stage.
    bins = np.linspace(0.0, 60.0, 31)

# [Context] Supporting line for the active lvqq analysis stage.
    for label, samples, color, linewidth in group_specs:
# [Context] Supporting line for the active lvqq analysis stage.
        values, weights = load_weighted_branch(samples, "d_34")
# [Context] Supporting line for the active lvqq analysis stage.
        x = np.sqrt(np.clip(values, 0.0, None))
# [Context] Supporting line for the active lvqq analysis stage.
        total = float(np.sum(weights))
# [Context] Supporting line for the active lvqq analysis stage.
        norm_weights = weights / total if total > 0.0 else weights
# [Context] Supporting line for the active lvqq analysis stage.
        ax.hist(
# [Context] Supporting line for the active lvqq analysis stage.
            x,
# [Context] Supporting line for the active lvqq analysis stage.
            bins=bins,
# [Context] Supporting line for the active lvqq analysis stage.
            weights=norm_weights,
# [Context] Supporting line for the active lvqq analysis stage.
            histtype="step",
# [Context] Supporting line for the active lvqq analysis stage.
            linewidth=linewidth,
# [Context] Supporting line for the active lvqq analysis stage.
            color=color,
# [Context] Supporting line for the active lvqq analysis stage.
            label=label,
# [Context] Supporting line for the active lvqq analysis stage.
        )

# [Context] Supporting line for the active lvqq analysis stage.
    ax.set_xlim(0.0, 60.0)
# [Context] Supporting line for the active lvqq analysis stage.
    ax.set_xlabel(r"$\sqrt{d_{34}}$ [GeV]")
# [Context] Supporting line for the active lvqq analysis stage.
    ax.set_ylabel("Normalized yield")
# [Context] Supporting line for the active lvqq analysis stage.
    ax.grid(axis="y", alpha=0.25)
# [Context] Supporting line for the active lvqq analysis stage.
    ax.spines["top"].set_visible(False)
# [Context] Supporting line for the active lvqq analysis stage.
    ax.spines["right"].set_visible(False)
# [Context] Supporting line for the active lvqq analysis stage.
    ax.legend(frameon=False, fontsize=8.5, loc="upper right")
# [Context] Supporting line for the active lvqq analysis stage.
    fig.tight_layout()
# [Workflow] Save inspection plots immediately after generation for review history.
    fig.savefig(PLOT_DIR / "d34_distribution.pdf")
# [Workflow] Save inspection plots immediately after generation for review history.
    fig.savefig(PLOT_DIR / "d34_distribution.png", dpi=180)
# [Context] Supporting line for the active lvqq analysis stage.
    plt.close(fig)


# [Workflow] generate_supporting_figures.py function draw_straight_line: modularize one operation for deterministic pipeline control.
def draw_straight_line(ax, x1: float, y1: float, x2: float, y2: float, **kwargs) -> None:
# [Context] Supporting line for the active lvqq analysis stage.
    ax.plot([x1, x2], [y1, y2], solid_capstyle="round", **kwargs)


# [Workflow] generate_supporting_figures.py function draw_fermion: modularize one operation for deterministic pipeline control.
def draw_fermion(ax, x1: float, y1: float, x2: float, y2: float, forward: bool = True, **kwargs) -> None:
# [Context] Supporting line for the active lvqq analysis stage.
    line_kwargs = {"color": "black", "linewidth": 2.5}
# [Context] Supporting line for the active lvqq analysis stage.
    line_kwargs.update(kwargs)
# [Context] Supporting line for the active lvqq analysis stage.
    draw_straight_line(ax, x1, y1, x2, y2, **line_kwargs)
# [Context] Supporting line for the active lvqq analysis stage.
    start = (x1, y1) if forward else (x2, y2)
# [Context] Supporting line for the active lvqq analysis stage.
    end = (x2, y2) if forward else (x1, y1)
# [Context] Supporting line for the active lvqq analysis stage.
    ax.annotate(
# [Context] Supporting line for the active lvqq analysis stage.
        "",
# [Context] Supporting line for the active lvqq analysis stage.
        xy=end,
# [Context] Supporting line for the active lvqq analysis stage.
        xytext=start,
# [Context] Supporting line for the active lvqq analysis stage.
        arrowprops={
# [Context] Supporting line for the active lvqq analysis stage.
            "arrowstyle": "-|>",
# [Context] Supporting line for the active lvqq analysis stage.
            "mutation_scale": 15,
# [Context] Supporting line for the active lvqq analysis stage.
            "lw": line_kwargs["linewidth"],
# [Context] Supporting line for the active lvqq analysis stage.
            "color": line_kwargs["color"],
# [Context] Supporting line for the active lvqq analysis stage.
            "shrinkA": 10,
# [Context] Supporting line for the active lvqq analysis stage.
            "shrinkB": 10,
# [Context] Supporting line for the active lvqq analysis stage.
        },
# [Context] Supporting line for the active lvqq analysis stage.
    )


# [Workflow] generate_supporting_figures.py function draw_boson: modularize one operation for deterministic pipeline control.
def draw_boson(ax, x1: float, y1: float, x2: float, y2: float, dashed: bool = False, **kwargs) -> None:
# [Context] Supporting line for the active lvqq analysis stage.
    style = {"color": "black", "linewidth": 2.2}
# [Context] Supporting line for the active lvqq analysis stage.
    style.update(kwargs)
# [Context] Supporting line for the active lvqq analysis stage.
    npts = 200
# [Context] Supporting line for the active lvqq analysis stage.
    x = np.linspace(x1, x2, npts)
# [Context] Supporting line for the active lvqq analysis stage.
    y = np.linspace(y1, y2, npts)
# [Context] Supporting line for the active lvqq analysis stage.
    dx = x2 - x1
# [Context] Supporting line for the active lvqq analysis stage.
    dy = y2 - y1
# [Context] Supporting line for the active lvqq analysis stage.
    length = np.hypot(dx, dy)
# [Context] Supporting line for the active lvqq analysis stage.
    if length == 0:
# [Workflow] Return value hands the constructed object/metric to the next module stage.
        return
# [Context] Supporting line for the active lvqq analysis stage.
    nx = -dy / length
# [Context] Supporting line for the active lvqq analysis stage.
    ny = dx / length
# [Context] Supporting line for the active lvqq analysis stage.
    n_waves = max(5.5, 8.0 * length)
# [Context] Supporting line for the active lvqq analysis stage.
    phase = np.linspace(0.0, 2.0 * np.pi * n_waves, npts)
# [Context] Supporting line for the active lvqq analysis stage.
    amp = 0.010
# [Context] Supporting line for the active lvqq analysis stage.
    x_wavy = x + amp * np.sin(phase) * nx
# [Context] Supporting line for the active lvqq analysis stage.
    y_wavy = y + amp * np.sin(phase) * ny
# [Context] Supporting line for the active lvqq analysis stage.
    if dashed:
# [Context] Supporting line for the active lvqq analysis stage.
        ax.plot(x_wavy, y_wavy, linestyle=(0, (4, 3)), solid_capstyle="round", **style)
# [Context] Supporting line for the active lvqq analysis stage.
    else:
# [Context] Supporting line for the active lvqq analysis stage.
        ax.plot(x_wavy, y_wavy, solid_capstyle="round", **style)


# [Workflow] generate_supporting_figures.py function add_label: modularize one operation for deterministic pipeline control.
def add_label(ax, x: float, y: float, text: str, **kwargs) -> None:
# [Context] Supporting line for the active lvqq analysis stage.
    defaults = {"fontsize": 11, "ha": "center", "va": "center"}
# [Context] Supporting line for the active lvqq analysis stage.
    defaults.update(kwargs)
# [Context] Supporting line for the active lvqq analysis stage.
    ax.text(x, y, text, **defaults)


# [Workflow] generate_supporting_figures.py function label_on_segment: modularize one operation for deterministic pipeline control.
def label_on_segment(
# [Context] Supporting line for the active lvqq analysis stage.
    ax,
# [Context] Supporting line for the active lvqq analysis stage.
    x1: float,
# [Context] Supporting line for the active lvqq analysis stage.
    y1: float,
# [Context] Supporting line for the active lvqq analysis stage.
    x2: float,
# [Context] Supporting line for the active lvqq analysis stage.
    y2: float,
# [Context] Supporting line for the active lvqq analysis stage.
    text: str,
# [Context] Supporting line for the active lvqq analysis stage.
    *,
# [Context] Supporting line for the active lvqq analysis stage.
    t: float = 0.5,
# [Context] Supporting line for the active lvqq analysis stage.
    offset: float = 0.035,
# [Context] Supporting line for the active lvqq analysis stage.
    side: float = 1.0,
# [Context] Supporting line for the active lvqq analysis stage.
    **kwargs,
# [Context] Supporting line for the active lvqq analysis stage.
) -> None:
# [Context] Supporting line for the active lvqq analysis stage.
    dx = x2 - x1
# [Context] Supporting line for the active lvqq analysis stage.
    dy = y2 - y1
# [Context] Supporting line for the active lvqq analysis stage.
    length = np.hypot(dx, dy)
# [Context] Supporting line for the active lvqq analysis stage.
    if length == 0:
# [Context] Supporting line for the active lvqq analysis stage.
        add_label(ax, x1, y1, text, **kwargs)
# [Workflow] Return value hands the constructed object/metric to the next module stage.
        return

# [Context] Supporting line for the active lvqq analysis stage.
    nx = -dy / length
# [Context] Supporting line for the active lvqq analysis stage.
    ny = dx / length
# [Context] Supporting line for the active lvqq analysis stage.
    x = x1 + t * dx + side * offset * nx
# [Context] Supporting line for the active lvqq analysis stage.
    y = y1 + t * dy + side * offset * ny
# [Context] Supporting line for the active lvqq analysis stage.
    defaults = {"fontsize": 11, "ha": "center", "va": "center"}
# [Context] Supporting line for the active lvqq analysis stage.
    defaults.update(kwargs)
# [Context] Supporting line for the active lvqq analysis stage.
    ax.text(x, y, text, **defaults)


# [Physics] Draw diagram summary for explanatory material.
def make_feynman_diagram() -> None:
# [Context] Supporting line for the active lvqq analysis stage.
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
# [Context] Supporting line for the active lvqq analysis stage.
    ax.set_xlim(0.0, 1.0)
# [Context] Supporting line for the active lvqq analysis stage.
    ax.set_ylim(0.0, 1.0)
# [Context] Supporting line for the active lvqq analysis stage.
    ax.set_aspect("equal")
# [Context] Supporting line for the active lvqq analysis stage.
    ax.axis("off")

# [Context] Supporting line for the active lvqq analysis stage.
    v0 = (0.24, 0.50)
# [Context] Supporting line for the active lvqq analysis stage.
    v1 = (0.44, 0.50)
# [Context] Supporting line for the active lvqq analysis stage.
    vz = (0.62, 0.73)
# [Context] Supporting line for the active lvqq analysis stage.
    vh = (0.62, 0.27)
# [Context] Supporting line for the active lvqq analysis stage.
    vw1 = (0.79, 0.39)
# [Context] Supporting line for the active lvqq analysis stage.
    vw2 = (0.79, 0.15)

# [Context] Supporting line for the active lvqq analysis stage.
    eplus = (0.05, 0.76)
# [Context] Supporting line for the active lvqq analysis stage.
    eminus = (0.05, 0.24)
# [Context] Supporting line for the active lvqq analysis stage.
    zq = (0.94, 0.86)
# [Context] Supporting line for the active lvqq analysis stage.
    zqbar = (0.94, 0.60)
# [Context] Supporting line for the active lvqq analysis stage.
    wl = (0.94, 0.49)
# [Context] Supporting line for the active lvqq analysis stage.
    wnu = (0.94, 0.29)
# [Context] Supporting line for the active lvqq analysis stage.
    wq = (0.94, 0.20)
# [Context] Supporting line for the active lvqq analysis stage.
    wqbar = (0.94, 0.04)

# [Context] Supporting line for the active lvqq analysis stage.
    draw_fermion(ax, *eplus, *v0, forward=False)
# [Context] Supporting line for the active lvqq analysis stage.
    draw_fermion(ax, *eminus, *v0, forward=True)
# [Context] Supporting line for the active lvqq analysis stage.
    draw_boson(ax, *v0, *v1)
# [Context] Supporting line for the active lvqq analysis stage.
    draw_boson(ax, *v1, *vz)
# [Context] Supporting line for the active lvqq analysis stage.
    draw_straight_line(ax, *v1, *vh, color="black", linewidth=2.3, linestyle=(0, (5, 3)))
# [Context] Supporting line for the active lvqq analysis stage.
    draw_fermion(ax, *vz, *zq, forward=True)
# [Context] Supporting line for the active lvqq analysis stage.
    draw_fermion(ax, *vz, *zqbar, forward=False)
# [Context] Supporting line for the active lvqq analysis stage.
    draw_boson(ax, *vh, *vw1)
# [Context] Supporting line for the active lvqq analysis stage.
    draw_boson(ax, *vh, *vw2, dashed=True)
# [Context] Supporting line for the active lvqq analysis stage.
    draw_fermion(ax, *vw1, *wl, forward=True)
# [Context] Supporting line for the active lvqq analysis stage.
    draw_fermion(ax, *vw1, *wnu, forward=False)
# [Context] Supporting line for the active lvqq analysis stage.
    draw_fermion(ax, *vw2, *wq, forward=True)
# [Context] Supporting line for the active lvqq analysis stage.
    draw_fermion(ax, *vw2, *wqbar, forward=False)

# [Context] Supporting line for the active lvqq analysis stage.
    ax.scatter(
# [Context] Supporting line for the active lvqq analysis stage.
        [v0[0], v1[0], vz[0], vh[0], vw1[0], vw2[0]],
# [Context] Supporting line for the active lvqq analysis stage.
        [v0[1], v1[1], vz[1], vh[1], vw1[1], vw2[1]],
# [Context] Supporting line for the active lvqq analysis stage.
        s=26,
# [Context] Supporting line for the active lvqq analysis stage.
        color="black",
# [Context] Supporting line for the active lvqq analysis stage.
        zorder=5,
# [Context] Supporting line for the active lvqq analysis stage.
    )

# [Context] Supporting line for the active lvqq analysis stage.
    label_on_segment(ax, *v0, *v1, r"$Z^*$", offset=0.045, side=1.0)
# [Context] Supporting line for the active lvqq analysis stage.
    label_on_segment(ax, *v1, *vz, r"$Z$", offset=0.04, side=1.0)
# [Context] Supporting line for the active lvqq analysis stage.
    label_on_segment(ax, *v1, *vh, r"$H$", offset=0.045, side=-1.0)
# [Context] Supporting line for the active lvqq analysis stage.
    label_on_segment(ax, *vh, *vw1, r"$W$", offset=0.04, side=1.0)
# [Context] Supporting line for the active lvqq analysis stage.
    label_on_segment(ax, *vh, *vw2, r"$W^*$", offset=0.04, side=-1.0)

# [Context] Supporting line for the active lvqq analysis stage.
    add_label(ax, 0.025, 0.78, r"$e^+$", ha="left")
# [Context] Supporting line for the active lvqq analysis stage.
    add_label(ax, 0.025, 0.22, r"$e^-$", ha="left")
# [Context] Supporting line for the active lvqq analysis stage.
    add_label(ax, 0.965, 0.88, r"$q$", ha="left")
# [Context] Supporting line for the active lvqq analysis stage.
    add_label(ax, 0.965, 0.58, r"$\bar{q}$", ha="left")
# [Context] Supporting line for the active lvqq analysis stage.
    add_label(ax, 0.965, 0.51, r"$\ell$", ha="left")
# [Context] Supporting line for the active lvqq analysis stage.
    add_label(ax, 0.965, 0.27, r"$\nu$", ha="left")
# [Context] Supporting line for the active lvqq analysis stage.
    add_label(ax, 0.965, 0.21, r"$q$", ha="left")
# [Context] Supporting line for the active lvqq analysis stage.
    add_label(ax, 0.965, 0.03, r"$\bar{q}'$", ha="left")

# [Context] Supporting line for the active lvqq analysis stage.
    fig.tight_layout(pad=0.15)
# [Workflow] Save inspection plots immediately after generation for review history.
    fig.savefig(PLOT_DIR / "feynman_diagram.pdf")
# [Workflow] Save inspection plots immediately after generation for review history.
    fig.savefig(PLOT_DIR / "feynman_diagram.png", dpi=180)
# [Context] Supporting line for the active lvqq analysis stage.
    plt.close(fig)


# [Workflow] Batch-generate all supplemental figures used by the analysis note/paper.
def main() -> None:
# [Context] Supporting line for the active lvqq analysis stage.
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
# [Context] Supporting line for the active lvqq analysis stage.
    make_pairing_validation()
# [Context] Supporting line for the active lvqq analysis stage.
    make_feynman_diagram()
# [Context] Supporting line for the active lvqq analysis stage.
    make_d34_distribution()
# [Context] Supporting line for the active lvqq analysis stage.
    print(f"Generated supporting figures in {PLOT_DIR}")


# [Context] Supporting line for the active lvqq analysis stage.
if __name__ == "__main__":
# [Context] Supporting line for the active lvqq analysis stage.
    main()
