#!/usr/bin/env python3
# Inference wrapper to push trained BDT into treemaker ntuples and persist score branches.
#
# This stage is physics-to-statistics boundary code:
# model output lives in the event trees and becomes the fit observable distribution.

"""Apply a trained XGBoost BDT to lvqq treemaker ntuples and write scored ROOT files.

This is the physics-to-statistics transfer stage:
- each event gets one scalar score from the trained multi-input classifier,
- that score becomes the observable for likelihood and uncertainty extraction.
- in the current repository, however, the default likelihood script still reads
  `kfold_scores.csv` / `test_scores.csv` from training outputs; these ROOT files
  are the exported scored-ntuple branch for inspection and reuse.
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
import uproot
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import xgboost as xgb

# [Workflow] Configuration binding; this line defines a stable contract across modules.
THIS_DIR = Path(__file__).resolve().parent
# [Workflow] Configuration binding; this line defines a stable contract across modules.
ANALYSIS_DIR = THIS_DIR.parent
# [Context] Supporting line for the active lvqq analysis stage.
sys.path.insert(0, str(ANALYSIS_DIR))

# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
from ml_config import (
# [Context] Supporting line for the active lvqq analysis stage.
    BACKGROUND_SAMPLES,
# [Context] Supporting line for the active lvqq analysis stage.
    DEFAULT_MODEL_DIR,
# [Context] Supporting line for the active lvqq analysis stage.
    DEFAULT_SCORE_BRANCH,
# [Context] Supporting line for the active lvqq analysis stage.
    DEFAULT_TREE_NAME,
# [Context] Supporting line for the active lvqq analysis stage.
    DEFAULT_TREEMAKER_DIR,
# [Context] Supporting line for the active lvqq analysis stage.
    ML_FEATURES,
# [Context] Supporting line for the active lvqq analysis stage.
    SIGNAL_SAMPLES,
# [Context] Supporting line for the active lvqq analysis stage.
)


# [Workflow] apply_xgboost_bdt.py function parse_args: modularize one operation for deterministic pipeline control.
def parse_args():
    # [Workflow] CLI is a compatibility layer; defaults align with training outputs.
    # Keep these args explicit because inference is often run long after training
    # and reproducibility depends on exact sample/model/branch choices.
# [Context] Supporting line for the active lvqq analysis stage.
    parser = argparse.ArgumentParser(description=__doc__)
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument('--input-dir', default=DEFAULT_TREEMAKER_DIR)
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument('--output-dir', default='output/h_hww_lvqq/bdt_scored/ecm240')
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument('--tree-name', default=DEFAULT_TREE_NAME)
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument('--model', default=str(Path(DEFAULT_MODEL_DIR) / 'xgboost_bdt.json'))
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument('--features-json', default=str(Path(DEFAULT_MODEL_DIR) / 'training_metrics.json'))
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument('--samples', nargs='*', default=SIGNAL_SAMPLES + BACKGROUND_SAMPLES)
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument('--score-branch', default=DEFAULT_SCORE_BRANCH)
# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return parser.parse_args()


# [Workflow] Keep feature contract in sync with the training artifact.
def load_features(features_json):
    # [ML] Contract check:
    # training saves the exact feature list; we prefer it over hard-coded defaults to prevent schema drift.
    # This prevents training/inference mismatch where identical physics events are embedded
    # into different feature orderings, which changes score semantics.
# [Context] Supporting line for the active lvqq analysis stage.
    path = Path(features_json)
# [Context] Supporting line for the active lvqq analysis stage.
    if path.exists():
# [Context] Supporting line for the active lvqq analysis stage.
        with open(path, 'r', encoding='ascii') as handle:
# [Workflow] Persist contracts and fit outputs to make every stage auditable.
            payload = json.load(handle)
# [Workflow] Return value hands the constructed object/metric to the next module stage.
        return payload.get('features', ML_FEATURES)
# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return ML_FEATURES


# [I/O] Skip 0-pass or malformed trees safely to avoid broken scored outputs.
def get_tree_status(root_file, tree_name):
    # Same tree-health guard as in training. A 0-pass or malformed ROOT chunk is
    # a production-level failure mode in large FCCAnalyses campaigns.
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


# [ML] Score each required sample and persist score branches for statistical inference.
def main():
    # [Physics/Stats] Apply once per sample and keep 1:1 feature alignment with training.
    # Scores are stored as a float32 branch for compact downstream I/O.
# [Context] Supporting line for the active lvqq analysis stage.
    args = parse_args()
# [Context] Supporting line for the active lvqq analysis stage.
    features = load_features(args.features_json)
# [Context] Supporting line for the active lvqq analysis stage.
    input_dir = Path(args.input_dir)
# [Context] Supporting line for the active lvqq analysis stage.
    output_dir = Path(args.output_dir)
# [Context] Supporting line for the active lvqq analysis stage.
    output_dir.mkdir(parents=True, exist_ok=True)

    # Model replay protocol: load exact serialized forest and apply it sample-by-sample;
    # this is the deterministic boundary between training and all downstream statistics.
    # If this step is decoupled, tiny upstream changes (features, branches, scaling)
    # can turn scores into a different observable and invalidate all downstream fits.

# [ML] Core estimator family (XGBoost) for non-linear kinematic separation.
    # instantiate then load serialized state to guarantee exact model replay.
    model = xgb.XGBClassifier()
# [Context] Supporting line for the active lvqq analysis stage.
    model.load_model(args.model)

    # Physics meaning:
    # each ROOT sample is transformed independently, so you can trace each scored output
    # back to its dataset and preserve per-process templates in fit stage.
# [Context] Supporting line for the active lvqq analysis stage.
    for sample in args.samples:
# [Context] Supporting line for the active lvqq analysis stage.
        in_path = input_dir / f'{sample}.root'
# [Context] Supporting line for the active lvqq analysis stage.
        if not in_path.exists():
# [Context] Supporting line for the active lvqq analysis stage.
            print(f'[warn] missing input: {in_path}')
# [Context] Supporting line for the active lvqq analysis stage.
            continue

# [I/O] Open/write ROOT containers for high-throughput HEP data exchange.
        with uproot.open(in_path) as root_file:
            # Validate the expected "events" table and guard against 0-pass jobs.
# [Context] Supporting line for the active lvqq analysis stage.
            status = get_tree_status(root_file, args.tree_name)
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
                        f'[info] {in_path} is a 0-pass sample '
# [Context] Supporting line for the active lvqq analysis stage.
                        f'(eventsSelected=0{processed_msg}); no tree "{args.tree_name}" was written, skipping'
# [Context] Supporting line for the active lvqq analysis stage.
                    )
# [Context] Supporting line for the active lvqq analysis stage.
                else:
# [Context] Supporting line for the active lvqq analysis stage.
                    print(f'[warn] {in_path} has no tree "{args.tree_name}", skipping')
# [Context] Supporting line for the active lvqq analysis stage.
                continue
# [Context] Supporting line for the active lvqq analysis stage.
            tree = root_file[args.tree_name]
# [Context] Supporting line for the active lvqq analysis stage.
            if tree.num_entries == 0:
# [Context] Supporting line for the active lvqq analysis stage.
                print(f'[info] {in_path} has tree "{args.tree_name}" but 0 entries, skipping')
# [Context] Supporting line for the active lvqq analysis stage.
                continue
# [Context] Supporting line for the active lvqq analysis stage.
            arrays = tree.arrays(library='np')

        # [ML] Strict, ordered feature matrix so tree splits match the training schema.
# [Context] Supporting line for the active lvqq analysis stage.
        missing = [feat for feat in features if feat not in arrays]
# [Context] Supporting line for the active lvqq analysis stage.
        # If any required feature is absent, stop instead of guessing defaults.
        # A BDT score built from shifted columns is one of the easiest silent physics bugs.
# [Context] Supporting line for the active lvqq analysis stage.
        if missing:
# [Context] Supporting line for the active lvqq analysis stage.
            raise RuntimeError(f'{in_path} missing features required by the model: {missing}')

# [Context] Supporting line for the active lvqq analysis stage.
        feature_matrix = np.column_stack([arrays[feat] for feat in features])
# [Context] Supporting line for the active lvqq analysis stage.
        # Use in-place deterministic score branch naming for all downstream scripts.
        scores = model.predict_proba(feature_matrix)[:, 1].astype('float32')
# [Context] Supporting line for the active lvqq analysis stage.
        arrays[args.score_branch] = scores

        # [I/O] Persist one full-tree output per sample; physics fit consumes these directly.
# [Context] Supporting line for the active lvqq analysis stage.
        out_path = output_dir / f'{sample}.root'
# [I/O] Open/write ROOT containers for high-throughput HEP data exchange.
        with uproot.recreate(out_path) as root_out:
# [Context] Supporting line for the active lvqq analysis stage.
            root_out[args.tree_name] = arrays

# [Context] Supporting line for the active lvqq analysis stage.
        print(f'[ok] wrote scored sample: {out_path}')


# [Context] Supporting line for the active lvqq analysis stage.
if __name__ == '__main__':
# [Context] Supporting line for the active lvqq analysis stage.
    main()
