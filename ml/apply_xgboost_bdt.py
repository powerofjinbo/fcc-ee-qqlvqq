#!/usr/bin/env python3
"""Apply a trained XGBoost BDT to lvqq treemaker ntuples and write scored ROOT files."""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import uproot
import xgboost as xgb

THIS_DIR = Path(__file__).resolve().parent
ANALYSIS_DIR = THIS_DIR.parent
sys.path.insert(0, str(ANALYSIS_DIR))

from ml_config import (
    BACKGROUND_SAMPLES,
    DEFAULT_MODEL_DIR,
    DEFAULT_SCORE_BRANCH,
    DEFAULT_TREE_NAME,
    DEFAULT_TREEMAKER_DIR,
    ML_FEATURES,
    SIGNAL_SAMPLES,
)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', default=DEFAULT_TREEMAKER_DIR)
    parser.add_argument('--output-dir', default='output/h_hww_lvqq/bdt_scored/ecm240')
    parser.add_argument('--tree-name', default=DEFAULT_TREE_NAME)
    parser.add_argument('--model', default=str(Path(DEFAULT_MODEL_DIR) / 'xgboost_bdt.json'))
    parser.add_argument('--features-json', default=str(Path(DEFAULT_MODEL_DIR) / 'training_metrics.json'))
    parser.add_argument('--samples', nargs='*', default=SIGNAL_SAMPLES + BACKGROUND_SAMPLES)
    parser.add_argument('--score-branch', default=DEFAULT_SCORE_BRANCH)
    return parser.parse_args()


def load_features(features_json):
    path = Path(features_json)
    if path.exists():
        with open(path, 'r', encoding='ascii') as handle:
            payload = json.load(handle)
        return payload.get('features', ML_FEATURES)
    return ML_FEATURES


def get_tree_status(root_file, tree_name):
    has_tree = tree_name in root_file
    num_entries = root_file[tree_name].num_entries if has_tree else 0

    selected = None
    if 'eventsSelected' in root_file:
        try:
            selected = int(root_file['eventsSelected'].member('fVal'))
        except Exception:
            selected = None

    processed = None
    if 'eventsProcessed' in root_file:
        try:
            processed = int(root_file['eventsProcessed'].member('fVal'))
        except Exception:
            processed = None

    return {
        'has_tree': has_tree,
        'num_entries': num_entries,
        'selected': selected,
        'processed': processed,
    }


def main():
    args = parse_args()
    features = load_features(args.features_json)
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    model = xgb.XGBClassifier()
    model.load_model(args.model)

    for sample in args.samples:
        in_path = input_dir / f'{sample}.root'
        if not in_path.exists():
            print(f'[warn] missing input: {in_path}')
            continue

        with uproot.open(in_path) as root_file:
            status = get_tree_status(root_file, args.tree_name)
            if not status['has_tree']:
                if status['selected'] == 0:
                    processed = status['processed']
                    processed_msg = f', processed={processed}' if processed is not None else ''
                    print(
                        f'[info] {in_path} is a 0-pass sample '
                        f'(eventsSelected=0{processed_msg}); no tree "{args.tree_name}" was written, skipping'
                    )
                else:
                    print(f'[warn] {in_path} has no tree "{args.tree_name}", skipping')
                continue
            tree = root_file[args.tree_name]
            if tree.num_entries == 0:
                print(f'[info] {in_path} has tree "{args.tree_name}" but 0 entries, skipping')
                continue
            arrays = tree.arrays(library='np')

        missing = [feat for feat in features if feat not in arrays]
        if missing:
            raise RuntimeError(f'{in_path} missing features required by the model: {missing}')

        feature_matrix = np.column_stack([arrays[feat] for feat in features])
        scores = model.predict_proba(feature_matrix)[:, 1].astype('float32')
        arrays[args.score_branch] = scores

        out_path = output_dir / f'{sample}.root'
        with uproot.recreate(out_path) as root_out:
            root_out[args.tree_name] = arrays

        print(f'[ok] wrote scored sample: {out_path}')


if __name__ == '__main__':
    main()
