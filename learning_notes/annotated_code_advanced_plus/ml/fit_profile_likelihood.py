#!/usr/bin/env python3
# Profile-likelihood inference layer using pyhf templates from BDT score space.
#
# ML outputs are compressed into a single score observable and then lifted into a
# full likelihood model that constrains signal strength and dedicated nuisance terms.

"""Profile likelihood fit for sigma_ZH x BR(H->WW*) measurement.

Methodology follows Jan Eysermans et al. (DOI: 10.17181/9v8ey-n6k50):
- Template fit to BDT score distribution
- Signal strength mu = (sigma x BR)_obs / (sigma x BR)_SM
- 1% flat normalization systematic on each background process
- Uses pyhf for the statistical model

Inputs:
  - BDT kfold_scores.csv (preferred, from train_xgboost_bdt.py)
  - Or: test_scores.csv (fallback, with weight rescaling by 1/test_frac)

Outputs:
  - Expected mu_hat, sigma(mu) from Asimov dataset
  - Expected relative uncertainty on sigma_ZH x BR(H->WW*)
"""

# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import argparse
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import json
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import sys
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
from pathlib import Path

# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import numpy as np
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import pandas as pd

# [Workflow] Configuration binding; this line defines a stable contract across modules.
THIS_DIR = Path(__file__).resolve().parent
# [Workflow] Configuration binding; this line defines a stable contract across modules.
ANALYSIS_DIR = THIS_DIR.parent
# [Context] Supporting line for the active lvqq analysis stage.
sys.path.insert(0, str(ANALYSIS_DIR))

# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
from ml_config import BACKGROUND_SAMPLES, DEFAULT_MODEL_DIR, SIGNAL_SAMPLES


# [I/O] Read score table containing labels, weights, and model scores.
def load_scores(scores_path):
    """Load BDT scores from CSV.

    Expected keys:
      - y_true: truth label (1 signal, 0 background)
      - phys_weight: expected event weight at target luminosity
      - sample_name: process label used for grouped nuisances
      - bdt_score: trained classifier output

    Missing columns break template construction silently in subtle ways, so explicit
    schema awareness is part of the statistical correctness argument here.
    """
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    df = pd.read_csv(scores_path)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    return df


# [Stats] Bin score distributions into signal/background templates for likelihood fitting.
def build_templates(df, nbins=20, bdt_cut=None, score_range=(0, 1)):
    """Build signal and background histograms from BDT scores.

    The ML score is treated as a physics observable: each bin becomes one piece
    of the template likelihood. Grouping by background family keeps nuisance
    control interpretable and prevents one large class from absorbing another.
    """
    # There are two "selection layers" here:
    # 1) event-level topology/filtering already happened in h_hww_lvqq and treemaker,
    # 2) optional score cut (bdt_cut) is a second-stage analysis choice for expected precision.
    # This block converts score choice into explicit binned templates for likelihood fitting.

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    if bdt_cut is not None:
# [Workflow] Copy exactly the curated deliverables to paper directories.
        df = df[df["bdt_score"] >= bdt_cut].copy()

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    bins = np.linspace(score_range[0], score_range[1], nbins + 1)

    # Signal template (with MC-stat error band).
    # This is expected event yield, not normalized probability.
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    sig_mask = df["y_true"] == 1
# [Stats] Build binned templates required by shape-based likelihood fitting.
    sig_hist, _ = np.histogram(
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        df.loc[sig_mask, "bdt_score"],
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        bins=bins,
# [Stats] Physics weights propagate cross-section and luminosity to training/fit observables.
        weights=df.loc[sig_mask, "phys_weight"],
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    )
# [Stats] Build binned templates required by shape-based likelihood fitting.
    sig_w2, _ = np.histogram(
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        df.loc[sig_mask, "bdt_score"],
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        bins=bins,
# [Stats] Physics weights propagate cross-section and luminosity to training/fit observables.
        weights=df.loc[sig_mask, "phys_weight"] ** 2,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    )
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    sig_err = np.sqrt(sig_w2)

    # Background grouping corresponds to independent normalisation systematics:
    # WW, ZZ, light qqqq-like 2f, tau pair, and subleading H-associated states.
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    bkg_groups = {
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        "WW": ["p8_ee_WW_ecm240"],
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        "ZZ": ["p8_ee_ZZ_ecm240"],
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        "qq": [s for s in BACKGROUND_SAMPLES if s.startswith("wz3p6_ee_") and "tautau" not in s],
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        "tautau": ["wz3p6_ee_tautau_ecm240"],
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        "ZH_other": [
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            s for s in BACKGROUND_SAMPLES
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            if s.startswith((
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                "wzp6_ee_qqH_H",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                "wzp6_ee_bbH_H",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                "wzp6_ee_ccH_H",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                "wzp6_ee_ssH_H",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            ))
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        ],
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    }

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    bkg_hists = {}
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    bkg_errs = {}
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    for group_name, samples in bkg_groups.items():
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        mask = df["sample_name"].isin(samples) & (df["y_true"] == 0)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        if mask.sum() == 0:
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            continue
# [Stats] Build binned templates required by shape-based likelihood fitting.
        h, _ = np.histogram(
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            df.loc[mask, "bdt_score"],
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            bins=bins,
# [Stats] Physics weights propagate cross-section and luminosity to training/fit observables.
            weights=df.loc[mask, "phys_weight"],
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        )
# [Stats] Build binned templates required by shape-based likelihood fitting.
        w2, _ = np.histogram(
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            df.loc[mask, "bdt_score"],
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            bins=bins,
# [Stats] Physics weights propagate cross-section and luminosity to training/fit observables.
            weights=df.loc[mask, "phys_weight"] ** 2,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        )
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        if h.sum() > 0:
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            bkg_hists[group_name] = h
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            bkg_errs[group_name] = np.sqrt(w2)

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    return sig_hist, sig_err, bkg_hists, bkg_errs, bins


# [Stats] Construct pyhf JSON spec with POI and nuisance parameters.
def build_pyhf_model(sig_hist, sig_err, bkg_hists, bkg_errs, norm_uncertainty=0.01, use_staterror=True):
    """Build a pyhf model with signal + backgrounds + normalization + MC stat.

    Each background group gets an independent normalization uncertainty.
    All samples get Barlow-Beeston MC statistical uncertainties (staterror).
    Signal is the POI (mu).
    """
    # The fit model is your final physics hypothesis test:
    #  - mu scales only signal strength;
    #  - each background group gets independent normalization nuisance;
    #  - optional staterror keeps MC statistical uncertainty explicit in each bin.

# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
    import pyhf

    # Ensure no negative/zero bins (pyhf requires positive expected rates).
    # Numerical clipping is a technical workaround; if this hits often, inspect
    # cut selections or sample loading first.
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    sig_hist = np.maximum(sig_hist, 1e-6)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    sig_err = np.maximum(sig_err, 1e-6)

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    samples = []

    # Signal sample with optional MC-stat uncertainty.
    # 'mu' is attached here as the final POI and multiplies only this component.
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    sig_modifiers = [
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        {"name": "mu", "type": "normfactor", "data": None},
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ]
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    if use_staterror:
# [Stats] Add systematic and MC-stat uncertainties for conservative, realistic error bars.
        sig_modifiers.append({"name": "staterror_sig", "type": "staterror", "data": sig_err.tolist()})
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    samples.append({
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        "name": "signal",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        "data": sig_hist.tolist(),
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        "modifiers": sig_modifiers,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    })

    # Background sample with independent normsys + optional staterror.
    # This is where each physics-family nuisance is decoupled from the others.
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    for group_name, hist in bkg_hists.items():
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        hist = np.maximum(hist, 1e-6)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        err = np.maximum(bkg_errs.get(group_name, np.zeros_like(hist)), 1e-6)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        modifiers = [
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            {
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                "name": f"norm_{group_name}",
# [Stats] Add systematic and MC-stat uncertainties for conservative, realistic error bars.
                "type": "normsys",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                "data": {"hi": 1.0 + norm_uncertainty, "lo": 1.0 - norm_uncertainty},
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            },
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        ]
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        if use_staterror:
# [Stats] Add systematic and MC-stat uncertainties for conservative, realistic error bars.
            modifiers.append({"name": f"staterror_{group_name}", "type": "staterror", "data": err.tolist()})
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        samples.append({
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            "name": group_name,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            "data": hist.tolist(),
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            "modifiers": modifiers,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        })

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    spec = {
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        "version": "1.0.0",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        "channels": [
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            {
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                "name": "bdt_score",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                "samples": samples,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            }
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        ],
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        "measurements": [
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            {
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                "name": "signal_strength",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                "config": {
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                    "poi": "mu",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                    "parameters": [
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                        {"name": "mu", "bounds": [[0.0, 5.0]], "inits": [1.0]},
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                    ],
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                },
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            }
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        ],
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        "observations": [
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            {
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                "name": "bdt_score",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                "data": [],  # filled by Asimov or observed
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            }
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        ],
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    }

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    return spec


# [Stats] Fit expected dataset at mu=1 to obtain central value and uncertainty estimate.
def fit_asimov(spec, sig_hist, bkg_hists):
    """Run an Asimov dataset fit and estimate local parameter uncertainties.

    Asimov data = expected bin counts at mu=1 from nominal signal and background
    templates. This bypasses detector noise and gives the *expected* precision
    under this model definition.
    """
    # Why Asimov here?
    # It answers “expected sensitivity” of your analysis design (model + cuts + bins),
    # independent of upward/downward statistical fluctuations that could mask structural issues.

# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
    import pyhf
# [Stats] Build likelihood with explicit nuisance structure for precision inference.
    pyhf.set_backend("numpy")

    # Asimov dataset: this is the nominal expected experiment, before statistical
    # fluctuation. We intentionally keep the same binning and nuisances as final fit.
# [Workflow] Copy exactly the curated deliverables to paper directories.
    total = sig_hist.copy()
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    for h in bkg_hists.values():
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        total += h
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    spec["observations"][0]["data"] = total.tolist()

# [Stats] Build likelihood with explicit nuisance structure for precision inference.
    ws = pyhf.Workspace(spec)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    model = ws.model()
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    data = total.tolist() + model.config.auxdata

    # MLE fit on the Asimov pseudo-data.
# [ML] Fit step learns model parameters from weighted event features.
    bestfit, twice_nll_val = pyhf.infer.mle.fit(
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        data, model, return_fitted_val=True
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    )
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    bestfit = np.asarray(bestfit)

    # Compute local covariance from finite-difference Hessian of NLL.
    # This gives a fast precision estimate around the optimum and is used for the
    # headline μ̂ ± σ(μ) reported by this script.
# [Workflow] fit_profile_likelihood.py function nll_func: modularize one operation for deterministic pipeline control.
    def nll_func(pars):
# [Stats] Build likelihood with explicit nuisance structure for precision inference.
        pars_tensor = pyhf.tensorlib.astensor(pars)
# [Stats] Build likelihood with explicit nuisance structure for precision inference.
        val = pyhf.infer.mle.twice_nll(pars_tensor, data, model)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        return float(np.asarray(val).item()) / 2.0

# [Context] Supporting line for the active lvqq analysis stage.
    n = len(bestfit)
# [Context] Supporting line for the active lvqq analysis stage.
    eps = 1e-4
# [Context] Supporting line for the active lvqq analysis stage.
    hessian = np.zeros((n, n))
# [Context] Supporting line for the active lvqq analysis stage.
    f0 = nll_func(bestfit)
# [Context] Supporting line for the active lvqq analysis stage.
    for i in range(n):
# [Context] Supporting line for the active lvqq analysis stage.
        for j in range(i, n):
# [Workflow] Copy exactly the curated deliverables to paper directories.
            pars_pp = bestfit.copy()
# [Context] Supporting line for the active lvqq analysis stage.
            pars_pp[i] += eps
# [Context] Supporting line for the active lvqq analysis stage.
            pars_pp[j] += eps
# [Workflow] Copy exactly the curated deliverables to paper directories.
            pars_pm = bestfit.copy()
# [Context] Supporting line for the active lvqq analysis stage.
            pars_pm[i] += eps
# [Context] Supporting line for the active lvqq analysis stage.
            pars_pm[j] -= eps
# [Workflow] Copy exactly the curated deliverables to paper directories.
            pars_mp = bestfit.copy()
# [Context] Supporting line for the active lvqq analysis stage.
            pars_mp[i] -= eps
# [Context] Supporting line for the active lvqq analysis stage.
            pars_mp[j] += eps
# [Workflow] Copy exactly the curated deliverables to paper directories.
            pars_mm = bestfit.copy()
# [Context] Supporting line for the active lvqq analysis stage.
            pars_mm[i] -= eps
# [Context] Supporting line for the active lvqq analysis stage.
            pars_mm[j] -= eps
# [Context] Supporting line for the active lvqq analysis stage.
            hessian[i, j] = (nll_func(pars_pp) - nll_func(pars_pm) - nll_func(pars_mp) + nll_func(pars_mm)) / (4 * eps * eps)
# [Context] Supporting line for the active lvqq analysis stage.
            hessian[j, i] = hessian[i, j]

# [Context] Supporting line for the active lvqq analysis stage.
    try:
# [Context] Supporting line for the active lvqq analysis stage.
        cov = np.linalg.inv(hessian)
# [Context] Supporting line for the active lvqq analysis stage.
        errors = np.sqrt(np.maximum(np.diag(cov), 0))
# [Context] Supporting line for the active lvqq analysis stage.
    except np.linalg.LinAlgError:
# [Context] Supporting line for the active lvqq analysis stage.
        errors = np.zeros(n)

# [Context] Supporting line for the active lvqq analysis stage.
    mu_idx = model.config.poi_index
# [Context] Supporting line for the active lvqq analysis stage.
    mu_hat = float(bestfit[mu_idx])
# [Context] Supporting line for the active lvqq analysis stage.
    mu_err = float(errors[mu_idx])

    # All parameter results
# [Context] Supporting line for the active lvqq analysis stage.
    par_names = model.config.par_names
# [Context] Supporting line for the active lvqq analysis stage.
    fit_results = {}
# [Context] Supporting line for the active lvqq analysis stage.
    for i, name in enumerate(par_names):
# [Context] Supporting line for the active lvqq analysis stage.
        fit_results[name] = {
# [Context] Supporting line for the active lvqq analysis stage.
            "value": float(bestfit[i]),
# [Context] Supporting line for the active lvqq analysis stage.
            "error": float(errors[i]),
# [Context] Supporting line for the active lvqq analysis stage.
        }

# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return mu_hat, mu_err, fit_results


# [Motivation] Evaluate cut-based reference working points before reporting final shape-fit result.
def scan_bdt_cut(df, cuts=None, fit_nbins=1, norm_uncertainty=0.01, use_staterror=True):
    """Scan score thresholds and evaluate expected precision at each point.

    `fit_nbins=1` gives a counting-style reference curve. It is compared with
    the final multi-bin shape fit to separate topology/threshold choice effects
    from pure shape information.
    """
    # This is a design-study loop, not a training loop:
    # it varies only the post-training BDT threshold and recomputes expected delta(mu)/mu.
    # So it is safe against BDT overtraining; it measures analysis operating point.

# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
    import pyhf

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    if cuts is None:
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        coarse_cuts = np.arange(0.0, 0.90, 0.05)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        fine_cuts = np.arange(0.90, 1.00, 0.01)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        cuts = np.unique(np.round(np.concatenate([coarse_cuts, fine_cuts]), 2))

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    results = []
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    for cut in cuts:
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        sig_hist, sig_err, bkg_hists, bkg_errs, bins = build_templates(
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            df, nbins=fit_nbins, bdt_cut=cut,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        )

# [Physics] Event- and significance-like metrics for sensitivity interpretation.
        n_sig = sig_hist.sum()
# [Physics] Event- and significance-like metrics for sensitivity interpretation.
        n_bkg = sum(h.sum() for h in bkg_hists.values())

# [Physics] Event- and significance-like metrics for sensitivity interpretation.
        if n_sig < 1 or n_bkg < 1:
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            continue

# [Stats] Likelihood/inference block logic and uncertainty quantification.
        spec = build_pyhf_model(sig_hist, sig_err, bkg_hists, bkg_errs, norm_uncertainty, use_staterror=use_staterror)

# [Stats] Likelihood/inference block logic and uncertainty quantification.
        try:
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            mu_hat, mu_err, _ = fit_asimov(spec, sig_hist, bkg_hists)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            rel_err = mu_err / mu_hat if mu_hat > 0 else float("inf")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        except Exception as e:
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            print(f"  cut={cut:.2f}: fit failed ({e})")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            continue

# [Stats] Likelihood/inference block logic and uncertainty quantification.
        results.append({
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            "bdt_cut": float(cut),
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            "fit_nbins": int(fit_nbins),
# [Physics] Event- and significance-like metrics for sensitivity interpretation.
            "n_sig": float(n_sig),
# [Physics] Event- and significance-like metrics for sensitivity interpretation.
            "n_bkg": float(n_bkg),
# [Physics] Event- and significance-like metrics for sensitivity interpretation.
            "s_over_b": float(n_sig / n_bkg) if n_bkg > 0 else 0,
# [Physics] Event- and significance-like metrics for sensitivity interpretation.
            "s_over_sqrt_b": float(n_sig / np.sqrt(n_bkg)) if n_bkg > 0 else 0,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            "mu_hat": mu_hat,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            "mu_err": mu_err,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            "rel_uncertainty": rel_err,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        })

# [Physics] Event- and significance-like metrics for sensitivity interpretation.
        print(f"  cut={cut:.2f}: S={n_sig:.0f}, B={n_bkg:.0f}, "
# [Physics] Event- and significance-like metrics for sensitivity interpretation.
              f"S/√B={n_sig/np.sqrt(n_bkg):.1f}, δμ/μ={rel_err*100:.2f}%")

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    return results


# [Physics] Produce physics-readable diagnostics: scan curve, template composition, and purity trend.
def make_fit_plots(output_dir, scan_results, best_result, sig_hist, bkg_hists, bins, shape_rel_unc_pct=None):
    """Generate physics-oriented diagnostics for the profile-likelihood stage.

    Plots show the score-threshold sensitivity curve, template composition at the
    chosen working point, and purity trend in score rank order.
    """
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
    import matplotlib
# [Workflow] Save inspection plots immediately after generation for review history.
    matplotlib.use("Agg")
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
    import matplotlib.pyplot as plt
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
    from matplotlib.ticker import LogLocator, NullFormatter

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    plots_dir = output_dir / "plots"
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    plots_dir.mkdir(parents=True, exist_ok=True)

    # 1. BDT cut optimization scan.
    # At very loose cuts backgrounds dominate; at too strict cuts, signal
    # statistics become the limiting factor. The minimum of this curve is the
    # typical operating-point compromise.
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    if len(scan_results) > 1:
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        fig, ax = plt.subplots(figsize=(6.0, 4.6))

# [Stats] Likelihood/inference block logic and uncertainty quantification.
        plot_results = [r for r in scan_results if r["bdt_cut"] >= 0.05]
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        cuts = [r["bdt_cut"] for r in plot_results]
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        rel_unc = [r["rel_uncertainty"] * 100 for r in plot_results]

# [Stats] Likelihood/inference block logic and uncertainty quantification.
        ax.plot(cuts, rel_unc, color="#2C7FB8", marker="o", markersize=4.5, linewidth=2.0)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        ax.set_xlabel("BDT score threshold")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        ax.set_ylabel(r"Expected $\delta\mu/\mu$ [%]")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        ax.set_title("1-bin counting reference scan")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        ax.grid(True, alpha=0.25)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        ax.set_xlim(0.05, 1.0)

# [Stats] Likelihood/inference block logic and uncertainty quantification.
        if shape_rel_unc_pct is not None:
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            ax.axhline(
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                shape_rel_unc_pct,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                color="#333333",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                linestyle=(0, (4, 3)),
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                linewidth=1.4,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                label=f"20-bin shape fit: {shape_rel_unc_pct:.2f}%",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            )

# [Stats] Likelihood/inference block logic and uncertainty quantification.
        if best_result:
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            best_cut = best_result["bdt_cut"]
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            best_unc = best_result["rel_uncertainty"] * 100
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            ax.axvline(best_cut, color="#D64F4F", linestyle="--", linewidth=1.4)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            ax.scatter([best_cut], [best_unc], color="#D64F4F", zorder=5)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            ax.annotate(
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                f"Best counting:\n{best_unc:.2f}% @ {best_cut:.2f}",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                xy=(best_cut, best_unc),
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                xytext=(-74, 22),
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                textcoords="offset points",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                fontsize=9,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": "#D64F4F", "alpha": 0.92},
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                arrowprops={"arrowstyle": "->", "color": "#D64F4F", "lw": 1.1},
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            )

# [Stats] Likelihood/inference block logic and uncertainty quantification.
        ax.legend(frameon=False, fontsize=9, loc="upper right")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        fig.tight_layout()
# [Workflow] Save inspection plots immediately after generation for review history.
        fig.savefig(plots_dir / "bdt_cut_scan.pdf", dpi=150)
# [Workflow] Save inspection plots immediately after generation for review history.
        fig.savefig(plots_dir / "bdt_cut_scan.png", dpi=150)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        plt.close(fig)

    # 2. Template shapes at best working point
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    fig, (ax_top, ax_bottom) = plt.subplots(
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        2,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        1,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        figsize=(7.5, 6.8),
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        sharex=True,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        gridspec_kw={"height_ratios": [2.5, 1.8], "hspace": 0.05},
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    )
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    bin_width = bins[1] - bins[0]

    # Stack backgrounds
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    bkg_labels = list(bkg_hists.keys())
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    bkg_arrays = [bkg_hists[k] for k in bkg_labels]
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    colors = ["#5B7BD5", "#D65F5F", "#4CAF50", "#F1C84B", "#F39C5A"]

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.hist(
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        [bin_centers] * len(bkg_arrays),
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        bins=bins,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        weights=bkg_arrays,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        stacked=True,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        label=[f"Bkg: {l}" for l in bkg_labels],
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        color=colors[:len(bkg_arrays)],
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        alpha=0.88,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    )

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    total_bkg = np.sum(np.asarray(bkg_arrays), axis=0)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.step(
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        bins[:-1],
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        total_bkg,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        where="post",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        color="#22313F",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        linewidth=1.2,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        alpha=0.95,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        label="Total background",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    )

    # Signal overlay (scaled for visibility)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    sig_scale = max(1, int(sum(h.sum() for h in bkg_hists.values()) / sig_hist.sum() / 5)) if sig_hist.sum() > 0 else 1
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.step(
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        bins[:-1],
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        sig_hist * sig_scale,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        where="post",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        color="black",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        linewidth=2.0,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        label=f"Signal (x{sig_scale})",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    )

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.set_ylabel(f"Events / {bin_width:.2f}")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.set_title("BDT score templates and background composition")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.legend(fontsize=8.7, ncol=2, frameon=False, loc="upper center")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.text(0.03, 0.95, r'$\mathbf{FCC\text{-}ee}$ Simulation',
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                transform=ax_top.transAxes, fontsize=10, va='top', fontstyle='italic')
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.text(0.03, 0.89, r'$\sqrt{s}=240$ GeV, $10.8\,\mathrm{ab}^{-1}$',
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                transform=ax_top.transAxes, fontsize=9, va='top')
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.set_yscale("log")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.set_ylim(bottom=0.1)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.yaxis.set_major_locator(LogLocator(base=10.0, numticks=12))
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.yaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2, 10), numticks=120))
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.yaxis.set_minor_formatter(NullFormatter())
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.grid(axis="y", which="major", alpha=0.24, linewidth=0.8)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.grid(axis="y", which="minor", alpha=0.14, linewidth=0.55)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.tick_params(axis="y", which="major", labelsize=9)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.tick_params(axis="y", which="minor", length=2.5)

    # Sub-dominant background yields panel (excluding WW)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    subdominant = [
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        (label, arr, color)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        for label, arr, color in zip(bkg_labels, bkg_arrays, colors)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        if label != "WW"
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ]
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_bottom.hist(
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        [bin_centers] * len(subdominant),
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        bins=bins,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        weights=[arr for _, arr, _ in subdominant],
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        stacked=True,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        label=[l for l, _, _ in subdominant],
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        color=[c for _, _, c in subdominant],
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        alpha=0.88,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    )
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_bottom.set_xlabel("BDT score")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_bottom.set_ylabel(f"Events / {bin_width:.2f}")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_bottom.set_xlim(0.0, 1.0)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_bottom.set_yscale("log")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_bottom.set_ylim(bottom=0.1)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_bottom.legend(fontsize=7, ncol=2, frameon=False, loc="upper right")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_bottom.grid(axis="y", which="major", alpha=0.24)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_bottom.text(
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        0.02,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        0.95,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        "Sub-dominant backgrounds (excl. WW)",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        transform=ax_bottom.transAxes,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        fontsize=8,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        va="top",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    )
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    fig.tight_layout()
# [Workflow] Save inspection plots immediately after generation for review history.
    fig.savefig(plots_dir / "fit_templates.pdf", dpi=150)
# [Workflow] Save inspection plots immediately after generation for review history.
    fig.savefig(plots_dir / "fit_templates.png", dpi=150)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    plt.close(fig)

    # 3. Rank-ordered BDT bins (highest score to lowest score)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    rank_order = np.arange(len(sig_hist))[::-1]
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    rank_bins = np.arange(1, len(sig_hist) + 1)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    sig_rank = sig_hist[rank_order]
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    bkg_rank_arrays = [arr[rank_order] for arr in bkg_arrays]
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    total_rank = np.sum(np.asarray(bkg_rank_arrays), axis=0)

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    fig, (ax_top, ax_bottom) = plt.subplots(
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        2,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        1,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        figsize=(7.4, 6.6),
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        sharex=True,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        gridspec_kw={"height_ratios": [3.0, 1.15], "hspace": 0.05},
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    )

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    cumulative = np.zeros_like(rank_bins, dtype=float)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    for label, arr, color in zip(bkg_labels, bkg_rank_arrays, colors):
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        ax_top.bar(
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            rank_bins,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            arr,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            bottom=cumulative,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            width=0.90,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            color=color,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            alpha=0.88,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            label=f"Bkg: {label}",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            linewidth=0.0,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        )
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        cumulative += arr

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    sig_scale_rank = sig_scale
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.step(
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        np.r_[rank_bins, rank_bins[-1] + 1] - 0.5,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        np.r_[sig_rank * sig_scale_rank, sig_rank[-1] * sig_scale_rank],
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        where="post",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        color="black",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        linewidth=2.0,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        label=f"Signal (x{sig_scale_rank})",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    )
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.set_ylabel("Events / rank bin")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.set_title("Rank-ordered BDT bins")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.set_yscale("log")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.set_ylim(bottom=0.1)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.yaxis.set_major_locator(LogLocator(base=10.0, numticks=12))
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.yaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2, 10), numticks=120))
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.yaxis.set_minor_formatter(NullFormatter())
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.grid(axis="y", which="major", alpha=0.24, linewidth=0.8)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.grid(axis="y", which="minor", alpha=0.14, linewidth=0.55)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.tick_params(axis="y", which="major", labelsize=9)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.tick_params(axis="y", which="minor", length=2.5)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.legend(fontsize=8.6, ncol=2, frameon=False, loc="upper center")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.text(
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        0.03,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        0.95,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        r'$\mathbf{FCC\text{-}ee}$ Simulation',
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        transform=ax_top.transAxes,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        fontsize=10,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        va='top',
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        fontstyle='italic',
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    )
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_top.text(
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        0.03,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        0.89,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        r'$\sqrt{s}=240$ GeV, $10.8\,\mathrm{ab}^{-1}$',
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        transform=ax_top.transAxes,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        fontsize=9,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        va='top',
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    )

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    purity = np.divide(sig_rank, sig_rank + total_rank, out=np.zeros_like(sig_rank), where=(sig_rank + total_rank) > 0)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_bottom.plot(rank_bins, purity, color="#2C7FB8", marker="o", markersize=3.8, linewidth=1.8)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_bottom.set_ylabel(r"$S/(S+B)$")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_bottom.set_xlabel("BDT rank bin (1 = highest score)")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_bottom.set_ylim(0.0, min(1.0, max(0.15, purity.max() * 1.25 if len(purity) else 0.15)))
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_bottom.set_xlim(0.5, len(rank_bins) + 0.5)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_bottom.set_xticks(rank_bins[::2] if len(rank_bins) > 10 else rank_bins)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_bottom.grid(axis="y", alpha=0.22)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    ax_bottom.text(
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        0.02,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        0.92,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        "Signal purity by ranked bin",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        transform=ax_bottom.transAxes,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        fontsize=9,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        va="top",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    )

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    fig.tight_layout()
# [Workflow] Save inspection plots immediately after generation for review history.
    fig.savefig(plots_dir / "bdt_score_rank.pdf", dpi=150)
# [Workflow] Save inspection plots immediately after generation for review history.
    fig.savefig(plots_dir / "bdt_score_rank.png", dpi=150)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    plt.close(fig)

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    print(f"  Fit plots saved to {plots_dir}/")


# [Workflow] Parse args, select score source, run scan/fit, save JSON and plots.
def main():
# [Stats] The main entrypoint keeps the entire statistical workflow deterministic:
# 1) choose which scored dataset to read
# 2) normalize weights for the score-sampling convention
# 3) scan cut thresholds (optional) and run the final shape-fit
# 4) serialize both numerical and plotting artifacts for reproducibility
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    parser = argparse.ArgumentParser(description="Profile likelihood fit for H->WW* measurement")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    parser.add_argument("--scores", type=str, default=None,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                       help="Path to test_scores.csv from BDT training")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    parser.add_argument("--model-dir", type=str, default=None,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                       help="Model directory (default: ml/models/xgboost_bdt)")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    parser.add_argument("--nbins", type=int, default=20,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                       help="Number of BDT score bins for template fit")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    parser.add_argument("--norm-unc", type=float, default=0.01,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                       help="Background normalization uncertainty (default: 1%%)")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    parser.add_argument("--bdt-cut", type=float, default=None,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                       help="Fixed BDT score cut (if None, scans for optimal)")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    parser.add_argument("--no-scan", action="store_true",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                       help="Skip BDT cut scan, use --bdt-cut or 0.0")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    parser.add_argument("--no-plots", action="store_true",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                       help="Skip diagnostic plots")
# [Stats] Add systematic and MC-stat uncertainties for conservative, realistic error bars.
    parser.add_argument("--no-staterror", action="store_true",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
                       help="Disable Barlow-Beeston MC stat uncertainty (show physics-only precision)")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    args = parser.parse_args()

    # Locate score input for fit.
    # Physics/statistics rule:
    # - explicit --scores path is always first (manual override),
    # - otherwise use kfold_scores.csv when available (OOF prediction for the full event set),
    # - otherwise fall back to test_scores.csv and restore full-luminosity normalization.
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    if args.scores:
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        scores_path = Path(args.scores)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    elif args.model_dir:
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        model_dir = Path(args.model_dir)
        # Prefer kfold_scores.csv (all events, no scaling needed)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        kfold_path = model_dir / "kfold_scores.csv"
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        test_path = model_dir / "test_scores.csv"
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        if kfold_path.exists():
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            scores_path = kfold_path
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        else:
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            scores_path = test_path
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    else:
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        model_dir = ANALYSIS_DIR / DEFAULT_MODEL_DIR
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        scores_path = model_dir / "test_scores.csv"
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        if not scores_path.exists():
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            scores_path = THIS_DIR / "models" / "xgboost_bdt_v6" / "test_scores.csv"

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    print(f"Loading scores from {scores_path}")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    df = load_scores(scores_path)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    print(f"  {len(df)} events loaded ({(df['y_true']==1).sum()} signal, {(df['y_true']==0).sum()} background)")

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    output_dir = scores_path.parent

    # Weight scaling depends on input file type:
    # - kfold_scores.csv: all events are scored out-of-fold, so yield sums are already global-statistical.
    # - test_scores.csv: only the 30% holdout is present, so every event weight must be scaled by 1/test_frac to rebuild
    #   the same event-count expectation used during fit construction.
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    if "kfold" in scores_path.name:
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        print("  Using k-fold scores (all events, no scaling)")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    else:
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        test_frac = 0.30  # must match --test-size in train_xgboost_bdt.py
# [Stats] Physics weights propagate cross-section and luminosity to training/fit observables.
        df["phys_weight"] = df["phys_weight"] / test_frac
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        print(f"  Scaling weights by 1/{test_frac} for test-set-only scores")

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    use_staterr = not args.no_staterror

    # Single-bin counting scan for the cut-and-count reference.
    # This is a bias/variance diagnostic used to choose a practical threshold;
    # it is not the final inference, which is the full template likelihood.
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    if not args.no_scan:
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        print("\nScanning BDT score cuts (1-bin counting reference):")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        scan_results = scan_bdt_cut(
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            df,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            fit_nbins=1,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            norm_uncertainty=args.norm_unc,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            use_staterror=use_staterr,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        )

# [Stats] Likelihood/inference block logic and uncertainty quantification.
        if not scan_results:
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            print("ERROR: All BDT cuts failed. Check input data.")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            return

# [Stats] Likelihood/inference block logic and uncertainty quantification.
        best_counting = min(scan_results, key=lambda r: r["rel_uncertainty"])
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        print(f"\n  Best 1-bin counting cut: {best_counting['bdt_cut']:.2f}")
# [Physics] Event- and significance-like metrics for sensitivity interpretation.
        print(f"  S={best_counting['n_sig']:.0f}, B={best_counting['n_bkg']:.0f}")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        print(f"  Expected δμ/μ = {best_counting['rel_uncertainty']*100:.2f}%")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    else:
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        scan_results = []
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        best_counting = None

    # The headline result is the full nbins-shape fit.
    # Keeping bdt_cut=0.0 means no pre-thresholding, so the fit keeps full score information.
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    bdt_cut = args.bdt_cut if args.bdt_cut is not None else 0.0

    # Final fit at chosen working point.
    # Here each BDT-score bin is treated as a Poisson counting channel tied by one POI (mu) and nuisance priors.
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    print(f"\nFinal {args.nbins}-bin shape fit at BDT cut = {bdt_cut:.2f}:")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    sig_hist, sig_err, bkg_hists, bkg_errs, bins = build_templates(df, nbins=args.nbins, bdt_cut=bdt_cut)

# [Physics] Event- and significance-like metrics for sensitivity interpretation.
    n_sig = sig_hist.sum()
# [Physics] Event- and significance-like metrics for sensitivity interpretation.
    n_bkg = sum(h.sum() for h in bkg_hists.values())
# [Physics] Event- and significance-like metrics for sensitivity interpretation.
    print(f"  Signal events: {n_sig:.0f}")
# [Physics] Event- and significance-like metrics for sensitivity interpretation.
    print(f"  Background events: {n_bkg:.0f}")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    for name, h in bkg_hists.items():
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        print(f"    {name}: {h.sum():.0f}")

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    spec = build_pyhf_model(sig_hist, sig_err, bkg_hists, bkg_errs, args.norm_unc, use_staterror=use_staterr)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    mu_hat, mu_err, fit_results = fit_asimov(spec, sig_hist, bkg_hists)

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    rel_unc = mu_err / mu_hat if mu_hat > 0 else float("inf")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    physics_only_mu_hat = None
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    physics_only_mu_err = None
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    physics_only_rel_unc = None
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    if use_staterr:
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        physics_spec = build_pyhf_model(
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            sig_hist, sig_err, bkg_hists, bkg_errs, args.norm_unc, use_staterror=False,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        )
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        physics_only_mu_hat, physics_only_mu_err, _ = fit_asimov(physics_spec, sig_hist, bkg_hists)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        physics_only_rel_unc = (
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            physics_only_mu_err / physics_only_mu_hat if physics_only_mu_hat > 0 else float("inf")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        )

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    print(f"\n  === RESULT ===")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    print(f"  mu_hat = {mu_hat:.4f} +/- {mu_err:.4f}")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    print(f"  Relative uncertainty: {rel_unc*100:.2f}%")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    print(f"  => Expected precision on sigma_ZH x BR(H->WW*): {rel_unc*100:.2f}%")
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    if physics_only_rel_unc is not None:
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        print(f"  Physics-only floor (no MC stat nuisance terms): {physics_only_rel_unc*100:.2f}%")

    # Save results:
    # - scalar precision summary
    # - per-parameter fit values and uncertainties
    # - counting scan results if performed (so downstream comparison is reproducible)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    result = {
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        "bdt_cut": bdt_cut,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        "nbins": args.nbins,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        "scan_mode": "counting_1bin",
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        "norm_uncertainty": args.norm_unc,
# [Physics] Event- and significance-like metrics for sensitivity interpretation.
        "n_signal": float(n_sig),
# [Physics] Event- and significance-like metrics for sensitivity interpretation.
        "n_background": float(n_bkg),
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        "mu_hat": mu_hat,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        "mu_err": mu_err,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        "relative_uncertainty_pct": rel_unc * 100,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        "fit_parameters": fit_results,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        "bkg_yields": {k: float(v.sum()) for k, v in bkg_hists.items()},
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    }

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    if physics_only_rel_unc is not None:
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        result["physics_only_mu_hat"] = physics_only_mu_hat
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        result["physics_only_mu_err"] = physics_only_mu_err
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        result["physics_only_rel_uncertainty_pct"] = physics_only_rel_unc * 100
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        result["physics_only_note"] = (
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            "Shape-fit precision with the same normalization systematics but without "
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            "Barlow-Beeston MC-stat nuisance terms."
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        )

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    if scan_results:
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        result["counting_scan_results"] = scan_results

# [Stats] Likelihood/inference block logic and uncertainty quantification.
    result_path = output_dir / "fit_results.json"
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    with open(result_path, "w") as f:
# [Workflow] Persist contracts and fit outputs to make every stage auditable.
        json.dump(result, f, indent=2)
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    print(f"\n  Results saved to {result_path}")

    # Plots
# [Stats] Likelihood/inference block logic and uncertainty quantification.
    if not args.no_plots:
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        make_fit_plots(
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            output_dir,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            scan_results,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            best_counting,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            sig_hist,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            bkg_hists,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            bins,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
            shape_rel_unc_pct=rel_unc * 100,
# [Stats] Likelihood/inference block logic and uncertainty quantification.
        )


# [Context] Supporting line for the active lvqq analysis stage.
if __name__ == "__main__":
# [Context] Supporting line for the active lvqq analysis stage.
    main()
