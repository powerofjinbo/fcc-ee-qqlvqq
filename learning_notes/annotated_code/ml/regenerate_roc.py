# Annotated rewrite generated for: ml/regenerate_roc.py
# L1 [Original comment]: #!/usr/bin/env python3
#!/usr/bin/env python3
# L2 [Executable statement]: """Regenerate ROC plots for the BDT classifier.
"""Regenerate ROC plots for the BDT classifier.
# L3 [Blank separator]: 

# L4 [Executable statement]: By default this writes the paper ROC figure from the 5-fold cross-validated
By default this writes the paper ROC figure from the 5-fold cross-validated
# L5 [Executable statement]: scores used in the final fit. An optional diagnostic train/test ROC can also be
scores used in the final fit. An optional diagnostic train/test ROC can also be
# L6 [Executable statement]: produced for development checks.
produced for development checks.
# L7 [Executable statement]: """
"""
# L8 [Import statement]: import argparse
import argparse
# L9 [Import statement]: import sys
import sys
# L10 [Import statement]: from pathlib import Path
from pathlib import Path
# L11 [Import statement]: import numpy as np
import numpy as np
# L12 [Import statement]: import pandas as pd
import pandas as pd
# L13 [Import statement]: import xgboost as xgb
import xgboost as xgb
# L14 [Import statement]: from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.metrics import roc_auc_score, roc_curve
# L15 [Import statement]: from sklearn.model_selection import train_test_split
from sklearn.model_selection import train_test_split
# L16 [Blank separator]: 

# L17 [Executable statement]: THIS_DIR = Path(__file__).resolve().parent
THIS_DIR = Path(__file__).resolve().parent
# L18 [Executable statement]: ANALYSIS_DIR = THIS_DIR.parent
ANALYSIS_DIR = THIS_DIR.parent
# L19 [Executable statement]: sys.path.insert(0, str(ANALYSIS_DIR))
sys.path.insert(0, str(ANALYSIS_DIR))
# L20 [Blank separator]: 

# L21 [Import statement]: from ml_config import (
from ml_config import (
# L22 [Executable statement]:     BACKGROUND_SAMPLES, DEFAULT_MODEL_DIR, DEFAULT_TREE_NAME, DEFAULT_TREEMAKER_DIR,
    BACKGROUND_SAMPLES, DEFAULT_MODEL_DIR, DEFAULT_TREE_NAME, DEFAULT_TREEMAKER_DIR,
# L23 [Executable statement]:     ML_FEATURES, SIGNAL_SAMPLES,
    ML_FEATURES, SIGNAL_SAMPLES,
# L24 [Executable statement]: )
)
# L25 [Blank separator]: 

# L26 [Original comment]: # Import sample info and reader from training script
# Import sample info and reader from training script
# L27 [Import statement]: from train_xgboost_bdt import read_samples
from train_xgboost_bdt import read_samples
# L28 [Blank separator]: 

# L29 [Executable statement]: MODEL_DIR = ANALYSIS_DIR / DEFAULT_MODEL_DIR
MODEL_DIR = ANALYSIS_DIR / DEFAULT_MODEL_DIR
# L30 [Blank separator]: 

# L31 [Function definition]: def make_axes():
def make_axes():
# L32 [Original comment]:     # Plot
    # Plot
# L33 [Import statement]:     import matplotlib
    import matplotlib
# L34 [Executable statement]:     matplotlib.use('Agg')
    matplotlib.use('Agg')
# L35 [Import statement]:     import matplotlib.pyplot as plt
    import matplotlib.pyplot as plt
# L36 [Executable statement]:     fig, ax = plt.subplots(figsize=(6, 6))
    fig, ax = plt.subplots(figsize=(6, 6))
# L37 [Executable statement]:     ax.plot([0, 1], [0, 1], 'k--', alpha=0.3)
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.3)
# L38 [Executable statement]:     ax.set_xlabel('False Positive Rate')
    ax.set_xlabel('False Positive Rate')
# L39 [Executable statement]:     ax.set_ylabel('True Positive Rate')
    ax.set_ylabel('True Positive Rate')
# L40 [Executable statement]:     ax.set_title('ROC Curve')
    ax.set_title('ROC Curve')
# L41 [Executable statement]:     ax.text(0.05, 0.97, r'$\mathbf{FCC\text{-}ee}$ Simulation',
    ax.text(0.05, 0.97, r'$\mathbf{FCC\text{-}ee}$ Simulation',
# L42 [Executable statement]:             transform=ax.transAxes, fontsize=10, va='top', fontstyle='italic')
            transform=ax.transAxes, fontsize=10, va='top', fontstyle='italic')
# L43 [Executable statement]:     ax.text(0.05, 0.91, r'$\sqrt{s}=240$ GeV, $10.8\,\mathrm{ab}^{-1}$',
    ax.text(0.05, 0.91, r'$\sqrt{s}=240$ GeV, $10.8\,\mathrm{ab}^{-1}$',
# L44 [Executable statement]:             transform=ax.transAxes, fontsize=9, va='top')
            transform=ax.transAxes, fontsize=9, va='top')
# L45 [Function return]:     return plt, fig, ax
    return plt, fig, ax
# L46 [Blank separator]: 

# L47 [Blank separator]: 

# L48 [Function definition]: def save_kfold_roc(plot_dir: Path) -> float:
def save_kfold_roc(plot_dir: Path) -> float:
# L49 [Runtime log output]:     print('Loading k-fold scores...')
    print('Loading k-fold scores...')
# L50 [Executable statement]:     df = pd.read_csv(MODEL_DIR / 'kfold_scores.csv')
    df = pd.read_csv(MODEL_DIR / 'kfold_scores.csv')
# L51 [Executable statement]:     y = df['y_true']
    y = df['y_true']
# L52 [Executable statement]:     score = df['bdt_score']
    score = df['bdt_score']
# L53 [Executable statement]:     w = df['phys_weight'].astype(float)
    w = df['phys_weight'].astype(float)
# L54 [Blank separator]: 

# L55 [Executable statement]:     auc = roc_auc_score(y, score, sample_weight=w)
    auc = roc_auc_score(y, score, sample_weight=w)
# L56 [Executable statement]:     fpr, tpr, _ = roc_curve(y, score, sample_weight=w)
    fpr, tpr, _ = roc_curve(y, score, sample_weight=w)
# L57 [Blank separator]: 

# L58 [Executable statement]:     plt, fig, ax = make_axes()
    plt, fig, ax = make_axes()
# L59 [Executable statement]:     ax.plot(fpr, tpr, label=f'5-fold AUC = {auc:.4f}')
    ax.plot(fpr, tpr, label=f'5-fold AUC = {auc:.4f}')
# L60 [Executable statement]:     ax.legend(loc='lower right')
    ax.legend(loc='lower right')
# L61 [Executable statement]:     fig.savefig(plot_dir / 'roc_curve.png', dpi=150, bbox_inches='tight')
    fig.savefig(plot_dir / 'roc_curve.png', dpi=150, bbox_inches='tight')
# L62 [Executable statement]:     fig.savefig(plot_dir / 'roc_curve.pdf', bbox_inches='tight')
    fig.savefig(plot_dir / 'roc_curve.pdf', bbox_inches='tight')
# L63 [Executable statement]:     plt.close(fig)
    plt.close(fig)
# L64 [Runtime log output]:     print(f'5-fold AUC: {auc:.4f}')
    print(f'5-fold AUC: {auc:.4f}')
# L65 [Runtime log output]:     print(f'Saved to {plot_dir}/roc_curve.{{png,pdf}}')
    print(f'Saved to {plot_dir}/roc_curve.{{png,pdf}}')
# L66 [Function return]:     return float(auc)
    return float(auc)
# L67 [Blank separator]: 

# L68 [Blank separator]: 

# L69 [Function definition]: def save_split_diagnostic(plot_dir: Path) -> tuple[float, float]:
def save_split_diagnostic(plot_dir: Path) -> tuple[float, float]:
# L70 [Runtime log output]:     print('Loading data for split diagnostic...')
    print('Loading data for split diagnostic...')
# L71 [Executable statement]:     sig_df = read_samples(DEFAULT_TREEMAKER_DIR, DEFAULT_TREE_NAME,
    sig_df = read_samples(DEFAULT_TREEMAKER_DIR, DEFAULT_TREE_NAME,
# L72 [Executable statement]:                           SIGNAL_SAMPLES, ML_FEATURES, 1)
                          SIGNAL_SAMPLES, ML_FEATURES, 1)
# L73 [Executable statement]:     bkg_df = read_samples(DEFAULT_TREEMAKER_DIR, DEFAULT_TREE_NAME,
    bkg_df = read_samples(DEFAULT_TREEMAKER_DIR, DEFAULT_TREE_NAME,
# L74 [Executable statement]:                           BACKGROUND_SAMPLES, ML_FEATURES, 0)
                          BACKGROUND_SAMPLES, ML_FEATURES, 0)
# L75 [Executable statement]:     full_df = pd.concat([sig_df, bkg_df], ignore_index=True)
    full_df = pd.concat([sig_df, bkg_df], ignore_index=True)
# L76 [Blank separator]: 

# L77 [Executable statement]:     available_features = [f for f in ML_FEATURES if f in full_df.columns]
    available_features = [f for f in ML_FEATURES if f in full_df.columns]
# L78 [Executable statement]:     X = full_df[available_features].copy()
    X = full_df[available_features].copy()
# L79 [Executable statement]:     y = full_df['label']
    y = full_df['label']
# L80 [Executable statement]:     w = full_df['phys_weight'].astype(float)
    w = full_df['phys_weight'].astype(float)
# L81 [Blank separator]: 

# L82 [Conditional block]:     if 'missingMass' in X.columns:
    if 'missingMass' in X.columns:
# L83 [Executable statement]:         X.loc[X['missingMass'] < -900, 'missingMass'] = 0.0
        X.loc[X['missingMass'] < -900, 'missingMass'] = 0.0
# L84 [Blank separator]: 

# L85 [Executable statement]:     indices = np.arange(len(X))
    indices = np.arange(len(X))
# L86 [Executable statement]:     idx_train, idx_test = train_test_split(
    idx_train, idx_test = train_test_split(
# L87 [Executable statement]:         indices, test_size=0.30, random_state=42, stratify=y,
        indices, test_size=0.30, random_state=42, stratify=y,
# L88 [Executable statement]:     )
    )
# L89 [Executable statement]:     X_train, X_test = X.iloc[idx_train], X.iloc[idx_test]
    X_train, X_test = X.iloc[idx_train], X.iloc[idx_test]
# L90 [Executable statement]:     y_train, y_test = y.iloc[idx_train], y.iloc[idx_test]
    y_train, y_test = y.iloc[idx_train], y.iloc[idx_test]
# L91 [Executable statement]:     w_phys_train, w_phys_test = w.iloc[idx_train], w.iloc[idx_test]
    w_phys_train, w_phys_test = w.iloc[idx_train], w.iloc[idx_test]
# L92 [Blank separator]: 

# L93 [Runtime log output]:     print('Loading model...')
    print('Loading model...')
# L94 [Executable statement]:     model = xgb.XGBClassifier()
    model = xgb.XGBClassifier()
# L95 [Executable statement]:     model.load_model(str(MODEL_DIR / 'xgboost_bdt.json'))
    model.load_model(str(MODEL_DIR / 'xgboost_bdt.json'))
# L96 [Blank separator]: 

# L97 [Executable statement]:     train_score = model.predict_proba(X_train)[:, 1]
    train_score = model.predict_proba(X_train)[:, 1]
# L98 [Executable statement]:     test_score = model.predict_proba(X_test)[:, 1]
    test_score = model.predict_proba(X_test)[:, 1]
# L99 [Blank separator]: 

# L100 [Executable statement]:     train_auc = roc_auc_score(y_train, train_score, sample_weight=w_phys_train)
    train_auc = roc_auc_score(y_train, train_score, sample_weight=w_phys_train)
# L101 [Executable statement]:     test_auc = roc_auc_score(y_test, test_score, sample_weight=w_phys_test)
    test_auc = roc_auc_score(y_test, test_score, sample_weight=w_phys_test)
# L102 [Blank separator]: 

# L103 [Executable statement]:     fpr_test, tpr_test, _ = roc_curve(y_test, test_score, sample_weight=w_phys_test)
    fpr_test, tpr_test, _ = roc_curve(y_test, test_score, sample_weight=w_phys_test)
# L104 [Executable statement]:     fpr_train, tpr_train, _ = roc_curve(y_train, train_score, sample_weight=w_phys_train)
    fpr_train, tpr_train, _ = roc_curve(y_train, train_score, sample_weight=w_phys_train)
# L105 [Blank separator]: 

# L106 [Executable statement]:     plt, fig, ax = make_axes()
    plt, fig, ax = make_axes()
# L107 [Executable statement]:     ax.plot(fpr_test, tpr_test, label=f'Test AUC = {test_auc:.4f}')
    ax.plot(fpr_test, tpr_test, label=f'Test AUC = {test_auc:.4f}')
# L108 [Executable statement]:     ax.plot(fpr_train, tpr_train, '--', label=f'Train AUC = {train_auc:.4f}')
    ax.plot(fpr_train, tpr_train, '--', label=f'Train AUC = {train_auc:.4f}')
# L109 [Executable statement]:     ax.legend(loc='lower right')
    ax.legend(loc='lower right')
# L110 [Executable statement]:     fig.savefig(plot_dir / 'roc_curve_split.png', dpi=150, bbox_inches='tight')
    fig.savefig(plot_dir / 'roc_curve_split.png', dpi=150, bbox_inches='tight')
# L111 [Executable statement]:     fig.savefig(plot_dir / 'roc_curve_split.pdf', bbox_inches='tight')
    fig.savefig(plot_dir / 'roc_curve_split.pdf', bbox_inches='tight')
# L112 [Executable statement]:     plt.close(fig)
    plt.close(fig)
# L113 [Runtime log output]:     print(f'Train AUC: {train_auc:.4f}')
    print(f'Train AUC: {train_auc:.4f}')
# L114 [Runtime log output]:     print(f'Test AUC:  {test_auc:.4f}')
    print(f'Test AUC:  {test_auc:.4f}')
# L115 [Runtime log output]:     print(f'Saved to {plot_dir}/roc_curve_split.{{png,pdf}}')
    print(f'Saved to {plot_dir}/roc_curve_split.{{png,pdf}}')
# L116 [Function return]:     return float(train_auc), float(test_auc)
    return float(train_auc), float(test_auc)
# L117 [Blank separator]: 

# L118 [Blank separator]: 

# L119 [Function definition]: def parse_args():
def parse_args():
# L120 [Executable statement]:     parser = argparse.ArgumentParser(description=__doc__)
    parser = argparse.ArgumentParser(description=__doc__)
# L121 [Executable statement]:     parser.add_argument(
    parser.add_argument(
# L122 [Executable statement]:         "--with-split-diagnostic",
        "--with-split-diagnostic",
# L123 [Executable statement]:         action="store_true",
        action="store_true",
# L124 [Executable statement]:         help="Also regenerate the train/test ROC as roc_curve_split.{png,pdf}.",
        help="Also regenerate the train/test ROC as roc_curve_split.{png,pdf}.",
# L125 [Executable statement]:     )
    )
# L126 [Function return]:     return parser.parse_args()
    return parser.parse_args()
# L127 [Blank separator]: 

# L128 [Function definition]: def main():
def main():
# L129 [Executable statement]:     args = parse_args()
    args = parse_args()
# L130 [Executable statement]:     plot_dir = MODEL_DIR / 'plots'
    plot_dir = MODEL_DIR / 'plots'
# L131 [Executable statement]:     plot_dir.mkdir(exist_ok=True)
    plot_dir.mkdir(exist_ok=True)
# L132 [Executable statement]:     save_kfold_roc(plot_dir)
    save_kfold_roc(plot_dir)
# L133 [Conditional block]:     if args.with_split_diagnostic:
    if args.with_split_diagnostic:
# L134 [Executable statement]:         save_split_diagnostic(plot_dir)
        save_split_diagnostic(plot_dir)
# L135 [Blank separator]: 

# L136 [Conditional block]: if __name__ == '__main__':
if __name__ == '__main__':
# L137 [Executable statement]:     main()
    main()
