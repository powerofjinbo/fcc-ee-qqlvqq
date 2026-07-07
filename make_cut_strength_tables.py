#!/usr/bin/env python3
"""Make per-cut strength tables from the normalized cutFlow histograms.

The tables compare the yield immediately before and after each cut for the
main physics groups. This is intentionally derived from saved ROOT cutFlow
histograms, so it does not rerun the event selection.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import uproot

from ml_config import (
    CUTFLOW_STAGES,
    DEFAULT_HISTMAKER_DIR,
    DEFAULT_PLOTS_DIR,
    SIGNAL_SAMPLES,
    ZH_OTHER_SAMPLES,
)


# (cut_id, latex_label) pairs, from the single source of truth in ml_config.
CUTS = [(stage_id, latex_label) for stage_id, _plot_label, latex_label in CUTFLOW_STAGES]

GROUPS = {
    "Signal": list(SIGNAL_SAMPLES),
    "WW": ["p8_ee_WW_ecm240"],
    "ZZ": ["p8_ee_ZZ_ecm240"],
    r"$q\bar{q}$": [
        "wz3p6_ee_uu_ecm240",
        "wz3p6_ee_dd_ecm240",
        "wz3p6_ee_cc_ecm240",
        "wz3p6_ee_ss_ecm240",
        "wz3p6_ee_bb_ecm240",
    ],
    r"$\tau\tau$": ["wz3p6_ee_tautau_ecm240"],
    "ZH(other)": list(ZH_OTHER_SAMPLES),
}

PROCESS_ORDER = ["Signal", "WW", "ZZ", r"$q\bar{q}$", r"$\tau\tau$", "ZH(other)"]
BAR_COLORS = {
    "Signal": "#c9252d",
    "WW": "#f39c12",
    "ZZ": "#2f80ed",
    r"$q\bar{q}$": "#27ae60",
    r"$\tau\tau$": "#7f8c8d",
    "ZH(other)": "#17a589",
}


def read_cutflow(input_dir: Path, sample: str, ncuts: int) -> list[float]:
    """Return the first ncuts bins of the cutFlow histogram for one sample."""
    root_file = input_dir / f"{sample}.root"
    if not root_file.exists():
        raise FileNotFoundError(root_file)
    with uproot.open(root_file) as handle:
        values = handle["cutFlow"].to_numpy(flow=False)[0]
    if len(values) > ncuts and abs(float(values[ncuts])) > 1e-9:
        raise RuntimeError(
            f"{root_file} has a nonzero cutFlow bin beyond the configured "
            f"{ncuts - 1}-cut sequence. These histmaker outputs were made with an "
            "older selection — rerun histmaker for this tag."
        )
    return [float(x) for x in values[:ncuts]]


def load_group_yields(input_dir: Path) -> dict[str, list[float]]:
    ncuts = len(CUTS)
    group_yields: dict[str, list[float]] = {}
    for group, samples in GROUPS.items():
        total = [0.0] * ncuts
        missing = []
        for sample in samples:
            try:
                values = read_cutflow(input_dir, sample, ncuts)
            except FileNotFoundError:
                missing.append(sample)
                continue
            total = [a + b for a, b in zip(total, values)]
        if missing:
            print(f"Warning: {group} missing {len(missing)} samples: {', '.join(missing)}")
        group_yields[group] = total
    return group_yields


def fmt_yield(value: float) -> str:
    if abs(value) >= 1e7:
        return f"{value:.3e}"
    if abs(value) >= 1000:
        return f"{value:,.0f}"
    if abs(value) >= 10:
        return f"{value:,.1f}"
    return f"{value:.3g}"


def fmt_pct(value: float) -> str:
    if math.isnan(value):
        return "-"
    if value < 0.01 and value > 0:
        return f"{value:.3f}%"
    if value < 1:
        return f"{value:.2f}%"
    return f"{value:.1f}%"


def precision_proxy(signal: float, background: float) -> float:
    """Counting-stat proxy for relative signal-strength precision."""
    if signal <= 0:
        return float("nan")
    return math.sqrt(max(signal + background, 0.0)) / signal


def total_background(group_yields: dict[str, list[float]], cut_idx: int) -> float:
    return sum(group_yields[process][cut_idx] for process in PROCESS_ORDER if process != "Signal")


def precision_metrics(group_yields: dict[str, list[float]], cut_idx: int) -> dict[str, float]:
    s_before = group_yields["Signal"][cut_idx - 1]
    b_before = total_background(group_yields, cut_idx - 1)
    s_after = group_yields["Signal"][cut_idx]
    b_after = total_background(group_yields, cut_idx)
    before = precision_proxy(s_before, b_before)
    after = precision_proxy(s_after, b_after)
    improvement = 100.0 * (before - after) / before if before > 0 else float("nan")
    factor = before / after if after > 0 else float("nan")
    return {
        "signal_before": s_before,
        "background_before": b_before,
        "signal_after": s_after,
        "background_after": b_after,
        "precision_before": before,
        "precision_after": after,
        "precision_improvement_percent": improvement,
        "precision_improvement_factor": factor,
    }


def fmt_precision(value: float) -> str:
    if math.isnan(value):
        return "-"
    return f"{100.0 * value:.2f}%"


def fmt_gain(value: float) -> str:
    if math.isnan(value):
        return "-"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.1f}%"


def rows_for_cut(group_yields: dict[str, list[float]], cut_idx: int) -> list[dict[str, float | str]]:
    rows = []
    metrics = precision_metrics(group_yields, cut_idx)
    for process in PROCESS_ORDER:
        before = group_yields[process][cut_idx - 1]
        after = group_yields[process][cut_idx]
        kept = 100.0 * after / before if before > 0 else float("nan")
        rejected = 100.0 - kept if before > 0 else float("nan")
        rows.append(
            {
                "cut": CUTS[cut_idx][0],
                "cut_label": CUTS[cut_idx][1],
                "process": process,
                "before_yield": before,
                "after_yield": after,
                "removed_yield": before - after,
                "kept_percent": kept,
                "rejected_percent": rejected,
                **metrics,
            }
        )
    return rows


def draw_cut_page(rows: list[dict[str, float | str]], cut_idx: int, outpath: Path | None = None):
    cut_id, cut_label = CUTS[cut_idx]
    prev_id, prev_label = CUTS[cut_idx - 1]

    fig = plt.figure(figsize=(11.5, 7.5), constrained_layout=False)
    gs = fig.add_gridspec(2, 1, height_ratios=[1.2, 1.0], hspace=0.18)
    ax_table = fig.add_subplot(gs[0])
    ax_bar = fig.add_subplot(gs[1])
    ax_table.axis("off")

    title = f"{cut_id}: cut strength"
    subtitle = f"Before: {prev_id} ({prev_label})   ->   After: {cut_label}"
    fig.suptitle(title, fontsize=19, fontweight="bold", y=0.985)
    fig.text(0.5, 0.93, subtitle, ha="center", va="center", fontsize=12)
    precision_before = float(rows[0]["precision_before"])
    precision_after = float(rows[0]["precision_after"])
    precision_gain = float(rows[0]["precision_improvement_percent"])
    precision_factor = float(rows[0]["precision_improvement_factor"])
    fig.text(
        0.5,
        0.895,
        (
            r"Counting precision proxy $\sqrt{S+B}/S$: "
            f"{fmt_precision(precision_before)} -> {fmt_precision(precision_after)}; "
            f"improved by {fmt_gain(precision_gain)} (x{precision_factor:.2f})"
        ),
        ha="center",
        va="center",
        fontsize=11,
        color="#334455",
    )

    table_rows = []
    for row in rows:
        table_rows.append(
            [
                row["process"],
                fmt_yield(float(row["before_yield"])),
                fmt_yield(float(row["after_yield"])),
                fmt_yield(float(row["removed_yield"])),
                fmt_pct(float(row["kept_percent"])),
                fmt_pct(float(row["rejected_percent"])),
                fmt_gain(float(row["precision_improvement_percent"])),
            ]
        )

    table = ax_table.table(
        cellText=table_rows,
        colLabels=["Process", "Before", "After", "Removed", "Kept", "Rejected", "Precision gain"],
        loc="center",
        cellLoc="center",
        colLoc="center",
        colWidths=[0.16, 0.15, 0.15, 0.15, 0.12, 0.12, 0.15],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.55)

    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor("#4d4d4d")
        cell.set_linewidth(0.7)
        if r == 0:
            cell.set_facecolor("#e9eef3")
            cell.set_text_props(weight="bold")
            cell.set_linewidth(1.0)
        elif c == 0:
            proc = table_rows[r - 1][0]
            cell.set_facecolor(BAR_COLORS.get(proc, "#ffffff"))
            cell.set_text_props(weight="bold", color="white" if proc != "ZZ" else "white")
        else:
            cell.set_facecolor("#ffffff" if r % 2 else "#f7f7f7")

    processes = [str(row["process"]) for row in rows]
    kept_values = [float(row["kept_percent"]) for row in rows]
    rejected_values = [float(row["rejected_percent"]) for row in rows]
    y = list(range(len(processes)))

    ax_bar.barh(y, kept_values, color=[BAR_COLORS[p] for p in processes], alpha=0.85, label="kept")
    ax_bar.barh(y, rejected_values, left=kept_values, color="#d9d9d9", alpha=0.95, label="rejected")
    ax_bar.set_xlim(0, 100)
    ax_bar.set_yticks(y)
    ax_bar.set_yticklabels(processes, fontsize=11)
    ax_bar.invert_yaxis()
    ax_bar.set_xlabel("Fraction of events before this cut [%]", fontsize=12)
    ax_bar.set_title("Instantaneous cut effect", fontsize=13, pad=8)
    ax_bar.grid(axis="x", color="#d0d0d0", linewidth=0.7, alpha=0.8)
    ax_bar.legend(loc="lower right", frameon=False)

    for i, kept in enumerate(kept_values):
        ax_bar.text(min(kept + 1.0, 97), i, fmt_pct(kept), va="center", fontsize=10)

    fig.text(
        0.5,
        0.02,
        "Yields are normalized to 10.8 ab$^{-1}$ using the saved cutFlow histograms.",
        ha="center",
        fontsize=10,
        color="#555555",
    )

    if outpath is not None:
        fig.savefig(outpath)
        fig.savefig(outpath.with_suffix(".png"), dpi=180)
        plt.close(fig)
    return fig


def draw_overview(summary: pd.DataFrame, outpath: Path):
    pivot = summary.pivot(index="process", columns="cut", values="rejected_percent").loc[PROCESS_ORDER]
    fig, ax = plt.subplots(figsize=(12.0, 4.8))
    im = ax.imshow(pivot.values, aspect="auto", cmap="YlOrRd", vmin=0, vmax=100)
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=35, ha="right")
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    ax.set_title("Per-cut rejection strength [% rejected at this cut]", fontsize=16, fontweight="bold")

    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            value = pivot.values[i, j]
            color = "white" if value > 55 else "black"
            ax.text(j, i, f"{value:.0f}", ha="center", va="center", fontsize=9, color=color)

    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cbar.set_label("Rejected [%]")
    fig.tight_layout()
    fig.savefig(outpath)
    fig.savefig(outpath.with_suffix(".png"), dpi=180)
    plt.close(fig)


def draw_precision_overview(summary: pd.DataFrame, outpath: Path):
    per_cut = summary.drop_duplicates("cut").copy()
    fig, ax = plt.subplots(figsize=(11.0, 4.8))
    colors = ["#2f80ed" if val >= 0 else "#c0392b" for val in per_cut["precision_improvement_percent"]]
    bars = ax.bar(per_cut["cut"], per_cut["precision_improvement_percent"], color=colors, alpha=0.9)
    ax.axhline(0, color="#333333", linewidth=0.8)
    ax.set_ylabel(r"Improvement in $\sqrt{S+B}/S$ [%]")
    ax.set_xlabel("Cut")
    ax.set_title("Per-cut improvement in counting precision proxy", fontsize=15, fontweight="bold")
    ax.grid(axis="y", color="#d0d0d0", linewidth=0.7, alpha=0.8)
    for bar, before, after, gain in zip(
        bars,
        per_cut["precision_before"],
        per_cut["precision_after"],
        per_cut["precision_improvement_percent"],
    ):
        y = bar.get_height()
        va = "bottom" if y >= 0 else "top"
        offset = 0.4 if y >= 0 else -0.4
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            y + offset,
            f"{gain:+.1f}%\n{100*before:.2f}%→{100*after:.2f}%",
            ha="center",
            va=va,
            fontsize=8.5,
        )
    fig.tight_layout()
    fig.savefig(outpath)
    fig.savefig(outpath.with_suffix(".png"), dpi=180)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", default=None,
                        help="Output tag; default follows LVQQ_OUTPUT_TAG via ml_config")
    parser.add_argument("--input-dir", default=None)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    if args.tag is not None:
        default_input = f"output/h_hww_lvqq_{args.tag}/histmaker/ecm240"
        default_output = f"plots_lvqq_{args.tag}/cut_strength_by_cut"
    else:
        args.tag = "current"
        default_input = DEFAULT_HISTMAKER_DIR
        default_output = f"{DEFAULT_PLOTS_DIR}/cut_strength_by_cut"
    input_dir = Path(args.input_dir or default_input)
    output_dir = Path(args.output_dir or default_output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_dir.exists():
        raise SystemExit(f"Input directory does not exist: {input_dir}")

    group_yields = load_group_yields(input_dir)

    all_rows = []
    multipage = output_dir / f"cut_strength_tables_{args.tag}.pdf"
    with PdfPages(multipage) as pdf:
        for cut_idx in range(1, len(CUTS)):
            rows = rows_for_cut(group_yields, cut_idx)
            all_rows.extend(rows)
            cut_id = CUTS[cut_idx][0]
            safe_label = cut_id
            per_cut_pdf = output_dir / f"{safe_label}_strength_table.pdf"
            fig = draw_cut_page(rows, cut_idx, per_cut_pdf)
            pdf.savefig(fig)
            plt.close(fig)
            pd.DataFrame(rows).to_csv(output_dir / f"{safe_label}_strength_table.csv", index=False)

    summary = pd.DataFrame(all_rows)
    summary.to_csv(output_dir / "cut_strength_summary.csv", index=False)
    draw_overview(summary, output_dir / "cut_strength_rejection_heatmap.pdf")
    draw_precision_overview(summary, output_dir / "cut_precision_improvement.pdf")

    print(f"Wrote per-cut strength tables to: {output_dir}")
    print(f"Wrote combined PDF: {multipage}")
    print(f"Wrote summary CSV: {output_dir / 'cut_strength_summary.csv'}")


if __name__ == "__main__":
    main()
