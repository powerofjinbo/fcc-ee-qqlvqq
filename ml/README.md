# XGBoost BDT workflow for `Z(qq)WW(lvqq)`

This directory contains the ML part of the standard lvqq analysis workflow.
For the full end-to-end chain, see the top-level [README.md](../README.md) and
`../run_lvqq.py`.

## 1. Produce ML ntuples

```bash
cd "/home/submit/jinboz1/work/Z(qq)WW(lvqq)"
python3 run_lvqq.py treemaker
```

This writes flat ntuples to:

```text
output/h_hww_lvqq/treemaker/ecm240/
```

The default configuration uses full background statistics:
- `WW`: `100%`
- `ZZ`: `100%`
- `tautau`: `100%`
- `qq`: `100%`

To force one common fraction for all reducible backgrounds, add for example
`--background-fraction 0.1`.

## 2. Train the XGBoost BDT

```bash
cd "/home/submit/jinboz1/work/Z(qq)WW(lvqq)"
python3 run_lvqq.py train
```

Outputs are written to (model directories are named after the output tag):

```text
ml/models/xgboost_bdt_<tag>/        # e.g. ml/models/xgboost_bdt_v_fable/
```

Important outputs:
- `xgboost_bdt.json`: trained model
- `training_metrics.json`: AUC and feature list
- `feature_importance.csv`: feature ranking
- `test_scores.csv`: holdout-sample score dump
- `kfold_scores.csv`: unbiased out-of-fold scores for all events

## 3. Apply the trained model to ntuples

```bash
cd "/home/submit/jinboz1/work/Z(qq)WW(lvqq)"
python3 run_lvqq.py apply
```

Scored ntuples are written to:

```text
output/h_hww_lvqq/bdt_scored/ecm240/
```

A new branch called `bdt_score` is added.

## 4. Run the profile-likelihood fit

```bash
cd "/home/submit/jinboz1/work/Z(qq)WW(lvqq)"
python3 run_lvqq.py fit
```

v_fable fit behaviour:
- the fit ALWAYS prefers `kfold_scores.csv` (out-of-fold scores for every
  selected event); `test_scores.csv` is a fallback with the weight scaling
  derived from `training_metrics.json`;
- missing score files are a hard error (no silent fallback to older models);
- MC template statistics use one shared (HistFactory-convention) `staterror`
  per channel (`--staterror-mode per-sample` restores the old behaviour);
- parameter errors come from MINUIT/HESSE, cross-checked by a 1D
  profile-likelihood scan of `mu` (`plots/mu_profile_scan.*`).

The default output file `fit_results.json` reports:
- `relative_uncertainty_pct`: main result with MC-stat nuisance parameters
- `physics_only_rel_uncertainty_pct`: floor without MC-stat terms
- `counting_scan_results`: true 1-bin cut-and-count scan used only for comparison
- `score_source` / `staterror_mode` / `error_method`: provenance of the result

## Default feature set

Training uses the 26-feature core list `ML_FEATURES` in `ml_config.py`.
The treemaker ntuples additionally contain `TREE_EXTRA_BRANCHES` (raw masses
and the ZW-chi2 alternative-pairing variables), so retraining with a different
feature set only requires rerunning the (fast) train step.
