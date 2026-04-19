#!/usr/bin/env python3
# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
"""Apply a trained XGBoost BDT to lvqq treemaker ntuples and write scored ROOT files."""

# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
import argparse
# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
import json
# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
import sys
# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
from pathlib import Path

# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
import numpy as np
# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
import uproot
# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
import xgboost as xgb

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
THIS_DIR = Path(__file__).resolve().parent
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
ANALYSIS_DIR = THIS_DIR.parent
# [Workflow] Ensure repository-local imports (ml_config, helpers) resolve regardless of execution context.
sys.path.insert(0, str(ANALYSIS_DIR))

# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
from ml_config import (
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    BACKGROUND_SAMPLES,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    DEFAULT_MODEL_DIR,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    DEFAULT_SCORE_BRANCH,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    DEFAULT_TREE_NAME,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    DEFAULT_TREEMAKER_DIR,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ML_FEATURES,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    SIGNAL_SAMPLES,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
)


# [Workflow] Argument parser: expose knobs for reproducibility (seed), split fractions, model options, and outputs.
def parse_args():
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    parser = argparse.ArgumentParser(description=__doc__)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    parser.add_argument('--input-dir', default=DEFAULT_TREEMAKER_DIR)
# [Physics] Fixed center-of-mass energy for FCC-ee running point; this drives recoil and kinematic normalization conventions.
    parser.add_argument('--output-dir', default='output/h_hww_lvqq/bdt_scored/ecm240')
# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
    parser.add_argument('--tree-name', default=DEFAULT_TREE_NAME)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    parser.add_argument('--model', default=str(Path(DEFAULT_MODEL_DIR) / 'xgboost_bdt.json'))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    parser.add_argument('--features-json', default=str(Path(DEFAULT_MODEL_DIR) / 'training_metrics.json'))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    parser.add_argument('--samples', nargs='*', default=SIGNAL_SAMPLES + BACKGROUND_SAMPLES)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    parser.add_argument('--score-branch', default=DEFAULT_SCORE_BRANCH)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    return parser.parse_args()


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def load_features(features_json):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    path = Path(features_json)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if path.exists():
# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
        with open(path, 'r', encoding='ascii') as handle:
# [Provenance] Persist artifacts to guarantee traceability of training hyperparameters, metrics, and inputs used by downstream inference.
            payload = json.load(handle)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        return payload.get('features', ML_FEATURES)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    return ML_FEATURES


# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
def get_tree_status(root_file, tree_name):
# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
    has_tree = tree_name in root_file
# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
    num_entries = root_file[tree_name].num_entries if has_tree else 0

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    selected = None
# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
    if 'eventsSelected' in root_file:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        try:
# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
            selected = int(root_file['eventsSelected'].member('fVal'))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        except Exception:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            selected = None

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    processed = None
# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
    if 'eventsProcessed' in root_file:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        try:
# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
            processed = int(root_file['eventsProcessed'].member('fVal'))
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        except Exception:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            processed = None

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    return {
# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
        'has_tree': has_tree,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        'num_entries': num_entries,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        'selected': selected,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        'processed': processed,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    }


# [Workflow] Main orchestrator for this module; executes the full chain for this script only.
def main():
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    args = parse_args()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    features = load_features(args.features_json)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    input_dir = Path(args.input_dir)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    output_dir = Path(args.output_dir)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    output_dir.mkdir(parents=True, exist_ok=True)

# [ML] Core model operation is tree-based boosted classification; this captures non-linear kinematic correlations in lvqq features.
    model = xgb.XGBClassifier()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    model.load_model(args.model)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for sample in args.samples:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        in_path = input_dir / f'{sample}.root'
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        if not in_path.exists():
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
            print(f'[warn] missing input: {in_path}')
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            continue

# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
        with uproot.open(in_path) as root_file:
# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
            status = get_tree_status(root_file, args.tree_name)
# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
            if not status['has_tree']:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
                if status['selected'] == 0:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
                    processed = status['processed']
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
                    processed_msg = f', processed={processed}' if processed is not None else ''
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
                    print(
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
                        f'[info] {in_path} is a 0-pass sample '
# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
                        f'(eventsSelected=0{processed_msg}); no tree "{args.tree_name}" was written, skipping'
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
                    )
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
                else:
# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
                    print(f'[warn] {in_path} has no tree "{args.tree_name}", skipping')
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
                continue
# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
            tree = root_file[args.tree_name]
# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
            if tree.num_entries == 0:
# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
                print(f'[info] {in_path} has tree "{args.tree_name}" but 0 entries, skipping')
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
                continue
# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
            arrays = tree.arrays(library='np')

# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        missing = [feat for feat in features if feat not in arrays]
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
        if missing:
# [Physics] Physics observable construction: shape variables and topology reconstruction are where signal-background separation is primarily encoded.
            raise RuntimeError(f'{in_path} missing features required by the model: {missing}')

# [Data] Convert event arrays into structured numeric frames for vectorized cuts, weighting, and sklearn-compatible training matrices.
        feature_matrix = np.column_stack([arrays[feat] for feat in features])
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        scores = model.predict_proba(feature_matrix)[:, 1].astype('float32')
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        arrays[args.score_branch] = scores

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        out_path = output_dir / f'{sample}.root'
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        with uproot.recreate(out_path) as root_out:
# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
            root_out[args.tree_name] = arrays

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        print(f'[ok] wrote scored sample: {out_path}')


# [Entry] Module entry point for direct execution from CLI.
if __name__ == '__main__':
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    main()
