# Annotated rewrite generated for: ml/apply_xgboost_bdt.py
# L1 [Original comment]: #!/usr/bin/env python3
#!/usr/bin/env python3
# L2 [Executable statement]: """Apply a trained XGBoost BDT to lvqq treemaker ntuples and write scored ROOT files."""
"""Apply a trained XGBoost BDT to lvqq treemaker ntuples and write scored ROOT files."""
# L3 [Blank separator]: 

# L4 [Import statement]: import argparse
import argparse
# L5 [Import statement]: import json
import json
# L6 [Import statement]: import sys
import sys
# L7 [Import statement]: from pathlib import Path
from pathlib import Path
# L8 [Blank separator]: 

# L9 [Import statement]: import numpy as np
import numpy as np
# L10 [Import statement]: import uproot
import uproot
# L11 [Import statement]: import xgboost as xgb
import xgboost as xgb
# L12 [Blank separator]: 

# L13 [Executable statement]: THIS_DIR = Path(__file__).resolve().parent
THIS_DIR = Path(__file__).resolve().parent
# L14 [Executable statement]: ANALYSIS_DIR = THIS_DIR.parent
ANALYSIS_DIR = THIS_DIR.parent
# L15 [Executable statement]: sys.path.insert(0, str(ANALYSIS_DIR))
sys.path.insert(0, str(ANALYSIS_DIR))
# L16 [Blank separator]: 

# L17 [Import statement]: from ml_config import (
from ml_config import (
# L18 [Executable statement]:     BACKGROUND_SAMPLES,
    BACKGROUND_SAMPLES,
# L19 [Executable statement]:     DEFAULT_MODEL_DIR,
    DEFAULT_MODEL_DIR,
# L20 [Executable statement]:     DEFAULT_SCORE_BRANCH,
    DEFAULT_SCORE_BRANCH,
# L21 [Executable statement]:     DEFAULT_TREE_NAME,
    DEFAULT_TREE_NAME,
# L22 [Executable statement]:     DEFAULT_TREEMAKER_DIR,
    DEFAULT_TREEMAKER_DIR,
# L23 [Executable statement]:     ML_FEATURES,
    ML_FEATURES,
# L24 [Executable statement]:     SIGNAL_SAMPLES,
    SIGNAL_SAMPLES,
# L25 [Executable statement]: )
)
# L26 [Blank separator]: 

# L27 [Blank separator]: 

# L28 [Function definition]: def parse_args():
def parse_args():
# L29 [Executable statement]:     parser = argparse.ArgumentParser(description=__doc__)
    parser = argparse.ArgumentParser(description=__doc__)
# L30 [Executable statement]:     parser.add_argument('--input-dir', default=DEFAULT_TREEMAKER_DIR)
    parser.add_argument('--input-dir', default=DEFAULT_TREEMAKER_DIR)
# L31 [Executable statement]:     parser.add_argument('--output-dir', default='output/h_hww_lvqq/bdt_scored/ecm240')
    parser.add_argument('--output-dir', default='output/h_hww_lvqq/bdt_scored/ecm240')
# L32 [Executable statement]:     parser.add_argument('--tree-name', default=DEFAULT_TREE_NAME)
    parser.add_argument('--tree-name', default=DEFAULT_TREE_NAME)
# L33 [Executable statement]:     parser.add_argument('--model', default=str(Path(DEFAULT_MODEL_DIR) / 'xgboost_bdt.json'))
    parser.add_argument('--model', default=str(Path(DEFAULT_MODEL_DIR) / 'xgboost_bdt.json'))
# L34 [Executable statement]:     parser.add_argument('--features-json', default=str(Path(DEFAULT_MODEL_DIR) / 'training_metrics.json'))
    parser.add_argument('--features-json', default=str(Path(DEFAULT_MODEL_DIR) / 'training_metrics.json'))
# L35 [Executable statement]:     parser.add_argument('--samples', nargs='*', default=SIGNAL_SAMPLES + BACKGROUND_SAMPLES)
    parser.add_argument('--samples', nargs='*', default=SIGNAL_SAMPLES + BACKGROUND_SAMPLES)
# L36 [Executable statement]:     parser.add_argument('--score-branch', default=DEFAULT_SCORE_BRANCH)
    parser.add_argument('--score-branch', default=DEFAULT_SCORE_BRANCH)
# L37 [Function return]:     return parser.parse_args()
    return parser.parse_args()
# L38 [Blank separator]: 

# L39 [Blank separator]: 

# L40 [Function definition]: def load_features(features_json):
def load_features(features_json):
# L41 [Executable statement]:     path = Path(features_json)
    path = Path(features_json)
# L42 [Conditional block]:     if path.exists():
    if path.exists():
# L43 [Context manager block]:         with open(path, 'r', encoding='ascii') as handle:
        with open(path, 'r', encoding='ascii') as handle:
# L44 [Executable statement]:             payload = json.load(handle)
            payload = json.load(handle)
# L45 [Function return]:         return payload.get('features', ML_FEATURES)
        return payload.get('features', ML_FEATURES)
# L46 [Function return]:     return ML_FEATURES
    return ML_FEATURES
# L47 [Blank separator]: 

# L48 [Blank separator]: 

# L49 [Function definition]: def get_tree_status(root_file, tree_name):
def get_tree_status(root_file, tree_name):
# L50 [Executable statement]:     has_tree = tree_name in root_file
    has_tree = tree_name in root_file
# L51 [Executable statement]:     num_entries = root_file[tree_name].num_entries if has_tree else 0
    num_entries = root_file[tree_name].num_entries if has_tree else 0
# L52 [Blank separator]: 

# L53 [Executable statement]:     selected = None
    selected = None
# L54 [Conditional block]:     if 'eventsSelected' in root_file:
    if 'eventsSelected' in root_file:
# L55 [Exception handling start]:         try:
        try:
# L56 [Executable statement]:             selected = int(root_file['eventsSelected'].member('fVal'))
            selected = int(root_file['eventsSelected'].member('fVal'))
# L57 [Exception handler]:         except Exception:
        except Exception:
# L58 [Executable statement]:             selected = None
            selected = None
# L59 [Blank separator]: 

# L60 [Executable statement]:     processed = None
    processed = None
# L61 [Conditional block]:     if 'eventsProcessed' in root_file:
    if 'eventsProcessed' in root_file:
# L62 [Exception handling start]:         try:
        try:
# L63 [Executable statement]:             processed = int(root_file['eventsProcessed'].member('fVal'))
            processed = int(root_file['eventsProcessed'].member('fVal'))
# L64 [Exception handler]:         except Exception:
        except Exception:
# L65 [Executable statement]:             processed = None
            processed = None
# L66 [Blank separator]: 

# L67 [Function return]:     return {
    return {
# L68 [Executable statement]:         'has_tree': has_tree,
        'has_tree': has_tree,
# L69 [Executable statement]:         'num_entries': num_entries,
        'num_entries': num_entries,
# L70 [Executable statement]:         'selected': selected,
        'selected': selected,
# L71 [Executable statement]:         'processed': processed,
        'processed': processed,
# L72 [Executable statement]:     }
    }
# L73 [Blank separator]: 

# L74 [Blank separator]: 

# L75 [Function definition]: def main():
def main():
# L76 [Executable statement]:     args = parse_args()
    args = parse_args()
# L77 [Executable statement]:     features = load_features(args.features_json)
    features = load_features(args.features_json)
# L78 [Executable statement]:     input_dir = Path(args.input_dir)
    input_dir = Path(args.input_dir)
# L79 [Executable statement]:     output_dir = Path(args.output_dir)
    output_dir = Path(args.output_dir)
# L80 [Executable statement]:     output_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
# L81 [Blank separator]: 

# L82 [Executable statement]:     model = xgb.XGBClassifier()
    model = xgb.XGBClassifier()
# L83 [Executable statement]:     model.load_model(args.model)
    model.load_model(args.model)
# L84 [Blank separator]: 

# L85 [Loop over iterable]:     for sample in args.samples:
    for sample in args.samples:
# L86 [Executable statement]:         in_path = input_dir / f'{sample}.root'
        in_path = input_dir / f'{sample}.root'
# L87 [Conditional block]:         if not in_path.exists():
        if not in_path.exists():
# L88 [Runtime log output]:             print(f'[warn] missing input: {in_path}')
            print(f'[warn] missing input: {in_path}')
# L89 [Executable statement]:             continue
            continue
# L90 [Blank separator]: 

# L91 [Context manager block]:         with uproot.open(in_path) as root_file:
        with uproot.open(in_path) as root_file:
# L92 [Executable statement]:             status = get_tree_status(root_file, args.tree_name)
            status = get_tree_status(root_file, args.tree_name)
# L93 [Conditional block]:             if not status['has_tree']:
            if not status['has_tree']:
# L94 [Conditional block]:                 if status['selected'] == 0:
                if status['selected'] == 0:
# L95 [Executable statement]:                     processed = status['processed']
                    processed = status['processed']
# L96 [Executable statement]:                     processed_msg = f', processed={processed}' if processed is not None else ''
                    processed_msg = f', processed={processed}' if processed is not None else ''
# L97 [Runtime log output]:                     print(
                    print(
# L98 [Executable statement]:                         f'[info] {in_path} is a 0-pass sample '
                        f'[info] {in_path} is a 0-pass sample '
# L99 [Executable statement]:                         f'(eventsSelected=0{processed_msg}); no tree "{args.tree_name}" was written, skipping'
                        f'(eventsSelected=0{processed_msg}); no tree "{args.tree_name}" was written, skipping'
# L100 [Executable statement]:                     )
                    )
# L101 [Else branch]:                 else:
                else:
# L102 [Runtime log output]:                     print(f'[warn] {in_path} has no tree "{args.tree_name}", skipping')
                    print(f'[warn] {in_path} has no tree "{args.tree_name}", skipping')
# L103 [Executable statement]:                 continue
                continue
# L104 [Executable statement]:             tree = root_file[args.tree_name]
            tree = root_file[args.tree_name]
# L105 [Conditional block]:             if tree.num_entries == 0:
            if tree.num_entries == 0:
# L106 [Runtime log output]:                 print(f'[info] {in_path} has tree "{args.tree_name}" but 0 entries, skipping')
                print(f'[info] {in_path} has tree "{args.tree_name}" but 0 entries, skipping')
# L107 [Executable statement]:                 continue
                continue
# L108 [Executable statement]:             arrays = tree.arrays(library='np')
            arrays = tree.arrays(library='np')
# L109 [Blank separator]: 

# L110 [Executable statement]:         missing = [feat for feat in features if feat not in arrays]
        missing = [feat for feat in features if feat not in arrays]
# L111 [Conditional block]:         if missing:
        if missing:
# L112 [Executable statement]:             raise RuntimeError(f'{in_path} missing features required by the model: {missing}')
            raise RuntimeError(f'{in_path} missing features required by the model: {missing}')
# L113 [Blank separator]: 

# L114 [Executable statement]:         feature_matrix = np.column_stack([arrays[feat] for feat in features])
        feature_matrix = np.column_stack([arrays[feat] for feat in features])
# L115 [Executable statement]:         scores = model.predict_proba(feature_matrix)[:, 1].astype('float32')
        scores = model.predict_proba(feature_matrix)[:, 1].astype('float32')
# L116 [Executable statement]:         arrays[args.score_branch] = scores
        arrays[args.score_branch] = scores
# L117 [Blank separator]: 

# L118 [Executable statement]:         out_path = output_dir / f'{sample}.root'
        out_path = output_dir / f'{sample}.root'
# L119 [Context manager block]:         with uproot.recreate(out_path) as root_out:
        with uproot.recreate(out_path) as root_out:
# L120 [Executable statement]:             root_out[args.tree_name] = arrays
            root_out[args.tree_name] = arrays
# L121 [Blank separator]: 

# L122 [Runtime log output]:         print(f'[ok] wrote scored sample: {out_path}')
        print(f'[ok] wrote scored sample: {out_path}')
# L123 [Blank separator]: 

# L124 [Blank separator]: 

# L125 [Conditional block]: if __name__ == '__main__':
if __name__ == '__main__':
# L126 [Executable statement]:     main()
    main()
