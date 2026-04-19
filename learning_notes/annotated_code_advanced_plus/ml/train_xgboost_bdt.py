#!/usr/bin/env python3
# BDT training and validation pipeline: weighted event ingestion, split strategy,
# hyperparameter search, early stopping, diagnostics, and scoring export.
#
# The objective is not just high in-sample separation; it is a calibrated model
# that remains stable under physics-aware uncertainty propagation and profile fits.

"""Train an XGBoost BDT for the lvqq analysis from FCCAnalyses treemaker ntuples.

v3 improvements (ML specialist review fixes):
- Physics-correct event weights (lumi * xsec / ngen)
- Normalized class weights for balanced learning
- Extended hyperparameter grid search (incl. min_child_weight, subsample)
- Early stopping in both grid search and final training
- Weighted KS overtraining test (binned chi2)
- missingMass sentinel value handling
- Background sculpting diagnostic (BDT score vs Hcand_m)
- Per-sample score distributions
- Training history saved (evals_result)
- Diagnostic plots (ROC, feature importance, BDT score, overtraining, sculpting)
"""
# Physics/ML objective:
# - Build a kinematic classifier weighted by physical cross sections and exposure.
# - Constrain training to reproducible optimization: stratified splitting, fixed seed, early stopping.
# - Export both test-level and k-fold scores so inference never uses in-sample predictions.

# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import argparse
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import json
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import sys
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
from pathlib import Path
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
from itertools import product

# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import numpy as np
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import pandas as pd
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import uproot
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import xgboost as xgb
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
from sklearn.metrics import roc_auc_score, roc_curve
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
from sklearn.model_selection import train_test_split, StratifiedKFold
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
from scipy.stats import ks_2samp

# [Workflow] Configuration binding; this line defines a stable contract across modules.
THIS_DIR = Path(__file__).resolve().parent
# [Workflow] Configuration binding; this line defines a stable contract across modules.
ANALYSIS_DIR = THIS_DIR.parent
# [Context] Supporting line for the active lvqq analysis stage.
sys.path.insert(0, str(ANALYSIS_DIR))

# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
from ml_config import (
# [Context] Supporting line for the active lvqq analysis stage.
    BACKGROUND_FRACTIONS,
# [Context] Supporting line for the active lvqq analysis stage.
    BACKGROUND_SAMPLES,
# [Context] Supporting line for the active lvqq analysis stage.
    DEFAULT_MODEL_DIR,
# [Context] Supporting line for the active lvqq analysis stage.
    DEFAULT_TREE_NAME,
# [Context] Supporting line for the active lvqq analysis stage.
    DEFAULT_TREEMAKER_DIR,
# [Context] Supporting line for the active lvqq analysis stage.
    ML_FEATURES,
# [Context] Supporting line for the active lvqq analysis stage.
    SAMPLE_PROCESSING_FRACTIONS,
# [Context] Supporting line for the active lvqq analysis stage.
    SIGNAL_SAMPLES,
# [Context] Supporting line for the active lvqq analysis stage.
)

# Cross-sections [pb], total generated events, and processing fraction.
# Event weight = lumi * xsec / (ngen * fraction) to correctly map MC statistics
# to expected yields at 10.8 ab^-1.
# [Workflow] Configuration binding; this line defines a stable contract across modules.
SAMPLE_INFO = {
    # Signal (fraction=1, all events processed)
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_qqH_HWW_ecm240": {"xsec": 0.01140, "ngen": 1100000, "fraction": 1.0},
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_bbH_HWW_ecm240": {"xsec": 0.006350, "ngen": 1000000, "fraction": 1.0},
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_ccH_HWW_ecm240": {"xsec": 0.004988, "ngen": 1200000, "fraction": 1.0},
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_ssH_HWW_ecm240": {"xsec": 0.006403, "ngen": 1200000, "fraction": 1.0},
    # Diboson and 2-fermion backgrounds. The processed fraction is shared with
    # the FCCAnalyses stage through ml_config.py to keep the whole chain aligned.
# [Context] Supporting line for the active lvqq analysis stage.
    "p8_ee_WW_ecm240":        {"xsec": 16.4385, "ngen": 373375386, "fraction": SAMPLE_PROCESSING_FRACTIONS["p8_ee_WW_ecm240"]},
# [Context] Supporting line for the active lvqq analysis stage.
    "p8_ee_ZZ_ecm240":        {"xsec": 1.35899, "ngen": 209700000, "fraction": SAMPLE_PROCESSING_FRACTIONS["p8_ee_ZZ_ecm240"]},
# [Context] Supporting line for the active lvqq analysis stage.
    "wz3p6_ee_uu_ecm240":     {"xsec": 11.9447, "ngen": 100790000, "fraction": SAMPLE_PROCESSING_FRACTIONS["wz3p6_ee_uu_ecm240"]},
# [Context] Supporting line for the active lvqq analysis stage.
    "wz3p6_ee_dd_ecm240":     {"xsec": 10.8037, "ngen": 100910000, "fraction": SAMPLE_PROCESSING_FRACTIONS["wz3p6_ee_dd_ecm240"]},
# [Context] Supporting line for the active lvqq analysis stage.
    "wz3p6_ee_cc_ecm240":     {"xsec": 11.0595, "ngen": 101290000, "fraction": SAMPLE_PROCESSING_FRACTIONS["wz3p6_ee_cc_ecm240"]},
# [Context] Supporting line for the active lvqq analysis stage.
    "wz3p6_ee_ss_ecm240":     {"xsec": 10.7725, "ngen": 102348636, "fraction": SAMPLE_PROCESSING_FRACTIONS["wz3p6_ee_ss_ecm240"]},
# [Context] Supporting line for the active lvqq analysis stage.
    "wz3p6_ee_bb_ecm240":     {"xsec": 10.4299, "ngen": 99490000, "fraction": SAMPLE_PROCESSING_FRACTIONS["wz3p6_ee_bb_ecm240"]},
# [Context] Supporting line for the active lvqq analysis stage.
    "wz3p6_ee_tautau_ecm240": {"xsec": 4.6682, "ngen": 235800000, "fraction": SAMPLE_PROCESSING_FRACTIONS["wz3p6_ee_tautau_ecm240"]},
    # ZH with H->other (fraction=1, all events processed)
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_qqH_Hbb_ecm240":    {"xsec": 0.03106, "ngen": 500000, "fraction": 1.0},
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_qqH_Htautau_ecm240": {"xsec": 0.003345, "ngen": 200000, "fraction": 1.0},
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_qqH_Hgg_ecm240":    {"xsec": 0.004367, "ngen": 400000, "fraction": 1.0},
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_qqH_Hcc_ecm240":    {"xsec": 0.001542, "ngen": 200000, "fraction": 1.0},
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_qqH_HZZ_ecm240":    {"xsec": 0.001397, "ngen": 1200000, "fraction": 1.0},
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_bbH_Hbb_ecm240":    {"xsec": 0.01731, "ngen": 100000, "fraction": 1.0},
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_bbH_Htautau_ecm240": {"xsec": 0.001864, "ngen": 400000, "fraction": 1.0},
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_bbH_Hgg_ecm240":    {"xsec": 0.002433, "ngen": 200000, "fraction": 1.0},
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_bbH_Hcc_ecm240":    {"xsec": 0.0008591, "ngen": 400000, "fraction": 1.0},
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_bbH_HZZ_ecm240":    {"xsec": 0.0007782, "ngen": 1000000, "fraction": 1.0},
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_ccH_Hbb_ecm240":    {"xsec": 0.01359, "ngen": 200000, "fraction": 1.0},
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_ccH_Htautau_ecm240": {"xsec": 0.001464, "ngen": 400000, "fraction": 1.0},
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_ccH_Hgg_ecm240":    {"xsec": 0.001911, "ngen": 400000, "fraction": 1.0},
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_ccH_Hcc_ecm240":    {"xsec": 0.0006748, "ngen": 400000, "fraction": 1.0},
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_ccH_HZZ_ecm240":    {"xsec": 0.0006113, "ngen": 1200000, "fraction": 1.0},
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_ssH_Hbb_ecm240":    {"xsec": 0.01745, "ngen": 200000, "fraction": 1.0},
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_ssH_Htautau_ecm240": {"xsec": 0.001879, "ngen": 400000, "fraction": 1.0},
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_ssH_Hgg_ecm240":    {"xsec": 0.002453, "ngen": 400000, "fraction": 1.0},
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_ssH_Hcc_ecm240":    {"xsec": 0.0008662, "ngen": 300000, "fraction": 1.0},
# [Context] Supporting line for the active lvqq analysis stage.
    "wzp6_ee_ssH_HZZ_ecm240":    {"xsec": 0.0007847, "ngen": 600000, "fraction": 1.0},
# [Context] Supporting line for the active lvqq analysis stage.
}
# [Workflow] Configuration binding; this line defines a stable contract across modules.
INT_LUMI = 10.8e6  # pb^-1


# [Workflow] train_xgboost_bdt.py function parse_args: modularize one operation for deterministic pipeline control.
def parse_args():
    """Parse command-line controls for one deterministic training run.

    These arguments are the reproducibility boundary:
    - fixed random seed, fixed split size, and fixed feature list ensure reruns are comparable;
    - path flags decouple dataset source and model/output location.
    - switches allow fast studies (skip grid search/plots) while preserving a stable API.
    """
    # Protocol intent:
    # 1) define exactly which reconstructed phase space and class definition enters the model;
    # 2) fix every stochastic knob (seed/splits) so two runs can be compared event-by-event;
    # 3) define where artifacts are written to keep inference and fit scripts deterministic.

# [ML] Parse-time flags encode the experimental protocol:
# - input/output paths and cut-level train/test randomization.
# - fixed seed for deterministic model reproducibility.
# - optional grid-search/k-fold switches to control speed vs. robustness.
# [Context] Supporting line for the active lvqq analysis stage.
    parser = argparse.ArgumentParser(description=__doc__)
# [ML] Data loading stage is fixed at the tree level to avoid accidental branch mismatches.
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument('--input-dir', default=DEFAULT_TREEMAKER_DIR)
# [Workflow] Output directory is the contract for downstream scoring/fit stages.
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument('--output-dir', default=DEFAULT_MODEL_DIR)
# [I/O] Tree selection must match treemaker output (`events` by default in this workflow).
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument('--tree-name', default=DEFAULT_TREE_NAME)
# [ML] Keep sample composition explicit per run for transparent signal-background definition.
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument('--signal-samples', nargs='*', default=SIGNAL_SAMPLES)
# [ML] Background list is also explicit to support targeted studies and sanity checks.
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument('--background-samples', nargs='*', default=BACKGROUND_SAMPLES)
# [ML] Feature contract is part of the learned model identity and must be versioned.
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument('--features', nargs='*', default=ML_FEATURES)
# [ML] Fixed holdout ratio gives consistent metric interpretation across experiments.
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument('--test-size', type=float, default=0.30)
# [Workflow] Random seed controls all random gates (subsampling and fit-time splits).
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument('--random-state', type=int, default=42)
# [Workflow] n_jobs controls training-time determinism/throughput tradeoffs.
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument('--n-jobs', type=int, default=8)
# [ML] Disable expensive sweeps for quick smoke tests.
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument('--no-grid-search', action='store_true',
# [Context] Supporting line for the active lvqq analysis stage.
                        help='Skip grid search, use default hyperparameters')
# [Stats] Plots are optional; disabling helps scripted CI and memory-constrained runs.
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument('--no-plots', action='store_true',
# [Context] Supporting line for the active lvqq analysis stage.
                        help='Skip diagnostic plots')
# [ML] k-fold controls score export strategy (unbiased full-statistics score file for fit).
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument('--kfold', type=int, default=5,
# [Context] Supporting line for the active lvqq analysis stage.
                        help='Number of folds for k-fold CV scoring (0 to disable)')
# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return parser.parse_args()


# [I/O] Detect missing trees and zero-event samples before model ingestion.
def get_tree_status(root_file, tree_name):
    """Inspect structural health of one ROOT input file.

    This is a guard before any array extraction:
    - missing tree => data-production incomplete;
    - tree exists but with 0 entries => valid file but no useful events;
    - normal files => continue to branch extraction.
    """
    # Rationale: if an ntuple is malformed or empty, fail-fast here avoids
    # silently building an empty feature table that later appears as model underperformance.

# [I/O] Data quality gate.
# Not every Monte Carlo chunk writes every expected tree (0-pass, crashed jobs, partial staging).
# This function turns structural issues into explicit metadata so model ingestion can skip cleanly.
# [Context] Supporting line for the active lvqq analysis stage.
    has_tree = tree_name in root_file
# [Context] Supporting line for the active lvqq analysis stage.
    num_entries = root_file[tree_name].num_entries if has_tree else 0

# [Context] Supporting line for the active lvqq analysis stage.
    selected = None
# [Context] Supporting line for the active lvqq analysis stage.
    if 'eventsSelected' in root_file:
# [Context] Supporting line for the active lvqq analysis stage.
        try:
# [Context] Supporting line for the active lvqq analysis stage.
            selected = int(root_file['eventsSelected'].member('fVal'))
# [Context] Supporting line for the active lvqq analysis stage.
        except Exception:
# [Context] Supporting line for the active lvqq analysis stage.
            selected = None

# [Context] Supporting line for the active lvqq analysis stage.
    processed = None
# [Context] Supporting line for the active lvqq analysis stage.
    if 'eventsProcessed' in root_file:
# [Context] Supporting line for the active lvqq analysis stage.
        try:
# [Context] Supporting line for the active lvqq analysis stage.
            processed = int(root_file['eventsProcessed'].member('fVal'))
# [Context] Supporting line for the active lvqq analysis stage.
        except Exception:
# [Context] Supporting line for the active lvqq analysis stage.
            processed = None

# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return {
# [Context] Supporting line for the active lvqq analysis stage.
        'has_tree': has_tree,
# [Context] Supporting line for the active lvqq analysis stage.
        'num_entries': num_entries,
# [Context] Supporting line for the active lvqq analysis stage.
        'selected': selected,
# [Context] Supporting line for the active lvqq analysis stage.
        'processed': processed,
# [Context] Supporting line for the active lvqq analysis stage.
    }


# [I/O] Load samples into one DataFrame with unified columns, labels, and physics weights.
def read_samples(input_dir, tree_name, sample_names, features, label):
    """Read samples and compute physics-correct per-event weights."""
# [Physics/ML] The combined dataframe guarantees a single training table and
# a single label definition (1 for signal, 0 for background) before any split.
# [Context] Supporting line for the active lvqq analysis stage.
    # ML/Physics intent:
    # - all samples are aligned into one schema (features + label + per-event xsec weight);
    # - label 1/0 defines the binary loss target; features are not yet conditioned on CV folds.
    # - skipped/malformed files do not crash the chain but reduce available training statistics with a warning.
    # [Workflow] Keep each sample independent during I/O so one malformed file does not break all.
    frames = []
# [Context] Supporting line for the active lvqq analysis stage.
    # [I/O] normalize to Path for deterministic path expansion across local and slurm contexts.
    input_dir = Path(input_dir)
# [Context] Supporting line for the active lvqq analysis stage.
    for sample in sample_names:
# [Context] Supporting line for the active lvqq analysis stage.
        root_path = input_dir / f'{sample}.root'
# [Context] Supporting line for the active lvqq analysis stage.
        if not root_path.exists():
# [Context] Supporting line for the active lvqq analysis stage.
            print(f'[warn] missing sample: {root_path}')
# [Context] Supporting line for the active lvqq analysis stage.
            continue

# [I/O] Open/write ROOT containers for high-throughput HEP data exchange.
        with uproot.open(root_path) as root_file:
# [Context] Supporting line for the active lvqq analysis stage.
            status = get_tree_status(root_file, tree_name)
# [Context] Supporting line for the active lvqq analysis stage.
            if not status['has_tree']:
# [Context] Supporting line for the active lvqq analysis stage.
                if status['selected'] == 0:
# [Context] Supporting line for the active lvqq analysis stage.
                    processed = status['processed']
# [Context] Supporting line for the active lvqq analysis stage.
                    processed_msg = f', processed={processed}' if processed is not None else ''
# [Context] Supporting line for the active lvqq analysis stage.
                    print(
# [Context] Supporting line for the active lvqq analysis stage.
                        f'[info] {root_path} is a 0-pass sample '
# [Context] Supporting line for the active lvqq analysis stage.
                        f'(eventsSelected=0{processed_msg}); no tree "{tree_name}" was written, skipping'
# [Context] Supporting line for the active lvqq analysis stage.
                    )
# [Context] Supporting line for the active lvqq analysis stage.
                else:
# [Context] Supporting line for the active lvqq analysis stage.
                    print(f'[warn] {root_path} has no tree "{tree_name}", skipping')
# [Context] Supporting line for the active lvqq analysis stage.
                continue
# [Context] Supporting line for the active lvqq analysis stage.
            tree = root_file[tree_name]
# [Context] Supporting line for the active lvqq analysis stage.
            if tree.num_entries == 0:
# [Context] Supporting line for the active lvqq analysis stage.
                print(f'[info] {root_path} has tree "{tree_name}" but 0 entries, skipping')
# [Context] Supporting line for the active lvqq analysis stage.
                continue
# [Context] Supporting line for the active lvqq analysis stage.
            available = set(tree.keys())
# [Context] Supporting line for the active lvqq analysis stage.
            use_features = [f for f in features if f in available]
# [Context] Supporting line for the active lvqq analysis stage.
            missing = [f for f in features if f not in available]
# [Context] Supporting line for the active lvqq analysis stage.
            if missing:
# [Context] Supporting line for the active lvqq analysis stage.
                print(f'[warn] {root_path} missing branches: {missing}')
# [Context] Supporting line for the active lvqq analysis stage.
            frame = tree.arrays(use_features, library='pd')

        # Compute physics weight: lumi * xsec / ngen_total
            # Physics interpretation:
            # - every event weight is the expected event yield contribution at 10.8 ab^-1.
            # - this is the only way class frequencies become physically comparable across processes.
# [Context] Supporting line for the active lvqq analysis stage.
            info = SAMPLE_INFO.get(sample, {})
# [Context] Supporting line for the active lvqq analysis stage.
        if info:
# [Context] Supporting line for the active lvqq analysis stage.
            frac = info.get('fraction', 1.0)
# [Stats] Physics weights propagate cross-section and luminosity to training/fit observables.
            phys_weight = INT_LUMI * info['xsec'] / (info['ngen'] * frac)
# [Context] Supporting line for the active lvqq analysis stage.
        else:
# [Stats] Physics weights propagate cross-section and luminosity to training/fit observables.
            phys_weight = 1.0
# [Context] Supporting line for the active lvqq analysis stage.
            print(f'[warn] no cross-section info for {sample}, using weight=1')

# [Stats] Physics weights propagate cross-section and luminosity to training/fit observables.
        frame['phys_weight'] = phys_weight
# [Context] Supporting line for the active lvqq analysis stage.
        frame['label'] = label
# [Context] Supporting line for the active lvqq analysis stage.
        frame['sample_name'] = sample
# [Context] Supporting line for the active lvqq analysis stage.
        n = len(frame)
# [Context] Supporting line for the active lvqq analysis stage.
        expected = INT_LUMI * info.get('xsec', 0)
# [Stats] Physics weights propagate cross-section and luminosity to training/fit observables.
        print(f'  {sample}: {n} events, phys_weight={phys_weight:.6f}, '
# [Stats] Physics weights propagate cross-section and luminosity to training/fit observables.
              f'effective={n*phys_weight:.0f} (expected total={expected:.0f})')
# [Context] Supporting line for the active lvqq analysis stage.
        frames.append(frame)

# [Context] Supporting line for the active lvqq analysis stage.
    if not frames:
# [Context] Supporting line for the active lvqq analysis stage.
        raise RuntimeError('No input ntuples found for training.')
# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return pd.concat(frames, ignore_index=True)


# [ML] Re-balance class totals so optimization is not dominated by one class weight scale.
def normalize_class_weights(w, y):
    """Normalize weights so signal and background have equal total weight.

    Preserves intra-class weight structure (relative weights within each class
    are unchanged). This ensures balanced learning while respecting the physics
    weight ratios between samples within each class.
    """
    # This is not undoing the physics prior; it is a training-time rebalancing.
    # We keep per-event xsec weights internally, then rescale each class envelope
    # so the classifier sees similar effective statistics for signal and background.

# [Workflow] Copy exactly the curated deliverables to paper directories.
    w = w.copy()
# [Context] Supporting line for the active lvqq analysis stage.
    sig_mask = y == 1
# [Context] Supporting line for the active lvqq analysis stage.
    bkg_mask = y == 0
# [Context] Supporting line for the active lvqq analysis stage.
    sig_total = w[sig_mask].sum()
# [Context] Supporting line for the active lvqq analysis stage.
    bkg_total = w[bkg_mask].sum()
    # Scale both classes to have total weight = number of events in smaller class
# [Context] Supporting line for the active lvqq analysis stage.
    target = min(sig_mask.sum(), bkg_mask.sum())
# [Context] Supporting line for the active lvqq analysis stage.
    w[sig_mask] *= target / sig_total
# [Context] Supporting line for the active lvqq analysis stage.
    w[bkg_mask] *= target / bkg_total
# [Context] Supporting line for the active lvqq analysis stage.
    print(f'  Normalized weights: sig total={w[sig_mask].sum():.0f}, '
# [Context] Supporting line for the active lvqq analysis stage.
          f'bkg total={w[bkg_mask].sum():.0f}')
# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return w


# [Workflow] train_xgboost_bdt.py function weighted_ks_test: modularize one operation for deterministic pipeline control.
def weighted_ks_test(scores_a, weights_a, scores_b, weights_b, n_bins=50):
    """Weighted KS-like test using binned chi2 comparison.

    Returns (chi2/ndf, p_value) using weighted histograms.
    scipy's ks_2samp doesn't support weights, so we use a binned approach.
    """
    # Weighted version is closer to your real objective:
    # events have unequal MC weight, so a plain KS statistic can underplay
    # high-impact regions and overplay low-weight tail entries.

# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
    from scipy.stats import chi2 as chi2_dist
# [Context] Supporting line for the active lvqq analysis stage.
    bins = np.linspace(0, 1, n_bins + 1)

# [Stats] Build binned templates required by shape-based likelihood fitting.
    h_a, _ = np.histogram(scores_a, bins=bins, weights=weights_a)
# [Stats] Build binned templates required by shape-based likelihood fitting.
    h_b, _ = np.histogram(scores_b, bins=bins, weights=weights_b)

    # Normalize to unit area
# [Context] Supporting line for the active lvqq analysis stage.
    sum_a = h_a.sum()
# [Context] Supporting line for the active lvqq analysis stage.
    sum_b = h_b.sum()
# [Context] Supporting line for the active lvqq analysis stage.
    if sum_a > 0:
# [Context] Supporting line for the active lvqq analysis stage.
        h_a = h_a / sum_a
# [Context] Supporting line for the active lvqq analysis stage.
    if sum_b > 0:
# [Context] Supporting line for the active lvqq analysis stage.
        h_b = h_b / sum_b

    # Binned chi2: sum (a - b)^2 / (var_a + var_b)
    # Variance from weighted histograms
# [Stats] Build binned templates required by shape-based likelihood fitting.
    h_a_w2, _ = np.histogram(scores_a, bins=bins, weights=weights_a**2)
# [Stats] Build binned templates required by shape-based likelihood fitting.
    h_b_w2, _ = np.histogram(scores_b, bins=bins, weights=weights_b**2)
# [Context] Supporting line for the active lvqq analysis stage.
    var_a = h_a_w2 / (sum_a**2) if sum_a > 0 else np.zeros_like(h_a)
# [Context] Supporting line for the active lvqq analysis stage.
    var_b = h_b_w2 / (sum_b**2) if sum_b > 0 else np.zeros_like(h_b)

# [Context] Supporting line for the active lvqq analysis stage.
    denom = var_a + var_b
# [Context] Supporting line for the active lvqq analysis stage.
    mask = denom > 0
# [Context] Supporting line for the active lvqq analysis stage.
    chi2_val = np.sum((h_a[mask] - h_b[mask])**2 / denom[mask])
# [Context] Supporting line for the active lvqq analysis stage.
    ndf = mask.sum() - 1
# [Context] Supporting line for the active lvqq analysis stage.
    p_value = 1.0 - chi2_dist.cdf(chi2_val, ndf) if ndf > 0 else 1.0
# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return chi2_val / max(ndf, 1), p_value


# [Workflow] train_xgboost_bdt.py function make_validation_split: modularize one operation for deterministic pipeline control.
def make_validation_split(X, y, w, random_state, test_size=0.2):
    """Create a validation split that is disjoint from the fit sample."""
# [Context] Supporting line for the active lvqq analysis stage.
    # Two-layer split architecture:
    # 1) train/val split inside fit_with_early_stopping for complexity selection;
    # 2) a separate held-out test split below for final reporting and overtraining checks.
    # This avoids reusing a single split for both model selection and evaluation.
    indices = np.arange(len(X))
# [ML] Split data into non-overlapping train/validation/test sets to estimate generalization.
    idx_fit, idx_val = train_test_split(
# [Context] Supporting line for the active lvqq analysis stage.
        indices, test_size=test_size, random_state=random_state, stratify=y,
# [Context] Supporting line for the active lvqq analysis stage.
    )
# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return (
# [Context] Supporting line for the active lvqq analysis stage.
        X.iloc[idx_fit], X.iloc[idx_val],
# [Context] Supporting line for the active lvqq analysis stage.
        y.iloc[idx_fit], y.iloc[idx_val],
# [Context] Supporting line for the active lvqq analysis stage.
        w.iloc[idx_fit], w.iloc[idx_val],
# [Context] Supporting line for the active lvqq analysis stage.
    )


# [ML] Add validation monitoring and early stopping to reduce overfitting.
def fit_with_early_stopping(X_train, y_train, w_train, params, random_state, n_jobs, eval_metric):
    """Choose the boosting length on a held-out validation split, then retrain."""
    # The held-out val sample is used only for this step:
    # it determines tree count and reduces overfit risk, then final fit runs on all
    # training rows using that selected complexity.

# [Context] Supporting line for the active lvqq analysis stage.
    X_fit, X_val, y_fit, y_val, w_fit, w_val = make_validation_split(
# [Context] Supporting line for the active lvqq analysis stage.
        X_train, y_train, w_train, random_state=random_state,
# [Context] Supporting line for the active lvqq analysis stage.
    )

# [Context] Supporting line for the active lvqq analysis stage.
    fit_kwargs = {
# [Context] Supporting line for the active lvqq analysis stage.
        'objective': 'binary:logistic',
# [Context] Supporting line for the active lvqq analysis stage.
        'eval_metric': eval_metric,
# [Context] Supporting line for the active lvqq analysis stage.
        'tree_method': 'hist',
# [Context] Supporting line for the active lvqq analysis stage.
        'random_state': random_state,
# [Context] Supporting line for the active lvqq analysis stage.
        'n_jobs': n_jobs,
# [Context] Supporting line for the active lvqq analysis stage.
        'verbosity': 0,
# [Context] Supporting line for the active lvqq analysis stage.
        **params,
# [Context] Supporting line for the active lvqq analysis stage.
    }
# [ML] Core estimator family (XGBoost) for non-linear kinematic separation.
    model_es = xgb.XGBClassifier(early_stopping_rounds=30, **fit_kwargs)
# [ML] Overfitting control:
# - Early stopping checks validation AUC/score plateau; tree growth stops if no gain is observed.
# - retraining on full set uses best_iteration+1, avoiding manual depth over-commitment.
# [ML] Fit step learns model parameters from weighted event features.
    model_es.fit(
# [Context] Supporting line for the active lvqq analysis stage.
        X_fit, y_fit, sample_weight=w_fit,
# [Context] Supporting line for the active lvqq analysis stage.
        eval_set=[(X_val, y_val)],
# [Context] Supporting line for the active lvqq analysis stage.
        sample_weight_eval_set=[w_val],
# [Context] Supporting line for the active lvqq analysis stage.
        verbose=False,
# [Context] Supporting line for the active lvqq analysis stage.
    )

# [Context] Supporting line for the active lvqq analysis stage.
    best_iteration = getattr(model_es, 'best_iteration', None)
# [Context] Supporting line for the active lvqq analysis stage.
    n_estimators_final = (best_iteration + 1
# [Context] Supporting line for the active lvqq analysis stage.
                          if best_iteration is not None
# [Context] Supporting line for the active lvqq analysis stage.
                          else params['n_estimators'])

# [Context] Supporting line for the active lvqq analysis stage.
    final_kwargs = dict(fit_kwargs)
# [Context] Supporting line for the active lvqq analysis stage.
    final_kwargs['n_estimators'] = n_estimators_final
# [ML] Core estimator family (XGBoost) for non-linear kinematic separation.
    model = xgb.XGBClassifier(**final_kwargs)
# [ML] Fit step learns model parameters from weighted event features.
    model.fit(X_train, y_train, sample_weight=w_train, verbose=False)

# [Context] Supporting line for the active lvqq analysis stage.
    val_score = model.predict_proba(X_val)[:, 1]
# [ML] ROC metrics provide threshold-independent ranking quality under class imbalance.
    val_auc = roc_auc_score(y_val, val_score, sample_weight=w_val)

# [Context] Supporting line for the active lvqq analysis stage.
    evals_result = model_es.evals_result() if hasattr(model_es, 'evals_result') else {}
# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return model, best_iteration, n_estimators_final, val_auc, evals_result


# [ML] Tune key XGBoost hyperparameters for robust signal-background separation.
def grid_search(X_train, y_train, w_train, random_state, n_jobs):
    """Run hyperparameter grid search on a subsample with early stopping."""
    # Search space is not exhaustive physics discovery; it's a constrained capacity scan.
    # The objective is stable ranking (AUC) under the same early-stop protocol, then reuse
    # the best hyperparameters for the full retraining on all training events.

# [Context] Supporting line for the active lvqq analysis stage.
    print('\n=== Hyperparameter Grid Search ===')
    # Subsample for speed
    # ML/compute rationale:
    # - sweep on a capped 50k subsample preserves signal/background pattern while keeping turnaround acceptable.
    # - all candidates are compared with the same internal validation protocol, so relative AUC ranking is stable.
# [Context] Supporting line for the active lvqq analysis stage.
    n_sub = min(50000, len(X_train))
# [Context] Supporting line for the active lvqq analysis stage.
    idx = np.random.RandomState(random_state).choice(len(X_train), n_sub, replace=False)
# [Context] Supporting line for the active lvqq analysis stage.
    X_sub = X_train.iloc[idx]
# [Context] Supporting line for the active lvqq analysis stage.
    y_sub = y_train.iloc[idx]
# [Context] Supporting line for the active lvqq analysis stage.
    w_sub = w_train.iloc[idx]

    # Split subsample into train/val
# [ML] Split data into non-overlapping train/validation/test sets to estimate generalization.
    X_t, X_v, y_t, y_v, w_t, w_v = train_test_split(
# [Context] Supporting line for the active lvqq analysis stage.
        X_sub, y_sub, w_sub, test_size=0.3, random_state=random_state, stratify=y_sub
# [Context] Supporting line for the active lvqq analysis stage.
    )

    # Extended grid: now includes min_child_weight and subsample
# [Context] Supporting line for the active lvqq analysis stage.
    param_grid = {
# [Context] Supporting line for the active lvqq analysis stage.
        'max_depth': [3, 4, 5],
# [Context] Supporting line for the active lvqq analysis stage.
        'learning_rate': [0.01, 0.05, 0.1],
# [Context] Supporting line for the active lvqq analysis stage.
        'n_estimators': [1000],  # single large value; early stopping finds optimum
# [Context] Supporting line for the active lvqq analysis stage.
        'min_child_weight': [5, 10, 20],
# [Context] Supporting line for the active lvqq analysis stage.
        'subsample': [0.7, 0.8],
# [Context] Supporting line for the active lvqq analysis stage.
        'colsample_bytree': [0.7, 0.8],
# [Context] Supporting line for the active lvqq analysis stage.
    }

# [Context] Supporting line for the active lvqq analysis stage.
    best_auc = 0
# [Context] Supporting line for the active lvqq analysis stage.
    best_params = {}
# [Context] Supporting line for the active lvqq analysis stage.
    results = []

# [Context] Supporting line for the active lvqq analysis stage.
    combos = list(product(
# [Context] Supporting line for the active lvqq analysis stage.
        param_grid['max_depth'],
# [Context] Supporting line for the active lvqq analysis stage.
        param_grid['learning_rate'],
# [Context] Supporting line for the active lvqq analysis stage.
        param_grid['n_estimators'],
# [Context] Supporting line for the active lvqq analysis stage.
        param_grid['min_child_weight'],
# [Context] Supporting line for the active lvqq analysis stage.
        param_grid['subsample'],
# [Context] Supporting line for the active lvqq analysis stage.
        param_grid['colsample_bytree'],
# [Context] Supporting line for the active lvqq analysis stage.
    ))
# [Context] Supporting line for the active lvqq analysis stage.
    print(f'  Testing {len(combos)} combinations...')

# [Context] Supporting line for the active lvqq analysis stage.
    for depth, lr, n_est, mcw, ss, csbt in combos:
# [ML] Core estimator family (XGBoost) for non-linear kinematic separation.
        model = xgb.XGBClassifier(
# [Context] Supporting line for the active lvqq analysis stage.
            objective='binary:logistic',
# [Context] Supporting line for the active lvqq analysis stage.
            eval_metric='auc',
# [Context] Supporting line for the active lvqq analysis stage.
            tree_method='hist',
# [Context] Supporting line for the active lvqq analysis stage.
            max_depth=depth,
# [Context] Supporting line for the active lvqq analysis stage.
            learning_rate=lr,
# [Context] Supporting line for the active lvqq analysis stage.
            n_estimators=n_est,
# [Context] Supporting line for the active lvqq analysis stage.
            min_child_weight=mcw,
# [Context] Supporting line for the active lvqq analysis stage.
            subsample=ss,
# [Context] Supporting line for the active lvqq analysis stage.
            colsample_bytree=csbt,
# [Context] Supporting line for the active lvqq analysis stage.
            random_state=random_state,
# [Context] Supporting line for the active lvqq analysis stage.
            n_jobs=n_jobs,
# [Context] Supporting line for the active lvqq analysis stage.
            early_stopping_rounds=30,
# [Context] Supporting line for the active lvqq analysis stage.
            verbosity=0,
# [Context] Supporting line for the active lvqq analysis stage.
        )
# [ML] Fit step learns model parameters from weighted event features.
        model.fit(
# [Context] Supporting line for the active lvqq analysis stage.
            X_t, y_t, sample_weight=w_t,
# [Context] Supporting line for the active lvqq analysis stage.
            eval_set=[(X_v, y_v)],
# [Context] Supporting line for the active lvqq analysis stage.
            sample_weight_eval_set=[w_v],
# [Context] Supporting line for the active lvqq analysis stage.
            verbose=False,
# [Context] Supporting line for the active lvqq analysis stage.
        )
# [Context] Supporting line for the active lvqq analysis stage.
        score = model.predict_proba(X_v)[:, 1]
# [ML] ROC metrics provide threshold-independent ranking quality under class imbalance.
        auc = roc_auc_score(y_v, score, sample_weight=w_v)
# [Context] Supporting line for the active lvqq analysis stage.
        results.append({
# [Context] Supporting line for the active lvqq analysis stage.
            'max_depth': depth, 'learning_rate': lr,
# [Context] Supporting line for the active lvqq analysis stage.
            'n_estimators': n_est, 'min_child_weight': mcw,
# [Context] Supporting line for the active lvqq analysis stage.
            'subsample': ss, 'colsample_bytree': csbt,
# [Context] Supporting line for the active lvqq analysis stage.
            'val_auc': auc,
# [Context] Supporting line for the active lvqq analysis stage.
            'best_iteration': model.best_iteration if hasattr(model, 'best_iteration') else n_est,
# [Context] Supporting line for the active lvqq analysis stage.
        })
# [Context] Supporting line for the active lvqq analysis stage.
        if auc > best_auc:
# [Context] Supporting line for the active lvqq analysis stage.
            best_auc = auc
# [Context] Supporting line for the active lvqq analysis stage.
            best_params = {
# [Context] Supporting line for the active lvqq analysis stage.
                'max_depth': depth, 'learning_rate': lr,
# [Context] Supporting line for the active lvqq analysis stage.
                'n_estimators': n_est, 'min_child_weight': mcw,
# [Context] Supporting line for the active lvqq analysis stage.
                'subsample': ss, 'colsample_bytree': csbt,
# [Context] Supporting line for the active lvqq analysis stage.
            }

# [Context] Supporting line for the active lvqq analysis stage.
    print(f'  Best: depth={best_params["max_depth"]}, '
# [Context] Supporting line for the active lvqq analysis stage.
          f'lr={best_params["learning_rate"]}, '
# [Context] Supporting line for the active lvqq analysis stage.
          f'n_est={best_params["n_estimators"]}, '
# [Context] Supporting line for the active lvqq analysis stage.
          f'mcw={best_params["min_child_weight"]}, '
# [Context] Supporting line for the active lvqq analysis stage.
          f'ss={best_params["subsample"]}, '
# [Context] Supporting line for the active lvqq analysis stage.
          f'csbt={best_params["colsample_bytree"]}, '
# [Context] Supporting line for the active lvqq analysis stage.
          f'AUC={best_auc:.4f}')
# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return best_params, results


# [Workflow] train_xgboost_bdt.py function make_plots: modularize one operation for deterministic pipeline control.
def make_plots(output_dir, y_train, y_test, train_score, test_score,
# [Context] Supporting line for the active lvqq analysis stage.
               w_train, w_test, model, features, full_df_test=None):
    """Generate diagnostic plots including sculpting and per-sample distributions."""
# [Context] Supporting line for the active lvqq analysis stage.
    try:
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
        import matplotlib
# [Workflow] Save inspection plots immediately after generation for review history.
        matplotlib.use('Agg')
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
        import matplotlib.pyplot as plt
# [Context] Supporting line for the active lvqq analysis stage.
    except ImportError:
# [Workflow] Save inspection plots immediately after generation for review history.
        print('[warn] matplotlib not available, skipping plots')
# [Workflow] Return value hands the constructed object/metric to the next module stage.
        return

# [Context] Supporting line for the active lvqq analysis stage.
    plot_dir = output_dir / 'plots'
# [Context] Supporting line for the active lvqq analysis stage.
    plot_dir.mkdir(exist_ok=True)

# [Workflow] train_xgboost_bdt.py function add_fcc_label: modularize one operation for deterministic pipeline control.
    def add_fcc_label(ax, x=0.05, y=0.97):
# [Context] Supporting line for the active lvqq analysis stage.
        ax.text(x, y, r'$\mathbf{FCC\text{-}ee}$ Simulation',
# [Context] Supporting line for the active lvqq analysis stage.
                transform=ax.transAxes, fontsize=10, va='top',
# [Context] Supporting line for the active lvqq analysis stage.
                fontstyle='italic')
# [Context] Supporting line for the active lvqq analysis stage.
        ax.text(x, y - 0.06, r'$\sqrt{s}=240$ GeV, $10.8\,\mathrm{ab}^{-1}$',
# [Context] Supporting line for the active lvqq analysis stage.
                transform=ax.transAxes, fontsize=9, va='top')

    # 1. ROC curve
    # ML meaning:
    # - score ranking quality is the core target before fixing any threshold.
    # - weighted ROC reflects expected physics sensitivity at target luminosity.
# [ML] ROC metrics provide threshold-independent ranking quality under class imbalance.
    fpr, tpr, _ = roc_curve(y_test, test_score, sample_weight=w_test)
# [ML] ROC metrics provide threshold-independent ranking quality under class imbalance.
    auc_val = roc_auc_score(y_test, test_score, sample_weight=w_test)
# [Context] Supporting line for the active lvqq analysis stage.
    fig, ax = plt.subplots(figsize=(6, 6))
# [Context] Supporting line for the active lvqq analysis stage.
    ax.plot(fpr, tpr, label=f'Test AUC = {auc_val:.4f}')
# [ML] ROC metrics provide threshold-independent ranking quality under class imbalance.
    fpr_tr, tpr_tr, _ = roc_curve(y_train, train_score, sample_weight=w_train)
# [ML] ROC metrics provide threshold-independent ranking quality under class imbalance.
    auc_tr = roc_auc_score(y_train, train_score, sample_weight=w_train)
# [Context] Supporting line for the active lvqq analysis stage.
    ax.plot(fpr_tr, tpr_tr, '--', label=f'Train AUC = {auc_tr:.4f}')
# [Context] Supporting line for the active lvqq analysis stage.
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.3)
# [Context] Supporting line for the active lvqq analysis stage.
    ax.set_xlabel('False Positive Rate')
# [Context] Supporting line for the active lvqq analysis stage.
    ax.set_ylabel('True Positive Rate')
# [Context] Supporting line for the active lvqq analysis stage.
    ax.set_title('ROC Curve')
# [Context] Supporting line for the active lvqq analysis stage.
    ax.legend(loc='lower right')
# [Context] Supporting line for the active lvqq analysis stage.
    add_fcc_label(ax)
# [ML] ROC metrics provide threshold-independent ranking quality under class imbalance.
    fig.savefig(plot_dir / 'roc_curve.png', dpi=150, bbox_inches='tight')
# [ML] ROC metrics provide threshold-independent ranking quality under class imbalance.
    fig.savefig(plot_dir / 'roc_curve.pdf', bbox_inches='tight')
# [Context] Supporting line for the active lvqq analysis stage.
    plt.close()

    # 2. Signal efficiency vs background rejection
    # Physics meaning:
    # - maps operating-point trade-offs directly to usable analysis sensitivity.
# [Context] Supporting line for the active lvqq analysis stage.
    fig, ax = plt.subplots(figsize=(6, 6))
# [Context] Supporting line for the active lvqq analysis stage.
    bkg_rej = 1 - fpr
# [Context] Supporting line for the active lvqq analysis stage.
    ax.plot(tpr, bkg_rej, label=f'Test AUC = {auc_val:.4f}')
# [Context] Supporting line for the active lvqq analysis stage.
    ax.set_xlabel('Signal Efficiency')
# [Context] Supporting line for the active lvqq analysis stage.
    ax.set_ylabel('Background Rejection')
# [Context] Supporting line for the active lvqq analysis stage.
    ax.set_title('Signal Efficiency vs Background Rejection')
# [Context] Supporting line for the active lvqq analysis stage.
    ax.legend()
# [Context] Supporting line for the active lvqq analysis stage.
    ax.set_xlim(0, 1)
# [Context] Supporting line for the active lvqq analysis stage.
    ax.set_ylim(0, 1)
# [Context] Supporting line for the active lvqq analysis stage.
    ax.grid(True, alpha=0.3)
# [Workflow] Save inspection plots immediately after generation for review history.
    fig.savefig(plot_dir / 'sig_eff_vs_bkg_rej.png', dpi=150, bbox_inches='tight')
# [Workflow] Save inspection plots immediately after generation for review history.
    fig.savefig(plot_dir / 'sig_eff_vs_bkg_rej.pdf', bbox_inches='tight')
# [Context] Supporting line for the active lvqq analysis stage.
    plt.close()

    # 3. BDT score distributions (overtraining check) - weighted
    # Overtraining interpretation:
    # - compare train (shape-smoothed) and test (binned-point) projections at identical weights.
    # - strong divergence undercuts generalization before likelihood fit.
# [Context] Supporting line for the active lvqq analysis stage.
    fig, ax = plt.subplots(figsize=(8, 6))
# [Context] Supporting line for the active lvqq analysis stage.
    bins = np.linspace(0, 1, 51)
    # Train - weighted
# [Context] Supporting line for the active lvqq analysis stage.
    ax.hist(train_score[y_train == 1], bins=bins, weights=w_train[y_train == 1],
# [Context] Supporting line for the active lvqq analysis stage.
            density=True, alpha=0.5,
# [Context] Supporting line for the active lvqq analysis stage.
            label='Signal (train)', color='blue', histtype='stepfilled')
# [Context] Supporting line for the active lvqq analysis stage.
    ax.hist(train_score[y_train == 0], bins=bins, weights=w_train[y_train == 0],
# [Context] Supporting line for the active lvqq analysis stage.
            density=True, alpha=0.5,
# [Context] Supporting line for the active lvqq analysis stage.
            label='Background (train)', color='red', histtype='stepfilled')
    # Test as points - weighted
# [Stats] Build binned templates required by shape-based likelihood fitting.
    h_sig, _ = np.histogram(test_score[y_test == 1], bins=bins,
# [Context] Supporting line for the active lvqq analysis stage.
                             weights=w_test[y_test == 1], density=True)
# [Stats] Build binned templates required by shape-based likelihood fitting.
    h_bkg, _ = np.histogram(test_score[y_test == 0], bins=bins,
# [Context] Supporting line for the active lvqq analysis stage.
                             weights=w_test[y_test == 0], density=True)
# [Context] Supporting line for the active lvqq analysis stage.
    centers = 0.5 * (bins[:-1] + bins[1:])
# [Context] Supporting line for the active lvqq analysis stage.
    ax.scatter(centers, h_sig, marker='o', s=20, color='blue',
# [Context] Supporting line for the active lvqq analysis stage.
               label='Signal (test)', zorder=5)
# [Context] Supporting line for the active lvqq analysis stage.
    ax.scatter(centers, h_bkg, marker='o', s=20, color='red',
# [Context] Supporting line for the active lvqq analysis stage.
               label='Background (test)', zorder=5)
# [Context] Supporting line for the active lvqq analysis stage.
    ax.set_xlabel('BDT Score')
# [Context] Supporting line for the active lvqq analysis stage.
    ax.set_ylabel('Normalised (weighted)')
# [Context] Supporting line for the active lvqq analysis stage.
    ax.set_title('BDT Score Distribution (Overtraining Check)')
# [Context] Supporting line for the active lvqq analysis stage.
    ax.legend(fontsize=9)
# [Context] Supporting line for the active lvqq analysis stage.
    add_fcc_label(ax, x=0.35, y=0.97)
# [Workflow] Save inspection plots immediately after generation for review history.
    fig.savefig(plot_dir / 'overtraining_check.png', dpi=150, bbox_inches='tight')
# [Workflow] Save inspection plots immediately after generation for review history.
    fig.savefig(plot_dir / 'overtraining_check.pdf', bbox_inches='tight')
# [Context] Supporting line for the active lvqq analysis stage.
    plt.close()

    # 4. Feature importance
    # Explainability use:
    # - verifies whether the main physics observables are driving separation.
    # - can reveal accidental dependence on fragile reconstruction artifacts.
# [Context] Supporting line for the active lvqq analysis stage.
    importance = pd.Series(model.feature_importances_, index=features).sort_values()
# [Context] Supporting line for the active lvqq analysis stage.
    fig, ax = plt.subplots(figsize=(8, max(6, len(features) * 0.3)))
# [Context] Supporting line for the active lvqq analysis stage.
    importance.plot(kind='barh', ax=ax)
# [Context] Supporting line for the active lvqq analysis stage.
    ax.set_xlabel('Feature Importance (Gain)')
# [Context] Supporting line for the active lvqq analysis stage.
    ax.set_title('Feature Importance')
# [Context] Supporting line for the active lvqq analysis stage.
    add_fcc_label(ax, x=0.60, y=0.97)
# [Workflow] Save inspection plots immediately after generation for review history.
    fig.savefig(plot_dir / 'feature_importance.png', dpi=150, bbox_inches='tight')
# [Workflow] Save inspection plots immediately after generation for review history.
    fig.savefig(plot_dir / 'feature_importance.pdf', bbox_inches='tight')
# [Context] Supporting line for the active lvqq analysis stage.
    plt.close()

    # 5. Background sculpting check: BDT score vs Hcand_m
    # Statistical safety check:
    # - in an ideal separation variable, score should not strongly sculpt the Higgs mass background shape.
    # - strong correlation near m_H hints that shape systematics may be underestimated in the fit.
# [Context] Supporting line for the active lvqq analysis stage.
    if full_df_test is not None and 'Hcand_m' in full_df_test.columns:
# [Context] Supporting line for the active lvqq analysis stage.
        bkg_mask = y_test == 0
# [Context] Supporting line for the active lvqq analysis stage.
        if bkg_mask.sum() > 0:
# [Context] Supporting line for the active lvqq analysis stage.
            fig, ax = plt.subplots(figsize=(8, 6))
# [Context] Supporting line for the active lvqq analysis stage.
            sc = ax.scatter(
# [Context] Supporting line for the active lvqq analysis stage.
                full_df_test.loc[bkg_mask, 'Hcand_m'],
# [Context] Supporting line for the active lvqq analysis stage.
                test_score[bkg_mask],
# [Context] Supporting line for the active lvqq analysis stage.
                c=w_test[bkg_mask], cmap='viridis', s=2, alpha=0.5,
# [Context] Supporting line for the active lvqq analysis stage.
            )
# [Context] Supporting line for the active lvqq analysis stage.
            fig.colorbar(sc, ax=ax, label='Event weight')
# [Context] Supporting line for the active lvqq analysis stage.
            ax.set_xlabel('$m_{H,cand}$ [GeV]')
# [Context] Supporting line for the active lvqq analysis stage.
            ax.set_ylabel('BDT Score')
# [Context] Supporting line for the active lvqq analysis stage.
            ax.set_title('Background Sculpting Check: BDT Score vs $m_{H,cand}$')
# [Context] Supporting line for the active lvqq analysis stage.
            ax.axvline(125, color='red', linestyle='--', alpha=0.5, label='$m_H = 125$ GeV')
# [Context] Supporting line for the active lvqq analysis stage.
            ax.legend()
# [Workflow] Save inspection plots immediately after generation for review history.
            fig.savefig(plot_dir / 'sculpting_check.png', dpi=150, bbox_inches='tight')
# [Workflow] Save inspection plots immediately after generation for review history.
            fig.savefig(plot_dir / 'sculpting_check.pdf', bbox_inches='tight')
# [Context] Supporting line for the active lvqq analysis stage.
            plt.close()

            # Profile plot: mean BDT score in Hcand_m bins
# [Context] Supporting line for the active lvqq analysis stage.
            fig, ax = plt.subplots(figsize=(8, 5))
# [Context] Supporting line for the active lvqq analysis stage.
            m_bins = np.linspace(50, 200, 31)
# [Context] Supporting line for the active lvqq analysis stage.
            m_centers = 0.5 * (m_bins[:-1] + m_bins[1:])
# [Context] Supporting line for the active lvqq analysis stage.
            bkg_hcand = full_df_test.loc[bkg_mask, 'Hcand_m'].values
# [Context] Supporting line for the active lvqq analysis stage.
            bkg_scores = test_score[bkg_mask]
# [Context] Supporting line for the active lvqq analysis stage.
            bkg_w = w_test[bkg_mask]
# [Context] Supporting line for the active lvqq analysis stage.
            mean_scores = []
# [Context] Supporting line for the active lvqq analysis stage.
            for i in range(len(m_bins) - 1):
# [Context] Supporting line for the active lvqq analysis stage.
                in_bin = (bkg_hcand >= m_bins[i]) & (bkg_hcand < m_bins[i+1])
# [Context] Supporting line for the active lvqq analysis stage.
                if in_bin.sum() > 0:
# [Context] Supporting line for the active lvqq analysis stage.
                    mean_scores.append(np.average(bkg_scores[in_bin], weights=bkg_w[in_bin]))
# [Context] Supporting line for the active lvqq analysis stage.
                else:
# [Context] Supporting line for the active lvqq analysis stage.
                    mean_scores.append(np.nan)
# [Context] Supporting line for the active lvqq analysis stage.
            ax.plot(m_centers, mean_scores, 'o-', color='red')
# [Context] Supporting line for the active lvqq analysis stage.
            ax.set_xlabel('$m_{H,cand}$ [GeV]')
# [Context] Supporting line for the active lvqq analysis stage.
            ax.set_ylabel('Mean BDT Score (background)')
# [Context] Supporting line for the active lvqq analysis stage.
            ax.set_title('Background Sculpting Profile')
# [Context] Supporting line for the active lvqq analysis stage.
            ax.axvline(125, color='gray', linestyle='--', alpha=0.5)
# [Context] Supporting line for the active lvqq analysis stage.
            ax.grid(True, alpha=0.3)
# [Workflow] Save inspection plots immediately after generation for review history.
            fig.savefig(plot_dir / 'sculpting_profile.png', dpi=150, bbox_inches='tight')
# [Workflow] Save inspection plots immediately after generation for review history.
            fig.savefig(plot_dir / 'sculpting_profile.pdf', bbox_inches='tight')
# [Context] Supporting line for the active lvqq analysis stage.
            plt.close()

    # 6. Per-sample score distributions
# [Context] Supporting line for the active lvqq analysis stage.
    if full_df_test is not None and 'sample_name' in full_df_test.columns:
# [Context] Supporting line for the active lvqq analysis stage.
        fig, ax = plt.subplots(figsize=(8, 6))
# [Context] Supporting line for the active lvqq analysis stage.
        bins = np.linspace(0, 1, 51)
# [Context] Supporting line for the active lvqq analysis stage.
        for sample_name in full_df_test['sample_name'].unique():
# [Context] Supporting line for the active lvqq analysis stage.
            mask = full_df_test['sample_name'] == sample_name
# [Context] Supporting line for the active lvqq analysis stage.
            if mask.sum() == 0:
# [Context] Supporting line for the active lvqq analysis stage.
                continue
# [Context] Supporting line for the active lvqq analysis stage.
            short_name = sample_name.replace('wzp6_ee_', '').replace('p8_ee_', '').replace('_ecm240', '')
# [Context] Supporting line for the active lvqq analysis stage.
            ax.hist(test_score[mask], bins=bins, weights=w_test[mask],
# [Context] Supporting line for the active lvqq analysis stage.
                    density=True, alpha=0.6, histtype='step', linewidth=1.5,
# [Context] Supporting line for the active lvqq analysis stage.
                    label=short_name)
# [Context] Supporting line for the active lvqq analysis stage.
        ax.set_xlabel('BDT Score')
# [Context] Supporting line for the active lvqq analysis stage.
        ax.set_ylabel('Normalised (weighted)')
# [Context] Supporting line for the active lvqq analysis stage.
        ax.set_title('Per-Sample BDT Score Distributions (Test Set)')
# [Context] Supporting line for the active lvqq analysis stage.
        ax.legend(fontsize=8, ncol=2)
# [Workflow] Save inspection plots immediately after generation for review history.
        fig.savefig(plot_dir / 'per_sample_scores.png', dpi=150, bbox_inches='tight')
# [Workflow] Save inspection plots immediately after generation for review history.
        fig.savefig(plot_dir / 'per_sample_scores.pdf', bbox_inches='tight')
# [Context] Supporting line for the active lvqq analysis stage.
        plt.close()

# [Context] Supporting line for the active lvqq analysis stage.
    print(f'  Plots saved to {plot_dir}/')


# [ML] Create out-of-fold scores so downstream fit uses unbiased predictions.
def kfold_score_all(X, y, w_phys, w_norm, full_df, best_params, n_folds=5, random_state=42, n_jobs=8):
    """Score ALL events using k-fold cross-validation.

    Each event is scored by a model that was NOT trained on it.
    This gives 100% of events with unbiased BDT scores for the fit,
    instead of only the 30% test set.
    """
    # This is the statistical handoff section:
    # k-fold scores are what the likelihood layer should consume first, because they are
    # out-of-fold and do not leak event information from the training pass that produced the model.

# [Context] Supporting line for the active lvqq analysis stage.
    print(f'\n=== {n_folds}-Fold Cross-Validation Scoring ===')
# [ML] Preserve class composition inside each CV fold.
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=random_state)

# [Context] Supporting line for the active lvqq analysis stage.
    scores = np.zeros(len(X))
# [Context] Supporting line for the active lvqq analysis stage.
    for fold_i, (train_idx, val_idx) in enumerate(skf.split(X, y)):
# [Context] Supporting line for the active lvqq analysis stage.
        X_t, y_t, w_t = X.iloc[train_idx], y.iloc[train_idx], w_norm.iloc[train_idx]
# [Context] Supporting line for the active lvqq analysis stage.
        X_v = X.iloc[val_idx]
# [ML] Fit step learns model parameters from weighted event features.
        model_k, best_iteration, _, _, _ = fit_with_early_stopping(
# [Context] Supporting line for the active lvqq analysis stage.
            X_t, y_t, w_t, best_params,
# [Context] Supporting line for the active lvqq analysis stage.
            random_state=random_state + fold_i,
# [Context] Supporting line for the active lvqq analysis stage.
            n_jobs=n_jobs,
# [Context] Supporting line for the active lvqq analysis stage.
            eval_metric='auc',
# [Context] Supporting line for the active lvqq analysis stage.
        )
# [Context] Supporting line for the active lvqq analysis stage.
        scores[val_idx] = model_k.predict_proba(X_v)[:, 1]
# [ML] ROC metrics provide threshold-independent ranking quality under class imbalance.
        auc_k = roc_auc_score(y.iloc[val_idx], scores[val_idx],
# [Context] Supporting line for the active lvqq analysis stage.
                              sample_weight=w_phys.iloc[val_idx])
# [Context] Supporting line for the active lvqq analysis stage.
        best_iter_text = 'NA' if best_iteration is None else str(best_iteration + 1)
# [Context] Supporting line for the active lvqq analysis stage.
        print(f'  Fold {fold_i+1}/{n_folds}: AUC={auc_k:.4f} '
# [Context] Supporting line for the active lvqq analysis stage.
              f'({len(val_idx)} events, {best_iter_text} trees)')

# [ML] ROC metrics provide threshold-independent ranking quality under class imbalance.
    overall_auc = roc_auc_score(y, scores, sample_weight=w_phys)
# [Context] Supporting line for the active lvqq analysis stage.
    print(f'  Overall k-fold AUC: {overall_auc:.4f}')

# [Context] Supporting line for the active lvqq analysis stage.
    kfold_df = pd.DataFrame({
# [Context] Supporting line for the active lvqq analysis stage.
        'y_true': y.to_numpy(),
# [Stats] Physics weights propagate cross-section and luminosity to training/fit observables.
        'phys_weight': w_phys.to_numpy(),
# [Context] Supporting line for the active lvqq analysis stage.
        'bdt_score': scores,
# [Context] Supporting line for the active lvqq analysis stage.
        'sample_name': full_df['sample_name'].to_numpy(),
# [Context] Supporting line for the active lvqq analysis stage.
    })
# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return kfold_df, overall_auc


# [Workflow] Orchestrates ingestion, training, validation, serialization, and optional diagnostics.
def main():
# [Context] Supporting line for the active lvqq analysis stage.
    args = parse_args()
    # End-to-end sequence for a stable analysis:
    # - data ingestion from treemaker ntuples
    # - physics-aware weight construction and class normalization
    # - strict train/test split
    # - optional hyperparameter search
    # - early-stop retraining
    # - diagnostic plots and statistical checks
    # - optional full-corpus OOF scoring for fit
# [Context] Supporting line for the active lvqq analysis stage.
    output_dir = Path(args.output_dir)
# [Context] Supporting line for the active lvqq analysis stage.
    output_dir.mkdir(parents=True, exist_ok=True)

# [Context] Supporting line for the active lvqq analysis stage.
    print('=== Loading Data ===')
# [Context] Supporting line for the active lvqq analysis stage.
    print(
# [Context] Supporting line for the active lvqq analysis stage.
        'Background fractions: '
# [Context] Supporting line for the active lvqq analysis stage.
        f"WW={BACKGROUND_FRACTIONS['ww']:.6g}, "
# [Context] Supporting line for the active lvqq analysis stage.
        f"ZZ={BACKGROUND_FRACTIONS['zz']:.6g}, "
# [Context] Supporting line for the active lvqq analysis stage.
        f"qq={BACKGROUND_FRACTIONS['qq']:.6g}, "
# [Context] Supporting line for the active lvqq analysis stage.
        f"tautau={BACKGROUND_FRACTIONS['tautau']:.6g}"
# [Context] Supporting line for the active lvqq analysis stage.
    )
# [Context] Supporting line for the active lvqq analysis stage.
    print('Signal:')
# [Context] Supporting line for the active lvqq analysis stage.
    sig_df = read_samples(args.input_dir, args.tree_name,
# [Context] Supporting line for the active lvqq analysis stage.
                          args.signal_samples, args.features, 1)
# [Context] Supporting line for the active lvqq analysis stage.
    print('Background:')
# [Context] Supporting line for the active lvqq analysis stage.
    bkg_df = read_samples(args.input_dir, args.tree_name,
# [Context] Supporting line for the active lvqq analysis stage.
                          args.background_samples, args.features, 0)
# [Context] Supporting line for the active lvqq analysis stage.
    full_df = pd.concat([sig_df, bkg_df], ignore_index=True)

    # Use only features that exist in the data
# [Context] Supporting line for the active lvqq analysis stage.
    available_features = [f for f in args.features if f in full_df.columns]
# [Context] Supporting line for the active lvqq analysis stage.
    missing_features = [f for f in args.features if f not in full_df.columns]
# [Context] Supporting line for the active lvqq analysis stage.
    if missing_features:
# [Context] Supporting line for the active lvqq analysis stage.
        print(f'[warn] Missing features (will skip): {missing_features}')
# [Context] Supporting line for the active lvqq analysis stage.
    print(f'\nUsing {len(available_features)} features')

# [Workflow] Configuration binding; this line defines a stable contract across modules.
    X = full_df[available_features].copy()
# [Context] Supporting line for the active lvqq analysis stage.
    y = full_df['label']
# [Stats] Physics weights propagate cross-section and luminosity to training/fit observables.
    w = full_df['phys_weight'].astype(float)

    # Fix sentinel values: missingMass uses -999 for undefined cases
# [Context] Supporting line for the active lvqq analysis stage.
    if 'missingMass' in X.columns:
# [Context] Supporting line for the active lvqq analysis stage.
        n_sentinel = (X['missingMass'] < -900).sum()
# [Context] Supporting line for the active lvqq analysis stage.
        if n_sentinel > 0:
# [Context] Supporting line for the active lvqq analysis stage.
            print(f'[fix] Replacing {n_sentinel} missingMass sentinel values (-999) with 0')
# [Context] Supporting line for the active lvqq analysis stage.
            X.loc[X['missingMass'] < -900, 'missingMass'] = 0.0

    # Report class balance with physics weights
# [Context] Supporting line for the active lvqq analysis stage.
    sig_weighted = w[y == 1].sum()
# [Context] Supporting line for the active lvqq analysis stage.
    bkg_weighted = w[y == 0].sum()
# [Context] Supporting line for the active lvqq analysis stage.
    print(f'\n=== Class Balance (physics-weighted) ===')
# [Context] Supporting line for the active lvqq analysis stage.
    print(f'  Signal:     {(y==1).sum()} events, weighted sum = {sig_weighted:.0f}')
# [Context] Supporting line for the active lvqq analysis stage.
    print(f'  Background: {(y==0).sum()} events, weighted sum = {bkg_weighted:.0f}')
# [Context] Supporting line for the active lvqq analysis stage.
    print(f'  Weighted ratio bkg/sig = {bkg_weighted/sig_weighted:.1f}')

    # Normalize class weights for balanced learning (ML review item 4)
# [Context] Supporting line for the active lvqq analysis stage.
    w_normalized = normalize_class_weights(w, y)

    # Single index-based split to guarantee consistency across all arrays.
    # Design principle:
    # - test_indices are never used for model-hyperparameter tuning, only for transparent
    #   performance reporting and to reduce "look-ahead" leakage into training decisions.
# [Context] Supporting line for the active lvqq analysis stage.
    indices = np.arange(len(X))
# [ML] Split data into non-overlapping train/validation/test sets to estimate generalization.
    idx_train, idx_test = train_test_split(
# [Context] Supporting line for the active lvqq analysis stage.
        indices, test_size=args.test_size,
# [Context] Supporting line for the active lvqq analysis stage.
        random_state=args.random_state, stratify=y,
# [Context] Supporting line for the active lvqq analysis stage.
    )
# [Context] Supporting line for the active lvqq analysis stage.
    X_train, X_test = X.iloc[idx_train], X.iloc[idx_test]
# [Context] Supporting line for the active lvqq analysis stage.
    y_train, y_test = y.iloc[idx_train], y.iloc[idx_test]
# [Context] Supporting line for the active lvqq analysis stage.
    w_train, w_test = w_normalized.iloc[idx_train], w_normalized.iloc[idx_test]
# [Context] Supporting line for the active lvqq analysis stage.
    w_phys_train, w_phys_test = w.iloc[idx_train], w.iloc[idx_test]
# [Context] Supporting line for the active lvqq analysis stage.
    full_df_test = full_df.iloc[idx_test]

    # This is the single "held-out test slice" used for unbiased reporting.
    # Anything reported here (AUC, overtraining tests, score plots) must not feed back
    # into hyperparameter selection, otherwise it is no longer a blind check.

    # Hyperparameter search
# [Context] Supporting line for the active lvqq analysis stage.
    if not args.no_grid_search:
# [Context] Supporting line for the active lvqq analysis stage.
        best_params, grid_results = grid_search(
# [Context] Supporting line for the active lvqq analysis stage.
            X_train, y_train, w_train, args.random_state, args.n_jobs
# [Context] Supporting line for the active lvqq analysis stage.
        )
        # Save grid search results
# [Context] Supporting line for the active lvqq analysis stage.
        pd.DataFrame(grid_results).to_csv(
# [Context] Supporting line for the active lvqq analysis stage.
            output_dir / 'grid_search_results.csv', index=False
# [Context] Supporting line for the active lvqq analysis stage.
        )
# [Context] Supporting line for the active lvqq analysis stage.
    else:
# [Context] Supporting line for the active lvqq analysis stage.
        best_params = {
# [Context] Supporting line for the active lvqq analysis stage.
            'max_depth': 4, 'learning_rate': 0.05, 'n_estimators': 1000,
# [Context] Supporting line for the active lvqq analysis stage.
            'min_child_weight': 5, 'subsample': 0.8, 'colsample_bytree': 0.8,
# [Context] Supporting line for the active lvqq analysis stage.
        }
# [Context] Supporting line for the active lvqq analysis stage.
        grid_results = []

    # Train final model with a held-out validation split for early stopping.
    # The test sample is kept untouched for the performance report.
    # In ML terms: validation controls complexity, test measures generalization, and k-fold later
    # upgrades statistical usage in the likelihood stage.
# [Context] Supporting line for the active lvqq analysis stage.
    print(f'\n=== Training Final Model ===')
# [Context] Supporting line for the active lvqq analysis stage.
    print(f'  Params: {best_params}')
# [ML] Fit step learns model parameters from weighted event features.
    model, best_iteration, final_n_estimators, val_auc, training_history = fit_with_early_stopping(
# [Context] Supporting line for the active lvqq analysis stage.
        X_train, y_train, w_train, best_params,
# [Context] Supporting line for the active lvqq analysis stage.
        random_state=args.random_state,
# [Context] Supporting line for the active lvqq analysis stage.
        n_jobs=args.n_jobs,
# [Context] Supporting line for the active lvqq analysis stage.
        eval_metric=['logloss', 'auc'],
# [Context] Supporting line for the active lvqq analysis stage.
    )
# [Context] Supporting line for the active lvqq analysis stage.
    print(f'  Validation AUC (held-out from training): {val_auc:.4f}')
# [Context] Supporting line for the active lvqq analysis stage.
    print(f'  Trees kept after early stopping: {final_n_estimators}')

# [Context] Supporting line for the active lvqq analysis stage.
    train_score = model.predict_proba(X_train)[:, 1]
# [Context] Supporting line for the active lvqq analysis stage.
    test_score = model.predict_proba(X_test)[:, 1]

    # Weighted AUC (use physics weights for evaluation, not normalized)
# [ML] ROC metrics provide threshold-independent ranking quality under class imbalance.
    train_auc = roc_auc_score(y_train, train_score, sample_weight=w_phys_train)
# [ML] ROC metrics provide threshold-independent ranking quality under class imbalance.
    test_auc = roc_auc_score(y_test, test_score, sample_weight=w_phys_test)

    # Overtraining check: weighted KS test (binned chi2) on signal and background.
    # This is not a formal hypothesis test; it is a practical bias signal detector.
    # AUC gap + significant shape drift = likely overtraining under current features/hyperparameters.
# [Context] Supporting line for the active lvqq analysis stage.
    ks_sig_chi2, ks_sig_p = weighted_ks_test(
# [Context] Supporting line for the active lvqq analysis stage.
        train_score[y_train == 1], w_train[y_train == 1],
# [Context] Supporting line for the active lvqq analysis stage.
        test_score[y_test == 1], w_test[y_test == 1],
# [Context] Supporting line for the active lvqq analysis stage.
    )
# [Context] Supporting line for the active lvqq analysis stage.
    ks_bkg_chi2, ks_bkg_p = weighted_ks_test(
# [Context] Supporting line for the active lvqq analysis stage.
        train_score[y_train == 0], w_train[y_train == 0],
# [Context] Supporting line for the active lvqq analysis stage.
        test_score[y_test == 0], w_test[y_test == 0],
# [Context] Supporting line for the active lvqq analysis stage.
    )
    # Also compute unweighted KS for comparison
# [Context] Supporting line for the active lvqq analysis stage.
    ks_sig_uw = ks_2samp(train_score[y_train == 1], test_score[y_test == 1])
# [Context] Supporting line for the active lvqq analysis stage.
    ks_bkg_uw = ks_2samp(train_score[y_train == 0], test_score[y_test == 0])

# [Context] Supporting line for the active lvqq analysis stage.
    print(f'\n=== Results ===')
# [Context] Supporting line for the active lvqq analysis stage.
    print(f'  Train AUC: {train_auc:.4f}')
# [Context] Supporting line for the active lvqq analysis stage.
    print(f'  Test AUC:  {test_auc:.4f}')
# [Context] Supporting line for the active lvqq analysis stage.
    print(f'  |delta AUC|:    {abs(train_auc - test_auc):.4f}')
# [Context] Supporting line for the active lvqq analysis stage.
    print(f'  Weighted chi2/ndf (signal):     {ks_sig_chi2:.2f}, p={ks_sig_p:.4f}')
# [Context] Supporting line for the active lvqq analysis stage.
    print(f'  Weighted chi2/ndf (background): {ks_bkg_chi2:.2f}, p={ks_bkg_p:.4f}')
# [Context] Supporting line for the active lvqq analysis stage.
    print(f'  Unweighted KS (signal):     stat={ks_sig_uw.statistic:.4f}, p={ks_sig_uw.pvalue:.4f}')
# [Context] Supporting line for the active lvqq analysis stage.
    print(f'  Unweighted KS (background): stat={ks_bkg_uw.statistic:.4f}, p={ks_bkg_uw.pvalue:.4f}')
    # Use KS statistic (not p-value) for overtraining check — p-value is too
    # sensitive with large samples and flags negligible differences.
# [Context] Supporting line for the active lvqq analysis stage.
    overtraining = (abs(train_auc - test_auc) > 0.02
# [Context] Supporting line for the active lvqq analysis stage.
                    or ks_sig_uw.statistic > 0.05
# [Context] Supporting line for the active lvqq analysis stage.
                    or ks_bkg_uw.statistic > 0.05)
# [Context] Supporting line for the active lvqq analysis stage.
    print(f'  Overtraining: {"WARNING!" if overtraining else "OK"}')

# [Context] Supporting line for the active lvqq analysis stage.
    serializable_history = {}
# [Context] Supporting line for the active lvqq analysis stage.
    for ds_name, ds_metrics in training_history.items():
# [Context] Supporting line for the active lvqq analysis stage.
        serializable_history[ds_name] = {
# [Context] Supporting line for the active lvqq analysis stage.
            k: [float(v) for v in vals] for k, vals in ds_metrics.items()
# [Context] Supporting line for the active lvqq analysis stage.
        }

# [Context] Supporting line for the active lvqq analysis stage.
    metrics = {
# [Context] Supporting line for the active lvqq analysis stage.
        'train_auc': float(train_auc),
# [Context] Supporting line for the active lvqq analysis stage.
        'test_auc': float(test_auc),
# [Context] Supporting line for the active lvqq analysis stage.
        'validation_auc': float(val_auc),
# [Context] Supporting line for the active lvqq analysis stage.
        'delta_auc': float(abs(train_auc - test_auc)),
# [Context] Supporting line for the active lvqq analysis stage.
        'weighted_chi2_signal': float(ks_sig_chi2),
# [Context] Supporting line for the active lvqq analysis stage.
        'weighted_chi2_signal_pvalue': float(ks_sig_p),
# [Context] Supporting line for the active lvqq analysis stage.
        'weighted_chi2_background': float(ks_bkg_chi2),
# [Context] Supporting line for the active lvqq analysis stage.
        'weighted_chi2_background_pvalue': float(ks_bkg_p),
# [Context] Supporting line for the active lvqq analysis stage.
        'ks_signal_stat': float(ks_sig_uw.statistic),
# [Context] Supporting line for the active lvqq analysis stage.
        'ks_signal_pvalue': float(ks_sig_uw.pvalue),
# [Context] Supporting line for the active lvqq analysis stage.
        'ks_background_stat': float(ks_bkg_uw.statistic),
# [Context] Supporting line for the active lvqq analysis stage.
        'ks_background_pvalue': float(ks_bkg_uw.pvalue),
# [Context] Supporting line for the active lvqq analysis stage.
        'overtraining_flag': bool(overtraining),
# [Context] Supporting line for the active lvqq analysis stage.
        'n_train': int(len(X_train)),
# [Context] Supporting line for the active lvqq analysis stage.
        'n_test': int(len(X_test)),
# [Context] Supporting line for the active lvqq analysis stage.
        'n_signal_train': int((y_train == 1).sum()),
# [Context] Supporting line for the active lvqq analysis stage.
        'n_background_train': int((y_train == 0).sum()),
# [Context] Supporting line for the active lvqq analysis stage.
        'weighted_signal_sum': float(sig_weighted),
# [Context] Supporting line for the active lvqq analysis stage.
        'weighted_background_sum': float(bkg_weighted),
# [Context] Supporting line for the active lvqq analysis stage.
        'features': available_features,
# [Context] Supporting line for the active lvqq analysis stage.
        'best_hyperparameters': best_params,
# [Context] Supporting line for the active lvqq analysis stage.
        'early_stopping_best_iteration': int(best_iteration + 1)
# [Context] Supporting line for the active lvqq analysis stage.
            if best_iteration is not None else best_params['n_estimators'],
# [Context] Supporting line for the active lvqq analysis stage.
        'weight_normalization': 'class-balanced',
# [Context] Supporting line for the active lvqq analysis stage.
        'validation_fraction': 0.20,
# [Context] Supporting line for the active lvqq analysis stage.
    }

# [Context] Supporting line for the active lvqq analysis stage.
    model_path = output_dir / 'xgboost_bdt.json'
# [Context] Supporting line for the active lvqq analysis stage.
    model.save_model(model_path)

# [Context] Supporting line for the active lvqq analysis stage.
    with open(output_dir / 'training_metrics.json', 'w') as handle:
# [Workflow] Persist contracts and fit outputs to make every stage auditable.
        json.dump(metrics, handle, indent=2, sort_keys=True)

    # Save training history separately (can be large)
# [Context] Supporting line for the active lvqq analysis stage.
    if serializable_history:
# [Context] Supporting line for the active lvqq analysis stage.
        with open(output_dir / 'training_history.json', 'w') as handle:
# [Workflow] Persist contracts and fit outputs to make every stage auditable.
            json.dump(serializable_history, handle, indent=2)

# [Context] Supporting line for the active lvqq analysis stage.
    importance = pd.Series(
# [Context] Supporting line for the active lvqq analysis stage.
        model.feature_importances_, index=available_features
# [Context] Supporting line for the active lvqq analysis stage.
    ).sort_values(ascending=False)
# [Context] Supporting line for the active lvqq analysis stage.
    importance.to_csv(output_dir / 'feature_importance.csv', header=['importance'])

# [Context] Supporting line for the active lvqq analysis stage.
    pd.DataFrame({
# [Context] Supporting line for the active lvqq analysis stage.
        'y_true': y_test.to_numpy(),
# [Stats] Physics weights propagate cross-section and luminosity to training/fit observables.
        'phys_weight': w_phys_test.to_numpy(),
# [Context] Supporting line for the active lvqq analysis stage.
        'norm_weight': w_test.to_numpy(),
# [Context] Supporting line for the active lvqq analysis stage.
        'bdt_score': test_score,
# [Context] Supporting line for the active lvqq analysis stage.
        'sample_name': full_df_test['sample_name'].to_numpy(),
# [Context] Supporting line for the active lvqq analysis stage.
    }).to_csv(output_dir / 'test_scores.csv', index=False)

    # Diagnostic plots
# [Context] Supporting line for the active lvqq analysis stage.
    if not args.no_plots:
# [Context] Supporting line for the active lvqq analysis stage.
        make_plots(output_dir, y_train, y_test, train_score, test_score,
# [Context] Supporting line for the active lvqq analysis stage.
                   w_phys_train, w_phys_test, model, available_features,
# [Context] Supporting line for the active lvqq analysis stage.
                   full_df_test=full_df_test)

    # K-fold cross-validation scoring (all events get unbiased OOF scores).
    # These OOF scores are the preferred source for likelihood fits because they remove
    # training/assessment leakage compared to plain train/test-slice scoring.
# [Context] Supporting line for the active lvqq analysis stage.
    if args.kfold > 0:
# [Context] Supporting line for the active lvqq analysis stage.
        kfold_df, kfold_auc = kfold_score_all(
# [Context] Supporting line for the active lvqq analysis stage.
            X, y, w, w_normalized, full_df, best_params,
# [Context] Supporting line for the active lvqq analysis stage.
            n_folds=args.kfold, random_state=args.random_state, n_jobs=args.n_jobs,
# [Context] Supporting line for the active lvqq analysis stage.
        )
# [Context] Supporting line for the active lvqq analysis stage.
        kfold_df.to_csv(output_dir / 'kfold_scores.csv', index=False)
# [Context] Supporting line for the active lvqq analysis stage.
        print(f'  k-fold scores saved ({len(kfold_df)} events, AUC={kfold_auc:.4f})')

# [Context] Supporting line for the active lvqq analysis stage.
    print(f'\n  model: {model_path}')
# [Context] Supporting line for the active lvqq analysis stage.
    print(f'  test AUC: {test_auc:.4f}')
# [Context] Supporting line for the active lvqq analysis stage.
    print(f'  features: {len(available_features)}')
# [Context] Supporting line for the active lvqq analysis stage.
    print('Done.')


# [Context] Supporting line for the active lvqq analysis stage.
if __name__ == '__main__':
# [Context] Supporting line for the active lvqq analysis stage.
    main()
