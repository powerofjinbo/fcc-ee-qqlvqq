#!/usr/bin/env python3
"""Profile likelihood fit for the sigma_ZH x BR(H->WW*) measurement.

Methodology follows Jan Eysermans et al. (DOI: 10.17181/9v8ey-n6k50):
- Template fit to the BDT score distribution (20 uniform bins in [0, 1])
- Signal strength mu = (sigma x BR)_obs / (sigma x BR)_SM
- 1% flat normalization systematic on each background process group
- MC template statistical uncertainties via a shared (HistFactory-convention)
  staterror modifier per channel
- Uses pyhf; parameter uncertainties from MINUIT/HESSE when iminuit is
  available, otherwise from a finite-difference Hessian fallback

v_fable changes relative to the v8-era script:
- The fit ALWAYS prefers kfold_scores.csv (out-of-fold scores for every
  selected event). test_scores.csv is only a fallback and its weight
  scaling is derived from training_metrics.json instead of a hardcoded 0.30.
- Missing score files are a hard error. There is no silent fallback to an
  older model directory.
- staterror is shared across samples in a channel by default
  (--staterror-mode per-sample restores the old per-sample gammas).
- A 1D profile-likelihood scan of mu validates the parabolic (HESSE) error.

Outputs: fit_results.json and plots under <model_dir>/plots/.
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

from ml_config import (
    DEFAULT_MODEL_DIR,
    FIT_BACKGROUND_GROUPS,
    SIGNAL_SAMPLES,
)

CATEGORY_LABELS = {
    "lep_on": "leptonic-W-on-shell-like",
    "had_on": "hadronic-W-on-shell-like",
}


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


# ----------------------------------------------------------------------------
# Score loading
# ----------------------------------------------------------------------------

def resolve_scores_path(args):
    """Locate the score file. kfold_scores.csv is strongly preferred.

    Returns (scores_path, model_dir). Raises on missing files instead of
    silently falling back to a different model version.
    """
    if args.scores:
        scores_path = Path(args.scores)
        if not scores_path.exists():
            raise RuntimeError(f"--scores file does not exist: {scores_path}")
        return scores_path, scores_path.parent

    model_dir = Path(args.model_dir) if args.model_dir else ANALYSIS_DIR / DEFAULT_MODEL_DIR
    kfold_path = model_dir / "kfold_scores.csv"
    test_path = model_dir / "test_scores.csv"
    if kfold_path.exists():
        return kfold_path, model_dir
    if test_path.exists():
        print(
            "[warn] kfold_scores.csv not found; falling back to test_scores.csv. "
            "The final result should use out-of-fold scores — rerun train with --kfold > 0."
        )
        return test_path, model_dir
    raise RuntimeError(
        f"No score file found in {model_dir} (looked for kfold_scores.csv and "
        "test_scores.csv). Run the train step first, or pass --scores/--model-dir "
        "explicitly. Refusing to fall back to another model directory."
    )


def load_scores(scores_path, model_dir):
    """Load scores and normalise weights to the full selected sample."""
    df = pd.read_csv(scores_path)
    if "kfold" in scores_path.name:
        print("  Using k-fold out-of-fold scores (all selected events, no scaling)")
        return df, "kfold_scores.csv"

    metrics_path = model_dir / "training_metrics.json"
    if not metrics_path.exists():
        raise RuntimeError(
            f"test_scores.csv requires {metrics_path} to derive the test fraction; "
            "file not found."
        )
    with open(metrics_path) as handle:
        metrics = json.load(handle)
    n_train = metrics.get("n_train")
    n_test = metrics.get("n_test")
    if not n_train or not n_test:
        raise RuntimeError(f"{metrics_path} lacks n_train/n_test; cannot scale test weights.")
    test_frac = n_test / (n_train + n_test)
    df["phys_weight"] = df["phys_weight"] / test_frac
    print(f"  Scaling test-set weights by 1/{test_frac:.4f} (from training_metrics.json)")
    return df, "test_scores.csv"


def ensure_score_categories(df):
    """Recover reco W-topology categories from score metadata when possible."""
    if "w_topology_category" not in df.columns and "lepW_offshell_like" in df.columns:
        df["w_topology_category"] = (df["lepW_offshell_like"] > 0.5).astype(float)
    if "w_topology_category" not in df.columns and "deltaW_onShell" in df.columns:
        df["w_topology_category"] = (df["deltaW_onShell"] >= 0).astype(float)
    return df


def filter_reco_category(df, category):
    """Filter score rows to one reco-level W-topology category."""
    if category == "all":
        return df
    if "w_topology_category" not in df.columns:
        raise RuntimeError(
            "Requested a W-topology category fit, but the score file does not "
            "contain w_topology_category/lepW_offshell_like/deltaW_onShell."
        )
    if category == "lep_on":
        return df[df["w_topology_category"] < 0.5].copy()
    if category == "had_on":
        return df[df["w_topology_category"] >= 0.5].copy()
    raise ValueError(f"Unknown category {category!r}")


# ----------------------------------------------------------------------------
# Templates
# ----------------------------------------------------------------------------

def build_templates(df, nbins=20, bdt_cut=None, score_range=(0, 1)):
    """Build signal and per-group background histograms from BDT scores."""
    if bdt_cut is not None:
        df = df[df["bdt_score"] >= bdt_cut]

    bins = np.linspace(score_range[0], score_range[1], nbins + 1)

    sig_mask = df["y_true"] == 1
    sig_hist, _ = np.histogram(
        df.loc[sig_mask, "bdt_score"], bins=bins, weights=df.loc[sig_mask, "phys_weight"],
    )
    sig_w2, _ = np.histogram(
        df.loc[sig_mask, "bdt_score"], bins=bins, weights=df.loc[sig_mask, "phys_weight"] ** 2,
    )
    sig_err = np.sqrt(sig_w2)

    bkg_hists = {}
    bkg_errs = {}
    for group_name, samples in FIT_BACKGROUND_GROUPS.items():
        mask = df["sample_name"].isin(samples) & (df["y_true"] == 0)
        if mask.sum() == 0:
            continue
        h, _ = np.histogram(
            df.loc[mask, "bdt_score"], bins=bins, weights=df.loc[mask, "phys_weight"],
        )
        w2, _ = np.histogram(
            df.loc[mask, "bdt_score"], bins=bins, weights=df.loc[mask, "phys_weight"] ** 2,
        )
        if h.sum() > 0:
            bkg_hists[group_name] = h
            bkg_errs[group_name] = np.sqrt(w2)

    return sig_hist, sig_err, bkg_hists, bkg_errs, bins


def build_templates_by_category(df, nbins=20, bdt_cut=None, score_range=(0, 1)):
    """Build one BDT template set per reco W-topology category."""
    templates = {}
    for category in ("lep_on", "had_on"):
        category_df = filter_reco_category(df, category)
        if category_df.empty:
            continue
        sig_hist, sig_err, bkg_hists, bkg_errs, bins = build_templates(
            category_df, nbins=nbins, bdt_cut=bdt_cut, score_range=score_range,
        )
        if sig_hist.sum() <= 0 and not bkg_hists:
            continue
        templates[category] = {
            "sig_hist": sig_hist,
            "sig_err": sig_err,
            "bkg_hists": bkg_hists,
            "bkg_errs": bkg_errs,
            "bins": bins,
        }
    if not templates:
        raise RuntimeError("No non-empty W-topology category templates were built.")
    return templates


# ----------------------------------------------------------------------------
# pyhf model
# ----------------------------------------------------------------------------

def _build_channel_samples(sig_hist, sig_err, bkg_hists, bkg_errs,
                           norm_uncertainty, staterror_mode, channel_name):
    """Build pyhf samples for one channel.

    staterror_mode:
      'shared'     — one HistFactory-convention staterror per channel, shared
                     by all samples (per-bin gammas on the total MC).
      'per-sample' — independent staterror per sample (legacy v8 behaviour).
      'off'        — no MC statistical nuisance parameters.
    Background normsys names are shared across channels so each process group
    has one correlated normalization nuisance.
    """
    sig_hist = np.maximum(sig_hist, 1e-6)
    sig_err = np.maximum(sig_err, 1e-6)
    shared_name = f"staterror_{channel_name}"

    sig_modifiers = [{"name": "mu", "type": "normfactor", "data": None}]
    if staterror_mode == "shared":
        sig_modifiers.append({"name": shared_name, "type": "staterror", "data": sig_err.tolist()})
    elif staterror_mode == "per-sample":
        sig_modifiers.append({"name": f"staterror_sig_{channel_name}", "type": "staterror",
                              "data": sig_err.tolist()})
    samples = [{"name": "signal", "data": sig_hist.tolist(), "modifiers": sig_modifiers}]

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
        if staterror_mode == "shared":
            modifiers.append({"name": shared_name, "type": "staterror", "data": err.tolist()})
        elif staterror_mode == "per-sample":
            modifiers.append({"name": f"staterror_{group_name}_{channel_name}",
                              "type": "staterror", "data": err.tolist()})
        samples.append({"name": group_name, "data": hist.tolist(), "modifiers": modifiers})
    return samples


def build_pyhf_spec(channel_payloads, norm_uncertainty=0.01, staterror_mode="shared"):
    """Build a single- or multi-channel pyhf spec.

    channel_payloads: dict channel_name -> {sig_hist, sig_err, bkg_hists, bkg_errs}
    """
    channels = []
    observations = []
    for channel_name, payload in channel_payloads.items():
        channels.append({
            "name": channel_name,
            "samples": _build_channel_samples(
                payload["sig_hist"], payload["sig_err"],
                payload["bkg_hists"], payload["bkg_errs"],
                norm_uncertainty, staterror_mode, channel_name,
            ),
        })
        observations.append({"name": channel_name, "data": []})

    return {
        "version": "1.0.0",
        "channels": channels,
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
        "observations": observations,
    }


# ----------------------------------------------------------------------------
# Fitting
# ----------------------------------------------------------------------------

def _set_backend(prefer_minuit=True):
    """Select the pyhf backend/optimizer; report which error method is active."""
    import pyhf
    if prefer_minuit:
        try:
            import iminuit  # noqa: F401
            pyhf.set_backend("numpy", "minuit")
            return "minuit-hesse"
        except ImportError:
            print("[warn] iminuit not available; using scipy + finite-difference Hessian")
    pyhf.set_backend("numpy", "scipy")
    return "fd-hessian"


def _fd_hessian_errors(model, data, bestfit):
    """Finite-difference Hessian fallback for parameter uncertainties."""
    import pyhf

    def nll(pars):
        val = pyhf.infer.mle.twice_nll(pyhf.tensorlib.astensor(pars), data, model)
        return float(np.asarray(val).item()) / 2.0

    n = len(bestfit)
    eps = 1e-4
    hessian = np.zeros((n, n))
    for i in range(n):
        for j in range(i, n):
            pp, pm, mp, mm = (bestfit.copy() for _ in range(4))
            pp[i] += eps; pp[j] += eps
            pm[i] += eps; pm[j] -= eps
            mp[i] -= eps; mp[j] += eps
            mm[i] -= eps; mm[j] -= eps
            hessian[i, j] = hessian[j, i] = (
                nll(pp) - nll(pm) - nll(mp) + nll(mm)
            ) / (4 * eps * eps)
    try:
        cov = np.linalg.inv(hessian)
    except np.linalg.LinAlgError as exc:
        raise RuntimeError(
            "Finite-difference Hessian is singular; parameter uncertainties "
            "unavailable. Install iminuit (Key4hep env) for MINUIT errors."
        ) from exc
    diag = np.diag(cov)
    if np.any(diag <= 0):
        raise RuntimeError(
            "Finite-difference Hessian has non-positive curvature; "
            "uncertainties invalid."
        )
    return np.sqrt(diag)


def fit_asimov(spec, channel_totals, error_method):
    """Asimov fit: expected data = nominal signal + background per channel."""
    import pyhf

    spec = json.loads(json.dumps(spec))
    for observation, total in zip(spec["observations"], channel_totals):
        observation["data"] = np.asarray(total, dtype=float).tolist()

    ws = pyhf.Workspace(spec)
    model = ws.model()
    data = ws.data(model)

    if error_method == "minuit-hesse":
        result = np.asarray(pyhf.infer.mle.fit(data, model, return_uncertainties=True))
        bestfit, errors = result[:, 0], result[:, 1]
    else:
        bestfit = np.asarray(pyhf.infer.mle.fit(data, model))
        errors = _fd_hessian_errors(model, data, bestfit)

    mu_idx = model.config.poi_index
    fit_results = {
        name: {"value": float(bestfit[i]), "error": float(errors[i])}
        for i, name in enumerate(model.config.par_names)
    }
    return float(bestfit[mu_idx]), float(errors[mu_idx]), fit_results, (model, data)


def profile_scan_mu(model, data, mu_hat, mu_err, n_points=21, width_sigma=2.5):
    """1D profile-likelihood scan of mu to validate the parabolic error.

    Returns dict with scan points and the +/- 1 sigma crossings of
    2*[NLL(mu) - NLL(mu_hat)] = 1.
    """
    import pyhf

    _, nll_hat = pyhf.infer.mle.fit(data, model, return_fitted_val=True)
    nll_hat = float(np.asarray(nll_hat).item())

    poi_bounds = model.config.suggested_bounds()[model.config.poi_index]
    lo = max(poi_bounds[0], mu_hat - width_sigma * mu_err)
    hi = min(poi_bounds[1], mu_hat + width_sigma * mu_err)
    mu_values = np.linspace(lo, hi, n_points)
    q_values = []
    for mu_test in mu_values:
        _, twice_nll = pyhf.infer.mle.fixed_poi_fit(
            float(mu_test), data, model, return_fitted_val=True,
        )
        q_values.append(float(np.asarray(twice_nll).item()) - nll_hat)
    q_values = np.asarray(q_values)

    def crossing(side):
        mask = mu_values > mu_hat if side > 0 else mu_values < mu_hat
        xs, qs = mu_values[mask], q_values[mask]
        if side < 0:
            xs, qs = xs[::-1], qs[::-1]
        for i in range(len(xs) - 1):
            if (qs[i] - 1.0) * (qs[i + 1] - 1.0) <= 0:
                x0, x1, q0, q1 = xs[i], xs[i + 1], qs[i], qs[i + 1]
                if q1 == q0:
                    return float(x0)
                return float(x0 + (1.0 - q0) * (x1 - x0) / (q1 - q0))
        return None

    up, down = crossing(+1), crossing(-1)
    return {
        "mu_values": mu_values.tolist(),
        "twice_delta_nll": q_values.tolist(),
        "sigma_up": (up - mu_hat) if up is not None else None,
        "sigma_down": (mu_hat - down) if down is not None else None,
    }


def scan_bdt_cut(df, cuts=None, fit_nbins=1, norm_uncertainty=0.01,
                 staterror_mode="shared", error_method="minuit-hesse"):
    """Single-bin counting reference: scan BDT thresholds."""
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

        payload = {"bdt_score": {"sig_hist": sig_hist, "sig_err": sig_err,
                                 "bkg_hists": bkg_hists, "bkg_errs": bkg_errs}}
        spec = build_pyhf_spec(payload, norm_uncertainty, staterror_mode)
        total = sig_hist + sum(bkg_hists.values())
        try:
            mu_hat, mu_err, _, _ = fit_asimov(spec, [total], error_method)
            rel_err = mu_err / mu_hat if mu_hat > 0 else float("inf")
        except Exception as exc:
            print(f"  cut={cut:.2f}: fit failed ({exc})")
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
              f"S/sqrt(B)={n_sig/np.sqrt(n_bkg):.1f}, dmu/mu={rel_err*100:.2f}%")

    return results


# ----------------------------------------------------------------------------
# Plots
# ----------------------------------------------------------------------------

def make_fit_plots(output_dir, scan_results, best_result, sig_hist, bkg_hists,
                   bins, shape_rel_unc_pct=None, profile_scan=None):
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

    # 2. Template shapes at the final working point
    fig, ax = plt.subplots(figsize=(7.6, 5.4))
    bin_width = bins[1] - bins[0]

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
            bins[:-1], arr, width=bin_width, align="edge", bottom=cumulative,
            color=color_map[label], edgecolor="white", linewidth=0.45, alpha=0.92,
        )
        cumulative += arr
        legend_handles.append(bars[0])
        legend_labels.append(label.replace("_", " "))

    total_bkg = cumulative.copy()
    total_bkg_handle = ax.step(
        bins[:-1], total_bkg, where="post",
        color="#1F2D3A", linewidth=1.4, alpha=0.95, label="Total background",
    )[0]

    raw_scale = (0.18 * total_bkg.max() / sig_hist.max()) if sig_hist.sum() > 0 and total_bkg.max() > 0 else 1.0
    sig_scale = _nice_scale_factor(raw_scale)
    sig_handle = ax.bar(
        bins[:-1], sig_hist * sig_scale, width=bin_width, align="edge",
        fill=False, edgecolor="#D62728", linewidth=1.8, linestyle="-",
        label=f"Signal x {sig_scale}", zorder=5,
    )[0]

    ax.set_ylabel(f"Events / {bin_width:.2f}")
    ax.set_xlabel("BDT score")
    ax.set_title(f"{len(sig_hist)}-bin BDT templates used in the profile-likelihood fit")
    ax.text(0.03, 0.95, r'$\mathbf{FCC\text{-}ee}$ Simulation',
            transform=ax.transAxes, fontsize=10, va='top', fontstyle='italic')
    ax.text(0.03, 0.89, r'$\sqrt{s}=240$ GeV, $10.8\,\mathrm{ab}^{-1}$',
            transform=ax.transAxes, fontsize=9, va='top')
    ax.set_yscale("log")
    ax.set_ylim(bottom=0.1, top=max(total_bkg.max(), (sig_hist * sig_scale).max()) * 12.0)
    ax.set_xlim(0.0, 1.0)
    ax.set_xticks(np.linspace(0.0, 1.0, 11))
    ax.yaxis.set_major_locator(LogLocator(base=10.0, numticks=12))
    ax.yaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2, 10), numticks=120))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.grid(axis="y", which="major", alpha=0.22, linewidth=0.8)
    ax.grid(axis="y", which="minor", alpha=0.10, linewidth=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(
        [sig_handle, total_bkg_handle, *legend_handles[::-1]],
        [f"Signal x {sig_scale}", "Total background", *legend_labels[::-1]],
        fontsize=8.3, ncol=3, frameon=False, loc="upper center",
        bbox_to_anchor=(0.5, 1.02), columnspacing=1.1, handlelength=2.4,
    )
    fig.tight_layout()
    fig.savefig(plots_dir / "fit_templates.pdf", dpi=170)
    fig.savefig(plots_dir / "fit_templates.png", dpi=170)
    plt.close(fig)

    # 3. Rank-ordered BDT bins with purity panel
    rank_order = np.arange(len(sig_hist))[::-1]
    rank_bins = np.arange(1, len(sig_hist) + 1)
    sig_rank = sig_hist[rank_order]
    bkg_rank_arrays = [arr[rank_order] for arr in bkg_arrays]
    bkg_rank_colors = [color_map[label] for label in bkg_labels]
    total_rank = np.sum(np.asarray(bkg_rank_arrays), axis=0) if bkg_rank_arrays else np.zeros_like(sig_rank)

    fig, (ax_top, ax_bottom) = plt.subplots(
        2, 1, figsize=(7.4, 6.6), sharex=True,
        gridspec_kw={"height_ratios": [3.0, 1.15], "hspace": 0.05},
    )
    cumulative = np.zeros_like(rank_bins, dtype=float)
    for label, arr, color in zip(bkg_labels, bkg_rank_arrays, bkg_rank_colors):
        ax_top.bar(rank_bins, arr, bottom=cumulative, width=0.90,
                   color=color, alpha=0.88, label=f"Bkg: {label}", linewidth=0.0)
        cumulative += arr
    ax_top.step(
        np.r_[rank_bins, rank_bins[-1] + 1] - 0.5,
        np.r_[sig_rank * sig_scale, sig_rank[-1] * sig_scale],
        where="post", color="black", linewidth=2.0, label=f"Signal (x{sig_scale})",
    )
    ax_top.set_ylabel("Events / rank bin")
    ax_top.set_title("Rank-ordered BDT bins")
    ax_top.set_yscale("log")
    ax_top.set_ylim(bottom=0.1)
    ax_top.legend(fontsize=8.6, ncol=2, frameon=False, loc="upper center")
    ax_top.text(0.03, 0.95, r'$\mathbf{FCC\text{-}ee}$ Simulation',
                transform=ax_top.transAxes, fontsize=10, va='top', fontstyle='italic')
    ax_top.text(0.03, 0.89, r'$\sqrt{s}=240$ GeV, $10.8\,\mathrm{ab}^{-1}$',
                transform=ax_top.transAxes, fontsize=9, va='top')

    purity = np.divide(sig_rank, sig_rank + total_rank,
                       out=np.zeros_like(sig_rank), where=(sig_rank + total_rank) > 0)
    ax_bottom.plot(rank_bins, purity, color="#2C7FB8", marker="o", markersize=3.8, linewidth=1.8)
    ax_bottom.set_ylabel(r"$S/(S+B)$")
    ax_bottom.set_xlabel("BDT rank bin (1 = highest score)")
    ax_bottom.set_ylim(0.0, min(1.0, max(0.15, purity.max() * 1.25 if len(purity) else 0.15)))
    ax_bottom.set_xlim(0.5, len(rank_bins) + 0.5)
    ax_bottom.grid(axis="y", alpha=0.22)
    fig.tight_layout()
    fig.savefig(plots_dir / "bdt_score_rank.pdf", dpi=150)
    fig.savefig(plots_dir / "bdt_score_rank.png", dpi=150)
    plt.close(fig)

    # 4. Profile likelihood scan of mu
    if profile_scan is not None:
        fig, ax = plt.subplots(figsize=(6.0, 4.4))
        ax.plot(profile_scan["mu_values"], profile_scan["twice_delta_nll"],
                color="#2C7FB8", marker="o", markersize=3.5, linewidth=1.6)
        ax.axhline(1.0, color="#888888", linestyle="--", linewidth=1.0)
        ax.set_xlabel(r"$\mu$")
        ax.set_ylabel(r"$2\,\Delta\mathrm{NLL}$")
        ax.set_title("Profile likelihood scan")
        up, down = profile_scan.get("sigma_up"), profile_scan.get("sigma_down")
        if up is not None and down is not None:
            ax.text(0.03, 0.95, rf"$+1\sigma$ = {up:.5f}, $-1\sigma$ = {down:.5f}",
                    transform=ax.transAxes, fontsize=9, va="top")
        ax.grid(alpha=0.25)
        fig.tight_layout()
        fig.savefig(plots_dir / "mu_profile_scan.pdf", dpi=150)
        fig.savefig(plots_dir / "mu_profile_scan.png", dpi=150)
        plt.close(fig)

    print(f"  Fit plots saved to {plots_dir}/")


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Profile likelihood fit for H->WW* measurement")
    parser.add_argument("--scores", type=str, default=None,
                        help="Explicit path to a score CSV (kfold_scores.csv preferred)")
    parser.add_argument("--model-dir", type=str, default=None,
                        help=f"Model directory (default: {DEFAULT_MODEL_DIR})")
    parser.add_argument("--nbins", type=int, default=20,
                        help="Number of BDT score bins for the template fit")
    parser.add_argument("--norm-unc", type=float, default=0.01,
                        help="Background normalization uncertainty (default: 1%%)")
    parser.add_argument("--bdt-cut", type=float, default=None,
                        help="Fixed BDT score cut for the shape fit (default: none)")
    parser.add_argument("--no-scan", action="store_true",
                        help="Skip the 1-bin counting reference scan")
    parser.add_argument("--no-plots", action="store_true", help="Skip diagnostic plots")
    parser.add_argument("--no-profile-scan", action="store_true",
                        help="Skip the 1D profile-likelihood scan of mu")
    parser.add_argument("--staterror-mode", choices=["shared", "per-sample", "off"],
                        default="shared",
                        help="MC template statistical uncertainty treatment (default: shared)")
    parser.add_argument("--category", choices=["all", "lep_on", "had_on"], default="all",
                        help="Fit one reco W-topology category instead of the inclusive sample.")
    parser.add_argument("--split-w-categories", action="store_true",
                        help="Simultaneous two-channel fit split by reco W-topology category.")
    args = parser.parse_args()

    scores_path, model_dir = resolve_scores_path(args)
    print(f"Loading scores from {scores_path}")
    df, score_source = load_scores(scores_path, model_dir)
    df = ensure_score_categories(df)
    print(f"  {len(df)} events loaded ({(df['y_true']==1).sum()} signal, "
          f"{(df['y_true']==0).sum()} background)")

    known_samples = set(SIGNAL_SAMPLES) | {
        s for samples in FIT_BACKGROUND_GROUPS.values() for s in samples
    }
    unknown = sorted(set(df["sample_name"].unique()) - known_samples)
    if unknown:
        raise RuntimeError(
            f"Score file contains samples not covered by the fit grouping: {unknown}. "
            "Update FIT_BACKGROUND_GROUPS in ml_config.py."
        )
    absent = sorted(known_samples - set(df["sample_name"].unique()))
    if absent:
        print(
            "[warn] expected samples with no scored events — legitimate only for "
            "0-pass samples (e.g. tautau after the full selection); verify the "
            f"treemaker/train logs if unexpected: {absent}"
        )

    output_dir = scores_path.parent
    error_method = _set_backend(prefer_minuit=True)
    print(f"  Error method: {error_method}; staterror mode: {args.staterror_mode}")

    if args.split_w_categories and args.category != "all":
        raise RuntimeError("--split-w-categories and --category are mutually exclusive.")
    if args.category != "all":
        before = len(df)
        df = filter_reco_category(df, args.category)
        print(f"  Category filter {args.category} ({CATEGORY_LABELS[args.category]}): "
              f"{len(df)}/{before} events")

    if args.split_w_categories:
        bdt_cut = args.bdt_cut if args.bdt_cut is not None else 0.0
        print(f"\nSimultaneous {args.nbins}-bin category shape fit at BDT cut = {bdt_cut:.2f}:")
        templates = build_templates_by_category(df, nbins=args.nbins, bdt_cut=bdt_cut)

        payloads = {f"bdt_score_{cat}": p for cat, p in templates.items()}
        channel_totals = []
        category_summary = {}
        for cat, payload in templates.items():
            total = payload["sig_hist"] + sum(payload["bkg_hists"].values())
            channel_totals.append(total)
            n_sig = float(payload["sig_hist"].sum())
            n_bkg = float(sum(h.sum() for h in payload["bkg_hists"].values()))
            category_summary[cat] = {
                "label": CATEGORY_LABELS[cat],
                "n_signal": n_sig,
                "n_background": n_bkg,
                "bkg_yields": {k: float(v.sum()) for k, v in payload["bkg_hists"].items()},
            }
            print(f"  {cat:6s} ({CATEGORY_LABELS[cat]}): S={n_sig:.0f}, B={n_bkg:.0f}")

        spec = build_pyhf_spec(payloads, args.norm_unc, args.staterror_mode)
        mu_hat, mu_err, fit_results, _ = fit_asimov(spec, channel_totals, error_method)
        rel_unc = mu_err / mu_hat if mu_hat > 0 else float("inf")

        floor_spec = build_pyhf_spec(payloads, args.norm_unc, "off")
        floor_mu, floor_err, _, _ = fit_asimov(floor_spec, channel_totals, error_method)
        floor_rel = floor_err / floor_mu if floor_mu > 0 else float("inf")

        print(f"\n  === CATEGORY RESULT ===")
        print(f"  mu_hat = {mu_hat:.4f} +/- {mu_err:.5f}")
        print(f"  Relative uncertainty: {rel_unc*100:.3f}%")
        print(f"  Physics-only floor (no MC-stat nuisances): {floor_rel*100:.3f}%")

        result = {
            "fit_mode": "simultaneous_reco_w_categories",
            "score_source": score_source,
            "error_method": error_method,
            "staterror_mode": args.staterror_mode,
            "bdt_cut": bdt_cut,
            "nbins": args.nbins,
            "norm_uncertainty": args.norm_unc,
            "mu_hat": mu_hat,
            "mu_err": mu_err,
            "relative_uncertainty_pct": rel_unc * 100,
            "physics_only_mu_hat": floor_mu,
            "physics_only_mu_err": floor_err,
            "physics_only_rel_uncertainty_pct": floor_rel * 100,
            "fit_parameters": fit_results,
            "categories": category_summary,
        }
        result_path = output_dir / "fit_results_w_categories.json"
        with open(result_path, "w") as handle:
            json.dump(result, handle, indent=2)
        print(f"\n  Category results saved to {result_path}")

        if not args.no_plots:
            for cat, payload in templates.items():
                make_fit_plots(
                    output_dir / f"category_{cat}", [], None,
                    payload["sig_hist"], payload["bkg_hists"], payload["bins"],
                )
        return

    # 1-bin counting reference scan
    if not args.no_scan:
        print("\nScanning BDT score cuts (1-bin counting reference):")
        scan_results = scan_bdt_cut(
            df, fit_nbins=1, norm_uncertainty=args.norm_unc,
            staterror_mode=args.staterror_mode, error_method=error_method,
        )
        if not scan_results:
            raise RuntimeError("All BDT counting-scan fits failed. Check input data.")
        best_counting = min(scan_results, key=lambda r: r["rel_uncertainty"])
        print(f"\n  Best 1-bin counting cut: {best_counting['bdt_cut']:.2f}")
        print(f"  S={best_counting['n_sig']:.0f}, B={best_counting['n_bkg']:.0f}")
        print(f"  Expected dmu/mu = {best_counting['rel_uncertainty']*100:.2f}%")
    else:
        scan_results = []
        best_counting = None

    # Headline shape fit over the full score range (unless a cut is requested)
    bdt_cut = args.bdt_cut if args.bdt_cut is not None else 0.0
    print(f"\nFinal {args.nbins}-bin shape fit at BDT cut = {bdt_cut:.2f}:")
    sig_hist, sig_err, bkg_hists, bkg_errs, bins = build_templates(
        df, nbins=args.nbins, bdt_cut=bdt_cut,
    )
    n_sig = sig_hist.sum()
    n_bkg = sum(h.sum() for h in bkg_hists.values())
    print(f"  Signal events: {n_sig:.1f}")
    print(f"  Background events: {n_bkg:.1f}")
    for name, h in bkg_hists.items():
        print(f"    {name}: {h.sum():.1f}")

    payload = {"bdt_score": {"sig_hist": sig_hist, "sig_err": sig_err,
                             "bkg_hists": bkg_hists, "bkg_errs": bkg_errs}}
    total = sig_hist + sum(bkg_hists.values())
    spec = build_pyhf_spec(payload, args.norm_unc, args.staterror_mode)
    mu_hat, mu_err, fit_results, (model, data) = fit_asimov(spec, [total], error_method)
    rel_unc = mu_err / mu_hat if mu_hat > 0 else float("inf")

    floor_spec = build_pyhf_spec(payload, args.norm_unc, "off")
    floor_mu, floor_err, _, _ = fit_asimov(floor_spec, [total], error_method)
    floor_rel = floor_err / floor_mu if floor_mu > 0 else float("inf")

    profile = None
    if not args.no_profile_scan:
        print("\n  Profile-likelihood scan of mu (validates the parabolic error):")
        try:
            profile = profile_scan_mu(model, data, mu_hat, mu_err)
        except Exception as exc:
            # The scan is a validation extra — never let it discard the fit.
            print(f"  [warn] profile scan failed ({exc}); continuing without it")
        if profile is not None:
            up, down = profile.get("sigma_up"), profile.get("sigma_down")
            if up is not None and down is not None:
                print(f"    +1 sigma = {up:.5f}, -1 sigma = {down:.5f} "
                      f"(HESSE: {mu_err:.5f})")

    print(f"\n  === RESULT ===")
    print(f"  mu_hat = {mu_hat:.4f} +/- {mu_err:.5f}")
    print(f"  Relative uncertainty: {rel_unc*100:.3f}%")
    print(f"  => Expected precision on sigma_ZH x BR(H->WW*): {rel_unc*100:.3f}%")
    print(f"  Physics-only floor (no MC-stat nuisances): {floor_rel*100:.3f}%")

    result = {
        "score_source": score_source,
        "error_method": error_method,
        "staterror_mode": args.staterror_mode,
        "category": args.category,
        "bdt_cut": bdt_cut,
        "nbins": args.nbins,
        "scan_mode": "counting_1bin",
        "norm_uncertainty": args.norm_unc,
        "n_signal": float(n_sig),
        "n_background": float(n_bkg),
        "mu_hat": mu_hat,
        "mu_err": mu_err,
        "relative_uncertainty_pct": rel_unc * 100,
        "physics_only_mu_hat": floor_mu,
        "physics_only_mu_err": floor_err,
        "physics_only_rel_uncertainty_pct": floor_rel * 100,
        "physics_only_note": (
            "Shape-fit precision with the same normalization systematics but "
            "without MC template statistical nuisance parameters."
        ),
        "fit_parameters": fit_results,
        "bkg_yields": {k: float(v.sum()) for k, v in bkg_hists.items()},
    }
    if profile is not None:
        result["mu_profile_scan"] = {
            "sigma_up": profile["sigma_up"],
            "sigma_down": profile["sigma_down"],
        }
    if scan_results:
        result["counting_scan_results"] = scan_results

    # Category-filtered fits get their own file so they can never be mistaken
    # for (or clobber) the headline inclusive result.
    suffix = "" if args.category == "all" else f"_{args.category}"
    result_path = output_dir / f"fit_results{suffix}.json"
    with open(result_path, "w") as handle:
        json.dump(result, handle, indent=2)
    print(f"\n  Results saved to {result_path}")

    if not args.no_plots:
        make_fit_plots(
            output_dir, scan_results, best_counting, sig_hist, bkg_hists, bins,
            shape_rel_unc_pct=rel_unc * 100, profile_scan=profile,
        )


if __name__ == "__main__":
    main()
