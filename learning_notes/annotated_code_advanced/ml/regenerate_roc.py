#!/usr/bin/env python3
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
"""Regenerate ROC plots for the BDT classifier.

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
By default this writes the paper ROC figure from the 5-fold cross-validated
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
scores used in the final fit. An optional diagnostic train/test ROC can also be
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
produced for development checks.
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
"""
# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
import argparse
# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
import sys
# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
from pathlib import Path
# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
import numpy as np
# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
import pandas as pd
# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
import xgboost as xgb
# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
from sklearn.metrics import roc_auc_score, roc_curve
# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
from sklearn.model_selection import train_test_split

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
THIS_DIR = Path(__file__).resolve().parent
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
ANALYSIS_DIR = THIS_DIR.parent
# [Workflow] Ensure repository-local imports (ml_config, helpers) resolve regardless of execution context.
sys.path.insert(0, str(ANALYSIS_DIR))

# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
from ml_config import (
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    BACKGROUND_SAMPLES, DEFAULT_MODEL_DIR, DEFAULT_TREE_NAME, DEFAULT_TREEMAKER_DIR,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ML_FEATURES, SIGNAL_SAMPLES,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
)

# Import sample info and reader from training script
# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
from train_xgboost_bdt import read_samples

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
MODEL_DIR = ANALYSIS_DIR / DEFAULT_MODEL_DIR

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def make_axes():
    # Plot
# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
    import matplotlib
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    matplotlib.use('Agg')
# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
    import matplotlib.pyplot as plt
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    fig, ax = plt.subplots(figsize=(6, 6))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.3)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ax.set_xlabel('False Positive Rate')
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ax.set_ylabel('True Positive Rate')
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ax.set_title('ROC Curve')
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ax.text(0.05, 0.97, r'$\mathbf{FCC\text{-}ee}$ Simulation',
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            transform=ax.transAxes, fontsize=10, va='top', fontstyle='italic')
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    ax.text(0.05, 0.91, r'$\sqrt{s}=240$ GeV, $10.8\,\mathrm{ab}^{-1}$',
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            transform=ax.transAxes, fontsize=9, va='top')
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    return plt, fig, ax


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def save_kfold_roc(plot_dir: Path) -> float:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print('Loading k-fold scores...')
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    df = pd.read_csv(MODEL_DIR / 'kfold_scores.csv')
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    y = df['y_true']
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    score = df['bdt_score']
# [Physics] Event weight setup: maps generated events to expected yields using cross section and integrated luminosity, with sample processing fraction correction.
    w = df['phys_weight'].astype(float)

# [ML] AUC / ROC are threshold-independent discrimination metrics; useful for checking class separation before relying on a fixed score cut in the fit.
    auc = roc_auc_score(y, score, sample_weight=w)
# [ML] AUC / ROC are threshold-independent discrimination metrics; useful for checking class separation before relying on a fixed score cut in the fit.
    fpr, tpr, _ = roc_curve(y, score, sample_weight=w)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    plt, fig, ax = make_axes()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ax.plot(fpr, tpr, label=f'5-fold AUC = {auc:.4f}')
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ax.legend(loc='lower right')
# [ML] AUC / ROC are threshold-independent discrimination metrics; useful for checking class separation before relying on a fixed score cut in the fit.
    fig.savefig(plot_dir / 'roc_curve.png', dpi=150, bbox_inches='tight')
# [ML] AUC / ROC are threshold-independent discrimination metrics; useful for checking class separation before relying on a fixed score cut in the fit.
    fig.savefig(plot_dir / 'roc_curve.pdf', bbox_inches='tight')
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    plt.close(fig)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print(f'5-fold AUC: {auc:.4f}')
# [ML] AUC / ROC are threshold-independent discrimination metrics; useful for checking class separation before relying on a fixed score cut in the fit.
    print(f'Saved to {plot_dir}/roc_curve.{{png,pdf}}')
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    return float(auc)


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def save_split_diagnostic(plot_dir: Path) -> tuple[float, float]:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print('Loading data for split diagnostic...')
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    sig_df = read_samples(DEFAULT_TREEMAKER_DIR, DEFAULT_TREE_NAME,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
                          SIGNAL_SAMPLES, ML_FEATURES, 1)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    bkg_df = read_samples(DEFAULT_TREEMAKER_DIR, DEFAULT_TREE_NAME,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
                          BACKGROUND_SAMPLES, ML_FEATURES, 0)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    full_df = pd.concat([sig_df, bkg_df], ignore_index=True)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    available_features = [f for f in ML_FEATURES if f in full_df.columns]
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    X = full_df[available_features].copy()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    y = full_df['label']
# [Physics] Event weight setup: maps generated events to expected yields using cross section and integrated luminosity, with sample processing fraction correction.
    w = full_df['phys_weight'].astype(float)

# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
    if 'missingMass' in X.columns:
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        X.loc[X['missingMass'] < -900, 'missingMass'] = 0.0

# [Data] Convert event arrays into structured numeric frames for vectorized cuts, weighting, and sklearn-compatible training matrices.
    indices = np.arange(len(X))
# [ML] Explicitly stratified splits preserve class fractions and protect against label imbalance shifts in training/evaluation partitions.
    idx_train, idx_test = train_test_split(
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        indices, test_size=0.30, random_state=42, stratify=y,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    )
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    X_train, X_test = X.iloc[idx_train], X.iloc[idx_test]
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    y_train, y_test = y.iloc[idx_train], y.iloc[idx_test]
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    w_phys_train, w_phys_test = w.iloc[idx_train], w.iloc[idx_test]

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print('Loading model...')
# [ML] Core model operation is tree-based boosted classification; this captures non-linear kinematic correlations in lvqq features.
    model = xgb.XGBClassifier()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    model.load_model(str(MODEL_DIR / 'xgboost_bdt.json'))

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    train_score = model.predict_proba(X_train)[:, 1]
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    test_score = model.predict_proba(X_test)[:, 1]

# [ML] AUC / ROC are threshold-independent discrimination metrics; useful for checking class separation before relying on a fixed score cut in the fit.
    train_auc = roc_auc_score(y_train, train_score, sample_weight=w_phys_train)
# [ML] AUC / ROC are threshold-independent discrimination metrics; useful for checking class separation before relying on a fixed score cut in the fit.
    test_auc = roc_auc_score(y_test, test_score, sample_weight=w_phys_test)

# [ML] AUC / ROC are threshold-independent discrimination metrics; useful for checking class separation before relying on a fixed score cut in the fit.
    fpr_test, tpr_test, _ = roc_curve(y_test, test_score, sample_weight=w_phys_test)
# [ML] AUC / ROC are threshold-independent discrimination metrics; useful for checking class separation before relying on a fixed score cut in the fit.
    fpr_train, tpr_train, _ = roc_curve(y_train, train_score, sample_weight=w_phys_train)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    plt, fig, ax = make_axes()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ax.plot(fpr_test, tpr_test, label=f'Test AUC = {test_auc:.4f}')
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ax.plot(fpr_train, tpr_train, '--', label=f'Train AUC = {train_auc:.4f}')
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ax.legend(loc='lower right')
# [ML] AUC / ROC are threshold-independent discrimination metrics; useful for checking class separation before relying on a fixed score cut in the fit.
    fig.savefig(plot_dir / 'roc_curve_split.png', dpi=150, bbox_inches='tight')
# [ML] AUC / ROC are threshold-independent discrimination metrics; useful for checking class separation before relying on a fixed score cut in the fit.
    fig.savefig(plot_dir / 'roc_curve_split.pdf', bbox_inches='tight')
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    plt.close(fig)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print(f'Train AUC: {train_auc:.4f}')
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print(f'Test AUC:  {test_auc:.4f}')
# [ML] AUC / ROC are threshold-independent discrimination metrics; useful for checking class separation before relying on a fixed score cut in the fit.
    print(f'Saved to {plot_dir}/roc_curve_split.{{png,pdf}}')
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    return float(train_auc), float(test_auc)


# [Workflow] Argument parser: expose knobs for reproducibility (seed), split fractions, model options, and outputs.
def parse_args():
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    parser = argparse.ArgumentParser(description=__doc__)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    parser.add_argument(
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "--with-split-diagnostic",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        action="store_true",
# [ML] AUC / ROC are threshold-independent discrimination metrics; useful for checking class separation before relying on a fixed score cut in the fit.
        help="Also regenerate the train/test ROC as roc_curve_split.{png,pdf}.",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    )
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    return parser.parse_args()

# [Workflow] Main orchestrator for this module; executes the full chain for this script only.
def main():
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    args = parse_args()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    plot_dir = MODEL_DIR / 'plots'
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    plot_dir.mkdir(exist_ok=True)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    save_kfold_roc(plot_dir)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if args.with_split_diagnostic:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        save_split_diagnostic(plot_dir)

# [Entry] Module entry point for direct execution from CLI.
if __name__ == '__main__':
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    main()
