# Annotated rewrite generated for: paper/generate_supporting_figures.py
# L1 [Original comment]: #!/usr/bin/env python3
#!/usr/bin/env python3
# L2 [Executable statement]: """Generate paper support figures from existing analysis outputs."""
"""Generate paper support figures from existing analysis outputs."""
# L3 [Blank separator]: 

# L4 [Import statement]: from __future__ import annotations
from __future__ import annotations
# L5 [Blank separator]: 

# L6 [Import statement]: from pathlib import Path
from pathlib import Path
# L7 [Blank separator]: 

# L8 [Import statement]: import matplotlib
import matplotlib
# L9 [Blank separator]: 

# L10 [Executable statement]: matplotlib.use("Agg")
matplotlib.use("Agg")
# L11 [Import statement]: import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
# L12 [Import statement]: import numpy as np
import numpy as np
# L13 [Import statement]: import sys
import sys
# L14 [Import statement]: import uproot
import uproot
# L15 [Blank separator]: 

# L16 [Blank separator]: 

# L17 [Executable statement]: THIS_DIR = Path(__file__).resolve().parent
THIS_DIR = Path(__file__).resolve().parent
# L18 [Executable statement]: ANALYSIS_DIR = THIS_DIR.parent
ANALYSIS_DIR = THIS_DIR.parent
# L19 [Executable statement]: sys.path.insert(0, str(ANALYSIS_DIR))
sys.path.insert(0, str(ANALYSIS_DIR))
# L20 [Blank separator]: 

# L21 [Import statement]: from ml_config import (
from ml_config import (
# L22 [Executable statement]:     DEFAULT_MODEL_DIR,
    DEFAULT_MODEL_DIR,
# L23 [Executable statement]:     QQ_SAMPLES,
    QQ_SAMPLES,
# L24 [Executable statement]:     SAMPLE_PROCESSING_FRACTIONS,
    SAMPLE_PROCESSING_FRACTIONS,
# L25 [Executable statement]:     SIGNAL_SAMPLES,
    SIGNAL_SAMPLES,
# L26 [Executable statement]:     WW_SAMPLES,
    WW_SAMPLES,
# L27 [Executable statement]:     ZZ_SAMPLES,
    ZZ_SAMPLES,
# L28 [Executable statement]: )
)
# L29 [Blank separator]: 

# L30 [Blank separator]: 

# L31 [Executable statement]: HIST_DIR = ANALYSIS_DIR / "output" / "h_hww_lvqq" / "histmaker" / "ecm240"
HIST_DIR = ANALYSIS_DIR / "output" / "h_hww_lvqq" / "histmaker" / "ecm240"
# L32 [Executable statement]: TREE_DIR = ANALYSIS_DIR / "output" / "h_hww_lvqq" / "treemaker" / "ecm240"
TREE_DIR = ANALYSIS_DIR / "output" / "h_hww_lvqq" / "treemaker" / "ecm240"
# L33 [Executable statement]: PLOT_DIR = ANALYSIS_DIR / DEFAULT_MODEL_DIR / "plots"
PLOT_DIR = ANALYSIS_DIR / DEFAULT_MODEL_DIR / "plots"
# L34 [Executable statement]: INT_LUMI = 10.8e6  # pb^-1
INT_LUMI = 10.8e6  # pb^-1
# L35 [Blank separator]: 

# L36 [Original comment]: # Minimal physics metadata needed for support-figure weighting.
# Minimal physics metadata needed for support-figure weighting.
# L37 [Executable statement]: SAMPLE_INFO = {
SAMPLE_INFO = {
# L38 [Executable statement]:     "wzp6_ee_qqH_HWW_ecm240": {"xsec": 0.01140, "ngen": 1100000},
    "wzp6_ee_qqH_HWW_ecm240": {"xsec": 0.01140, "ngen": 1100000},
# L39 [Executable statement]:     "wzp6_ee_bbH_HWW_ecm240": {"xsec": 0.006350, "ngen": 1000000},
    "wzp6_ee_bbH_HWW_ecm240": {"xsec": 0.006350, "ngen": 1000000},
# L40 [Executable statement]:     "wzp6_ee_ccH_HWW_ecm240": {"xsec": 0.004988, "ngen": 1200000},
    "wzp6_ee_ccH_HWW_ecm240": {"xsec": 0.004988, "ngen": 1200000},
# L41 [Executable statement]:     "wzp6_ee_ssH_HWW_ecm240": {"xsec": 0.006403, "ngen": 1200000},
    "wzp6_ee_ssH_HWW_ecm240": {"xsec": 0.006403, "ngen": 1200000},
# L42 [Executable statement]:     "p8_ee_WW_ecm240": {"xsec": 16.4385, "ngen": 373375386},
    "p8_ee_WW_ecm240": {"xsec": 16.4385, "ngen": 373375386},
# L43 [Executable statement]:     "p8_ee_ZZ_ecm240": {"xsec": 1.35899, "ngen": 209700000},
    "p8_ee_ZZ_ecm240": {"xsec": 1.35899, "ngen": 209700000},
# L44 [Executable statement]:     "wz3p6_ee_uu_ecm240": {"xsec": 11.9447, "ngen": 100790000},
    "wz3p6_ee_uu_ecm240": {"xsec": 11.9447, "ngen": 100790000},
# L45 [Executable statement]:     "wz3p6_ee_dd_ecm240": {"xsec": 10.8037, "ngen": 100910000},
    "wz3p6_ee_dd_ecm240": {"xsec": 10.8037, "ngen": 100910000},
# L46 [Executable statement]:     "wz3p6_ee_cc_ecm240": {"xsec": 11.0595, "ngen": 101290000},
    "wz3p6_ee_cc_ecm240": {"xsec": 11.0595, "ngen": 101290000},
# L47 [Executable statement]:     "wz3p6_ee_ss_ecm240": {"xsec": 10.7725, "ngen": 102348636},
    "wz3p6_ee_ss_ecm240": {"xsec": 10.7725, "ngen": 102348636},
# L48 [Executable statement]:     "wz3p6_ee_bb_ecm240": {"xsec": 10.4299, "ngen": 99490000},
    "wz3p6_ee_bb_ecm240": {"xsec": 10.4299, "ngen": 99490000},
# L49 [Executable statement]: }
}
# L50 [Blank separator]: 

# L51 [Blank separator]: 

# L52 [Function definition]: def load_merged_hist(samples: list[str], hist_name: str) -> tuple[np.ndarray, np.ndarray]:
def load_merged_hist(samples: list[str], hist_name: str) -> tuple[np.ndarray, np.ndarray]:
# L53 [Executable statement]:     values = None
    values = None
# L54 [Executable statement]:     edges = None
    edges = None
# L55 [Loop over iterable]:     for sample in samples:
    for sample in samples:
# L56 [Executable statement]:         path = HIST_DIR / f"{sample}.root"
        path = HIST_DIR / f"{sample}.root"
# L57 [Context manager block]:         with uproot.open(path) as root_file:
        with uproot.open(path) as root_file:
# L58 [Executable statement]:             hist = root_file[hist_name]
            hist = root_file[hist_name]
# L59 [Executable statement]:             sample_values, sample_edges = hist.to_numpy()
            sample_values, sample_edges = hist.to_numpy()
# L60 [Conditional block]:         if values is None:
        if values is None:
# L61 [Executable statement]:             values = sample_values.astype(float)
            values = sample_values.astype(float)
# L62 [Executable statement]:             edges = sample_edges.astype(float)
            edges = sample_edges.astype(float)
# L63 [Else branch]:         else:
        else:
# L64 [Executable statement]:             values += sample_values
            values += sample_values
# L65 [Conditional block]:     if values is None or edges is None:
    if values is None or edges is None:
# L66 [Executable statement]:         raise RuntimeError(f"Could not load histogram {hist_name!r} from {samples!r}")
        raise RuntimeError(f"Could not load histogram {hist_name!r} from {samples!r}")
# L67 [Function return]:     return values, edges
    return values, edges
# L68 [Blank separator]: 

# L69 [Blank separator]: 

# L70 [Function definition]: def normalize(values: np.ndarray) -> np.ndarray:
def normalize(values: np.ndarray) -> np.ndarray:
# L71 [Executable statement]:     total = float(np.sum(values))
    total = float(np.sum(values))
# L72 [Function return]:     return values / total if total > 0.0 else values.copy()
    return values / total if total > 0.0 else values.copy()
# L73 [Blank separator]: 

# L74 [Blank separator]: 

# L75 [Function definition]: def sample_phys_weight(sample: str) -> float:
def sample_phys_weight(sample: str) -> float:
# L76 [Executable statement]:     info = SAMPLE_INFO[sample]
    info = SAMPLE_INFO[sample]
# L77 [Executable statement]:     frac = SAMPLE_PROCESSING_FRACTIONS.get(sample, 1.0)
    frac = SAMPLE_PROCESSING_FRACTIONS.get(sample, 1.0)
# L78 [Function return]:     return INT_LUMI * info["xsec"] / (info["ngen"] * frac)
    return INT_LUMI * info["xsec"] / (info["ngen"] * frac)
# L79 [Blank separator]: 

# L80 [Blank separator]: 

# L81 [Function definition]: def load_weighted_branch(samples: list[str], branch_name: str) -> tuple[np.ndarray, np.ndarray]:
def load_weighted_branch(samples: list[str], branch_name: str) -> tuple[np.ndarray, np.ndarray]:
# L82 [Executable statement]:     values_list: list[np.ndarray] = []
    values_list: list[np.ndarray] = []
# L83 [Executable statement]:     weights_list: list[np.ndarray] = []
    weights_list: list[np.ndarray] = []
# L84 [Blank separator]: 

# L85 [Loop over iterable]:     for sample in samples:
    for sample in samples:
# L86 [Executable statement]:         path = TREE_DIR / f"{sample}.root"
        path = TREE_DIR / f"{sample}.root"
# L87 [Context manager block]:         with uproot.open(path) as root_file:
        with uproot.open(path) as root_file:
# L88 [Conditional block]:             if "events" not in root_file:
            if "events" not in root_file:
# L89 [Executable statement]:                 continue
                continue
# L90 [Executable statement]:             tree = root_file["events"]
            tree = root_file["events"]
# L91 [Conditional block]:             if branch_name not in tree:
            if branch_name not in tree:
# L92 [Executable statement]:                 continue
                continue
# L93 [Executable statement]:             sample_values = np.asarray(tree[branch_name].array(library="np"), dtype=float)
            sample_values = np.asarray(tree[branch_name].array(library="np"), dtype=float)
# L94 [Blank separator]: 

# L95 [Conditional block]:         if sample_values.size == 0:
        if sample_values.size == 0:
# L96 [Executable statement]:             continue
            continue
# L97 [Blank separator]: 

# L98 [Executable statement]:         sample_weight = sample_phys_weight(sample)
        sample_weight = sample_phys_weight(sample)
# L99 [Executable statement]:         values_list.append(sample_values)
        values_list.append(sample_values)
# L100 [Executable statement]:         weights_list.append(np.full(sample_values.shape, sample_weight, dtype=float))
        weights_list.append(np.full(sample_values.shape, sample_weight, dtype=float))
# L101 [Blank separator]: 

# L102 [Conditional block]:     if not values_list:
    if not values_list:
# L103 [Executable statement]:         raise RuntimeError(f"Could not load branch {branch_name!r} from {samples!r}")
        raise RuntimeError(f"Could not load branch {branch_name!r} from {samples!r}")
# L104 [Blank separator]: 

# L105 [Function return]:     return np.concatenate(values_list), np.concatenate(weights_list)
    return np.concatenate(values_list), np.concatenate(weights_list)
# L106 [Blank separator]: 

# L107 [Blank separator]: 

# L108 [Function definition]: def make_pairing_validation() -> None:
def make_pairing_validation() -> None:
# L109 [Executable statement]:     figure_specs = [
    figure_specs = [
# L110 [Executable statement]:         ("Zcand_m", r"$m_{Z,\mathrm{cand}}$ [GeV]", 91.1876, (40.0, 140.0), r"$Z$ candidate"),
        ("Zcand_m", r"$m_{Z,\mathrm{cand}}$ [GeV]", 91.1876, (40.0, 140.0), r"$Z$ candidate"),
# L111 [Executable statement]:         ("Wstar_m", r"$m_{W^*}$ [GeV]", None, (0.0, 95.0), r"Hadronic $W^*$ candidate"),
        ("Wstar_m", r"$m_{W^*}$ [GeV]", None, (0.0, 95.0), r"Hadronic $W^*$ candidate"),
# L112 [Executable statement]:         ("Wlep_m", r"$m_{W,\mathrm{lep}}$ [GeV]", 80.379, (30.0, 150.0), r"Leptonic $W$ candidate"),
        ("Wlep_m", r"$m_{W,\mathrm{lep}}$ [GeV]", 80.379, (30.0, 150.0), r"Leptonic $W$ candidate"),
# L113 [Executable statement]:         ("Hcand_m_final", r"$m_{H,\mathrm{cand}}$ [GeV]", 125.0, (95.0, 155.0), r"Higgs candidate"),
        ("Hcand_m_final", r"$m_{H,\mathrm{cand}}$ [GeV]", 125.0, (95.0, 155.0), r"Higgs candidate"),
# L114 [Executable statement]:     ]
    ]
# L115 [Blank separator]: 

# L116 [Executable statement]:     fig, axes = plt.subplots(2, 2, figsize=(9.2, 6.8))
    fig, axes = plt.subplots(2, 2, figsize=(9.2, 6.8))
# L117 [Executable statement]:     axes = axes.flatten()
    axes = axes.flatten()
# L118 [Blank separator]: 

# L119 [Loop over iterable]:     for ax, (hist_name, xlabel, ref_mass, xlim, title) in zip(axes, figure_specs):
    for ax, (hist_name, xlabel, ref_mass, xlim, title) in zip(axes, figure_specs):
# L120 [Executable statement]:         sig_values, edges = load_merged_hist(SIGNAL_SAMPLES, hist_name)
        sig_values, edges = load_merged_hist(SIGNAL_SAMPLES, hist_name)
# L121 [Executable statement]:         ww_values, _ = load_merged_hist(["p8_ee_WW_ecm240"], hist_name)
        ww_values, _ = load_merged_hist(["p8_ee_WW_ecm240"], hist_name)
# L122 [Executable statement]:         centers = 0.5 * (edges[:-1] + edges[1:])
        centers = 0.5 * (edges[:-1] + edges[1:])
# L123 [Executable statement]:         sig_norm = normalize(sig_values)
        sig_norm = normalize(sig_values)
# L124 [Executable statement]:         ww_norm = normalize(ww_values)
        ww_norm = normalize(ww_values)
# L125 [Blank separator]: 

# L126 [Executable statement]:         ax.fill_between(
        ax.fill_between(
# L127 [Executable statement]:             centers,
            centers,
# L128 [Executable statement]:             ww_norm,
            ww_norm,
# L129 [Executable statement]:             step="mid",
            step="mid",
# L130 [Executable statement]:             color="#4C78A8",
            color="#4C78A8",
# L131 [Executable statement]:             alpha=0.22,
            alpha=0.22,
# L132 [Executable statement]:         )
        )
# L133 [Executable statement]:         ax.step(
        ax.step(
# L134 [Executable statement]:             centers,
            centers,
# L135 [Executable statement]:             ww_norm,
            ww_norm,
# L136 [Executable statement]:             where="mid",
            where="mid",
# L137 [Executable statement]:             color="#4C78A8",
            color="#4C78A8",
# L138 [Executable statement]:             linewidth=1.8,
            linewidth=1.8,
# L139 [Executable statement]:             label=r"Background: WW",
            label=r"Background: WW",
# L140 [Executable statement]:         )
        )
# L141 [Executable statement]:         ax.step(
        ax.step(
# L142 [Executable statement]:             centers,
            centers,
# L143 [Executable statement]:             sig_norm,
            sig_norm,
# L144 [Executable statement]:             where="mid",
            where="mid",
# L145 [Executable statement]:             color="#D64F4F",
            color="#D64F4F",
# L146 [Executable statement]:             linewidth=2.2,
            linewidth=2.2,
# L147 [Executable statement]:             label=r"Signal: ZH, H$\rightarrow$WW$^*$",
            label=r"Signal: ZH, H$\rightarrow$WW$^*$",
# L148 [Executable statement]:         )
        )
# L149 [Executable statement]:         ref_handle = None
        ref_handle = None
# L150 [Conditional block]:         if ref_mass is not None:
        if ref_mass is not None:
# L151 [Executable statement]:             ref_handle = ax.axvline(
            ref_handle = ax.axvline(
# L152 [Executable statement]:                 ref_mass,
                ref_mass,
# L153 [Executable statement]:                 color="#222222",
                color="#222222",
# L154 [Executable statement]:                 linestyle="--",
                linestyle="--",
# L155 [Executable statement]:                 linewidth=1.3,
                linewidth=1.3,
# L156 [Executable statement]:                 label="Reference mass",
                label="Reference mass",
# L157 [Executable statement]:             )
            )
# L158 [Executable statement]:         ax.set_title(title, fontsize=11)
        ax.set_title(title, fontsize=11)
# L159 [Executable statement]:         ax.set_xlabel(xlabel)
        ax.set_xlabel(xlabel)
# L160 [Executable statement]:         ax.set_ylabel("Normalized yield")
        ax.set_ylabel("Normalized yield")
# L161 [Executable statement]:         ax.set_xlim(*xlim)
        ax.set_xlim(*xlim)
# L162 [Executable statement]:         ax.grid(axis="y", alpha=0.25)
        ax.grid(axis="y", alpha=0.25)
# L163 [Executable statement]:         ax.spines["top"].set_visible(False)
        ax.spines["top"].set_visible(False)
# L164 [Executable statement]:         ax.spines["right"].set_visible(False)
        ax.spines["right"].set_visible(False)
# L165 [Executable statement]:         ax.legend(frameon=False, fontsize=8.3, loc="upper right")
        ax.legend(frameon=False, fontsize=8.3, loc="upper right")
# L166 [Blank separator]: 

# L167 [Executable statement]:     fig.tight_layout()
    fig.tight_layout()
# L168 [Executable statement]:     fig.savefig(PLOT_DIR / "pairing_validation.pdf")
    fig.savefig(PLOT_DIR / "pairing_validation.pdf")
# L169 [Executable statement]:     fig.savefig(PLOT_DIR / "pairing_validation.png", dpi=180)
    fig.savefig(PLOT_DIR / "pairing_validation.png", dpi=180)
# L170 [Executable statement]:     plt.close(fig)
    plt.close(fig)
# L171 [Blank separator]: 

# L172 [Blank separator]: 

# L173 [Function definition]: def make_d34_distribution() -> None:
def make_d34_distribution() -> None:
# L174 [Executable statement]:     group_specs = [
    group_specs = [
# L175 [Executable statement]:         (r"Signal: ZH, H$\rightarrow$WW$^*$", SIGNAL_SAMPLES, "#D64F4F", 2.3),
        (r"Signal: ZH, H$\rightarrow$WW$^*$", SIGNAL_SAMPLES, "#D64F4F", 2.3),
# L176 [Executable statement]:         ("Background: WW", WW_SAMPLES, "#E68613", 2.0),
        ("Background: WW", WW_SAMPLES, "#E68613", 2.0),
# L177 [Executable statement]:         ("Background: ZZ", ZZ_SAMPLES, "#4C78A8", 1.8),
        ("Background: ZZ", ZZ_SAMPLES, "#4C78A8", 1.8),
# L178 [Executable statement]:         (r"Background: $q\bar{q}$", QQ_SAMPLES, "#54A24B", 1.8),
        (r"Background: $q\bar{q}$", QQ_SAMPLES, "#54A24B", 1.8),
# L179 [Executable statement]:     ]
    ]
# L180 [Blank separator]: 

# L181 [Executable statement]:     fig, ax = plt.subplots(figsize=(6.4, 4.4))
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
# L182 [Executable statement]:     bins = np.linspace(0.0, 60.0, 31)
    bins = np.linspace(0.0, 60.0, 31)
# L183 [Blank separator]: 

# L184 [Loop over iterable]:     for label, samples, color, linewidth in group_specs:
    for label, samples, color, linewidth in group_specs:
# L185 [Executable statement]:         values, weights = load_weighted_branch(samples, "d_34")
        values, weights = load_weighted_branch(samples, "d_34")
# L186 [Executable statement]:         x = np.sqrt(np.clip(values, 0.0, None))
        x = np.sqrt(np.clip(values, 0.0, None))
# L187 [Executable statement]:         total = float(np.sum(weights))
        total = float(np.sum(weights))
# L188 [Executable statement]:         norm_weights = weights / total if total > 0.0 else weights
        norm_weights = weights / total if total > 0.0 else weights
# L189 [Executable statement]:         ax.hist(
        ax.hist(
# L190 [Executable statement]:             x,
            x,
# L191 [Executable statement]:             bins=bins,
            bins=bins,
# L192 [Executable statement]:             weights=norm_weights,
            weights=norm_weights,
# L193 [Executable statement]:             histtype="step",
            histtype="step",
# L194 [Executable statement]:             linewidth=linewidth,
            linewidth=linewidth,
# L195 [Executable statement]:             color=color,
            color=color,
# L196 [Executable statement]:             label=label,
            label=label,
# L197 [Executable statement]:         )
        )
# L198 [Blank separator]: 

# L199 [Executable statement]:     ax.set_xlim(0.0, 60.0)
    ax.set_xlim(0.0, 60.0)
# L200 [Executable statement]:     ax.set_xlabel(r"$\sqrt{d_{34}}$ [GeV]")
    ax.set_xlabel(r"$\sqrt{d_{34}}$ [GeV]")
# L201 [Executable statement]:     ax.set_ylabel("Normalized yield")
    ax.set_ylabel("Normalized yield")
# L202 [Executable statement]:     ax.grid(axis="y", alpha=0.25)
    ax.grid(axis="y", alpha=0.25)
# L203 [Executable statement]:     ax.spines["top"].set_visible(False)
    ax.spines["top"].set_visible(False)
# L204 [Executable statement]:     ax.spines["right"].set_visible(False)
    ax.spines["right"].set_visible(False)
# L205 [Executable statement]:     ax.legend(frameon=False, fontsize=8.5, loc="upper right")
    ax.legend(frameon=False, fontsize=8.5, loc="upper right")
# L206 [Executable statement]:     fig.tight_layout()
    fig.tight_layout()
# L207 [Executable statement]:     fig.savefig(PLOT_DIR / "d34_distribution.pdf")
    fig.savefig(PLOT_DIR / "d34_distribution.pdf")
# L208 [Executable statement]:     fig.savefig(PLOT_DIR / "d34_distribution.png", dpi=180)
    fig.savefig(PLOT_DIR / "d34_distribution.png", dpi=180)
# L209 [Executable statement]:     plt.close(fig)
    plt.close(fig)
# L210 [Blank separator]: 

# L211 [Blank separator]: 

# L212 [Function definition]: def draw_straight_line(ax, x1: float, y1: float, x2: float, y2: float, **kwargs) -> None:
def draw_straight_line(ax, x1: float, y1: float, x2: float, y2: float, **kwargs) -> None:
# L213 [Executable statement]:     ax.plot([x1, x2], [y1, y2], solid_capstyle="round", **kwargs)
    ax.plot([x1, x2], [y1, y2], solid_capstyle="round", **kwargs)
# L214 [Blank separator]: 

# L215 [Blank separator]: 

# L216 [Function definition]: def draw_fermion(ax, x1: float, y1: float, x2: float, y2: float, forward: bool = True, **kwargs) -> None:
def draw_fermion(ax, x1: float, y1: float, x2: float, y2: float, forward: bool = True, **kwargs) -> None:
# L217 [Executable statement]:     line_kwargs = {"color": "black", "linewidth": 2.5}
    line_kwargs = {"color": "black", "linewidth": 2.5}
# L218 [Executable statement]:     line_kwargs.update(kwargs)
    line_kwargs.update(kwargs)
# L219 [Executable statement]:     draw_straight_line(ax, x1, y1, x2, y2, **line_kwargs)
    draw_straight_line(ax, x1, y1, x2, y2, **line_kwargs)
# L220 [Executable statement]:     start = (x1, y1) if forward else (x2, y2)
    start = (x1, y1) if forward else (x2, y2)
# L221 [Executable statement]:     end = (x2, y2) if forward else (x1, y1)
    end = (x2, y2) if forward else (x1, y1)
# L222 [Executable statement]:     ax.annotate(
    ax.annotate(
# L223 [Executable statement]:         "",
        "",
# L224 [Executable statement]:         xy=end,
        xy=end,
# L225 [Executable statement]:         xytext=start,
        xytext=start,
# L226 [Executable statement]:         arrowprops={
        arrowprops={
# L227 [Executable statement]:             "arrowstyle": "-|>",
            "arrowstyle": "-|>",
# L228 [Executable statement]:             "mutation_scale": 15,
            "mutation_scale": 15,
# L229 [Executable statement]:             "lw": line_kwargs["linewidth"],
            "lw": line_kwargs["linewidth"],
# L230 [Executable statement]:             "color": line_kwargs["color"],
            "color": line_kwargs["color"],
# L231 [Executable statement]:             "shrinkA": 10,
            "shrinkA": 10,
# L232 [Executable statement]:             "shrinkB": 10,
            "shrinkB": 10,
# L233 [Executable statement]:         },
        },
# L234 [Executable statement]:     )
    )
# L235 [Blank separator]: 

# L236 [Blank separator]: 

# L237 [Function definition]: def draw_boson(ax, x1: float, y1: float, x2: float, y2: float, dashed: bool = False, **kwargs) -> None:
def draw_boson(ax, x1: float, y1: float, x2: float, y2: float, dashed: bool = False, **kwargs) -> None:
# L238 [Executable statement]:     style = {"color": "black", "linewidth": 2.2}
    style = {"color": "black", "linewidth": 2.2}
# L239 [Executable statement]:     style.update(kwargs)
    style.update(kwargs)
# L240 [Executable statement]:     npts = 200
    npts = 200
# L241 [Executable statement]:     x = np.linspace(x1, x2, npts)
    x = np.linspace(x1, x2, npts)
# L242 [Executable statement]:     y = np.linspace(y1, y2, npts)
    y = np.linspace(y1, y2, npts)
# L243 [Executable statement]:     dx = x2 - x1
    dx = x2 - x1
# L244 [Executable statement]:     dy = y2 - y1
    dy = y2 - y1
# L245 [Executable statement]:     length = np.hypot(dx, dy)
    length = np.hypot(dx, dy)
# L246 [Conditional block]:     if length == 0:
    if length == 0:
# L247 [Return from function]:         return
        return
# L248 [Executable statement]:     nx = -dy / length
    nx = -dy / length
# L249 [Executable statement]:     ny = dx / length
    ny = dx / length
# L250 [Executable statement]:     n_waves = max(5.5, 8.0 * length)
    n_waves = max(5.5, 8.0 * length)
# L251 [Executable statement]:     phase = np.linspace(0.0, 2.0 * np.pi * n_waves, npts)
    phase = np.linspace(0.0, 2.0 * np.pi * n_waves, npts)
# L252 [Executable statement]:     amp = 0.010
    amp = 0.010
# L253 [Executable statement]:     x_wavy = x + amp * np.sin(phase) * nx
    x_wavy = x + amp * np.sin(phase) * nx
# L254 [Executable statement]:     y_wavy = y + amp * np.sin(phase) * ny
    y_wavy = y + amp * np.sin(phase) * ny
# L255 [Conditional block]:     if dashed:
    if dashed:
# L256 [Executable statement]:         ax.plot(x_wavy, y_wavy, linestyle=(0, (4, 3)), solid_capstyle="round", **style)
        ax.plot(x_wavy, y_wavy, linestyle=(0, (4, 3)), solid_capstyle="round", **style)
# L257 [Else branch]:     else:
    else:
# L258 [Executable statement]:         ax.plot(x_wavy, y_wavy, solid_capstyle="round", **style)
        ax.plot(x_wavy, y_wavy, solid_capstyle="round", **style)
# L259 [Blank separator]: 

# L260 [Blank separator]: 

# L261 [Function definition]: def add_label(ax, x: float, y: float, text: str, **kwargs) -> None:
def add_label(ax, x: float, y: float, text: str, **kwargs) -> None:
# L262 [Executable statement]:     defaults = {"fontsize": 11, "ha": "center", "va": "center"}
    defaults = {"fontsize": 11, "ha": "center", "va": "center"}
# L263 [Executable statement]:     defaults.update(kwargs)
    defaults.update(kwargs)
# L264 [Executable statement]:     ax.text(x, y, text, **defaults)
    ax.text(x, y, text, **defaults)
# L265 [Blank separator]: 

# L266 [Blank separator]: 

# L267 [Function definition]: def label_on_segment(
def label_on_segment(
# L268 [Executable statement]:     ax,
    ax,
# L269 [Executable statement]:     x1: float,
    x1: float,
# L270 [Executable statement]:     y1: float,
    y1: float,
# L271 [Executable statement]:     x2: float,
    x2: float,
# L272 [Executable statement]:     y2: float,
    y2: float,
# L273 [Executable statement]:     text: str,
    text: str,
# L274 [Executable statement]:     *,
    *,
# L275 [Executable statement]:     t: float = 0.5,
    t: float = 0.5,
# L276 [Executable statement]:     offset: float = 0.035,
    offset: float = 0.035,
# L277 [Executable statement]:     side: float = 1.0,
    side: float = 1.0,
# L278 [Executable statement]:     **kwargs,
    **kwargs,
# L279 [Executable statement]: ) -> None:
) -> None:
# L280 [Executable statement]:     dx = x2 - x1
    dx = x2 - x1
# L281 [Executable statement]:     dy = y2 - y1
    dy = y2 - y1
# L282 [Executable statement]:     length = np.hypot(dx, dy)
    length = np.hypot(dx, dy)
# L283 [Conditional block]:     if length == 0:
    if length == 0:
# L284 [Executable statement]:         add_label(ax, x1, y1, text, **kwargs)
        add_label(ax, x1, y1, text, **kwargs)
# L285 [Return from function]:         return
        return
# L286 [Blank separator]: 

# L287 [Executable statement]:     nx = -dy / length
    nx = -dy / length
# L288 [Executable statement]:     ny = dx / length
    ny = dx / length
# L289 [Executable statement]:     x = x1 + t * dx + side * offset * nx
    x = x1 + t * dx + side * offset * nx
# L290 [Executable statement]:     y = y1 + t * dy + side * offset * ny
    y = y1 + t * dy + side * offset * ny
# L291 [Executable statement]:     defaults = {"fontsize": 11, "ha": "center", "va": "center"}
    defaults = {"fontsize": 11, "ha": "center", "va": "center"}
# L292 [Executable statement]:     defaults.update(kwargs)
    defaults.update(kwargs)
# L293 [Executable statement]:     ax.text(x, y, text, **defaults)
    ax.text(x, y, text, **defaults)
# L294 [Blank separator]: 

# L295 [Blank separator]: 

# L296 [Function definition]: def make_feynman_diagram() -> None:
def make_feynman_diagram() -> None:
# L297 [Executable statement]:     fig, ax = plt.subplots(figsize=(7.6, 4.8))
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
# L298 [Executable statement]:     ax.set_xlim(0.0, 1.0)
    ax.set_xlim(0.0, 1.0)
# L299 [Executable statement]:     ax.set_ylim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
# L300 [Executable statement]:     ax.set_aspect("equal")
    ax.set_aspect("equal")
# L301 [Executable statement]:     ax.axis("off")
    ax.axis("off")
# L302 [Blank separator]: 

# L303 [Executable statement]:     v0 = (0.24, 0.50)
    v0 = (0.24, 0.50)
# L304 [Executable statement]:     v1 = (0.44, 0.50)
    v1 = (0.44, 0.50)
# L305 [Executable statement]:     vz = (0.62, 0.73)
    vz = (0.62, 0.73)
# L306 [Executable statement]:     vh = (0.62, 0.27)
    vh = (0.62, 0.27)
# L307 [Executable statement]:     vw1 = (0.79, 0.39)
    vw1 = (0.79, 0.39)
# L308 [Executable statement]:     vw2 = (0.79, 0.15)
    vw2 = (0.79, 0.15)
# L309 [Blank separator]: 

# L310 [Executable statement]:     eplus = (0.05, 0.76)
    eplus = (0.05, 0.76)
# L311 [Executable statement]:     eminus = (0.05, 0.24)
    eminus = (0.05, 0.24)
# L312 [Executable statement]:     zq = (0.94, 0.86)
    zq = (0.94, 0.86)
# L313 [Executable statement]:     zqbar = (0.94, 0.60)
    zqbar = (0.94, 0.60)
# L314 [Executable statement]:     wl = (0.94, 0.49)
    wl = (0.94, 0.49)
# L315 [Executable statement]:     wnu = (0.94, 0.29)
    wnu = (0.94, 0.29)
# L316 [Executable statement]:     wq = (0.94, 0.20)
    wq = (0.94, 0.20)
# L317 [Executable statement]:     wqbar = (0.94, 0.04)
    wqbar = (0.94, 0.04)
# L318 [Blank separator]: 

# L319 [Executable statement]:     draw_fermion(ax, *eplus, *v0, forward=False)
    draw_fermion(ax, *eplus, *v0, forward=False)
# L320 [Executable statement]:     draw_fermion(ax, *eminus, *v0, forward=True)
    draw_fermion(ax, *eminus, *v0, forward=True)
# L321 [Executable statement]:     draw_boson(ax, *v0, *v1)
    draw_boson(ax, *v0, *v1)
# L322 [Executable statement]:     draw_boson(ax, *v1, *vz)
    draw_boson(ax, *v1, *vz)
# L323 [Executable statement]:     draw_straight_line(ax, *v1, *vh, color="black", linewidth=2.3, linestyle=(0, (5, 3)))
    draw_straight_line(ax, *v1, *vh, color="black", linewidth=2.3, linestyle=(0, (5, 3)))
# L324 [Executable statement]:     draw_fermion(ax, *vz, *zq, forward=True)
    draw_fermion(ax, *vz, *zq, forward=True)
# L325 [Executable statement]:     draw_fermion(ax, *vz, *zqbar, forward=False)
    draw_fermion(ax, *vz, *zqbar, forward=False)
# L326 [Executable statement]:     draw_boson(ax, *vh, *vw1)
    draw_boson(ax, *vh, *vw1)
# L327 [Executable statement]:     draw_boson(ax, *vh, *vw2, dashed=True)
    draw_boson(ax, *vh, *vw2, dashed=True)
# L328 [Executable statement]:     draw_fermion(ax, *vw1, *wl, forward=True)
    draw_fermion(ax, *vw1, *wl, forward=True)
# L329 [Executable statement]:     draw_fermion(ax, *vw1, *wnu, forward=False)
    draw_fermion(ax, *vw1, *wnu, forward=False)
# L330 [Executable statement]:     draw_fermion(ax, *vw2, *wq, forward=True)
    draw_fermion(ax, *vw2, *wq, forward=True)
# L331 [Executable statement]:     draw_fermion(ax, *vw2, *wqbar, forward=False)
    draw_fermion(ax, *vw2, *wqbar, forward=False)
# L332 [Blank separator]: 

# L333 [Executable statement]:     ax.scatter(
    ax.scatter(
# L334 [Executable statement]:         [v0[0], v1[0], vz[0], vh[0], vw1[0], vw2[0]],
        [v0[0], v1[0], vz[0], vh[0], vw1[0], vw2[0]],
# L335 [Executable statement]:         [v0[1], v1[1], vz[1], vh[1], vw1[1], vw2[1]],
        [v0[1], v1[1], vz[1], vh[1], vw1[1], vw2[1]],
# L336 [Executable statement]:         s=26,
        s=26,
# L337 [Executable statement]:         color="black",
        color="black",
# L338 [Executable statement]:         zorder=5,
        zorder=5,
# L339 [Executable statement]:     )
    )
# L340 [Blank separator]: 

# L341 [Executable statement]:     label_on_segment(ax, *v0, *v1, r"$Z^*$", offset=0.045, side=1.0)
    label_on_segment(ax, *v0, *v1, r"$Z^*$", offset=0.045, side=1.0)
# L342 [Executable statement]:     label_on_segment(ax, *v1, *vz, r"$Z$", offset=0.04, side=1.0)
    label_on_segment(ax, *v1, *vz, r"$Z$", offset=0.04, side=1.0)
# L343 [Executable statement]:     label_on_segment(ax, *v1, *vh, r"$H$", offset=0.045, side=-1.0)
    label_on_segment(ax, *v1, *vh, r"$H$", offset=0.045, side=-1.0)
# L344 [Executable statement]:     label_on_segment(ax, *vh, *vw1, r"$W$", offset=0.04, side=1.0)
    label_on_segment(ax, *vh, *vw1, r"$W$", offset=0.04, side=1.0)
# L345 [Executable statement]:     label_on_segment(ax, *vh, *vw2, r"$W^*$", offset=0.04, side=-1.0)
    label_on_segment(ax, *vh, *vw2, r"$W^*$", offset=0.04, side=-1.0)
# L346 [Blank separator]: 

# L347 [Executable statement]:     add_label(ax, 0.025, 0.78, r"$e^+$", ha="left")
    add_label(ax, 0.025, 0.78, r"$e^+$", ha="left")
# L348 [Executable statement]:     add_label(ax, 0.025, 0.22, r"$e^-$", ha="left")
    add_label(ax, 0.025, 0.22, r"$e^-$", ha="left")
# L349 [Executable statement]:     add_label(ax, 0.965, 0.88, r"$q$", ha="left")
    add_label(ax, 0.965, 0.88, r"$q$", ha="left")
# L350 [Executable statement]:     add_label(ax, 0.965, 0.58, r"$\bar{q}$", ha="left")
    add_label(ax, 0.965, 0.58, r"$\bar{q}$", ha="left")
# L351 [Executable statement]:     add_label(ax, 0.965, 0.51, r"$\ell$", ha="left")
    add_label(ax, 0.965, 0.51, r"$\ell$", ha="left")
# L352 [Executable statement]:     add_label(ax, 0.965, 0.27, r"$\nu$", ha="left")
    add_label(ax, 0.965, 0.27, r"$\nu$", ha="left")
# L353 [Executable statement]:     add_label(ax, 0.965, 0.21, r"$q$", ha="left")
    add_label(ax, 0.965, 0.21, r"$q$", ha="left")
# L354 [Executable statement]:     add_label(ax, 0.965, 0.03, r"$\bar{q}'$", ha="left")
    add_label(ax, 0.965, 0.03, r"$\bar{q}'$", ha="left")
# L355 [Blank separator]: 

# L356 [Executable statement]:     fig.tight_layout(pad=0.15)
    fig.tight_layout(pad=0.15)
# L357 [Executable statement]:     fig.savefig(PLOT_DIR / "feynman_diagram.pdf")
    fig.savefig(PLOT_DIR / "feynman_diagram.pdf")
# L358 [Executable statement]:     fig.savefig(PLOT_DIR / "feynman_diagram.png", dpi=180)
    fig.savefig(PLOT_DIR / "feynman_diagram.png", dpi=180)
# L359 [Executable statement]:     plt.close(fig)
    plt.close(fig)
# L360 [Blank separator]: 

# L361 [Blank separator]: 

# L362 [Function definition]: def main() -> None:
def main() -> None:
# L363 [Executable statement]:     PLOT_DIR.mkdir(parents=True, exist_ok=True)
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
# L364 [Executable statement]:     make_pairing_validation()
    make_pairing_validation()
# L365 [Executable statement]:     make_feynman_diagram()
    make_feynman_diagram()
# L366 [Executable statement]:     make_d34_distribution()
    make_d34_distribution()
# L367 [Runtime log output]:     print(f"Generated supporting figures in {PLOT_DIR}")
    print(f"Generated supporting figures in {PLOT_DIR}")
# L368 [Blank separator]: 

# L369 [Blank separator]: 

# L370 [Conditional block]: if __name__ == "__main__":
if __name__ == "__main__":
# L371 [Executable statement]:     main()
    main()
