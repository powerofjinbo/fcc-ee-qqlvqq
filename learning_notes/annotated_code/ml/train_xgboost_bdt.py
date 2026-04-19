# Annotated rewrite generated for: ml/train_xgboost_bdt.py
# L1 [Original comment]: #!/usr/bin/env python3
#!/usr/bin/env python3
# L2 [Executable statement]: """Train an XGBoost BDT for the lvqq analysis from FCCAnalyses treemaker ntuples.
"""Train an XGBoost BDT for the lvqq analysis from FCCAnalyses treemaker ntuples.
# L3 [Blank separator]: 

# L4 [Executable statement]: v3 improvements (ML specialist review fixes):
v3 improvements (ML specialist review fixes):
# L5 [Executable statement]: - Physics-correct event weights (lumi * xsec / ngen)
- Physics-correct event weights (lumi * xsec / ngen)
# L6 [Executable statement]: - Normalized class weights for balanced learning
- Normalized class weights for balanced learning
# L7 [Executable statement]: - Extended hyperparameter grid search (incl. min_child_weight, subsample)
- Extended hyperparameter grid search (incl. min_child_weight, subsample)
# L8 [Executable statement]: - Early stopping in both grid search and final training
- Early stopping in both grid search and final training
# L9 [Executable statement]: - Weighted KS overtraining test (binned chi2)
- Weighted KS overtraining test (binned chi2)
# L10 [Executable statement]: - missingMass sentinel value handling
- missingMass sentinel value handling
# L11 [Executable statement]: - Background sculpting diagnostic (BDT score vs Hcand_m)
- Background sculpting diagnostic (BDT score vs Hcand_m)
# L12 [Executable statement]: - Per-sample score distributions
- Per-sample score distributions
# L13 [Executable statement]: - Training history saved (evals_result)
- Training history saved (evals_result)
# L14 [Executable statement]: - Diagnostic plots (ROC, feature importance, BDT score, overtraining, sculpting)
- Diagnostic plots (ROC, feature importance, BDT score, overtraining, sculpting)
# L15 [Executable statement]: """
"""
# L16 [Blank separator]: 

# L17 [Import statement]: import argparse
import argparse
# L18 [Import statement]: import json
import json
# L19 [Import statement]: import sys
import sys
# L20 [Import statement]: from pathlib import Path
from pathlib import Path
# L21 [Import statement]: from itertools import product
from itertools import product
# L22 [Blank separator]: 

# L23 [Import statement]: import numpy as np
import numpy as np
# L24 [Import statement]: import pandas as pd
import pandas as pd
# L25 [Import statement]: import uproot
import uproot
# L26 [Import statement]: import xgboost as xgb
import xgboost as xgb
# L27 [Import statement]: from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.metrics import roc_auc_score, roc_curve
# L28 [Import statement]: from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.model_selection import train_test_split, StratifiedKFold
# L29 [Import statement]: from scipy.stats import ks_2samp
from scipy.stats import ks_2samp
# L30 [Blank separator]: 

# L31 [Executable statement]: THIS_DIR = Path(__file__).resolve().parent
THIS_DIR = Path(__file__).resolve().parent
# L32 [Executable statement]: ANALYSIS_DIR = THIS_DIR.parent
ANALYSIS_DIR = THIS_DIR.parent
# L33 [Executable statement]: sys.path.insert(0, str(ANALYSIS_DIR))
sys.path.insert(0, str(ANALYSIS_DIR))
# L34 [Blank separator]: 

# L35 [Import statement]: from ml_config import (
from ml_config import (
# L36 [Executable statement]:     BACKGROUND_FRACTIONS,
    BACKGROUND_FRACTIONS,
# L37 [Executable statement]:     BACKGROUND_SAMPLES,
    BACKGROUND_SAMPLES,
# L38 [Executable statement]:     DEFAULT_MODEL_DIR,
    DEFAULT_MODEL_DIR,
# L39 [Executable statement]:     DEFAULT_TREE_NAME,
    DEFAULT_TREE_NAME,
# L40 [Executable statement]:     DEFAULT_TREEMAKER_DIR,
    DEFAULT_TREEMAKER_DIR,
# L41 [Executable statement]:     ML_FEATURES,
    ML_FEATURES,
# L42 [Executable statement]:     SAMPLE_PROCESSING_FRACTIONS,
    SAMPLE_PROCESSING_FRACTIONS,
# L43 [Executable statement]:     SIGNAL_SAMPLES,
    SIGNAL_SAMPLES,
# L44 [Executable statement]: )
)
# L45 [Blank separator]: 

# L46 [Original comment]: # Cross-sections [pb], total generated events, and processing fraction.
# Cross-sections [pb], total generated events, and processing fraction.
# L47 [Original comment]: # Weight = lumi * xsec / (ngen * fraction) to correctly account for
# Weight = lumi * xsec / (ngen * fraction) to correctly account for
# L48 [Original comment]: # only processing a subset of generated events.
# only processing a subset of generated events.
# L49 [Executable statement]: SAMPLE_INFO = {
SAMPLE_INFO = {
# L50 [Original comment]:     # Signal (fraction=1, all events processed)
    # Signal (fraction=1, all events processed)
# L51 [Executable statement]:     "wzp6_ee_qqH_HWW_ecm240": {"xsec": 0.01140, "ngen": 1100000, "fraction": 1.0},
    "wzp6_ee_qqH_HWW_ecm240": {"xsec": 0.01140, "ngen": 1100000, "fraction": 1.0},
# L52 [Executable statement]:     "wzp6_ee_bbH_HWW_ecm240": {"xsec": 0.006350, "ngen": 1000000, "fraction": 1.0},
    "wzp6_ee_bbH_HWW_ecm240": {"xsec": 0.006350, "ngen": 1000000, "fraction": 1.0},
# L53 [Executable statement]:     "wzp6_ee_ccH_HWW_ecm240": {"xsec": 0.004988, "ngen": 1200000, "fraction": 1.0},
    "wzp6_ee_ccH_HWW_ecm240": {"xsec": 0.004988, "ngen": 1200000, "fraction": 1.0},
# L54 [Executable statement]:     "wzp6_ee_ssH_HWW_ecm240": {"xsec": 0.006403, "ngen": 1200000, "fraction": 1.0},
    "wzp6_ee_ssH_HWW_ecm240": {"xsec": 0.006403, "ngen": 1200000, "fraction": 1.0},
# L55 [Original comment]:     # Diboson and 2-fermion backgrounds. The processed fraction is shared with
    # Diboson and 2-fermion backgrounds. The processed fraction is shared with
# L56 [Original comment]:     # the FCCAnalyses stage through ml_config.py to keep the whole chain aligned.
    # the FCCAnalyses stage through ml_config.py to keep the whole chain aligned.
# L57 [Executable statement]:     "p8_ee_WW_ecm240":        {"xsec": 16.4385, "ngen": 373375386, "fraction": SAMPLE_PROCESSING_FRACTIONS["p8_ee_WW_ecm240"]},
    "p8_ee_WW_ecm240":        {"xsec": 16.4385, "ngen": 373375386, "fraction": SAMPLE_PROCESSING_FRACTIONS["p8_ee_WW_ecm240"]},
# L58 [Executable statement]:     "p8_ee_ZZ_ecm240":        {"xsec": 1.35899, "ngen": 209700000, "fraction": SAMPLE_PROCESSING_FRACTIONS["p8_ee_ZZ_ecm240"]},
    "p8_ee_ZZ_ecm240":        {"xsec": 1.35899, "ngen": 209700000, "fraction": SAMPLE_PROCESSING_FRACTIONS["p8_ee_ZZ_ecm240"]},
# L59 [Executable statement]:     "wz3p6_ee_uu_ecm240":     {"xsec": 11.9447, "ngen": 100790000, "fraction": SAMPLE_PROCESSING_FRACTIONS["wz3p6_ee_uu_ecm240"]},
    "wz3p6_ee_uu_ecm240":     {"xsec": 11.9447, "ngen": 100790000, "fraction": SAMPLE_PROCESSING_FRACTIONS["wz3p6_ee_uu_ecm240"]},
# L60 [Executable statement]:     "wz3p6_ee_dd_ecm240":     {"xsec": 10.8037, "ngen": 100910000, "fraction": SAMPLE_PROCESSING_FRACTIONS["wz3p6_ee_dd_ecm240"]},
    "wz3p6_ee_dd_ecm240":     {"xsec": 10.8037, "ngen": 100910000, "fraction": SAMPLE_PROCESSING_FRACTIONS["wz3p6_ee_dd_ecm240"]},
# L61 [Executable statement]:     "wz3p6_ee_cc_ecm240":     {"xsec": 11.0595, "ngen": 101290000, "fraction": SAMPLE_PROCESSING_FRACTIONS["wz3p6_ee_cc_ecm240"]},
    "wz3p6_ee_cc_ecm240":     {"xsec": 11.0595, "ngen": 101290000, "fraction": SAMPLE_PROCESSING_FRACTIONS["wz3p6_ee_cc_ecm240"]},
# L62 [Executable statement]:     "wz3p6_ee_ss_ecm240":     {"xsec": 10.7725, "ngen": 102348636, "fraction": SAMPLE_PROCESSING_FRACTIONS["wz3p6_ee_ss_ecm240"]},
    "wz3p6_ee_ss_ecm240":     {"xsec": 10.7725, "ngen": 102348636, "fraction": SAMPLE_PROCESSING_FRACTIONS["wz3p6_ee_ss_ecm240"]},
# L63 [Executable statement]:     "wz3p6_ee_bb_ecm240":     {"xsec": 10.4299, "ngen": 99490000, "fraction": SAMPLE_PROCESSING_FRACTIONS["wz3p6_ee_bb_ecm240"]},
    "wz3p6_ee_bb_ecm240":     {"xsec": 10.4299, "ngen": 99490000, "fraction": SAMPLE_PROCESSING_FRACTIONS["wz3p6_ee_bb_ecm240"]},
# L64 [Executable statement]:     "wz3p6_ee_tautau_ecm240": {"xsec": 4.6682, "ngen": 235800000, "fraction": SAMPLE_PROCESSING_FRACTIONS["wz3p6_ee_tautau_ecm240"]},
    "wz3p6_ee_tautau_ecm240": {"xsec": 4.6682, "ngen": 235800000, "fraction": SAMPLE_PROCESSING_FRACTIONS["wz3p6_ee_tautau_ecm240"]},
# L65 [Original comment]:     # ZH with H->other (fraction=1, all events processed)
    # ZH with H->other (fraction=1, all events processed)
# L66 [Executable statement]:     "wzp6_ee_qqH_Hbb_ecm240":    {"xsec": 0.03106, "ngen": 500000, "fraction": 1.0},
    "wzp6_ee_qqH_Hbb_ecm240":    {"xsec": 0.03106, "ngen": 500000, "fraction": 1.0},
# L67 [Executable statement]:     "wzp6_ee_qqH_Htautau_ecm240": {"xsec": 0.003345, "ngen": 200000, "fraction": 1.0},
    "wzp6_ee_qqH_Htautau_ecm240": {"xsec": 0.003345, "ngen": 200000, "fraction": 1.0},
# L68 [Executable statement]:     "wzp6_ee_qqH_Hgg_ecm240":    {"xsec": 0.004367, "ngen": 400000, "fraction": 1.0},
    "wzp6_ee_qqH_Hgg_ecm240":    {"xsec": 0.004367, "ngen": 400000, "fraction": 1.0},
# L69 [Executable statement]:     "wzp6_ee_qqH_Hcc_ecm240":    {"xsec": 0.001542, "ngen": 200000, "fraction": 1.0},
    "wzp6_ee_qqH_Hcc_ecm240":    {"xsec": 0.001542, "ngen": 200000, "fraction": 1.0},
# L70 [Executable statement]:     "wzp6_ee_qqH_HZZ_ecm240":    {"xsec": 0.001397, "ngen": 1200000, "fraction": 1.0},
    "wzp6_ee_qqH_HZZ_ecm240":    {"xsec": 0.001397, "ngen": 1200000, "fraction": 1.0},
# L71 [Executable statement]:     "wzp6_ee_bbH_Hbb_ecm240":    {"xsec": 0.01731, "ngen": 100000, "fraction": 1.0},
    "wzp6_ee_bbH_Hbb_ecm240":    {"xsec": 0.01731, "ngen": 100000, "fraction": 1.0},
# L72 [Executable statement]:     "wzp6_ee_bbH_Htautau_ecm240": {"xsec": 0.001864, "ngen": 400000, "fraction": 1.0},
    "wzp6_ee_bbH_Htautau_ecm240": {"xsec": 0.001864, "ngen": 400000, "fraction": 1.0},
# L73 [Executable statement]:     "wzp6_ee_bbH_Hgg_ecm240":    {"xsec": 0.002433, "ngen": 200000, "fraction": 1.0},
    "wzp6_ee_bbH_Hgg_ecm240":    {"xsec": 0.002433, "ngen": 200000, "fraction": 1.0},
# L74 [Executable statement]:     "wzp6_ee_bbH_Hcc_ecm240":    {"xsec": 0.0008591, "ngen": 400000, "fraction": 1.0},
    "wzp6_ee_bbH_Hcc_ecm240":    {"xsec": 0.0008591, "ngen": 400000, "fraction": 1.0},
# L75 [Executable statement]:     "wzp6_ee_bbH_HZZ_ecm240":    {"xsec": 0.0007782, "ngen": 1000000, "fraction": 1.0},
    "wzp6_ee_bbH_HZZ_ecm240":    {"xsec": 0.0007782, "ngen": 1000000, "fraction": 1.0},
# L76 [Executable statement]:     "wzp6_ee_ccH_Hbb_ecm240":    {"xsec": 0.01359, "ngen": 200000, "fraction": 1.0},
    "wzp6_ee_ccH_Hbb_ecm240":    {"xsec": 0.01359, "ngen": 200000, "fraction": 1.0},
# L77 [Executable statement]:     "wzp6_ee_ccH_Htautau_ecm240": {"xsec": 0.001464, "ngen": 400000, "fraction": 1.0},
    "wzp6_ee_ccH_Htautau_ecm240": {"xsec": 0.001464, "ngen": 400000, "fraction": 1.0},
# L78 [Executable statement]:     "wzp6_ee_ccH_Hgg_ecm240":    {"xsec": 0.001911, "ngen": 400000, "fraction": 1.0},
    "wzp6_ee_ccH_Hgg_ecm240":    {"xsec": 0.001911, "ngen": 400000, "fraction": 1.0},
# L79 [Executable statement]:     "wzp6_ee_ccH_Hcc_ecm240":    {"xsec": 0.0006748, "ngen": 400000, "fraction": 1.0},
    "wzp6_ee_ccH_Hcc_ecm240":    {"xsec": 0.0006748, "ngen": 400000, "fraction": 1.0},
# L80 [Executable statement]:     "wzp6_ee_ccH_HZZ_ecm240":    {"xsec": 0.0006113, "ngen": 1200000, "fraction": 1.0},
    "wzp6_ee_ccH_HZZ_ecm240":    {"xsec": 0.0006113, "ngen": 1200000, "fraction": 1.0},
# L81 [Executable statement]:     "wzp6_ee_ssH_Hbb_ecm240":    {"xsec": 0.01745, "ngen": 200000, "fraction": 1.0},
    "wzp6_ee_ssH_Hbb_ecm240":    {"xsec": 0.01745, "ngen": 200000, "fraction": 1.0},
# L82 [Executable statement]:     "wzp6_ee_ssH_Htautau_ecm240": {"xsec": 0.001879, "ngen": 400000, "fraction": 1.0},
    "wzp6_ee_ssH_Htautau_ecm240": {"xsec": 0.001879, "ngen": 400000, "fraction": 1.0},
# L83 [Executable statement]:     "wzp6_ee_ssH_Hgg_ecm240":    {"xsec": 0.002453, "ngen": 400000, "fraction": 1.0},
    "wzp6_ee_ssH_Hgg_ecm240":    {"xsec": 0.002453, "ngen": 400000, "fraction": 1.0},
# L84 [Executable statement]:     "wzp6_ee_ssH_Hcc_ecm240":    {"xsec": 0.0008662, "ngen": 300000, "fraction": 1.0},
    "wzp6_ee_ssH_Hcc_ecm240":    {"xsec": 0.0008662, "ngen": 300000, "fraction": 1.0},
# L85 [Executable statement]:     "wzp6_ee_ssH_HZZ_ecm240":    {"xsec": 0.0007847, "ngen": 600000, "fraction": 1.0},
    "wzp6_ee_ssH_HZZ_ecm240":    {"xsec": 0.0007847, "ngen": 600000, "fraction": 1.0},
# L86 [Executable statement]: }
}
# L87 [Executable statement]: INT_LUMI = 10.8e6  # pb^-1
INT_LUMI = 10.8e6  # pb^-1
# L88 [Blank separator]: 

# L89 [Blank separator]: 

# L90 [Function definition]: def parse_args():
def parse_args():
# L91 [Executable statement]:     parser = argparse.ArgumentParser(description=__doc__)
    parser = argparse.ArgumentParser(description=__doc__)
# L92 [Executable statement]:     parser.add_argument('--input-dir', default=DEFAULT_TREEMAKER_DIR)
    parser.add_argument('--input-dir', default=DEFAULT_TREEMAKER_DIR)
# L93 [Executable statement]:     parser.add_argument('--output-dir', default=DEFAULT_MODEL_DIR)
    parser.add_argument('--output-dir', default=DEFAULT_MODEL_DIR)
# L94 [Executable statement]:     parser.add_argument('--tree-name', default=DEFAULT_TREE_NAME)
    parser.add_argument('--tree-name', default=DEFAULT_TREE_NAME)
# L95 [Executable statement]:     parser.add_argument('--signal-samples', nargs='*', default=SIGNAL_SAMPLES)
    parser.add_argument('--signal-samples', nargs='*', default=SIGNAL_SAMPLES)
# L96 [Executable statement]:     parser.add_argument('--background-samples', nargs='*', default=BACKGROUND_SAMPLES)
    parser.add_argument('--background-samples', nargs='*', default=BACKGROUND_SAMPLES)
# L97 [Executable statement]:     parser.add_argument('--features', nargs='*', default=ML_FEATURES)
    parser.add_argument('--features', nargs='*', default=ML_FEATURES)
# L98 [Executable statement]:     parser.add_argument('--test-size', type=float, default=0.30)
    parser.add_argument('--test-size', type=float, default=0.30)
# L99 [Executable statement]:     parser.add_argument('--random-state', type=int, default=42)
    parser.add_argument('--random-state', type=int, default=42)
# L100 [Executable statement]:     parser.add_argument('--n-jobs', type=int, default=8)
    parser.add_argument('--n-jobs', type=int, default=8)
# L101 [Executable statement]:     parser.add_argument('--no-grid-search', action='store_true',
    parser.add_argument('--no-grid-search', action='store_true',
# L102 [Executable statement]:                         help='Skip grid search, use default hyperparameters')
                        help='Skip grid search, use default hyperparameters')
# L103 [Executable statement]:     parser.add_argument('--no-plots', action='store_true',
    parser.add_argument('--no-plots', action='store_true',
# L104 [Executable statement]:                         help='Skip diagnostic plots')
                        help='Skip diagnostic plots')
# L105 [Executable statement]:     parser.add_argument('--kfold', type=int, default=5,
    parser.add_argument('--kfold', type=int, default=5,
# L106 [Executable statement]:                         help='Number of folds for k-fold CV scoring (0 to disable)')
                        help='Number of folds for k-fold CV scoring (0 to disable)')
# L107 [Function return]:     return parser.parse_args()
    return parser.parse_args()
# L108 [Blank separator]: 

# L109 [Blank separator]: 

# L110 [Function definition]: def get_tree_status(root_file, tree_name):
def get_tree_status(root_file, tree_name):
# L111 [Executable statement]:     has_tree = tree_name in root_file
    has_tree = tree_name in root_file
# L112 [Executable statement]:     num_entries = root_file[tree_name].num_entries if has_tree else 0
    num_entries = root_file[tree_name].num_entries if has_tree else 0
# L113 [Blank separator]: 

# L114 [Executable statement]:     selected = None
    selected = None
# L115 [Conditional block]:     if 'eventsSelected' in root_file:
    if 'eventsSelected' in root_file:
# L116 [Exception handling start]:         try:
        try:
# L117 [Executable statement]:             selected = int(root_file['eventsSelected'].member('fVal'))
            selected = int(root_file['eventsSelected'].member('fVal'))
# L118 [Exception handler]:         except Exception:
        except Exception:
# L119 [Executable statement]:             selected = None
            selected = None
# L120 [Blank separator]: 

# L121 [Executable statement]:     processed = None
    processed = None
# L122 [Conditional block]:     if 'eventsProcessed' in root_file:
    if 'eventsProcessed' in root_file:
# L123 [Exception handling start]:         try:
        try:
# L124 [Executable statement]:             processed = int(root_file['eventsProcessed'].member('fVal'))
            processed = int(root_file['eventsProcessed'].member('fVal'))
# L125 [Exception handler]:         except Exception:
        except Exception:
# L126 [Executable statement]:             processed = None
            processed = None
# L127 [Blank separator]: 

# L128 [Function return]:     return {
    return {
# L129 [Executable statement]:         'has_tree': has_tree,
        'has_tree': has_tree,
# L130 [Executable statement]:         'num_entries': num_entries,
        'num_entries': num_entries,
# L131 [Executable statement]:         'selected': selected,
        'selected': selected,
# L132 [Executable statement]:         'processed': processed,
        'processed': processed,
# L133 [Executable statement]:     }
    }
# L134 [Blank separator]: 

# L135 [Blank separator]: 

# L136 [Function definition]: def read_samples(input_dir, tree_name, sample_names, features, label):
def read_samples(input_dir, tree_name, sample_names, features, label):
# L137 [Executable statement]:     """Read samples and compute physics-correct per-event weights."""
    """Read samples and compute physics-correct per-event weights."""
# L138 [Executable statement]:     frames = []
    frames = []
# L139 [Executable statement]:     input_dir = Path(input_dir)
    input_dir = Path(input_dir)
# L140 [Loop over iterable]:     for sample in sample_names:
    for sample in sample_names:
# L141 [Executable statement]:         root_path = input_dir / f'{sample}.root'
        root_path = input_dir / f'{sample}.root'
# L142 [Conditional block]:         if not root_path.exists():
        if not root_path.exists():
# L143 [Runtime log output]:             print(f'[warn] missing sample: {root_path}')
            print(f'[warn] missing sample: {root_path}')
# L144 [Executable statement]:             continue
            continue
# L145 [Blank separator]: 

# L146 [Context manager block]:         with uproot.open(root_path) as root_file:
        with uproot.open(root_path) as root_file:
# L147 [Executable statement]:             status = get_tree_status(root_file, tree_name)
            status = get_tree_status(root_file, tree_name)
# L148 [Conditional block]:             if not status['has_tree']:
            if not status['has_tree']:
# L149 [Conditional block]:                 if status['selected'] == 0:
                if status['selected'] == 0:
# L150 [Executable statement]:                     processed = status['processed']
                    processed = status['processed']
# L151 [Executable statement]:                     processed_msg = f', processed={processed}' if processed is not None else ''
                    processed_msg = f', processed={processed}' if processed is not None else ''
# L152 [Runtime log output]:                     print(
                    print(
# L153 [Executable statement]:                         f'[info] {root_path} is a 0-pass sample '
                        f'[info] {root_path} is a 0-pass sample '
# L154 [Executable statement]:                         f'(eventsSelected=0{processed_msg}); no tree "{tree_name}" was written, skipping'
                        f'(eventsSelected=0{processed_msg}); no tree "{tree_name}" was written, skipping'
# L155 [Executable statement]:                     )
                    )
# L156 [Else branch]:                 else:
                else:
# L157 [Runtime log output]:                     print(f'[warn] {root_path} has no tree "{tree_name}", skipping')
                    print(f'[warn] {root_path} has no tree "{tree_name}", skipping')
# L158 [Executable statement]:                 continue
                continue
# L159 [Executable statement]:             tree = root_file[tree_name]
            tree = root_file[tree_name]
# L160 [Conditional block]:             if tree.num_entries == 0:
            if tree.num_entries == 0:
# L161 [Runtime log output]:                 print(f'[info] {root_path} has tree "{tree_name}" but 0 entries, skipping')
                print(f'[info] {root_path} has tree "{tree_name}" but 0 entries, skipping')
# L162 [Executable statement]:                 continue
                continue
# L163 [Executable statement]:             available = set(tree.keys())
            available = set(tree.keys())
# L164 [Executable statement]:             use_features = [f for f in features if f in available]
            use_features = [f for f in features if f in available]
# L165 [Executable statement]:             missing = [f for f in features if f not in available]
            missing = [f for f in features if f not in available]
# L166 [Conditional block]:             if missing:
            if missing:
# L167 [Runtime log output]:                 print(f'[warn] {root_path} missing branches: {missing}')
                print(f'[warn] {root_path} missing branches: {missing}')
# L168 [Executable statement]:             frame = tree.arrays(use_features, library='pd')
            frame = tree.arrays(use_features, library='pd')
# L169 [Blank separator]: 

# L170 [Original comment]:         # Compute physics weight: lumi * xsec / ngen_total
        # Compute physics weight: lumi * xsec / ngen_total
# L171 [Executable statement]:         info = SAMPLE_INFO.get(sample, {})
        info = SAMPLE_INFO.get(sample, {})
# L172 [Conditional block]:         if info:
        if info:
# L173 [Executable statement]:             frac = info.get('fraction', 1.0)
            frac = info.get('fraction', 1.0)
# L174 [Executable statement]:             phys_weight = INT_LUMI * info['xsec'] / (info['ngen'] * frac)
            phys_weight = INT_LUMI * info['xsec'] / (info['ngen'] * frac)
# L175 [Else branch]:         else:
        else:
# L176 [Executable statement]:             phys_weight = 1.0
            phys_weight = 1.0
# L177 [Runtime log output]:             print(f'[warn] no cross-section info for {sample}, using weight=1')
            print(f'[warn] no cross-section info for {sample}, using weight=1')
# L178 [Blank separator]: 

# L179 [Executable statement]:         frame['phys_weight'] = phys_weight
        frame['phys_weight'] = phys_weight
# L180 [Executable statement]:         frame['label'] = label
        frame['label'] = label
# L181 [Executable statement]:         frame['sample_name'] = sample
        frame['sample_name'] = sample
# L182 [Executable statement]:         n = len(frame)
        n = len(frame)
# L183 [Executable statement]:         expected = INT_LUMI * info.get('xsec', 0)
        expected = INT_LUMI * info.get('xsec', 0)
# L184 [Runtime log output]:         print(f'  {sample}: {n} events, phys_weight={phys_weight:.6f}, '
        print(f'  {sample}: {n} events, phys_weight={phys_weight:.6f}, '
# L185 [Executable statement]:               f'effective={n*phys_weight:.0f} (expected total={expected:.0f})')
              f'effective={n*phys_weight:.0f} (expected total={expected:.0f})')
# L186 [Executable statement]:         frames.append(frame)
        frames.append(frame)
# L187 [Blank separator]: 

# L188 [Conditional block]:     if not frames:
    if not frames:
# L189 [Executable statement]:         raise RuntimeError('No input ntuples found for training.')
        raise RuntimeError('No input ntuples found for training.')
# L190 [Function return]:     return pd.concat(frames, ignore_index=True)
    return pd.concat(frames, ignore_index=True)
# L191 [Blank separator]: 

# L192 [Blank separator]: 

# L193 [Function definition]: def normalize_class_weights(w, y):
def normalize_class_weights(w, y):
# L194 [Executable statement]:     """Normalize weights so signal and background have equal total weight.
    """Normalize weights so signal and background have equal total weight.
# L195 [Blank separator]: 

# L196 [Executable statement]:     Preserves intra-class weight structure (relative weights within each class
    Preserves intra-class weight structure (relative weights within each class
# L197 [Executable statement]:     are unchanged). This ensures balanced learning while respecting the physics
    are unchanged). This ensures balanced learning while respecting the physics
# L198 [Executable statement]:     weight ratios between samples within each class.
    weight ratios between samples within each class.
# L199 [Executable statement]:     """
    """
# L200 [Executable statement]:     w = w.copy()
    w = w.copy()
# L201 [Executable statement]:     sig_mask = y == 1
    sig_mask = y == 1
# L202 [Executable statement]:     bkg_mask = y == 0
    bkg_mask = y == 0
# L203 [Executable statement]:     sig_total = w[sig_mask].sum()
    sig_total = w[sig_mask].sum()
# L204 [Executable statement]:     bkg_total = w[bkg_mask].sum()
    bkg_total = w[bkg_mask].sum()
# L205 [Original comment]:     # Scale both classes to have total weight = number of events in smaller class
    # Scale both classes to have total weight = number of events in smaller class
# L206 [Executable statement]:     target = min(sig_mask.sum(), bkg_mask.sum())
    target = min(sig_mask.sum(), bkg_mask.sum())
# L207 [Executable statement]:     w[sig_mask] *= target / sig_total
    w[sig_mask] *= target / sig_total
# L208 [Executable statement]:     w[bkg_mask] *= target / bkg_total
    w[bkg_mask] *= target / bkg_total
# L209 [Runtime log output]:     print(f'  Normalized weights: sig total={w[sig_mask].sum():.0f}, '
    print(f'  Normalized weights: sig total={w[sig_mask].sum():.0f}, '
# L210 [Executable statement]:           f'bkg total={w[bkg_mask].sum():.0f}')
          f'bkg total={w[bkg_mask].sum():.0f}')
# L211 [Function return]:     return w
    return w
# L212 [Blank separator]: 

# L213 [Blank separator]: 

# L214 [Function definition]: def weighted_ks_test(scores_a, weights_a, scores_b, weights_b, n_bins=50):
def weighted_ks_test(scores_a, weights_a, scores_b, weights_b, n_bins=50):
# L215 [Executable statement]:     """Weighted KS-like test using binned chi2 comparison.
    """Weighted KS-like test using binned chi2 comparison.
# L216 [Blank separator]: 

# L217 [Executable statement]:     Returns (chi2/ndf, p_value) using weighted histograms.
    Returns (chi2/ndf, p_value) using weighted histograms.
# L218 [Executable statement]:     scipy's ks_2samp doesn't support weights, so we use a binned approach.
    scipy's ks_2samp doesn't support weights, so we use a binned approach.
# L219 [Executable statement]:     """
    """
# L220 [Import statement]:     from scipy.stats import chi2 as chi2_dist
    from scipy.stats import chi2 as chi2_dist
# L221 [Executable statement]:     bins = np.linspace(0, 1, n_bins + 1)
    bins = np.linspace(0, 1, n_bins + 1)
# L222 [Blank separator]: 

# L223 [Executable statement]:     h_a, _ = np.histogram(scores_a, bins=bins, weights=weights_a)
    h_a, _ = np.histogram(scores_a, bins=bins, weights=weights_a)
# L224 [Executable statement]:     h_b, _ = np.histogram(scores_b, bins=bins, weights=weights_b)
    h_b, _ = np.histogram(scores_b, bins=bins, weights=weights_b)
# L225 [Blank separator]: 

# L226 [Original comment]:     # Normalize to unit area
    # Normalize to unit area
# L227 [Executable statement]:     sum_a = h_a.sum()
    sum_a = h_a.sum()
# L228 [Executable statement]:     sum_b = h_b.sum()
    sum_b = h_b.sum()
# L229 [Conditional block]:     if sum_a > 0:
    if sum_a > 0:
# L230 [Executable statement]:         h_a = h_a / sum_a
        h_a = h_a / sum_a
# L231 [Conditional block]:     if sum_b > 0:
    if sum_b > 0:
# L232 [Executable statement]:         h_b = h_b / sum_b
        h_b = h_b / sum_b
# L233 [Blank separator]: 

# L234 [Original comment]:     # Binned chi2: sum (a - b)^2 / (var_a + var_b)
    # Binned chi2: sum (a - b)^2 / (var_a + var_b)
# L235 [Original comment]:     # Variance from weighted histograms
    # Variance from weighted histograms
# L236 [Executable statement]:     h_a_w2, _ = np.histogram(scores_a, bins=bins, weights=weights_a**2)
    h_a_w2, _ = np.histogram(scores_a, bins=bins, weights=weights_a**2)
# L237 [Executable statement]:     h_b_w2, _ = np.histogram(scores_b, bins=bins, weights=weights_b**2)
    h_b_w2, _ = np.histogram(scores_b, bins=bins, weights=weights_b**2)
# L238 [Executable statement]:     var_a = h_a_w2 / (sum_a**2) if sum_a > 0 else np.zeros_like(h_a)
    var_a = h_a_w2 / (sum_a**2) if sum_a > 0 else np.zeros_like(h_a)
# L239 [Executable statement]:     var_b = h_b_w2 / (sum_b**2) if sum_b > 0 else np.zeros_like(h_b)
    var_b = h_b_w2 / (sum_b**2) if sum_b > 0 else np.zeros_like(h_b)
# L240 [Blank separator]: 

# L241 [Executable statement]:     denom = var_a + var_b
    denom = var_a + var_b
# L242 [Executable statement]:     mask = denom > 0
    mask = denom > 0
# L243 [Executable statement]:     chi2_val = np.sum((h_a[mask] - h_b[mask])**2 / denom[mask])
    chi2_val = np.sum((h_a[mask] - h_b[mask])**2 / denom[mask])
# L244 [Executable statement]:     ndf = mask.sum() - 1
    ndf = mask.sum() - 1
# L245 [Executable statement]:     p_value = 1.0 - chi2_dist.cdf(chi2_val, ndf) if ndf > 0 else 1.0
    p_value = 1.0 - chi2_dist.cdf(chi2_val, ndf) if ndf > 0 else 1.0
# L246 [Function return]:     return chi2_val / max(ndf, 1), p_value
    return chi2_val / max(ndf, 1), p_value
# L247 [Blank separator]: 

# L248 [Blank separator]: 

# L249 [Function definition]: def make_validation_split(X, y, w, random_state, test_size=0.2):
def make_validation_split(X, y, w, random_state, test_size=0.2):
# L250 [Executable statement]:     """Create a validation split that is disjoint from the fit sample."""
    """Create a validation split that is disjoint from the fit sample."""
# L251 [Executable statement]:     indices = np.arange(len(X))
    indices = np.arange(len(X))
# L252 [Executable statement]:     idx_fit, idx_val = train_test_split(
    idx_fit, idx_val = train_test_split(
# L253 [Executable statement]:         indices, test_size=test_size, random_state=random_state, stratify=y,
        indices, test_size=test_size, random_state=random_state, stratify=y,
# L254 [Executable statement]:     )
    )
# L255 [Function return]:     return (
    return (
# L256 [Executable statement]:         X.iloc[idx_fit], X.iloc[idx_val],
        X.iloc[idx_fit], X.iloc[idx_val],
# L257 [Executable statement]:         y.iloc[idx_fit], y.iloc[idx_val],
        y.iloc[idx_fit], y.iloc[idx_val],
# L258 [Executable statement]:         w.iloc[idx_fit], w.iloc[idx_val],
        w.iloc[idx_fit], w.iloc[idx_val],
# L259 [Executable statement]:     )
    )
# L260 [Blank separator]: 

# L261 [Blank separator]: 

# L262 [Function definition]: def fit_with_early_stopping(X_train, y_train, w_train, params, random_state, n_jobs, eval_metric):
def fit_with_early_stopping(X_train, y_train, w_train, params, random_state, n_jobs, eval_metric):
# L263 [Executable statement]:     """Choose the boosting length on a held-out validation split, then retrain."""
    """Choose the boosting length on a held-out validation split, then retrain."""
# L264 [Executable statement]:     X_fit, X_val, y_fit, y_val, w_fit, w_val = make_validation_split(
    X_fit, X_val, y_fit, y_val, w_fit, w_val = make_validation_split(
# L265 [Executable statement]:         X_train, y_train, w_train, random_state=random_state,
        X_train, y_train, w_train, random_state=random_state,
# L266 [Executable statement]:     )
    )
# L267 [Blank separator]: 

# L268 [Executable statement]:     fit_kwargs = {
    fit_kwargs = {
# L269 [Executable statement]:         'objective': 'binary:logistic',
        'objective': 'binary:logistic',
# L270 [Executable statement]:         'eval_metric': eval_metric,
        'eval_metric': eval_metric,
# L271 [Executable statement]:         'tree_method': 'hist',
        'tree_method': 'hist',
# L272 [Executable statement]:         'random_state': random_state,
        'random_state': random_state,
# L273 [Executable statement]:         'n_jobs': n_jobs,
        'n_jobs': n_jobs,
# L274 [Executable statement]:         'verbosity': 0,
        'verbosity': 0,
# L275 [Executable statement]:         **params,
        **params,
# L276 [Executable statement]:     }
    }
# L277 [Executable statement]:     model_es = xgb.XGBClassifier(early_stopping_rounds=30, **fit_kwargs)
    model_es = xgb.XGBClassifier(early_stopping_rounds=30, **fit_kwargs)
# L278 [Executable statement]:     model_es.fit(
    model_es.fit(
# L279 [Executable statement]:         X_fit, y_fit, sample_weight=w_fit,
        X_fit, y_fit, sample_weight=w_fit,
# L280 [Executable statement]:         eval_set=[(X_val, y_val)],
        eval_set=[(X_val, y_val)],
# L281 [Executable statement]:         sample_weight_eval_set=[w_val],
        sample_weight_eval_set=[w_val],
# L282 [Executable statement]:         verbose=False,
        verbose=False,
# L283 [Executable statement]:     )
    )
# L284 [Blank separator]: 

# L285 [Executable statement]:     best_iteration = getattr(model_es, 'best_iteration', None)
    best_iteration = getattr(model_es, 'best_iteration', None)
# L286 [Executable statement]:     n_estimators_final = (best_iteration + 1
    n_estimators_final = (best_iteration + 1
# L287 [Conditional block]:                           if best_iteration is not None
                          if best_iteration is not None
# L288 [Executable statement]:                           else params['n_estimators'])
                          else params['n_estimators'])
# L289 [Blank separator]: 

# L290 [Executable statement]:     final_kwargs = dict(fit_kwargs)
    final_kwargs = dict(fit_kwargs)
# L291 [Executable statement]:     final_kwargs['n_estimators'] = n_estimators_final
    final_kwargs['n_estimators'] = n_estimators_final
# L292 [Executable statement]:     model = xgb.XGBClassifier(**final_kwargs)
    model = xgb.XGBClassifier(**final_kwargs)
# L293 [Executable statement]:     model.fit(X_train, y_train, sample_weight=w_train, verbose=False)
    model.fit(X_train, y_train, sample_weight=w_train, verbose=False)
# L294 [Blank separator]: 

# L295 [Executable statement]:     val_score = model.predict_proba(X_val)[:, 1]
    val_score = model.predict_proba(X_val)[:, 1]
# L296 [Executable statement]:     val_auc = roc_auc_score(y_val, val_score, sample_weight=w_val)
    val_auc = roc_auc_score(y_val, val_score, sample_weight=w_val)
# L297 [Blank separator]: 

# L298 [Executable statement]:     evals_result = model_es.evals_result() if hasattr(model_es, 'evals_result') else {}
    evals_result = model_es.evals_result() if hasattr(model_es, 'evals_result') else {}
# L299 [Function return]:     return model, best_iteration, n_estimators_final, val_auc, evals_result
    return model, best_iteration, n_estimators_final, val_auc, evals_result
# L300 [Blank separator]: 

# L301 [Blank separator]: 

# L302 [Function definition]: def grid_search(X_train, y_train, w_train, random_state, n_jobs):
def grid_search(X_train, y_train, w_train, random_state, n_jobs):
# L303 [Executable statement]:     """Run hyperparameter grid search on a subsample with early stopping."""
    """Run hyperparameter grid search on a subsample with early stopping."""
# L304 [Runtime log output]:     print('\n=== Hyperparameter Grid Search ===')
    print('\n=== Hyperparameter Grid Search ===')
# L305 [Original comment]:     # Subsample for speed
    # Subsample for speed
# L306 [Executable statement]:     n_sub = min(50000, len(X_train))
    n_sub = min(50000, len(X_train))
# L307 [Executable statement]:     idx = np.random.RandomState(random_state).choice(len(X_train), n_sub, replace=False)
    idx = np.random.RandomState(random_state).choice(len(X_train), n_sub, replace=False)
# L308 [Executable statement]:     X_sub = X_train.iloc[idx]
    X_sub = X_train.iloc[idx]
# L309 [Executable statement]:     y_sub = y_train.iloc[idx]
    y_sub = y_train.iloc[idx]
# L310 [Executable statement]:     w_sub = w_train.iloc[idx]
    w_sub = w_train.iloc[idx]
# L311 [Blank separator]: 

# L312 [Original comment]:     # Split subsample into train/val
    # Split subsample into train/val
# L313 [Executable statement]:     X_t, X_v, y_t, y_v, w_t, w_v = train_test_split(
    X_t, X_v, y_t, y_v, w_t, w_v = train_test_split(
# L314 [Executable statement]:         X_sub, y_sub, w_sub, test_size=0.3, random_state=random_state, stratify=y_sub
        X_sub, y_sub, w_sub, test_size=0.3, random_state=random_state, stratify=y_sub
# L315 [Executable statement]:     )
    )
# L316 [Blank separator]: 

# L317 [Original comment]:     # Extended grid: now includes min_child_weight and subsample
    # Extended grid: now includes min_child_weight and subsample
# L318 [Executable statement]:     param_grid = {
    param_grid = {
# L319 [Executable statement]:         'max_depth': [3, 4, 5],
        'max_depth': [3, 4, 5],
# L320 [Executable statement]:         'learning_rate': [0.01, 0.05, 0.1],
        'learning_rate': [0.01, 0.05, 0.1],
# L321 [Executable statement]:         'n_estimators': [1000],  # single large value; early stopping finds optimum
        'n_estimators': [1000],  # single large value; early stopping finds optimum
# L322 [Executable statement]:         'min_child_weight': [5, 10, 20],
        'min_child_weight': [5, 10, 20],
# L323 [Executable statement]:         'subsample': [0.7, 0.8],
        'subsample': [0.7, 0.8],
# L324 [Executable statement]:         'colsample_bytree': [0.7, 0.8],
        'colsample_bytree': [0.7, 0.8],
# L325 [Executable statement]:     }
    }
# L326 [Blank separator]: 

# L327 [Executable statement]:     best_auc = 0
    best_auc = 0
# L328 [Executable statement]:     best_params = {}
    best_params = {}
# L329 [Executable statement]:     results = []
    results = []
# L330 [Blank separator]: 

# L331 [Executable statement]:     combos = list(product(
    combos = list(product(
# L332 [Executable statement]:         param_grid['max_depth'],
        param_grid['max_depth'],
# L333 [Executable statement]:         param_grid['learning_rate'],
        param_grid['learning_rate'],
# L334 [Executable statement]:         param_grid['n_estimators'],
        param_grid['n_estimators'],
# L335 [Executable statement]:         param_grid['min_child_weight'],
        param_grid['min_child_weight'],
# L336 [Executable statement]:         param_grid['subsample'],
        param_grid['subsample'],
# L337 [Executable statement]:         param_grid['colsample_bytree'],
        param_grid['colsample_bytree'],
# L338 [Executable statement]:     ))
    ))
# L339 [Runtime log output]:     print(f'  Testing {len(combos)} combinations...')
    print(f'  Testing {len(combos)} combinations...')
# L340 [Blank separator]: 

# L341 [Loop over iterable]:     for depth, lr, n_est, mcw, ss, csbt in combos:
    for depth, lr, n_est, mcw, ss, csbt in combos:
# L342 [Executable statement]:         model = xgb.XGBClassifier(
        model = xgb.XGBClassifier(
# L343 [Executable statement]:             objective='binary:logistic',
            objective='binary:logistic',
# L344 [Executable statement]:             eval_metric='auc',
            eval_metric='auc',
# L345 [Executable statement]:             tree_method='hist',
            tree_method='hist',
# L346 [Executable statement]:             max_depth=depth,
            max_depth=depth,
# L347 [Executable statement]:             learning_rate=lr,
            learning_rate=lr,
# L348 [Executable statement]:             n_estimators=n_est,
            n_estimators=n_est,
# L349 [Executable statement]:             min_child_weight=mcw,
            min_child_weight=mcw,
# L350 [Executable statement]:             subsample=ss,
            subsample=ss,
# L351 [Executable statement]:             colsample_bytree=csbt,
            colsample_bytree=csbt,
# L352 [Executable statement]:             random_state=random_state,
            random_state=random_state,
# L353 [Executable statement]:             n_jobs=n_jobs,
            n_jobs=n_jobs,
# L354 [Executable statement]:             early_stopping_rounds=30,
            early_stopping_rounds=30,
# L355 [Executable statement]:             verbosity=0,
            verbosity=0,
# L356 [Executable statement]:         )
        )
# L357 [Executable statement]:         model.fit(
        model.fit(
# L358 [Executable statement]:             X_t, y_t, sample_weight=w_t,
            X_t, y_t, sample_weight=w_t,
# L359 [Executable statement]:             eval_set=[(X_v, y_v)],
            eval_set=[(X_v, y_v)],
# L360 [Executable statement]:             sample_weight_eval_set=[w_v],
            sample_weight_eval_set=[w_v],
# L361 [Executable statement]:             verbose=False,
            verbose=False,
# L362 [Executable statement]:         )
        )
# L363 [Executable statement]:         score = model.predict_proba(X_v)[:, 1]
        score = model.predict_proba(X_v)[:, 1]
# L364 [Executable statement]:         auc = roc_auc_score(y_v, score, sample_weight=w_v)
        auc = roc_auc_score(y_v, score, sample_weight=w_v)
# L365 [Executable statement]:         results.append({
        results.append({
# L366 [Executable statement]:             'max_depth': depth, 'learning_rate': lr,
            'max_depth': depth, 'learning_rate': lr,
# L367 [Executable statement]:             'n_estimators': n_est, 'min_child_weight': mcw,
            'n_estimators': n_est, 'min_child_weight': mcw,
# L368 [Executable statement]:             'subsample': ss, 'colsample_bytree': csbt,
            'subsample': ss, 'colsample_bytree': csbt,
# L369 [Executable statement]:             'val_auc': auc,
            'val_auc': auc,
# L370 [Executable statement]:             'best_iteration': model.best_iteration if hasattr(model, 'best_iteration') else n_est,
            'best_iteration': model.best_iteration if hasattr(model, 'best_iteration') else n_est,
# L371 [Executable statement]:         })
        })
# L372 [Conditional block]:         if auc > best_auc:
        if auc > best_auc:
# L373 [Executable statement]:             best_auc = auc
            best_auc = auc
# L374 [Executable statement]:             best_params = {
            best_params = {
# L375 [Executable statement]:                 'max_depth': depth, 'learning_rate': lr,
                'max_depth': depth, 'learning_rate': lr,
# L376 [Executable statement]:                 'n_estimators': n_est, 'min_child_weight': mcw,
                'n_estimators': n_est, 'min_child_weight': mcw,
# L377 [Executable statement]:                 'subsample': ss, 'colsample_bytree': csbt,
                'subsample': ss, 'colsample_bytree': csbt,
# L378 [Executable statement]:             }
            }
# L379 [Blank separator]: 

# L380 [Runtime log output]:     print(f'  Best: depth={best_params["max_depth"]}, '
    print(f'  Best: depth={best_params["max_depth"]}, '
# L381 [Executable statement]:           f'lr={best_params["learning_rate"]}, '
          f'lr={best_params["learning_rate"]}, '
# L382 [Executable statement]:           f'n_est={best_params["n_estimators"]}, '
          f'n_est={best_params["n_estimators"]}, '
# L383 [Executable statement]:           f'mcw={best_params["min_child_weight"]}, '
          f'mcw={best_params["min_child_weight"]}, '
# L384 [Executable statement]:           f'ss={best_params["subsample"]}, '
          f'ss={best_params["subsample"]}, '
# L385 [Executable statement]:           f'csbt={best_params["colsample_bytree"]}, '
          f'csbt={best_params["colsample_bytree"]}, '
# L386 [Executable statement]:           f'AUC={best_auc:.4f}')
          f'AUC={best_auc:.4f}')
# L387 [Function return]:     return best_params, results
    return best_params, results
# L388 [Blank separator]: 

# L389 [Blank separator]: 

# L390 [Function definition]: def make_plots(output_dir, y_train, y_test, train_score, test_score,
def make_plots(output_dir, y_train, y_test, train_score, test_score,
# L391 [Executable statement]:                w_train, w_test, model, features, full_df_test=None):
               w_train, w_test, model, features, full_df_test=None):
# L392 [Executable statement]:     """Generate diagnostic plots including sculpting and per-sample distributions."""
    """Generate diagnostic plots including sculpting and per-sample distributions."""
# L393 [Exception handling start]:     try:
    try:
# L394 [Import statement]:         import matplotlib
        import matplotlib
# L395 [Executable statement]:         matplotlib.use('Agg')
        matplotlib.use('Agg')
# L396 [Import statement]:         import matplotlib.pyplot as plt
        import matplotlib.pyplot as plt
# L397 [Exception handler]:     except ImportError:
    except ImportError:
# L398 [Runtime log output]:         print('[warn] matplotlib not available, skipping plots')
        print('[warn] matplotlib not available, skipping plots')
# L399 [Return from function]:         return
        return
# L400 [Blank separator]: 

# L401 [Executable statement]:     plot_dir = output_dir / 'plots'
    plot_dir = output_dir / 'plots'
# L402 [Executable statement]:     plot_dir.mkdir(exist_ok=True)
    plot_dir.mkdir(exist_ok=True)
# L403 [Blank separator]: 

# L404 [Function definition]:     def add_fcc_label(ax, x=0.05, y=0.97):
    def add_fcc_label(ax, x=0.05, y=0.97):
# L405 [Executable statement]:         ax.text(x, y, r'$\mathbf{FCC\text{-}ee}$ Simulation',
        ax.text(x, y, r'$\mathbf{FCC\text{-}ee}$ Simulation',
# L406 [Executable statement]:                 transform=ax.transAxes, fontsize=10, va='top',
                transform=ax.transAxes, fontsize=10, va='top',
# L407 [Executable statement]:                 fontstyle='italic')
                fontstyle='italic')
# L408 [Executable statement]:         ax.text(x, y - 0.06, r'$\sqrt{s}=240$ GeV, $10.8\,\mathrm{ab}^{-1}$',
        ax.text(x, y - 0.06, r'$\sqrt{s}=240$ GeV, $10.8\,\mathrm{ab}^{-1}$',
# L409 [Executable statement]:                 transform=ax.transAxes, fontsize=9, va='top')
                transform=ax.transAxes, fontsize=9, va='top')
# L410 [Blank separator]: 

# L411 [Original comment]:     # 1. ROC curve
    # 1. ROC curve
# L412 [Executable statement]:     fpr, tpr, _ = roc_curve(y_test, test_score, sample_weight=w_test)
    fpr, tpr, _ = roc_curve(y_test, test_score, sample_weight=w_test)
# L413 [Executable statement]:     auc_val = roc_auc_score(y_test, test_score, sample_weight=w_test)
    auc_val = roc_auc_score(y_test, test_score, sample_weight=w_test)
# L414 [Executable statement]:     fig, ax = plt.subplots(figsize=(6, 6))
    fig, ax = plt.subplots(figsize=(6, 6))
# L415 [Executable statement]:     ax.plot(fpr, tpr, label=f'Test AUC = {auc_val:.4f}')
    ax.plot(fpr, tpr, label=f'Test AUC = {auc_val:.4f}')
# L416 [Executable statement]:     fpr_tr, tpr_tr, _ = roc_curve(y_train, train_score, sample_weight=w_train)
    fpr_tr, tpr_tr, _ = roc_curve(y_train, train_score, sample_weight=w_train)
# L417 [Executable statement]:     auc_tr = roc_auc_score(y_train, train_score, sample_weight=w_train)
    auc_tr = roc_auc_score(y_train, train_score, sample_weight=w_train)
# L418 [Executable statement]:     ax.plot(fpr_tr, tpr_tr, '--', label=f'Train AUC = {auc_tr:.4f}')
    ax.plot(fpr_tr, tpr_tr, '--', label=f'Train AUC = {auc_tr:.4f}')
# L419 [Executable statement]:     ax.plot([0, 1], [0, 1], 'k--', alpha=0.3)
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.3)
# L420 [Executable statement]:     ax.set_xlabel('False Positive Rate')
    ax.set_xlabel('False Positive Rate')
# L421 [Executable statement]:     ax.set_ylabel('True Positive Rate')
    ax.set_ylabel('True Positive Rate')
# L422 [Executable statement]:     ax.set_title('ROC Curve')
    ax.set_title('ROC Curve')
# L423 [Executable statement]:     ax.legend(loc='lower right')
    ax.legend(loc='lower right')
# L424 [Executable statement]:     add_fcc_label(ax)
    add_fcc_label(ax)
# L425 [Executable statement]:     fig.savefig(plot_dir / 'roc_curve.png', dpi=150, bbox_inches='tight')
    fig.savefig(plot_dir / 'roc_curve.png', dpi=150, bbox_inches='tight')
# L426 [Executable statement]:     fig.savefig(plot_dir / 'roc_curve.pdf', bbox_inches='tight')
    fig.savefig(plot_dir / 'roc_curve.pdf', bbox_inches='tight')
# L427 [Executable statement]:     plt.close()
    plt.close()
# L428 [Blank separator]: 

# L429 [Original comment]:     # 2. Signal efficiency vs background rejection
    # 2. Signal efficiency vs background rejection
# L430 [Executable statement]:     fig, ax = plt.subplots(figsize=(6, 6))
    fig, ax = plt.subplots(figsize=(6, 6))
# L431 [Executable statement]:     bkg_rej = 1 - fpr
    bkg_rej = 1 - fpr
# L432 [Executable statement]:     ax.plot(tpr, bkg_rej, label=f'Test AUC = {auc_val:.4f}')
    ax.plot(tpr, bkg_rej, label=f'Test AUC = {auc_val:.4f}')
# L433 [Executable statement]:     ax.set_xlabel('Signal Efficiency')
    ax.set_xlabel('Signal Efficiency')
# L434 [Executable statement]:     ax.set_ylabel('Background Rejection')
    ax.set_ylabel('Background Rejection')
# L435 [Executable statement]:     ax.set_title('Signal Efficiency vs Background Rejection')
    ax.set_title('Signal Efficiency vs Background Rejection')
# L436 [Executable statement]:     ax.legend()
    ax.legend()
# L437 [Executable statement]:     ax.set_xlim(0, 1)
    ax.set_xlim(0, 1)
# L438 [Executable statement]:     ax.set_ylim(0, 1)
    ax.set_ylim(0, 1)
# L439 [Executable statement]:     ax.grid(True, alpha=0.3)
    ax.grid(True, alpha=0.3)
# L440 [Executable statement]:     fig.savefig(plot_dir / 'sig_eff_vs_bkg_rej.png', dpi=150, bbox_inches='tight')
    fig.savefig(plot_dir / 'sig_eff_vs_bkg_rej.png', dpi=150, bbox_inches='tight')
# L441 [Executable statement]:     fig.savefig(plot_dir / 'sig_eff_vs_bkg_rej.pdf', bbox_inches='tight')
    fig.savefig(plot_dir / 'sig_eff_vs_bkg_rej.pdf', bbox_inches='tight')
# L442 [Executable statement]:     plt.close()
    plt.close()
# L443 [Blank separator]: 

# L444 [Original comment]:     # 3. BDT score distributions (overtraining check) - weighted
    # 3. BDT score distributions (overtraining check) - weighted
# L445 [Executable statement]:     fig, ax = plt.subplots(figsize=(8, 6))
    fig, ax = plt.subplots(figsize=(8, 6))
# L446 [Executable statement]:     bins = np.linspace(0, 1, 51)
    bins = np.linspace(0, 1, 51)
# L447 [Original comment]:     # Train - weighted
    # Train - weighted
# L448 [Executable statement]:     ax.hist(train_score[y_train == 1], bins=bins, weights=w_train[y_train == 1],
    ax.hist(train_score[y_train == 1], bins=bins, weights=w_train[y_train == 1],
# L449 [Executable statement]:             density=True, alpha=0.5,
            density=True, alpha=0.5,
# L450 [Executable statement]:             label='Signal (train)', color='blue', histtype='stepfilled')
            label='Signal (train)', color='blue', histtype='stepfilled')
# L451 [Executable statement]:     ax.hist(train_score[y_train == 0], bins=bins, weights=w_train[y_train == 0],
    ax.hist(train_score[y_train == 0], bins=bins, weights=w_train[y_train == 0],
# L452 [Executable statement]:             density=True, alpha=0.5,
            density=True, alpha=0.5,
# L453 [Executable statement]:             label='Background (train)', color='red', histtype='stepfilled')
            label='Background (train)', color='red', histtype='stepfilled')
# L454 [Original comment]:     # Test as points - weighted
    # Test as points - weighted
# L455 [Executable statement]:     h_sig, _ = np.histogram(test_score[y_test == 1], bins=bins,
    h_sig, _ = np.histogram(test_score[y_test == 1], bins=bins,
# L456 [Executable statement]:                              weights=w_test[y_test == 1], density=True)
                             weights=w_test[y_test == 1], density=True)
# L457 [Executable statement]:     h_bkg, _ = np.histogram(test_score[y_test == 0], bins=bins,
    h_bkg, _ = np.histogram(test_score[y_test == 0], bins=bins,
# L458 [Executable statement]:                              weights=w_test[y_test == 0], density=True)
                             weights=w_test[y_test == 0], density=True)
# L459 [Executable statement]:     centers = 0.5 * (bins[:-1] + bins[1:])
    centers = 0.5 * (bins[:-1] + bins[1:])
# L460 [Executable statement]:     ax.scatter(centers, h_sig, marker='o', s=20, color='blue',
    ax.scatter(centers, h_sig, marker='o', s=20, color='blue',
# L461 [Executable statement]:                label='Signal (test)', zorder=5)
               label='Signal (test)', zorder=5)
# L462 [Executable statement]:     ax.scatter(centers, h_bkg, marker='o', s=20, color='red',
    ax.scatter(centers, h_bkg, marker='o', s=20, color='red',
# L463 [Executable statement]:                label='Background (test)', zorder=5)
               label='Background (test)', zorder=5)
# L464 [Executable statement]:     ax.set_xlabel('BDT Score')
    ax.set_xlabel('BDT Score')
# L465 [Executable statement]:     ax.set_ylabel('Normalised (weighted)')
    ax.set_ylabel('Normalised (weighted)')
# L466 [Executable statement]:     ax.set_title('BDT Score Distribution (Overtraining Check)')
    ax.set_title('BDT Score Distribution (Overtraining Check)')
# L467 [Executable statement]:     ax.legend(fontsize=9)
    ax.legend(fontsize=9)
# L468 [Executable statement]:     add_fcc_label(ax, x=0.35, y=0.97)
    add_fcc_label(ax, x=0.35, y=0.97)
# L469 [Executable statement]:     fig.savefig(plot_dir / 'overtraining_check.png', dpi=150, bbox_inches='tight')
    fig.savefig(plot_dir / 'overtraining_check.png', dpi=150, bbox_inches='tight')
# L470 [Executable statement]:     fig.savefig(plot_dir / 'overtraining_check.pdf', bbox_inches='tight')
    fig.savefig(plot_dir / 'overtraining_check.pdf', bbox_inches='tight')
# L471 [Executable statement]:     plt.close()
    plt.close()
# L472 [Blank separator]: 

# L473 [Original comment]:     # 4. Feature importance
    # 4. Feature importance
# L474 [Executable statement]:     importance = pd.Series(model.feature_importances_, index=features).sort_values()
    importance = pd.Series(model.feature_importances_, index=features).sort_values()
# L475 [Executable statement]:     fig, ax = plt.subplots(figsize=(8, max(6, len(features) * 0.3)))
    fig, ax = plt.subplots(figsize=(8, max(6, len(features) * 0.3)))
# L476 [Executable statement]:     importance.plot(kind='barh', ax=ax)
    importance.plot(kind='barh', ax=ax)
# L477 [Executable statement]:     ax.set_xlabel('Feature Importance (Gain)')
    ax.set_xlabel('Feature Importance (Gain)')
# L478 [Executable statement]:     ax.set_title('Feature Importance')
    ax.set_title('Feature Importance')
# L479 [Executable statement]:     add_fcc_label(ax, x=0.60, y=0.97)
    add_fcc_label(ax, x=0.60, y=0.97)
# L480 [Executable statement]:     fig.savefig(plot_dir / 'feature_importance.png', dpi=150, bbox_inches='tight')
    fig.savefig(plot_dir / 'feature_importance.png', dpi=150, bbox_inches='tight')
# L481 [Executable statement]:     fig.savefig(plot_dir / 'feature_importance.pdf', bbox_inches='tight')
    fig.savefig(plot_dir / 'feature_importance.pdf', bbox_inches='tight')
# L482 [Executable statement]:     plt.close()
    plt.close()
# L483 [Blank separator]: 

# L484 [Original comment]:     # 5. Background sculpting check: BDT score vs Hcand_m
    # 5. Background sculpting check: BDT score vs Hcand_m
# L485 [Conditional block]:     if full_df_test is not None and 'Hcand_m' in full_df_test.columns:
    if full_df_test is not None and 'Hcand_m' in full_df_test.columns:
# L486 [Executable statement]:         bkg_mask = y_test == 0
        bkg_mask = y_test == 0
# L487 [Conditional block]:         if bkg_mask.sum() > 0:
        if bkg_mask.sum() > 0:
# L488 [Executable statement]:             fig, ax = plt.subplots(figsize=(8, 6))
            fig, ax = plt.subplots(figsize=(8, 6))
# L489 [Executable statement]:             sc = ax.scatter(
            sc = ax.scatter(
# L490 [Executable statement]:                 full_df_test.loc[bkg_mask, 'Hcand_m'],
                full_df_test.loc[bkg_mask, 'Hcand_m'],
# L491 [Executable statement]:                 test_score[bkg_mask],
                test_score[bkg_mask],
# L492 [Executable statement]:                 c=w_test[bkg_mask], cmap='viridis', s=2, alpha=0.5,
                c=w_test[bkg_mask], cmap='viridis', s=2, alpha=0.5,
# L493 [Executable statement]:             )
            )
# L494 [Executable statement]:             fig.colorbar(sc, ax=ax, label='Event weight')
            fig.colorbar(sc, ax=ax, label='Event weight')
# L495 [Executable statement]:             ax.set_xlabel('$m_{H,cand}$ [GeV]')
            ax.set_xlabel('$m_{H,cand}$ [GeV]')
# L496 [Executable statement]:             ax.set_ylabel('BDT Score')
            ax.set_ylabel('BDT Score')
# L497 [Executable statement]:             ax.set_title('Background Sculpting Check: BDT Score vs $m_{H,cand}$')
            ax.set_title('Background Sculpting Check: BDT Score vs $m_{H,cand}$')
# L498 [Executable statement]:             ax.axvline(125, color='red', linestyle='--', alpha=0.5, label='$m_H = 125$ GeV')
            ax.axvline(125, color='red', linestyle='--', alpha=0.5, label='$m_H = 125$ GeV')
# L499 [Executable statement]:             ax.legend()
            ax.legend()
# L500 [Executable statement]:             fig.savefig(plot_dir / 'sculpting_check.png', dpi=150, bbox_inches='tight')
            fig.savefig(plot_dir / 'sculpting_check.png', dpi=150, bbox_inches='tight')
# L501 [Executable statement]:             fig.savefig(plot_dir / 'sculpting_check.pdf', bbox_inches='tight')
            fig.savefig(plot_dir / 'sculpting_check.pdf', bbox_inches='tight')
# L502 [Executable statement]:             plt.close()
            plt.close()
# L503 [Blank separator]: 

# L504 [Original comment]:             # Profile plot: mean BDT score in Hcand_m bins
            # Profile plot: mean BDT score in Hcand_m bins
# L505 [Executable statement]:             fig, ax = plt.subplots(figsize=(8, 5))
            fig, ax = plt.subplots(figsize=(8, 5))
# L506 [Executable statement]:             m_bins = np.linspace(50, 200, 31)
            m_bins = np.linspace(50, 200, 31)
# L507 [Executable statement]:             m_centers = 0.5 * (m_bins[:-1] + m_bins[1:])
            m_centers = 0.5 * (m_bins[:-1] + m_bins[1:])
# L508 [Executable statement]:             bkg_hcand = full_df_test.loc[bkg_mask, 'Hcand_m'].values
            bkg_hcand = full_df_test.loc[bkg_mask, 'Hcand_m'].values
# L509 [Executable statement]:             bkg_scores = test_score[bkg_mask]
            bkg_scores = test_score[bkg_mask]
# L510 [Executable statement]:             bkg_w = w_test[bkg_mask]
            bkg_w = w_test[bkg_mask]
# L511 [Executable statement]:             mean_scores = []
            mean_scores = []
# L512 [Loop over iterable]:             for i in range(len(m_bins) - 1):
            for i in range(len(m_bins) - 1):
# L513 [Executable statement]:                 in_bin = (bkg_hcand >= m_bins[i]) & (bkg_hcand < m_bins[i+1])
                in_bin = (bkg_hcand >= m_bins[i]) & (bkg_hcand < m_bins[i+1])
# L514 [Conditional block]:                 if in_bin.sum() > 0:
                if in_bin.sum() > 0:
# L515 [Executable statement]:                     mean_scores.append(np.average(bkg_scores[in_bin], weights=bkg_w[in_bin]))
                    mean_scores.append(np.average(bkg_scores[in_bin], weights=bkg_w[in_bin]))
# L516 [Else branch]:                 else:
                else:
# L517 [Executable statement]:                     mean_scores.append(np.nan)
                    mean_scores.append(np.nan)
# L518 [Executable statement]:             ax.plot(m_centers, mean_scores, 'o-', color='red')
            ax.plot(m_centers, mean_scores, 'o-', color='red')
# L519 [Executable statement]:             ax.set_xlabel('$m_{H,cand}$ [GeV]')
            ax.set_xlabel('$m_{H,cand}$ [GeV]')
# L520 [Executable statement]:             ax.set_ylabel('Mean BDT Score (background)')
            ax.set_ylabel('Mean BDT Score (background)')
# L521 [Executable statement]:             ax.set_title('Background Sculpting Profile')
            ax.set_title('Background Sculpting Profile')
# L522 [Executable statement]:             ax.axvline(125, color='gray', linestyle='--', alpha=0.5)
            ax.axvline(125, color='gray', linestyle='--', alpha=0.5)
# L523 [Executable statement]:             ax.grid(True, alpha=0.3)
            ax.grid(True, alpha=0.3)
# L524 [Executable statement]:             fig.savefig(plot_dir / 'sculpting_profile.png', dpi=150, bbox_inches='tight')
            fig.savefig(plot_dir / 'sculpting_profile.png', dpi=150, bbox_inches='tight')
# L525 [Executable statement]:             fig.savefig(plot_dir / 'sculpting_profile.pdf', bbox_inches='tight')
            fig.savefig(plot_dir / 'sculpting_profile.pdf', bbox_inches='tight')
# L526 [Executable statement]:             plt.close()
            plt.close()
# L527 [Blank separator]: 

# L528 [Original comment]:     # 6. Per-sample score distributions
    # 6. Per-sample score distributions
# L529 [Conditional block]:     if full_df_test is not None and 'sample_name' in full_df_test.columns:
    if full_df_test is not None and 'sample_name' in full_df_test.columns:
# L530 [Executable statement]:         fig, ax = plt.subplots(figsize=(8, 6))
        fig, ax = plt.subplots(figsize=(8, 6))
# L531 [Executable statement]:         bins = np.linspace(0, 1, 51)
        bins = np.linspace(0, 1, 51)
# L532 [Loop over iterable]:         for sample_name in full_df_test['sample_name'].unique():
        for sample_name in full_df_test['sample_name'].unique():
# L533 [Executable statement]:             mask = full_df_test['sample_name'] == sample_name
            mask = full_df_test['sample_name'] == sample_name
# L534 [Conditional block]:             if mask.sum() == 0:
            if mask.sum() == 0:
# L535 [Executable statement]:                 continue
                continue
# L536 [Executable statement]:             short_name = sample_name.replace('wzp6_ee_', '').replace('p8_ee_', '').replace('_ecm240', '')
            short_name = sample_name.replace('wzp6_ee_', '').replace('p8_ee_', '').replace('_ecm240', '')
# L537 [Executable statement]:             ax.hist(test_score[mask], bins=bins, weights=w_test[mask],
            ax.hist(test_score[mask], bins=bins, weights=w_test[mask],
# L538 [Executable statement]:                     density=True, alpha=0.6, histtype='step', linewidth=1.5,
                    density=True, alpha=0.6, histtype='step', linewidth=1.5,
# L539 [Executable statement]:                     label=short_name)
                    label=short_name)
# L540 [Executable statement]:         ax.set_xlabel('BDT Score')
        ax.set_xlabel('BDT Score')
# L541 [Executable statement]:         ax.set_ylabel('Normalised (weighted)')
        ax.set_ylabel('Normalised (weighted)')
# L542 [Executable statement]:         ax.set_title('Per-Sample BDT Score Distributions (Test Set)')
        ax.set_title('Per-Sample BDT Score Distributions (Test Set)')
# L543 [Executable statement]:         ax.legend(fontsize=8, ncol=2)
        ax.legend(fontsize=8, ncol=2)
# L544 [Executable statement]:         fig.savefig(plot_dir / 'per_sample_scores.png', dpi=150, bbox_inches='tight')
        fig.savefig(plot_dir / 'per_sample_scores.png', dpi=150, bbox_inches='tight')
# L545 [Executable statement]:         fig.savefig(plot_dir / 'per_sample_scores.pdf', bbox_inches='tight')
        fig.savefig(plot_dir / 'per_sample_scores.pdf', bbox_inches='tight')
# L546 [Executable statement]:         plt.close()
        plt.close()
# L547 [Blank separator]: 

# L548 [Runtime log output]:     print(f'  Plots saved to {plot_dir}/')
    print(f'  Plots saved to {plot_dir}/')
# L549 [Blank separator]: 

# L550 [Blank separator]: 

# L551 [Function definition]: def kfold_score_all(X, y, w_phys, w_norm, full_df, best_params, n_folds=5, random_state=42, n_jobs=8):
def kfold_score_all(X, y, w_phys, w_norm, full_df, best_params, n_folds=5, random_state=42, n_jobs=8):
# L552 [Executable statement]:     """Score ALL events using k-fold cross-validation.
    """Score ALL events using k-fold cross-validation.
# L553 [Blank separator]: 

# L554 [Executable statement]:     Each event is scored by a model that was NOT trained on it.
    Each event is scored by a model that was NOT trained on it.
# L555 [Executable statement]:     This gives 100% of events with unbiased BDT scores for the fit,
    This gives 100% of events with unbiased BDT scores for the fit,
# L556 [Executable statement]:     instead of only the 30% test set.
    instead of only the 30% test set.
# L557 [Executable statement]:     """
    """
# L558 [Runtime log output]:     print(f'\n=== {n_folds}-Fold Cross-Validation Scoring ===')
    print(f'\n=== {n_folds}-Fold Cross-Validation Scoring ===')
# L559 [Executable statement]:     skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=random_state)
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=random_state)
# L560 [Blank separator]: 

# L561 [Executable statement]:     scores = np.zeros(len(X))
    scores = np.zeros(len(X))
# L562 [Loop over iterable]:     for fold_i, (train_idx, val_idx) in enumerate(skf.split(X, y)):
    for fold_i, (train_idx, val_idx) in enumerate(skf.split(X, y)):
# L563 [Executable statement]:         X_t, y_t, w_t = X.iloc[train_idx], y.iloc[train_idx], w_norm.iloc[train_idx]
        X_t, y_t, w_t = X.iloc[train_idx], y.iloc[train_idx], w_norm.iloc[train_idx]
# L564 [Executable statement]:         X_v = X.iloc[val_idx]
        X_v = X.iloc[val_idx]
# L565 [Executable statement]:         model_k, best_iteration, _, _, _ = fit_with_early_stopping(
        model_k, best_iteration, _, _, _ = fit_with_early_stopping(
# L566 [Executable statement]:             X_t, y_t, w_t, best_params,
            X_t, y_t, w_t, best_params,
# L567 [Executable statement]:             random_state=random_state + fold_i,
            random_state=random_state + fold_i,
# L568 [Executable statement]:             n_jobs=n_jobs,
            n_jobs=n_jobs,
# L569 [Executable statement]:             eval_metric='auc',
            eval_metric='auc',
# L570 [Executable statement]:         )
        )
# L571 [Executable statement]:         scores[val_idx] = model_k.predict_proba(X_v)[:, 1]
        scores[val_idx] = model_k.predict_proba(X_v)[:, 1]
# L572 [Executable statement]:         auc_k = roc_auc_score(y.iloc[val_idx], scores[val_idx],
        auc_k = roc_auc_score(y.iloc[val_idx], scores[val_idx],
# L573 [Executable statement]:                               sample_weight=w_phys.iloc[val_idx])
                              sample_weight=w_phys.iloc[val_idx])
# L574 [Executable statement]:         best_iter_text = 'NA' if best_iteration is None else str(best_iteration + 1)
        best_iter_text = 'NA' if best_iteration is None else str(best_iteration + 1)
# L575 [Runtime log output]:         print(f'  Fold {fold_i+1}/{n_folds}: AUC={auc_k:.4f} '
        print(f'  Fold {fold_i+1}/{n_folds}: AUC={auc_k:.4f} '
# L576 [Executable statement]:               f'({len(val_idx)} events, {best_iter_text} trees)')
              f'({len(val_idx)} events, {best_iter_text} trees)')
# L577 [Blank separator]: 

# L578 [Executable statement]:     overall_auc = roc_auc_score(y, scores, sample_weight=w_phys)
    overall_auc = roc_auc_score(y, scores, sample_weight=w_phys)
# L579 [Runtime log output]:     print(f'  Overall k-fold AUC: {overall_auc:.4f}')
    print(f'  Overall k-fold AUC: {overall_auc:.4f}')
# L580 [Blank separator]: 

# L581 [Executable statement]:     kfold_df = pd.DataFrame({
    kfold_df = pd.DataFrame({
# L582 [Executable statement]:         'y_true': y.to_numpy(),
        'y_true': y.to_numpy(),
# L583 [Executable statement]:         'phys_weight': w_phys.to_numpy(),
        'phys_weight': w_phys.to_numpy(),
# L584 [Executable statement]:         'bdt_score': scores,
        'bdt_score': scores,
# L585 [Executable statement]:         'sample_name': full_df['sample_name'].to_numpy(),
        'sample_name': full_df['sample_name'].to_numpy(),
# L586 [Executable statement]:     })
    })
# L587 [Function return]:     return kfold_df, overall_auc
    return kfold_df, overall_auc
# L588 [Blank separator]: 

# L589 [Blank separator]: 

# L590 [Function definition]: def main():
def main():
# L591 [Executable statement]:     args = parse_args()
    args = parse_args()
# L592 [Executable statement]:     output_dir = Path(args.output_dir)
    output_dir = Path(args.output_dir)
# L593 [Executable statement]:     output_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
# L594 [Blank separator]: 

# L595 [Runtime log output]:     print('=== Loading Data ===')
    print('=== Loading Data ===')
# L596 [Runtime log output]:     print(
    print(
# L597 [Executable statement]:         'Background fractions: '
        'Background fractions: '
# L598 [Executable statement]:         f"WW={BACKGROUND_FRACTIONS['ww']:.6g}, "
        f"WW={BACKGROUND_FRACTIONS['ww']:.6g}, "
# L599 [Executable statement]:         f"ZZ={BACKGROUND_FRACTIONS['zz']:.6g}, "
        f"ZZ={BACKGROUND_FRACTIONS['zz']:.6g}, "
# L600 [Executable statement]:         f"qq={BACKGROUND_FRACTIONS['qq']:.6g}, "
        f"qq={BACKGROUND_FRACTIONS['qq']:.6g}, "
# L601 [Executable statement]:         f"tautau={BACKGROUND_FRACTIONS['tautau']:.6g}"
        f"tautau={BACKGROUND_FRACTIONS['tautau']:.6g}"
# L602 [Executable statement]:     )
    )
# L603 [Runtime log output]:     print('Signal:')
    print('Signal:')
# L604 [Executable statement]:     sig_df = read_samples(args.input_dir, args.tree_name,
    sig_df = read_samples(args.input_dir, args.tree_name,
# L605 [Executable statement]:                           args.signal_samples, args.features, 1)
                          args.signal_samples, args.features, 1)
# L606 [Runtime log output]:     print('Background:')
    print('Background:')
# L607 [Executable statement]:     bkg_df = read_samples(args.input_dir, args.tree_name,
    bkg_df = read_samples(args.input_dir, args.tree_name,
# L608 [Executable statement]:                           args.background_samples, args.features, 0)
                          args.background_samples, args.features, 0)
# L609 [Executable statement]:     full_df = pd.concat([sig_df, bkg_df], ignore_index=True)
    full_df = pd.concat([sig_df, bkg_df], ignore_index=True)
# L610 [Blank separator]: 

# L611 [Original comment]:     # Use only features that exist in the data
    # Use only features that exist in the data
# L612 [Executable statement]:     available_features = [f for f in args.features if f in full_df.columns]
    available_features = [f for f in args.features if f in full_df.columns]
# L613 [Executable statement]:     missing_features = [f for f in args.features if f not in full_df.columns]
    missing_features = [f for f in args.features if f not in full_df.columns]
# L614 [Conditional block]:     if missing_features:
    if missing_features:
# L615 [Runtime log output]:         print(f'[warn] Missing features (will skip): {missing_features}')
        print(f'[warn] Missing features (will skip): {missing_features}')
# L616 [Runtime log output]:     print(f'\nUsing {len(available_features)} features')
    print(f'\nUsing {len(available_features)} features')
# L617 [Blank separator]: 

# L618 [Executable statement]:     X = full_df[available_features].copy()
    X = full_df[available_features].copy()
# L619 [Executable statement]:     y = full_df['label']
    y = full_df['label']
# L620 [Executable statement]:     w = full_df['phys_weight'].astype(float)
    w = full_df['phys_weight'].astype(float)
# L621 [Blank separator]: 

# L622 [Original comment]:     # Fix sentinel values: missingMass uses -999 for undefined cases
    # Fix sentinel values: missingMass uses -999 for undefined cases
# L623 [Conditional block]:     if 'missingMass' in X.columns:
    if 'missingMass' in X.columns:
# L624 [Executable statement]:         n_sentinel = (X['missingMass'] < -900).sum()
        n_sentinel = (X['missingMass'] < -900).sum()
# L625 [Conditional block]:         if n_sentinel > 0:
        if n_sentinel > 0:
# L626 [Runtime log output]:             print(f'[fix] Replacing {n_sentinel} missingMass sentinel values (-999) with 0')
            print(f'[fix] Replacing {n_sentinel} missingMass sentinel values (-999) with 0')
# L627 [Executable statement]:             X.loc[X['missingMass'] < -900, 'missingMass'] = 0.0
            X.loc[X['missingMass'] < -900, 'missingMass'] = 0.0
# L628 [Blank separator]: 

# L629 [Original comment]:     # Report class balance with physics weights
    # Report class balance with physics weights
# L630 [Executable statement]:     sig_weighted = w[y == 1].sum()
    sig_weighted = w[y == 1].sum()
# L631 [Executable statement]:     bkg_weighted = w[y == 0].sum()
    bkg_weighted = w[y == 0].sum()
# L632 [Runtime log output]:     print(f'\n=== Class Balance (physics-weighted) ===')
    print(f'\n=== Class Balance (physics-weighted) ===')
# L633 [Runtime log output]:     print(f'  Signal:     {(y==1).sum()} events, weighted sum = {sig_weighted:.0f}')
    print(f'  Signal:     {(y==1).sum()} events, weighted sum = {sig_weighted:.0f}')
# L634 [Runtime log output]:     print(f'  Background: {(y==0).sum()} events, weighted sum = {bkg_weighted:.0f}')
    print(f'  Background: {(y==0).sum()} events, weighted sum = {bkg_weighted:.0f}')
# L635 [Runtime log output]:     print(f'  Weighted ratio bkg/sig = {bkg_weighted/sig_weighted:.1f}')
    print(f'  Weighted ratio bkg/sig = {bkg_weighted/sig_weighted:.1f}')
# L636 [Blank separator]: 

# L637 [Original comment]:     # Normalize class weights for balanced learning (ML review item 4)
    # Normalize class weights for balanced learning (ML review item 4)
# L638 [Executable statement]:     w_normalized = normalize_class_weights(w, y)
    w_normalized = normalize_class_weights(w, y)
# L639 [Blank separator]: 

# L640 [Original comment]:     # Single index-based split to guarantee consistency across all arrays
    # Single index-based split to guarantee consistency across all arrays
# L641 [Executable statement]:     indices = np.arange(len(X))
    indices = np.arange(len(X))
# L642 [Executable statement]:     idx_train, idx_test = train_test_split(
    idx_train, idx_test = train_test_split(
# L643 [Executable statement]:         indices, test_size=args.test_size,
        indices, test_size=args.test_size,
# L644 [Executable statement]:         random_state=args.random_state, stratify=y,
        random_state=args.random_state, stratify=y,
# L645 [Executable statement]:     )
    )
# L646 [Executable statement]:     X_train, X_test = X.iloc[idx_train], X.iloc[idx_test]
    X_train, X_test = X.iloc[idx_train], X.iloc[idx_test]
# L647 [Executable statement]:     y_train, y_test = y.iloc[idx_train], y.iloc[idx_test]
    y_train, y_test = y.iloc[idx_train], y.iloc[idx_test]
# L648 [Executable statement]:     w_train, w_test = w_normalized.iloc[idx_train], w_normalized.iloc[idx_test]
    w_train, w_test = w_normalized.iloc[idx_train], w_normalized.iloc[idx_test]
# L649 [Executable statement]:     w_phys_train, w_phys_test = w.iloc[idx_train], w.iloc[idx_test]
    w_phys_train, w_phys_test = w.iloc[idx_train], w.iloc[idx_test]
# L650 [Executable statement]:     full_df_test = full_df.iloc[idx_test]
    full_df_test = full_df.iloc[idx_test]
# L651 [Blank separator]: 

# L652 [Original comment]:     # Hyperparameter search
    # Hyperparameter search
# L653 [Conditional block]:     if not args.no_grid_search:
    if not args.no_grid_search:
# L654 [Executable statement]:         best_params, grid_results = grid_search(
        best_params, grid_results = grid_search(
# L655 [Executable statement]:             X_train, y_train, w_train, args.random_state, args.n_jobs
            X_train, y_train, w_train, args.random_state, args.n_jobs
# L656 [Executable statement]:         )
        )
# L657 [Original comment]:         # Save grid search results
        # Save grid search results
# L658 [Executable statement]:         pd.DataFrame(grid_results).to_csv(
        pd.DataFrame(grid_results).to_csv(
# L659 [Executable statement]:             output_dir / 'grid_search_results.csv', index=False
            output_dir / 'grid_search_results.csv', index=False
# L660 [Executable statement]:         )
        )
# L661 [Else branch]:     else:
    else:
# L662 [Executable statement]:         best_params = {
        best_params = {
# L663 [Executable statement]:             'max_depth': 4, 'learning_rate': 0.05, 'n_estimators': 1000,
            'max_depth': 4, 'learning_rate': 0.05, 'n_estimators': 1000,
# L664 [Executable statement]:             'min_child_weight': 5, 'subsample': 0.8, 'colsample_bytree': 0.8,
            'min_child_weight': 5, 'subsample': 0.8, 'colsample_bytree': 0.8,
# L665 [Executable statement]:         }
        }
# L666 [Executable statement]:         grid_results = []
        grid_results = []
# L667 [Blank separator]: 

# L668 [Original comment]:     # Train final model with a held-out validation split for early stopping.
    # Train final model with a held-out validation split for early stopping.
# L669 [Original comment]:     # The test sample is kept untouched for the performance report.
    # The test sample is kept untouched for the performance report.
# L670 [Runtime log output]:     print(f'\n=== Training Final Model ===')
    print(f'\n=== Training Final Model ===')
# L671 [Runtime log output]:     print(f'  Params: {best_params}')
    print(f'  Params: {best_params}')
# L672 [Executable statement]:     model, best_iteration, final_n_estimators, val_auc, training_history = fit_with_early_stopping(
    model, best_iteration, final_n_estimators, val_auc, training_history = fit_with_early_stopping(
# L673 [Executable statement]:         X_train, y_train, w_train, best_params,
        X_train, y_train, w_train, best_params,
# L674 [Executable statement]:         random_state=args.random_state,
        random_state=args.random_state,
# L675 [Executable statement]:         n_jobs=args.n_jobs,
        n_jobs=args.n_jobs,
# L676 [Executable statement]:         eval_metric=['logloss', 'auc'],
        eval_metric=['logloss', 'auc'],
# L677 [Executable statement]:     )
    )
# L678 [Runtime log output]:     print(f'  Validation AUC (held-out from training): {val_auc:.4f}')
    print(f'  Validation AUC (held-out from training): {val_auc:.4f}')
# L679 [Runtime log output]:     print(f'  Trees kept after early stopping: {final_n_estimators}')
    print(f'  Trees kept after early stopping: {final_n_estimators}')
# L680 [Blank separator]: 

# L681 [Executable statement]:     train_score = model.predict_proba(X_train)[:, 1]
    train_score = model.predict_proba(X_train)[:, 1]
# L682 [Executable statement]:     test_score = model.predict_proba(X_test)[:, 1]
    test_score = model.predict_proba(X_test)[:, 1]
# L683 [Blank separator]: 

# L684 [Original comment]:     # Weighted AUC (use physics weights for evaluation, not normalized)
    # Weighted AUC (use physics weights for evaluation, not normalized)
# L685 [Executable statement]:     train_auc = roc_auc_score(y_train, train_score, sample_weight=w_phys_train)
    train_auc = roc_auc_score(y_train, train_score, sample_weight=w_phys_train)
# L686 [Executable statement]:     test_auc = roc_auc_score(y_test, test_score, sample_weight=w_phys_test)
    test_auc = roc_auc_score(y_test, test_score, sample_weight=w_phys_test)
# L687 [Blank separator]: 

# L688 [Original comment]:     # Overtraining check: weighted KS test (binned chi2) on signal and background
    # Overtraining check: weighted KS test (binned chi2) on signal and background
# L689 [Executable statement]:     ks_sig_chi2, ks_sig_p = weighted_ks_test(
    ks_sig_chi2, ks_sig_p = weighted_ks_test(
# L690 [Executable statement]:         train_score[y_train == 1], w_train[y_train == 1],
        train_score[y_train == 1], w_train[y_train == 1],
# L691 [Executable statement]:         test_score[y_test == 1], w_test[y_test == 1],
        test_score[y_test == 1], w_test[y_test == 1],
# L692 [Executable statement]:     )
    )
# L693 [Executable statement]:     ks_bkg_chi2, ks_bkg_p = weighted_ks_test(
    ks_bkg_chi2, ks_bkg_p = weighted_ks_test(
# L694 [Executable statement]:         train_score[y_train == 0], w_train[y_train == 0],
        train_score[y_train == 0], w_train[y_train == 0],
# L695 [Executable statement]:         test_score[y_test == 0], w_test[y_test == 0],
        test_score[y_test == 0], w_test[y_test == 0],
# L696 [Executable statement]:     )
    )
# L697 [Original comment]:     # Also compute unweighted KS for comparison
    # Also compute unweighted KS for comparison
# L698 [Executable statement]:     ks_sig_uw = ks_2samp(train_score[y_train == 1], test_score[y_test == 1])
    ks_sig_uw = ks_2samp(train_score[y_train == 1], test_score[y_test == 1])
# L699 [Executable statement]:     ks_bkg_uw = ks_2samp(train_score[y_train == 0], test_score[y_test == 0])
    ks_bkg_uw = ks_2samp(train_score[y_train == 0], test_score[y_test == 0])
# L700 [Blank separator]: 

# L701 [Runtime log output]:     print(f'\n=== Results ===')
    print(f'\n=== Results ===')
# L702 [Runtime log output]:     print(f'  Train AUC: {train_auc:.4f}')
    print(f'  Train AUC: {train_auc:.4f}')
# L703 [Runtime log output]:     print(f'  Test AUC:  {test_auc:.4f}')
    print(f'  Test AUC:  {test_auc:.4f}')
# L704 [Runtime log output]:     print(f'  |delta AUC|:    {abs(train_auc - test_auc):.4f}')
    print(f'  |delta AUC|:    {abs(train_auc - test_auc):.4f}')
# L705 [Runtime log output]:     print(f'  Weighted chi2/ndf (signal):     {ks_sig_chi2:.2f}, p={ks_sig_p:.4f}')
    print(f'  Weighted chi2/ndf (signal):     {ks_sig_chi2:.2f}, p={ks_sig_p:.4f}')
# L706 [Runtime log output]:     print(f'  Weighted chi2/ndf (background): {ks_bkg_chi2:.2f}, p={ks_bkg_p:.4f}')
    print(f'  Weighted chi2/ndf (background): {ks_bkg_chi2:.2f}, p={ks_bkg_p:.4f}')
# L707 [Runtime log output]:     print(f'  Unweighted KS (signal):     stat={ks_sig_uw.statistic:.4f}, p={ks_sig_uw.pvalue:.4f}')
    print(f'  Unweighted KS (signal):     stat={ks_sig_uw.statistic:.4f}, p={ks_sig_uw.pvalue:.4f}')
# L708 [Runtime log output]:     print(f'  Unweighted KS (background): stat={ks_bkg_uw.statistic:.4f}, p={ks_bkg_uw.pvalue:.4f}')
    print(f'  Unweighted KS (background): stat={ks_bkg_uw.statistic:.4f}, p={ks_bkg_uw.pvalue:.4f}')
# L709 [Original comment]:     # Use KS statistic (not p-value) for overtraining check — p-value is too
    # Use KS statistic (not p-value) for overtraining check — p-value is too
# L710 [Original comment]:     # sensitive with large samples and flags negligible differences.
    # sensitive with large samples and flags negligible differences.
# L711 [Executable statement]:     overtraining = (abs(train_auc - test_auc) > 0.02
    overtraining = (abs(train_auc - test_auc) > 0.02
# L712 [Executable statement]:                     or ks_sig_uw.statistic > 0.05
                    or ks_sig_uw.statistic > 0.05
# L713 [Executable statement]:                     or ks_bkg_uw.statistic > 0.05)
                    or ks_bkg_uw.statistic > 0.05)
# L714 [Runtime log output]:     print(f'  Overtraining: {"WARNING!" if overtraining else "OK"}')
    print(f'  Overtraining: {"WARNING!" if overtraining else "OK"}')
# L715 [Blank separator]: 

# L716 [Executable statement]:     serializable_history = {}
    serializable_history = {}
# L717 [Loop over iterable]:     for ds_name, ds_metrics in training_history.items():
    for ds_name, ds_metrics in training_history.items():
# L718 [Executable statement]:         serializable_history[ds_name] = {
        serializable_history[ds_name] = {
# L719 [Executable statement]:             k: [float(v) for v in vals] for k, vals in ds_metrics.items()
            k: [float(v) for v in vals] for k, vals in ds_metrics.items()
# L720 [Executable statement]:         }
        }
# L721 [Blank separator]: 

# L722 [Executable statement]:     metrics = {
    metrics = {
# L723 [Executable statement]:         'train_auc': float(train_auc),
        'train_auc': float(train_auc),
# L724 [Executable statement]:         'test_auc': float(test_auc),
        'test_auc': float(test_auc),
# L725 [Executable statement]:         'validation_auc': float(val_auc),
        'validation_auc': float(val_auc),
# L726 [Executable statement]:         'delta_auc': float(abs(train_auc - test_auc)),
        'delta_auc': float(abs(train_auc - test_auc)),
# L727 [Executable statement]:         'weighted_chi2_signal': float(ks_sig_chi2),
        'weighted_chi2_signal': float(ks_sig_chi2),
# L728 [Executable statement]:         'weighted_chi2_signal_pvalue': float(ks_sig_p),
        'weighted_chi2_signal_pvalue': float(ks_sig_p),
# L729 [Executable statement]:         'weighted_chi2_background': float(ks_bkg_chi2),
        'weighted_chi2_background': float(ks_bkg_chi2),
# L730 [Executable statement]:         'weighted_chi2_background_pvalue': float(ks_bkg_p),
        'weighted_chi2_background_pvalue': float(ks_bkg_p),
# L731 [Executable statement]:         'ks_signal_stat': float(ks_sig_uw.statistic),
        'ks_signal_stat': float(ks_sig_uw.statistic),
# L732 [Executable statement]:         'ks_signal_pvalue': float(ks_sig_uw.pvalue),
        'ks_signal_pvalue': float(ks_sig_uw.pvalue),
# L733 [Executable statement]:         'ks_background_stat': float(ks_bkg_uw.statistic),
        'ks_background_stat': float(ks_bkg_uw.statistic),
# L734 [Executable statement]:         'ks_background_pvalue': float(ks_bkg_uw.pvalue),
        'ks_background_pvalue': float(ks_bkg_uw.pvalue),
# L735 [Executable statement]:         'overtraining_flag': bool(overtraining),
        'overtraining_flag': bool(overtraining),
# L736 [Executable statement]:         'n_train': int(len(X_train)),
        'n_train': int(len(X_train)),
# L737 [Executable statement]:         'n_test': int(len(X_test)),
        'n_test': int(len(X_test)),
# L738 [Executable statement]:         'n_signal_train': int((y_train == 1).sum()),
        'n_signal_train': int((y_train == 1).sum()),
# L739 [Executable statement]:         'n_background_train': int((y_train == 0).sum()),
        'n_background_train': int((y_train == 0).sum()),
# L740 [Executable statement]:         'weighted_signal_sum': float(sig_weighted),
        'weighted_signal_sum': float(sig_weighted),
# L741 [Executable statement]:         'weighted_background_sum': float(bkg_weighted),
        'weighted_background_sum': float(bkg_weighted),
# L742 [Executable statement]:         'features': available_features,
        'features': available_features,
# L743 [Executable statement]:         'best_hyperparameters': best_params,
        'best_hyperparameters': best_params,
# L744 [Executable statement]:         'early_stopping_best_iteration': int(best_iteration + 1)
        'early_stopping_best_iteration': int(best_iteration + 1)
# L745 [Conditional block]:             if best_iteration is not None else best_params['n_estimators'],
            if best_iteration is not None else best_params['n_estimators'],
# L746 [Executable statement]:         'weight_normalization': 'class-balanced',
        'weight_normalization': 'class-balanced',
# L747 [Executable statement]:         'validation_fraction': 0.20,
        'validation_fraction': 0.20,
# L748 [Executable statement]:     }
    }
# L749 [Blank separator]: 

# L750 [Executable statement]:     model_path = output_dir / 'xgboost_bdt.json'
    model_path = output_dir / 'xgboost_bdt.json'
# L751 [Executable statement]:     model.save_model(model_path)
    model.save_model(model_path)
# L752 [Blank separator]: 

# L753 [Context manager block]:     with open(output_dir / 'training_metrics.json', 'w') as handle:
    with open(output_dir / 'training_metrics.json', 'w') as handle:
# L754 [Executable statement]:         json.dump(metrics, handle, indent=2, sort_keys=True)
        json.dump(metrics, handle, indent=2, sort_keys=True)
# L755 [Blank separator]: 

# L756 [Original comment]:     # Save training history separately (can be large)
    # Save training history separately (can be large)
# L757 [Conditional block]:     if serializable_history:
    if serializable_history:
# L758 [Context manager block]:         with open(output_dir / 'training_history.json', 'w') as handle:
        with open(output_dir / 'training_history.json', 'w') as handle:
# L759 [Executable statement]:             json.dump(serializable_history, handle, indent=2)
            json.dump(serializable_history, handle, indent=2)
# L760 [Blank separator]: 

# L761 [Executable statement]:     importance = pd.Series(
    importance = pd.Series(
# L762 [Executable statement]:         model.feature_importances_, index=available_features
        model.feature_importances_, index=available_features
# L763 [Executable statement]:     ).sort_values(ascending=False)
    ).sort_values(ascending=False)
# L764 [Executable statement]:     importance.to_csv(output_dir / 'feature_importance.csv', header=['importance'])
    importance.to_csv(output_dir / 'feature_importance.csv', header=['importance'])
# L765 [Blank separator]: 

# L766 [Executable statement]:     pd.DataFrame({
    pd.DataFrame({
# L767 [Executable statement]:         'y_true': y_test.to_numpy(),
        'y_true': y_test.to_numpy(),
# L768 [Executable statement]:         'phys_weight': w_phys_test.to_numpy(),
        'phys_weight': w_phys_test.to_numpy(),
# L769 [Executable statement]:         'norm_weight': w_test.to_numpy(),
        'norm_weight': w_test.to_numpy(),
# L770 [Executable statement]:         'bdt_score': test_score,
        'bdt_score': test_score,
# L771 [Executable statement]:         'sample_name': full_df_test['sample_name'].to_numpy(),
        'sample_name': full_df_test['sample_name'].to_numpy(),
# L772 [Executable statement]:     }).to_csv(output_dir / 'test_scores.csv', index=False)
    }).to_csv(output_dir / 'test_scores.csv', index=False)
# L773 [Blank separator]: 

# L774 [Original comment]:     # Diagnostic plots
    # Diagnostic plots
# L775 [Conditional block]:     if not args.no_plots:
    if not args.no_plots:
# L776 [Executable statement]:         make_plots(output_dir, y_train, y_test, train_score, test_score,
        make_plots(output_dir, y_train, y_test, train_score, test_score,
# L777 [Executable statement]:                    w_phys_train, w_phys_test, model, available_features,
                   w_phys_train, w_phys_test, model, available_features,
# L778 [Executable statement]:                    full_df_test=full_df_test)
                   full_df_test=full_df_test)
# L779 [Blank separator]: 

# L780 [Original comment]:     # K-fold cross-validation scoring (all events get unbiased scores)
    # K-fold cross-validation scoring (all events get unbiased scores)
# L781 [Conditional block]:     if args.kfold > 0:
    if args.kfold > 0:
# L782 [Executable statement]:         kfold_df, kfold_auc = kfold_score_all(
        kfold_df, kfold_auc = kfold_score_all(
# L783 [Executable statement]:             X, y, w, w_normalized, full_df, best_params,
            X, y, w, w_normalized, full_df, best_params,
# L784 [Executable statement]:             n_folds=args.kfold, random_state=args.random_state, n_jobs=args.n_jobs,
            n_folds=args.kfold, random_state=args.random_state, n_jobs=args.n_jobs,
# L785 [Executable statement]:         )
        )
# L786 [Executable statement]:         kfold_df.to_csv(output_dir / 'kfold_scores.csv', index=False)
        kfold_df.to_csv(output_dir / 'kfold_scores.csv', index=False)
# L787 [Runtime log output]:         print(f'  k-fold scores saved ({len(kfold_df)} events, AUC={kfold_auc:.4f})')
        print(f'  k-fold scores saved ({len(kfold_df)} events, AUC={kfold_auc:.4f})')
# L788 [Blank separator]: 

# L789 [Runtime log output]:     print(f'\n  model: {model_path}')
    print(f'\n  model: {model_path}')
# L790 [Runtime log output]:     print(f'  test AUC: {test_auc:.4f}')
    print(f'  test AUC: {test_auc:.4f}')
# L791 [Runtime log output]:     print(f'  features: {len(available_features)}')
    print(f'  features: {len(available_features)}')
# L792 [Runtime log output]:     print('Done.')
    print('Done.')
# L793 [Blank separator]: 

# L794 [Blank separator]: 

# L795 [Conditional block]: if __name__ == '__main__':
if __name__ == '__main__':
# L796 [Executable statement]:     main()
    main()
