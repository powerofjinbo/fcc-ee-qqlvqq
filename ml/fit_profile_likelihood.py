#!/usr/bin/env python3
"""Profile likelihood fit for sigma_ZH x BR(H->WW*) measurement.

Methodology follows Jan Eysermans et al. (DOI: 10.17181/9v8ey-n6k50):
- Template fit to BDT score distribution
- Signal strength mu = (sigma x BR)_obs / (sigma x BR)_SM
- 1% flat normalization systematic on each background process
- Uses pyhf for the statistical model

Inputs:
  - BDT kfold_scores.csv (preferred, from train_xgboost_bdt.py)
  - Or: test_scores.csv (fallback, with 1/test_frac weight rescaling)

Outputs:
  - Expected mu_hat, sigma(mu) from Asimov dataset
  - Expected relative uncertainty on sigma_ZH x BR(H->WW*)
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

THIS_DIR = Path(__file__).resolve().parent
ANALYSIS_DIR = THIS_DIR.parent
sys.path.insert(0, str(ANALYSIS_DIR))

from ml_config import BACKGROUND_SAMPLES, DEFAULT_MODEL_DIR, SIGNAL_SAMPLES


def _nice_scale_factor(raw_scale: float) -> int:
    """Round a signal scale factor to a readable 1/2/5 x 10^n value."""
    if raw_scale <= 1:
        return 1
    exponent = int(np.floor(np.log10(raw_scale)))
    base = 10 ** exponent
    for multiplier in (1, 2, 5, 10):
        candidate = multiplier * base
        if raw_scale <= candidate:
            return int(candidate)
    return int(10 * base)


def load_scores(scores_path):
    """Load BDT scores from CSV."""
    df = pd.read_csv(scores_path)
    return df


def build_templates(df, nbins=20, bdt_cut=None, score_range=(0, 1)):
    """Build signal and background histograms from BDT scores.

    Groups backgrounds by physics process type for independent normalization.
    """
    if bdt_cut is not None:
        df = df[df["bdt_score"] >= bdt_cut].copy()

    bins = np.linspace(score_range[0], score_range[1], nbins + 1)            

  
  # 我们的物理事件是带着不同权重（phys_weight）的！
  # 以代码里先用 phys_weight  2 算了一遍直方图（sig_w2），然后再开根号得到真实的误差 sig_err。
  # 这保证了后续放入 pyhf 时，模型知道哪个格子的数据是“实打实”的，哪个格子是“虚胖（高权重导致的偶然波动）
    # Signal template (with MC stat errors)
    sig_mask = df["y_true"] == 1
    sig_hist, _ = np.histogram(
        df.loc[sig_mask, "bdt_score"],
        bins=bins,
        weights=df.loc[sig_mask, "phys_weight"],
    )
    sig_w2, _ = np.histogram(
        df.loc[sig_mask, "bdt_score"],
        bins=bins,
        weights=df.loc[sig_mask, "phys_weight"] ** 2,
    )
    sig_err = np.sqrt(sig_w2)

    # Group backgrounds by process type for separate normalization systematics
    bkg_groups = {
        "WW": ["p8_ee_WW_ecm240"],
        "ZZ": ["p8_ee_ZZ_ecm240"],
        "qq": [s for s in BACKGROUND_SAMPLES if s.startswith("wz3p6_ee_") and "tautau" not in s],    # 背景家族大分家
        "tautau": ["wz3p6_ee_tautau_ecm240"],
        "ZH_other": [
            s for s in BACKGROUND_SAMPLES
            if s.startswith((
                "wzp6_ee_qqH_H",
                "wzp6_ee_bbH_H",
                "wzp6_ee_ccH_H",
                "wzp6_ee_ssH_H",
            ))
        ],
    }

    bkg_hists = {}
    bkg_errs = {}
    for group_name, samples in bkg_groups.items():
        mask = df["sample_name"].isin(samples) & (df["y_true"] == 0)
        if mask.sum() == 0:
            continue
        h, _ = np.histogram(
            df.loc[mask, "bdt_score"],
            bins=bins,
            weights=df.loc[mask, "phys_weight"],
        )
        w2, _ = np.histogram(
            df.loc[mask, "bdt_score"],
            bins=bins,
            weights=df.loc[mask, "phys_weight"] ** 2,
        )
        if h.sum() > 0:
            bkg_hists[group_name] = h
            bkg_errs[group_name] = np.sqrt(w2)

    return sig_hist, sig_err, bkg_hists, bkg_errs, bins


def build_pyhf_model(sig_hist, sig_err, bkg_hists, bkg_errs, norm_uncertainty=0.01, use_staterror=True):
    """Build a pyhf model with signal + backgrounds + normalization + MC stat.

    Each background group gets an independent normalization uncertainty.
    All samples get Barlow-Beeston MC statistical uncertainties (staterror).
    Signal is the POI (mu).
    """
    import pyhf

    # Ensure no negative/zero bins (pyhf requires positive expected rates)
    sig_hist = np.maximum(sig_hist, 1e-6)
    sig_err = np.maximum(sig_err, 1e-6)

    samples = []

    # Signal sample with MC stat uncertainty

  
    # 在这份契约里，信号（Signal）被赋予了一个极其特殊的属性：mu (信号强度 $\mu$)。这就是你整个实验、砸了几百亿建对撞机想要找的那个终极答案！
    sig_modifiers = [
        {"name": "mu", "type": "normfactor", "data": None},
    ]
    if use_staterror:
        sig_modifiers.append({"name": "staterror_sig", "type": "staterror", "data": sig_err.tolist()})
    samples.append({
        "name": "signal",
        "data": sig_hist.tolist(),
        "modifiers": sig_modifiers,
    })

    # Background samples with normalization + MC stat systematics
    for group_name, hist in bkg_hists.items():                                    
        hist = np.maximum(hist, 1e-6)
        err = np.maximum(bkg_errs.get(group_name, np.zeros_like(hist)), 1e-6)
        modifiers = [
            {
                "name": f"norm_{group_name}",
                "type": "normsys",
                "data": {"hi": 1.0 + norm_uncertainty, "lo": 1.0 - norm_uncertainty},
            },
        ]

      
      # type: "staterror" 就是在告诉模型：“由于我的模拟数据是在超级计算机里用蒙特卡洛投骰子投出来的，它本身就带有随机波动的误差。
      # 请你在做最终判定的时候，把这种‘骰子带来的不确定性’也算进总误差里！”
        if use_staterror:
            modifiers.append({"name": f"staterror_{group_name}", "type": "staterror", "data": err.tolist()})
        samples.append({
            "name": group_name,
            "data": hist.tolist(),
            "modifiers": modifiers,
        })

    spec = {
        "version": "1.0.0",
        "channels": [
            {
                "name": "bdt_score",
                "samples": samples,
            }
        ],
        "measurements": [
            {
                "name": "signal_strength",
                "config": {
                    "poi": "mu",
                    "parameters": [
                        {"name": "mu", "bounds": [[0.0, 5.0]], "inits": [1.0]},
                    ],
                },
            }
        ],
        "observations": [
            {
                "name": "bdt_score",
                "data": [],  # filled by Asimov or observed
            }
        ],
    }

    return spec

# 我们把这份完美数据喂给模型，算出来的 $\mu$ 必然等于 $1.0$。但我们真正在乎的不是 $\mu$，而是此时模型给出的误差范围（$\sigma$）！这就是我们这个实验的“预期敏感度（Expected Sensitivity）”。
def fit_asimov(spec, sig_hist, bkg_hists):
    """Run Asimov fit: generate expected data at mu=1 and fit."""
    import pyhf
    pyhf.set_backend("numpy")

    # Build Asimov data (sum of signal + all backgrounds at nominal)
    total = sig_hist.copy()
    for h in bkg_hists.values():
        total += h
    spec["observations"][0]["data"] = total.tolist()

    ws = pyhf.Workspace(spec)
    model = ws.model()
    data = total.tolist() + model.config.auxdata
  # 这里启动了 pyhf 的核心优化器。它在玩一个高维度的“下山游戏”：调整所有的参数（信号强度、背景的上下浮动、各种误差），试图找到一个点，使得负对数似然函数（Negative Log-Likelihood, NLL）的值最小。
  # 因为我们喂的是完美阿西莫夫数据，所以它找到的 bestfit 里，信号强度 $\mu$ 肯定稳稳地停在 1.0 附近。
    # MLE fit
    bestfit, twice_nll_val = pyhf.infer.mle.fit(
        data, model, return_fitted_val=True
    )
    bestfit = np.asarray(bestfit)

    # Compute uncertainties via numerical Hessian of NLL
    def nll_func(pars):
        pars_tensor = pyhf.tensorlib.astensor(pars)
        val = pyhf.infer.mle.twice_nll(pars_tensor, data, model)
        return float(np.asarray(val).item()) / 2.0

    n = len(bestfit)
    eps = 1e-4
    hessian = np.zeros((n, n))
    f0 = nll_func(bestfit)
    for i in range(n):
        for j in range(i, n):
            pars_pp = bestfit.copy()
            pars_pp[i] += eps
            pars_pp[j] += eps
            pars_pm = bestfit.copy()
            pars_pm[i] += eps
            pars_pm[j] -= eps
            pars_mp = bestfit.copy()
            pars_mp[i] -= eps
            pars_mp[j] += eps
            pars_mm = bestfit.copy()
            pars_mm[i] -= eps
            pars_mm[j] -= eps
            hessian[i, j] = (nll_func(pars_pp) - nll_func(pars_pm) - nll_func(pars_mp) + nll_func(pars_mm)) / (4 * eps * eps)
            hessian[j, i] = hessian[i, j]

    try:
        cov = np.linalg.inv(hessian)
        errors = np.sqrt(np.maximum(np.diag(cov), 0))
    except np.linalg.LinAlgError:
        errors = np.zeros(n)


  # 提取终极大奖
  # 给出了 FCC-ee 这台对撞机对测量希格斯粒子信号的理论极限误差 (mu_err)。
    mu_idx = model.config.poi_index
    mu_hat = float(bestfit[mu_idx])
    mu_err = float(errors[mu_idx])

    # All parameter results
    par_names = model.config.par_names
    fit_results = {}
    for i, name in enumerate(par_names):
        fit_results[name] = {
            "value": float(bestfit[i]),
            "error": float(errors[i]),
        }

    return mu_hat, mu_err, fit_results


def scan_bdt_cut(df, cuts=None, fit_nbins=1, norm_uncertainty=0.01, use_staterror=True):
    """Scan BDT cuts for a fixed fit granularity.

    The paper comparison between "counting" and "shape" fits should use a true
    single-bin model after the threshold cut. `fit_nbins=1` implements that
    counting baseline, while larger values can be used for shape studies.
    """
    import pyhf

    if cuts is None:
        coarse_cuts = np.arange(0.0, 0.90, 0.05)
        fine_cuts = np.arange(0.90, 1.00, 0.01)
        cuts = np.unique(np.round(np.concatenate([coarse_cuts, fine_cuts]), 2))

    results = []
    for cut in cuts:
        sig_hist, sig_err, bkg_hists, bkg_errs, bins = build_templates(
            df, nbins=fit_nbins, bdt_cut=cut,
        )

        n_sig = sig_hist.sum()
        n_bkg = sum(h.sum() for h in bkg_hists.values())

        if n_sig < 1 or n_bkg < 1:
            continue

        spec = build_pyhf_model(sig_hist, sig_err, bkg_hists, bkg_errs, norm_uncertainty, use_staterror=use_staterror)

        try:
            mu_hat, mu_err, _ = fit_asimov(spec, sig_hist, bkg_hists)
            rel_err = mu_err / mu_hat if mu_hat > 0 else float("inf")
        except Exception as e:
            print(f"  cut={cut:.2f}: fit failed ({e})")
            continue

        results.append({
            "bdt_cut": float(cut),
            "fit_nbins": int(fit_nbins),
            "n_sig": float(n_sig),
            "n_bkg": float(n_bkg),
            "s_over_b": float(n_sig / n_bkg) if n_bkg > 0 else 0,
            "s_over_sqrt_b": float(n_sig / np.sqrt(n_bkg)) if n_bkg > 0 else 0,
            "mu_hat": mu_hat,
            "mu_err": mu_err,
            "rel_uncertainty": rel_err,
        })

        print(f"  cut={cut:.2f}: S={n_sig:.0f}, B={n_bkg:.0f}, "
              f"S/√B={n_sig/np.sqrt(n_bkg):.1f}, δμ/μ={rel_err*100:.2f}%")

    return results


def make_fit_plots(output_dir, scan_results, best_result, sig_hist, bkg_hists, bins, shape_rel_unc_pct=None):
    """Generate fit diagnostic plots."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import LogLocator, NullFormatter

    plots_dir = output_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    # 1. BDT cut optimization scan
    if len(scan_results) > 1:
        fig, ax = plt.subplots(figsize=(6.0, 4.6))

        plot_results = [r for r in scan_results if r["bdt_cut"] >= 0.05]
        cuts = [r["bdt_cut"] for r in plot_results]
        rel_unc = [r["rel_uncertainty"] * 100 for r in plot_results]

        ax.plot(cuts, rel_unc, color="#2C7FB8", marker="o", markersize=4.5, linewidth=2.0)
        ax.set_xlabel("BDT score threshold")
        ax.set_ylabel(r"Expected $\delta\mu/\mu$ [%]")
        ax.set_title("1-bin counting reference scan")
        ax.grid(True, alpha=0.25)
        ax.set_xlim(0.05, 1.0)

        if shape_rel_unc_pct is not None:
            ax.axhline(
                shape_rel_unc_pct,
                color="#333333",
                linestyle=(0, (4, 3)),
                linewidth=1.4,
                label=f"20-bin shape fit: {shape_rel_unc_pct:.2f}%",
            )

        if best_result:
            best_cut = best_result["bdt_cut"]
            best_unc = best_result["rel_uncertainty"] * 100
            ax.axvline(best_cut, color="#D64F4F", linestyle="--", linewidth=1.4)
            ax.scatter([best_cut], [best_unc], color="#D64F4F", zorder=5)
            ax.annotate(
                f"Best counting:\n{best_unc:.2f}% @ {best_cut:.2f}",
                xy=(best_cut, best_unc),
                xytext=(-74, 22),
                textcoords="offset points",
                fontsize=9,
                bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": "#D64F4F", "alpha": 0.92},
                arrowprops={"arrowstyle": "->", "color": "#D64F4F", "lw": 1.1},
            )

        ax.legend(frameon=False, fontsize=9, loc="upper right")
        fig.tight_layout()
        fig.savefig(plots_dir / "bdt_cut_scan.pdf", dpi=150)
        fig.savefig(plots_dir / "bdt_cut_scan.png", dpi=150)
        plt.close(fig)

    # 2. Template shapes at the final 20-bin working point
    fig, ax = plt.subplots(figsize=(7.6, 5.4))
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    bin_width = bins[1] - bins[0]

    # Use a stable plotting order so the legend and stack read cleanly.
    preferred_order = ["tautau", "ZH_other", "qq", "ZZ", "WW"]
    bkg_labels = [label for label in preferred_order if label in bkg_hists]
    bkg_arrays = [np.asarray(bkg_hists[label], dtype=float) for label in bkg_labels]
    color_map = {
        "WW": "#E69F00",
        "ZZ": "#4C78A8",
        "qq": "#59A14F",
        "tautau": "#9C755F",
        "ZH_other": "#B07AA1",
    }

    cumulative = np.zeros_like(sig_hist, dtype=float)
    legend_handles = []
    legend_labels = []
    for label, arr in zip(bkg_labels, bkg_arrays):
        bars = ax.bar(
            bins[:-1],
            arr,
            width=bin_width,
            align="edge",
            bottom=cumulative,
            color=color_map[label],
            edgecolor="white",
            linewidth=0.45,
            alpha=0.92,
        )
        cumulative += arr
        legend_handles.append(bars[0])
        legend_labels.append(label.replace("_", " "))

    total_bkg = cumulative.copy()
    total_bkg_handle = ax.step(
        bins[:-1],
        total_bkg,
        where="post",
        color="#1F2D3A",
        linewidth=1.4,
        alpha=0.95,
        label="Total background",
    )[0]

    raw_scale = (0.18 * total_bkg.max() / sig_hist.max()) if sig_hist.sum() > 0 and total_bkg.max() > 0 else 1.0
    sig_scale = _nice_scale_factor(raw_scale)
    sig_handle = ax.bar(
        bins[:-1],
        sig_hist * sig_scale,
        width=bin_width,
        align="edge",
        fill=False,
        edgecolor="#D62728",
        linewidth=1.8,
        linestyle="-",
        label=f"Signal × {sig_scale}",
        zorder=5,
    )[0]

    ax.set_ylabel(f"Events / {bin_width:.2f}")
    ax.set_xlabel("BDT score")
    ax.set_title("20-bin BDT templates used in the profile-likelihood fit")
    ax.text(
        0.03,
        0.95,
        r'$\mathbf{FCC\text{-}ee}$ Simulation',
        transform=ax.transAxes,
        fontsize=10,
        va='top',
        fontstyle='italic',
    )
    ax.text(
        0.03,
        0.89,
        r'$\sqrt{s}=240$ GeV, $10.8\,\mathrm{ab}^{-1}$',
        transform=ax.transAxes,
        fontsize=9,
        va='top',
    )
    ax.text(
        0.97,
        0.95,
        "20 bins in [0, 1]",
        transform=ax.transAxes,
        fontsize=9,
        va="top",
        ha="right",
        color="#334455",
    )
    ax.set_yscale("log")
    ax.set_ylim(bottom=0.1, top=max(total_bkg.max(), (sig_hist * sig_scale).max()) * 12.0)
    ax.set_xlim(0.0, 1.0)
    ax.set_xticks(np.linspace(0.0, 1.0, 11))
    ax.yaxis.set_major_locator(LogLocator(base=10.0, numticks=12))
    ax.yaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2, 10), numticks=120))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.grid(axis="y", which="major", alpha=0.22, linewidth=0.8)
    ax.grid(axis="y", which="minor", alpha=0.10, linewidth=0.5)
    ax.tick_params(axis="y", which="major", labelsize=9)
    ax.tick_params(axis="y", which="minor", length=2.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(
        [sig_handle, total_bkg_handle, *legend_handles[::-1]],
        [f"Signal × {sig_scale}", "Total background", *legend_labels[::-1]],
        fontsize=8.3,
        ncol=3,
        frameon=False,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.02),
        columnspacing=1.1,
        handlelength=2.4,
    )

    fig.tight_layout()
    fig.savefig(plots_dir / "fit_templates.pdf", dpi=170)
    fig.savefig(plots_dir / "fit_templates.png", dpi=170)
    plt.close(fig)

    # 3. Rank-ordered BDT bins (highest score to lowest score)
    rank_order = np.arange(len(sig_hist))[::-1]
    rank_bins = np.arange(1, len(sig_hist) + 1)
    sig_rank = sig_hist[rank_order]
    bkg_rank_arrays = [arr[rank_order] for arr in bkg_arrays]
    bkg_rank_colors = [color_map[label] for label in bkg_labels]
    total_rank = np.sum(np.asarray(bkg_rank_arrays), axis=0)

    fig, (ax_top, ax_bottom) = plt.subplots(
        2,
        1,
        figsize=(7.4, 6.6),
        sharex=True,
        gridspec_kw={"height_ratios": [3.0, 1.15], "hspace": 0.05},
    )

    cumulative = np.zeros_like(rank_bins, dtype=float)
    for label, arr, color in zip(bkg_labels, bkg_rank_arrays, bkg_rank_colors):
        ax_top.bar(
            rank_bins,
            arr,
            bottom=cumulative,
            width=0.90,
            color=color,
            alpha=0.88,
            label=f"Bkg: {label}",
            linewidth=0.0,
        )
        cumulative += arr

    sig_scale_rank = sig_scale
    ax_top.step(
        np.r_[rank_bins, rank_bins[-1] + 1] - 0.5,
        np.r_[sig_rank * sig_scale_rank, sig_rank[-1] * sig_scale_rank],
        where="post",
        color="black",
        linewidth=2.0,
        label=f"Signal (x{sig_scale_rank})",
    )
    ax_top.set_ylabel("Events / rank bin")
    ax_top.set_title("Rank-ordered BDT bins")
    ax_top.set_yscale("log")
    ax_top.set_ylim(bottom=0.1)
    ax_top.yaxis.set_major_locator(LogLocator(base=10.0, numticks=12))
    ax_top.yaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2, 10), numticks=120))
    ax_top.yaxis.set_minor_formatter(NullFormatter())
    ax_top.grid(axis="y", which="major", alpha=0.24, linewidth=0.8)
    ax_top.grid(axis="y", which="minor", alpha=0.14, linewidth=0.55)
    ax_top.tick_params(axis="y", which="major", labelsize=9)
    ax_top.tick_params(axis="y", which="minor", length=2.5)
    ax_top.legend(fontsize=8.6, ncol=2, frameon=False, loc="upper center")
    ax_top.text(
        0.03,
        0.95,
        r'$\mathbf{FCC\text{-}ee}$ Simulation',
        transform=ax_top.transAxes,
        fontsize=10,
        va='top',
        fontstyle='italic',
    )
    ax_top.text(
        0.03,
        0.89,
        r'$\sqrt{s}=240$ GeV, $10.8\,\mathrm{ab}^{-1}$',
        transform=ax_top.transAxes,
        fontsize=9,
        va='top',
    )

    purity = np.divide(sig_rank, sig_rank + total_rank, out=np.zeros_like(sig_rank), where=(sig_rank + total_rank) > 0)
    ax_bottom.plot(rank_bins, purity, color="#2C7FB8", marker="o", markersize=3.8, linewidth=1.8)
    ax_bottom.set_ylabel(r"$S/(S+B)$")
    ax_bottom.set_xlabel("BDT rank bin (1 = highest score)")
    ax_bottom.set_ylim(0.0, min(1.0, max(0.15, purity.max() * 1.25 if len(purity) else 0.15)))
    ax_bottom.set_xlim(0.5, len(rank_bins) + 0.5)
    ax_bottom.set_xticks(rank_bins[::2] if len(rank_bins) > 10 else rank_bins)
    ax_bottom.grid(axis="y", alpha=0.22)
    ax_bottom.text(
        0.02,
        0.92,
        "Signal purity by ranked bin",
        transform=ax_bottom.transAxes,
        fontsize=9,
        va="top",
    )

    fig.tight_layout()
    fig.savefig(plots_dir / "bdt_score_rank.pdf", dpi=150)
    fig.savefig(plots_dir / "bdt_score_rank.png", dpi=150)
    plt.close(fig)

    print(f"  Fit plots saved to {plots_dir}/")


def main():
    parser = argparse.ArgumentParser(description="Profile likelihood fit for H->WW* measurement")
    parser.add_argument("--scores", type=str, default=None,
                       help="Path to kfold_scores.csv or test_scores.csv from BDT training")
    parser.add_argument("--model-dir", type=str, default=None,
                       help="Model directory (default: ml/models/xgboost_bdt)")
    parser.add_argument("--nbins", type=int, default=20,
                       help="Number of BDT score bins for template fit")
    parser.add_argument("--norm-unc", type=float, default=0.01,
                       help="Background normalization uncertainty (default: 1%%)")
    parser.add_argument("--bdt-cut", type=float, default=None,
                       help="Fixed BDT score cut (if None, scans for optimal)")
    parser.add_argument("--no-scan", action="store_true",
                       help="Skip BDT cut scan, use --bdt-cut or 0.0")
    parser.add_argument("--no-plots", action="store_true",
                       help="Skip diagnostic plots")
    parser.add_argument("--no-staterror", action="store_true",
                       help="Disable Barlow-Beeston MC stat uncertainty (show physics-only precision)")
    args = parser.parse_args()

    # Locate scores file
    if args.scores:
        scores_path = Path(args.scores)
    elif args.model_dir:
        model_dir = Path(args.model_dir)
        # Prefer kfold_scores.csv (all events, no scaling needed)
        kfold_path = model_dir / "kfold_scores.csv"
        test_path = model_dir / "test_scores.csv"
        if kfold_path.exists():
            scores_path = kfold_path
        else:
            scores_path = test_path
    else:
        model_dir = ANALYSIS_DIR / DEFAULT_MODEL_DIR
        scores_path = model_dir / "test_scores.csv"
        if not scores_path.exists():
            scores_path = THIS_DIR / "models" / "xgboost_bdt_v6" / "test_scores.csv"

    print(f"Loading scores from {scores_path}")
    df = load_scores(scores_path)
    print(f"  {len(df)} events loaded ({(df['y_true']==1).sum()} signal, {(df['y_true']==0).sum()} background)")

    output_dir = scores_path.parent

    # Weight scaling depends on input file type:
    # - kfold_scores.csv: ALL events scored, no scaling needed
    # - test_scores.csv: only test fraction, scale by 1/test_frac
    if "kfold" in scores_path.name:
        print("  Using k-fold scores (all events, no scaling)")
    else:
        test_frac = 0.30  # must match --test-size in train_xgboost_bdt.py
        df["phys_weight"] = df["phys_weight"] / test_frac
        print(f"  Scaling weights by 1/{test_frac} for test-set-only scores")

    use_staterr = not args.no_staterror

    # Single-bin counting scan for the cut-and-count reference.
    if not args.no_scan:
        print("\nScanning BDT score cuts (1-bin counting reference):")
        scan_results = scan_bdt_cut(
            df,
            fit_nbins=1,
            norm_uncertainty=args.norm_unc,
            use_staterror=use_staterr,
        )

        if not scan_results:
            print("ERROR: All BDT cuts failed. Check input data.")
            return

        best_counting = min(scan_results, key=lambda r: r["rel_uncertainty"])
        print(f"\n  Best 1-bin counting cut: {best_counting['bdt_cut']:.2f}")
        print(f"  S={best_counting['n_sig']:.0f}, B={best_counting['n_bkg']:.0f}")
        print(f"  Expected δμ/μ = {best_counting['rel_uncertainty']*100:.2f}%")
    else:
        scan_results = []
        best_counting = None

    # The headline result is the full 20-bin shape fit. By default we keep the
    # full BDT score range unless the caller explicitly requests a threshold.
    bdt_cut = args.bdt_cut if args.bdt_cut is not None else 0.0

    # Final fit at chosen working point
    print(f"\nFinal {args.nbins}-bin shape fit at BDT cut = {bdt_cut:.2f}:")
    sig_hist, sig_err, bkg_hists, bkg_errs, bins = build_templates(df, nbins=args.nbins, bdt_cut=bdt_cut)

    n_sig = sig_hist.sum()
    n_bkg = sum(h.sum() for h in bkg_hists.values())
    print(f"  Signal events: {n_sig:.0f}")
    print(f"  Background events: {n_bkg:.0f}")
    for name, h in bkg_hists.items():
        print(f"    {name}: {h.sum():.0f}")

    spec = build_pyhf_model(sig_hist, sig_err, bkg_hists, bkg_errs, args.norm_unc, use_staterror=use_staterr)
    mu_hat, mu_err, fit_results = fit_asimov(spec, sig_hist, bkg_hists)

    rel_unc = mu_err / mu_hat if mu_hat > 0 else float("inf")
    physics_only_mu_hat = None
    physics_only_mu_err = None
    physics_only_rel_unc = None
    if use_staterr:
        physics_spec = build_pyhf_model(
            sig_hist, sig_err, bkg_hists, bkg_errs, args.norm_unc, use_staterror=False,
        )
        physics_only_mu_hat, physics_only_mu_err, _ = fit_asimov(physics_spec, sig_hist, bkg_hists)
        physics_only_rel_unc = (
            physics_only_mu_err / physics_only_mu_hat if physics_only_mu_hat > 0 else float("inf")
        )

    print(f"\n  === RESULT ===")
    print(f"  mu_hat = {mu_hat:.4f} +/- {mu_err:.4f}")
    print(f"  Relative uncertainty: {rel_unc*100:.2f}%")
    print(f"  => Expected precision on sigma_ZH x BR(H->WW*): {rel_unc*100:.2f}%")
    if physics_only_rel_unc is not None:
        print(f"  Physics-only floor (no MC stat nuisance terms): {physics_only_rel_unc*100:.2f}%")

    # Save results
    result = {
        "bdt_cut": bdt_cut,
        "nbins": args.nbins,
        "scan_mode": "counting_1bin",
        "norm_uncertainty": args.norm_unc,
        "n_signal": float(n_sig),
        "n_background": float(n_bkg),
        "mu_hat": mu_hat,
        "mu_err": mu_err,
        "relative_uncertainty_pct": rel_unc * 100,
        "fit_parameters": fit_results,
        "bkg_yields": {k: float(v.sum()) for k, v in bkg_hists.items()},
    }

    if physics_only_rel_unc is not None:
        result["physics_only_mu_hat"] = physics_only_mu_hat
        result["physics_only_mu_err"] = physics_only_mu_err
        result["physics_only_rel_uncertainty_pct"] = physics_only_rel_unc * 100
        result["physics_only_note"] = (
            "Shape-fit precision with the same normalization systematics but without "
            "Barlow-Beeston MC-stat nuisance terms."
        )

    if scan_results:
        result["counting_scan_results"] = scan_results

    result_path = output_dir / "fit_results.json"
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\n  Results saved to {result_path}")

    # Plots
    if not args.no_plots:
        make_fit_plots(
            output_dir,
            scan_results,
            best_counting,
            sig_hist,
            bkg_hists,
            bins,
            shape_rel_unc_pct=rel_unc * 100,
        )


if __name__ == "__main__":
    main()
