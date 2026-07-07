#!/usr/bin/env python3
"""Scan hard-cut windows on Zcand_p (and Zcand_m) against the 20-bin shape fit.

Motivation: a hard window on a variable that is already a BDT input can only
remove information from the shape fit, but a poorly chosen window is not
evidence against a well chosen one. This scan filters the out-of-fold scores
to each candidate window, rebuilds the 20-bin templates, and reruns the full
profile-likelihood fit (shared staterror, MINUIT errors), so every window is
judged by the ACTUAL final-fit precision rather than the counting proxy.

Requires kfold_scores.csv with Zcand_p/Zcand_m columns (train_xgboost_bdt.py
writes them via SCORE_CARRY_BRANCHES). Note the single approximation: the BDT
is trained once on the no-window sample; a window-specific retraining could
differ at the margin, so the winning window should be confirmed with one full
pipeline run.

Usage:
  python3 ml/scan_zcand_windows.py [--model-dir ml/models/xgboost_bdt_<tag>]
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
sys.path.insert(0, str(THIS_DIR))

from ml_config import DEFAULT_MODEL_DIR
from fit_profile_likelihood import (
    _set_backend,
    build_pyhf_spec,
    build_templates,
    fit_asimov,
)

# Window grids. None = unbounded on that side; (None, None) = no cut at all.
PZ_LOS = [None, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0]
PZ_HIS = [55.0, 60.0, 65.0, 70.0, 80.0, None]
MZ_LOS = [None, 70.0, 75.0, 80.0, 85.0]
MZ_HIS = [95.0, 100.0, 105.0, 110.0, None]


def window_mask(values, lo, hi):
    mask = np.ones(len(values), dtype=bool)
    if lo is not None:
        mask &= values > lo
    if hi is not None:
        mask &= values < hi
    return mask


def fit_window(df, error_method, norm_unc, nbins):
    sig_hist, sig_err, bkg_hists, bkg_errs, _bins = build_templates(df, nbins=nbins)
    n_sig = float(sig_hist.sum())
    n_bkg = float(sum(h.sum() for h in bkg_hists.values()))
    if n_sig < 1 or n_bkg < 1:
        return n_sig, n_bkg, None
    payload = {"bdt_score": {"sig_hist": sig_hist, "sig_err": sig_err,
                             "bkg_hists": bkg_hists, "bkg_errs": bkg_errs}}
    spec = build_pyhf_spec(payload, norm_unc, "shared")
    total = sig_hist + sum(bkg_hists.values())
    mu_hat, mu_err, _, _ = fit_asimov(spec, [total], error_method)
    return n_sig, n_bkg, (mu_err / mu_hat if mu_hat > 0 else float("inf"))


def scan_variable(df, var, los, his, error_method, norm_unc, nbins):
    values = df[var].to_numpy()
    rows = []
    for lo in los:
        for hi in his:
            if lo is not None and hi is not None and lo >= hi:
                continue
            sub = df[window_mask(values, lo, hi)]
            n_sig, n_bkg, rel = fit_window(sub, error_method, norm_unc, nbins)
            proxy = float(np.sqrt(n_sig + n_bkg) / n_sig) if n_sig > 0 else float("nan")
            rows.append({
                "variable": var,
                "lo": lo if lo is not None else -np.inf,
                "hi": hi if hi is not None else np.inf,
                "n_sig": n_sig,
                "n_bkg": n_bkg,
                "counting_proxy_pct": 100.0 * proxy,
                "fit_rel_uncertainty_pct": 100.0 * rel if rel is not None else np.nan,
            })
            lo_s = "-inf" if lo is None else f"{lo:g}"
            hi_s = "+inf" if hi is None else f"{hi:g}"
            rel_s = "fit failed" if rel is None else f"{100.0*rel:.3f}%"
            print(f"  {var} in ({lo_s:>5s}, {hi_s:>5s}): S={n_sig:8.0f} B={n_bkg:8.0f} "
                  f"proxy={100.0*proxy:.3f}%  fit dmu/mu={rel_s}")
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", default=str(ANALYSIS_DIR / DEFAULT_MODEL_DIR))
    parser.add_argument("--nbins", type=int, default=20)
    parser.add_argument("--norm-unc", type=float, default=0.01)
    parser.add_argument("--variables", nargs="*", default=["Zcand_p", "Zcand_m"])
    args = parser.parse_args()

    model_dir = Path(args.model_dir)
    scores_path = model_dir / "kfold_scores.csv"
    if not scores_path.exists():
        raise SystemExit(f"missing {scores_path}; run the train step first")
    df = pd.read_csv(scores_path)
    missing = [v for v in args.variables if v not in df.columns]
    if missing:
        raise SystemExit(
            f"{scores_path} lacks columns {missing}. Retrain with the updated "
            "train_xgboost_bdt.py (SCORE_CARRY_BRANCHES) so the scan can re-window."
        )
    print(f"Loaded {len(df)} out-of-fold scores from {scores_path}")

    error_method = _set_backend(prefer_minuit=True)
    print(f"Error method: {error_method}\n")

    grids = {"Zcand_p": (PZ_LOS, PZ_HIS), "Zcand_m": (MZ_LOS, MZ_HIS)}
    all_frames = []
    for var in args.variables:
        los, his = grids[var]
        print(f"=== window scan: {var} ===")
        frame = scan_variable(df, var, los, his, error_method, args.norm_unc, args.nbins)
        all_frames.append(frame)
        best = frame.loc[frame["fit_rel_uncertainty_pct"].idxmin()]
        nocut = frame[(frame["lo"] == -np.inf) & (frame["hi"] == np.inf)].iloc[0]
        print(f"\n  best window : {var} in ({best['lo']:g}, {best['hi']:g})"
              f" -> dmu/mu = {best['fit_rel_uncertainty_pct']:.3f}%")
        print(f"  no cut      : dmu/mu = {nocut['fit_rel_uncertainty_pct']:.3f}%\n")

    out = pd.concat(all_frames, ignore_index=True)
    out_path = model_dir / "zcand_window_scan.csv"
    out.to_csv(out_path, index=False)
    print(f"Scan table saved to {out_path}")


if __name__ == "__main__":
    main()
