#!/usr/bin/env python3
"""Regenerate ROC plots for the BDT classifier.

By default this writes the paper ROC figure from the 5-fold cross-validated
scores used in the final fit. An optional diagnostic train/test ROC can also be
produced for development checks.
"""
import argparse
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split

THIS_DIR = Path(__file__).resolve().parent
ANALYSIS_DIR = THIS_DIR.parent
sys.path.insert(0, str(ANALYSIS_DIR))

from ml_config import (
    BACKGROUND_SAMPLES, DEFAULT_MODEL_DIR, DEFAULT_TREE_NAME, DEFAULT_TREEMAKER_DIR,
    ML_FEATURES, SIGNAL_SAMPLES,
)

# Import sample info and reader from training script
from train_xgboost_bdt import read_samples

MODEL_DIR = ANALYSIS_DIR / DEFAULT_MODEL_DIR

def make_axes():
    # Plot
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.3)
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title('ROC Curve')
    ax.text(0.05, 0.97, r'$\mathbf{FCC\text{-}ee}$ Simulation',
            transform=ax.transAxes, fontsize=10, va='top', fontstyle='italic')
    ax.text(0.05, 0.91, r'$\sqrt{s}=240$ GeV, $10.8\,\mathrm{ab}^{-1}$',
            transform=ax.transAxes, fontsize=9, va='top')
    return plt, fig, ax


def save_kfold_roc(plot_dir: Path) -> float:
    print('Loading k-fold scores...')
    df = pd.read_csv(MODEL_DIR / 'kfold_scores.csv')
    y = df['y_true']
    score = df['bdt_score']
    w = df['phys_weight'].astype(float)

    auc = roc_auc_score(y, score, sample_weight=w)
    fpr, tpr, _ = roc_curve(y, score, sample_weight=w)

    plt, fig, ax = make_axes()
    ax.plot(fpr, tpr, label=f'5-fold AUC = {auc:.4f}')
    ax.legend(loc='lower right')
    fig.savefig(plot_dir / 'roc_curve.png', dpi=150, bbox_inches='tight')
    fig.savefig(plot_dir / 'roc_curve.pdf', bbox_inches='tight')
    plt.close(fig)
    print(f'5-fold AUC: {auc:.4f}')
    print(f'Saved to {plot_dir}/roc_curve.{{png,pdf}}')
    return float(auc)


def save_split_diagnostic(plot_dir: Path) -> tuple[float, float]:
    print('Loading data for split diagnostic...')
    sig_df = read_samples(DEFAULT_TREEMAKER_DIR, DEFAULT_TREE_NAME,
                          SIGNAL_SAMPLES, ML_FEATURES, 1)
    bkg_df = read_samples(DEFAULT_TREEMAKER_DIR, DEFAULT_TREE_NAME,
                          BACKGROUND_SAMPLES, ML_FEATURES, 0)
    full_df = pd.concat([sig_df, bkg_df], ignore_index=True)

    available_features = [f for f in ML_FEATURES if f in full_df.columns]
    X = full_df[available_features].copy()
    y = full_df['label']
    w = full_df['phys_weight'].astype(float)

    if 'missingMass' in X.columns:
        X.loc[X['missingMass'] < -900, 'missingMass'] = 0.0

    indices = np.arange(len(X))
    idx_train, idx_test = train_test_split(
        indices, test_size=0.30, random_state=42, stratify=y,
    )
    X_train, X_test = X.iloc[idx_train], X.iloc[idx_test]
    y_train, y_test = y.iloc[idx_train], y.iloc[idx_test]
    w_phys_train, w_phys_test = w.iloc[idx_train], w.iloc[idx_test]

    print('Loading model...')
    model = xgb.XGBClassifier()
    model.load_model(str(MODEL_DIR / 'xgboost_bdt.json'))

    train_score = model.predict_proba(X_train)[:, 1]
    test_score = model.predict_proba(X_test)[:, 1]

    train_auc = roc_auc_score(y_train, train_score, sample_weight=w_phys_train)
    test_auc = roc_auc_score(y_test, test_score, sample_weight=w_phys_test)

    fpr_test, tpr_test, _ = roc_curve(y_test, test_score, sample_weight=w_phys_test)
    fpr_train, tpr_train, _ = roc_curve(y_train, train_score, sample_weight=w_phys_train)

    plt, fig, ax = make_axes()
    ax.plot(fpr_test, tpr_test, label=f'Test AUC = {test_auc:.4f}')
    ax.plot(fpr_train, tpr_train, '--', label=f'Train AUC = {train_auc:.4f}')
    ax.legend(loc='lower right')
    fig.savefig(plot_dir / 'roc_curve_split.png', dpi=150, bbox_inches='tight')
    fig.savefig(plot_dir / 'roc_curve_split.pdf', bbox_inches='tight')
    plt.close(fig)
    print(f'Train AUC: {train_auc:.4f}')
    print(f'Test AUC:  {test_auc:.4f}')
    print(f'Saved to {plot_dir}/roc_curve_split.{{png,pdf}}')
    return float(train_auc), float(test_auc)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--with-split-diagnostic",
        action="store_true",
        help="Also regenerate the train/test ROC as roc_curve_split.{png,pdf}.",
    )
    return parser.parse_args()

def main():
    args = parse_args()
    plot_dir = MODEL_DIR / 'plots'
    plot_dir.mkdir(exist_ok=True)
    save_kfold_roc(plot_dir)
    if args.with_split_diagnostic:
        save_split_diagnostic(plot_dir)

if __name__ == '__main__':
    main()
