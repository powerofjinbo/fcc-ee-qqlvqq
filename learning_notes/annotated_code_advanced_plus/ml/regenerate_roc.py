#!/usr/bin/env python3
# ROC rebuild utility for quality control on train/test split and k-fold inference.
#
# Purpose in the chain:
# - 5-fold ROC uses out-of-fold scores and is the unbiased central figure of merit.
# - optional split ROC is a complementary diagnostic for overfitting and split-sensitivity.

"""Regenerate ROC plots for the BDT classifier.

By default this writes the paper ROC figure from the 5-fold cross-validated
scores used in the final fit. An optional diagnostic train/test ROC can also be
produced for development checks.
"""
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import argparse
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import sys
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
from pathlib import Path
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import numpy as np
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import pandas as pd
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import xgboost as xgb
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
from sklearn.metrics import roc_auc_score, roc_curve
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
from sklearn.model_selection import train_test_split

# [Workflow] Configuration binding; this line defines a stable contract across modules.
THIS_DIR = Path(__file__).resolve().parent
# [Workflow] Configuration binding; this line defines a stable contract across modules.
ANALYSIS_DIR = THIS_DIR.parent
# [Context] Supporting line for the active lvqq analysis stage.
sys.path.insert(0, str(ANALYSIS_DIR))

# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
from ml_config import (
# [Context] Supporting line for the active lvqq analysis stage.
    BACKGROUND_SAMPLES, DEFAULT_MODEL_DIR, DEFAULT_TREE_NAME, DEFAULT_TREEMAKER_DIR,
# [Context] Supporting line for the active lvqq analysis stage.
    ML_FEATURES, SIGNAL_SAMPLES,
# [Context] Supporting line for the active lvqq analysis stage.
)

# Import sample info and reader from training script
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
from train_xgboost_bdt import read_samples

# [Workflow] Configuration binding; this line defines a stable contract across modules.
MODEL_DIR = ANALYSIS_DIR / DEFAULT_MODEL_DIR

# [Workflow] Centralize plotting style and FCC-ee labels for repeatable quality-control figures.
def make_axes():
    # Plot
    # [ML] Same styling and axis convention used by all CV/fit plots in this repo,
    # to keep model quality plots comparable across reruns.
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
    import matplotlib
# [Workflow] Save inspection plots immediately after generation for review history.
    matplotlib.use('Agg')
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
    import matplotlib.pyplot as plt
# [Context] Supporting line for the active lvqq analysis stage.
    fig, ax = plt.subplots(figsize=(6, 6))
# [Context] Supporting line for the active lvqq analysis stage.
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.3)
# [Context] Supporting line for the active lvqq analysis stage.
    ax.set_xlabel('False Positive Rate')
# [Context] Supporting line for the active lvqq analysis stage.
    ax.set_ylabel('True Positive Rate')
# [Context] Supporting line for the active lvqq analysis stage.
    ax.set_title('ROC Curve')
# [Context] Supporting line for the active lvqq analysis stage.
    ax.text(0.05, 0.97, r'$\mathbf{FCC\text{-}ee}$ Simulation',
# [Context] Supporting line for the active lvqq analysis stage.
            transform=ax.transAxes, fontsize=10, va='top', fontstyle='italic')
# [Context] Supporting line for the active lvqq analysis stage.
    ax.text(0.05, 0.91, r'$\sqrt{s}=240$ GeV, $10.8\,\mathrm{ab}^{-1}$',
# [Context] Supporting line for the active lvqq analysis stage.
            transform=ax.transAxes, fontsize=9, va='top')
# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return plt, fig, ax


# [ML] Primary ROC from k-fold outputs (least biased performance estimate).
def save_kfold_roc(plot_dir: Path) -> float:
    # [ML] k-fold scores are less biased than train/test for this study because every event
    # has a score assigned by a model that did not see it during optimization.
# [Context] Supporting line for the active lvqq analysis stage.
    print('Loading k-fold scores...')
# [Context] Supporting line for the active lvqq analysis stage.
    df = pd.read_csv(MODEL_DIR / 'kfold_scores.csv')
# [Context] Supporting line for the active lvqq analysis stage.
    y = df['y_true']
# [Context] Supporting line for the active lvqq analysis stage.
    score = df['bdt_score']
# [Stats] Physics weights propagate cross-section and luminosity to training/fit observables.
    w = df['phys_weight'].astype(float)

# [ML] ROC metrics provide threshold-independent ranking quality under class imbalance.
    auc = roc_auc_score(y, score, sample_weight=w)
# [ML] ROC metrics provide threshold-independent ranking quality under class imbalance.
    fpr, tpr, _ = roc_curve(y, score, sample_weight=w)

# [Context] Supporting line for the active lvqq analysis stage.
    plt, fig, ax = make_axes()
# [Context] Supporting line for the active lvqq analysis stage.
    ax.plot(fpr, tpr, label=f'5-fold AUC = {auc:.4f}')
# [Context] Supporting line for the active lvqq analysis stage.
    ax.legend(loc='lower right')
# [ML] ROC metrics provide threshold-independent ranking quality under class imbalance.
    fig.savefig(plot_dir / 'roc_curve.png', dpi=150, bbox_inches='tight')
# [ML] ROC metrics provide threshold-independent ranking quality under class imbalance.
    fig.savefig(plot_dir / 'roc_curve.pdf', bbox_inches='tight')
# [Context] Supporting line for the active lvqq analysis stage.
    plt.close(fig)
# [Context] Supporting line for the active lvqq analysis stage.
    print(f'5-fold AUC: {auc:.4f}')
# [ML] ROC metrics provide threshold-independent ranking quality under class imbalance.
    print(f'Saved to {plot_dir}/roc_curve.{{png,pdf}}')
# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return float(auc)


# [ML] Optional train/test ROC to expose possible leakage or calibration shifts.
def save_split_diagnostic(plot_dir: Path) -> tuple[float, float]:
# [Context] Supporting line for the active lvqq analysis stage.
    print('Loading data for split diagnostic...')
# [Context] Supporting line for the active lvqq analysis stage.
    sig_df = read_samples(DEFAULT_TREEMAKER_DIR, DEFAULT_TREE_NAME,
# [Context] Supporting line for the active lvqq analysis stage.
                          SIGNAL_SAMPLES, ML_FEATURES, 1)
# [Context] Supporting line for the active lvqq analysis stage.
    bkg_df = read_samples(DEFAULT_TREEMAKER_DIR, DEFAULT_TREE_NAME,
# [Context] Supporting line for the active lvqq analysis stage.
                          BACKGROUND_SAMPLES, ML_FEATURES, 0)
# [Context] Supporting line for the active lvqq analysis stage.
    full_df = pd.concat([sig_df, bkg_df], ignore_index=True)

# [Context] Supporting line for the active lvqq analysis stage.
    available_features = [f for f in ML_FEATURES if f in full_df.columns]
# [Workflow] Configuration binding; this line defines a stable contract across modules.
    X = full_df[available_features].copy()
# [Context] Supporting line for the active lvqq analysis stage.
    y = full_df['label']
# [Stats] Physics weights propagate cross-section and luminosity to training/fit observables.
    w = full_df['phys_weight'].astype(float)

# [Context] Supporting line for the active lvqq analysis stage.
    if 'missingMass' in X.columns:
# [Context] Supporting line for the active lvqq analysis stage.
        X.loc[X['missingMass'] < -900, 'missingMass'] = 0.0

# [Context] Supporting line for the active lvqq analysis stage.
    indices = np.arange(len(X))
# [ML] Split data into non-overlapping train/validation/test sets to estimate generalization.
    idx_train, idx_test = train_test_split(
# [Context] Supporting line for the active lvqq analysis stage.
        indices, test_size=0.30, random_state=42, stratify=y,
# [Context] Supporting line for the active lvqq analysis stage.
    )
# [Context] Supporting line for the active lvqq analysis stage.
    X_train, X_test = X.iloc[idx_train], X.iloc[idx_test]
# [Context] Supporting line for the active lvqq analysis stage.
    y_train, y_test = y.iloc[idx_train], y.iloc[idx_test]
# [Context] Supporting line for the active lvqq analysis stage.
    w_phys_train, w_phys_test = w.iloc[idx_train], w.iloc[idx_test]

# [Context] Supporting line for the active lvqq analysis stage.
    print('Loading model...')
# [ML] Core estimator family (XGBoost) for non-linear kinematic separation.
    model = xgb.XGBClassifier()
# [Context] Supporting line for the active lvqq analysis stage.
    model.load_model(str(MODEL_DIR / 'xgboost_bdt.json'))

# [Context] Supporting line for the active lvqq analysis stage.
    train_score = model.predict_proba(X_train)[:, 1]
# [Context] Supporting line for the active lvqq analysis stage.
    test_score = model.predict_proba(X_test)[:, 1]

# [ML] ROC metrics provide threshold-independent ranking quality under class imbalance.
    train_auc = roc_auc_score(y_train, train_score, sample_weight=w_phys_train)
# [ML] ROC metrics provide threshold-independent ranking quality under class imbalance.
    test_auc = roc_auc_score(y_test, test_score, sample_weight=w_phys_test)

# [ML] ROC metrics provide threshold-independent ranking quality under class imbalance.
    fpr_test, tpr_test, _ = roc_curve(y_test, test_score, sample_weight=w_phys_test)
# [ML] ROC metrics provide threshold-independent ranking quality under class imbalance.
    fpr_train, tpr_train, _ = roc_curve(y_train, train_score, sample_weight=w_phys_train)

# [Context] Supporting line for the active lvqq analysis stage.
    plt, fig, ax = make_axes()
# [Context] Supporting line for the active lvqq analysis stage.
    ax.plot(fpr_test, tpr_test, label=f'Test AUC = {test_auc:.4f}')
# [Context] Supporting line for the active lvqq analysis stage.
    ax.plot(fpr_train, tpr_train, '--', label=f'Train AUC = {train_auc:.4f}')
# [Context] Supporting line for the active lvqq analysis stage.
    ax.legend(loc='lower right')
# [Workflow] Save inspection plots immediately after generation for review history.
    fig.savefig(plot_dir / 'roc_curve_split.png', dpi=150, bbox_inches='tight')
# [Workflow] Save inspection plots immediately after generation for review history.
    fig.savefig(plot_dir / 'roc_curve_split.pdf', bbox_inches='tight')
# [Context] Supporting line for the active lvqq analysis stage.
    plt.close(fig)
# [Context] Supporting line for the active lvqq analysis stage.
    print(f'Train AUC: {train_auc:.4f}')
# [Context] Supporting line for the active lvqq analysis stage.
    print(f'Test AUC:  {test_auc:.4f}')
# [Context] Supporting line for the active lvqq analysis stage.
    print(f'Saved to {plot_dir}/roc_curve_split.{{png,pdf}}')
# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return float(train_auc), float(test_auc)


# [Workflow] regenerate_roc.py function parse_args: modularize one operation for deterministic pipeline control.
def parse_args():
# [Context] Supporting line for the active lvqq analysis stage.
    parser = argparse.ArgumentParser(description=__doc__)
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument(
# [Context] Supporting line for the active lvqq analysis stage.
        "--with-split-diagnostic",
# [Context] Supporting line for the active lvqq analysis stage.
        action="store_true",
# [Context] Supporting line for the active lvqq analysis stage.
        help="Also regenerate the train/test ROC as roc_curve_split.{png,pdf}.",
# [Context] Supporting line for the active lvqq analysis stage.
    )
# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return parser.parse_args()

# [Workflow] Command entrypoint for ROC regeneration tasks.
def main():
# [Context] Supporting line for the active lvqq analysis stage.
    args = parse_args()
# [Context] Supporting line for the active lvqq analysis stage.
    plot_dir = MODEL_DIR / 'plots'
# [Context] Supporting line for the active lvqq analysis stage.
    plot_dir.mkdir(exist_ok=True)
# [Context] Supporting line for the active lvqq analysis stage.
    save_kfold_roc(plot_dir)
# [Context] Supporting line for the active lvqq analysis stage.
    if args.with_split_diagnostic:
# [Context] Supporting line for the active lvqq analysis stage.
        save_split_diagnostic(plot_dir)

# [Context] Supporting line for the active lvqq analysis stage.
if __name__ == '__main__':
# [Context] Supporting line for the active lvqq analysis stage.
    main()
