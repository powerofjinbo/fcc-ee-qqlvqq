#!/usr/bin/env python3
"""Regenerate the train/test BDT score distribution plot from an existing model."""

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split

from train_xgboost_bdt import (
    BACKGROUND_SAMPLES,
    DEFAULT_MODEL_DIR,
    DEFAULT_TREEMAKER_DIR,
    DEFAULT_TREE_NAME,
    SIGNAL_SAMPLES,
    normalize_class_weights,
    read_samples,
)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", default=DEFAULT_TREEMAKER_DIR)
    parser.add_argument("--model-dir", default=DEFAULT_MODEL_DIR)
    parser.add_argument("--tree-name", default=DEFAULT_TREE_NAME)
    parser.add_argument("--test-size", type=float, default=0.30)
    parser.add_argument("--random-state", type=int, default=42)
    return parser.parse_args()


def add_fcc_label(ax, x=0.35, y=0.97):
    ax.text(
        x, y, r"$\mathbf{FCC\text{-}ee}$ Simulation",
        transform=ax.transAxes, fontsize=10, va="top", fontstyle="italic",
    )
    ax.text(
        x, y - 0.06, r"$\sqrt{s}=240$ GeV, $10.8\,\mathrm{ab}^{-1}$",
        transform=ax.transAxes, fontsize=9, va="top",
    )


def main():
    args = parse_args()
    model_dir = Path(args.model_dir)
    metrics_path = model_dir / "training_metrics.json"
    model_path = model_dir / "xgboost_bdt.json"
    plot_dir = model_dir / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)

    with metrics_path.open() as handle:
        metrics = json.load(handle)

    features = metrics["features"]

    print("=== Reloading samples for overtraining plot ===")
    print("Signal:")
    sig_df = read_samples(args.input_dir, args.tree_name, SIGNAL_SAMPLES, features, 1)
    print("Background:")
    bkg_df = read_samples(args.input_dir, args.tree_name, BACKGROUND_SAMPLES, features, 0)

    import pandas as pd
    full_df = pd.concat([sig_df, bkg_df], ignore_index=True)

    X = full_df[features].copy()
    y = full_df["label"]
    w_phys = full_df["phys_weight"].astype(float)

    if "missingMass" in X.columns:
        n_sentinel = (X["missingMass"] < -900).sum()
        if n_sentinel > 0:
            print(f"[fix] Replacing {n_sentinel} missingMass sentinel values (-999) with 0")
            X.loc[X["missingMass"] < -900, "missingMass"] = 0.0

    normalize_class_weights(w_phys, y)

    indices = np.arange(len(X))
    idx_train, idx_test = train_test_split(
        indices,
        test_size=args.test_size,
        random_state=args.random_state,
        stratify=y,
    )

    X_train, X_test = X.iloc[idx_train], X.iloc[idx_test]
    y_train, y_test = y.iloc[idx_train], y.iloc[idx_test]
    w_phys_train, w_phys_test = w_phys.iloc[idx_train], w_phys.iloc[idx_test]

    model = xgb.XGBClassifier()
    model.load_model(model_path)

    train_score = model.predict_proba(X_train)[:, 1]
    test_score = model.predict_proba(X_test)[:, 1]

    # Match the final profile-likelihood fit binning for easier comparison.
    bins = np.linspace(0, 1, 21)
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.hist(
        train_score[y_train == 1],
        bins=bins,
        weights=w_phys_train[y_train == 1],
        density=True,
        alpha=0.5,
        label="Signal (train)",
        color="blue",
        histtype="stepfilled",
    )
    ax.hist(
        train_score[y_train == 0],
        bins=bins,
        weights=w_phys_train[y_train == 0],
        density=True,
        alpha=0.5,
        label="Background (train)",
        color="red",
        histtype="stepfilled",
    )

    h_sig, _ = np.histogram(
        test_score[y_test == 1],
        bins=bins,
        weights=w_phys_test[y_test == 1],
        density=True,
    )
    h_bkg, _ = np.histogram(
        test_score[y_test == 0],
        bins=bins,
        weights=w_phys_test[y_test == 0],
        density=True,
    )
    centers = 0.5 * (bins[:-1] + bins[1:])

    ax.scatter(centers, h_sig, marker="o", s=20, color="blue", label="Signal (test)", zorder=5)
    ax.scatter(centers, h_bkg, marker="o", s=20, color="red", label="Background (test)", zorder=5)

    ax.set_xlabel("BDT Score")
    ax.set_ylabel("Normalised (weighted)")
    ax.set_title("BDT Score Distributions")
    ax.legend(fontsize=9)
    add_fcc_label(ax)

    fig.savefig(plot_dir / "overtraining_check.png", dpi=150, bbox_inches="tight")
    fig.savefig(plot_dir / "overtraining_check.pdf", bbox_inches="tight")
    plt.close(fig)

    print(f"Saved to {plot_dir / 'overtraining_check.pdf'}")


if __name__ == "__main__":
    main()
