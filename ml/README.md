# XGBoost BDT workflow for `Z(qq)WW(lvqq)`

This directory contains the ML part of the standard lvqq analysis workflow.
For the full end-to-end chain, see the top-level [README.md](../README.md) and
`../run_lvqq.py`.

## 1. Produce ML ntuples

```bash
cd /path/to/fcc-ee
python3 run_lvqq.py treemaker
```

This writes flat ntuples to:

```text
output/h_hww_lvqq/treemaker/ecm240/
```

The default configuration uses a mixed background setup:
- `WW`: `10%`
- `ZZ`: `10%`
- `tautau`: `10%`
- `qq`: `5%`

To force one common fraction for all reducible backgrounds, add for example
`--background-fraction 0.1`.

## 2. Train the XGBoost BDT

```bash
cd /path/to/fcc-ee
python3 run_lvqq.py train
```

Outputs are written to:

```text
ml/models/xgboost_bdt_v6/
```

Important outputs:
- `xgboost_bdt.json`: trained model
- `training_metrics.json`: AUC and feature list
- `feature_importance.csv`: feature ranking
- `test_scores.csv`: holdout-sample score dump
- `kfold_scores.csv`: unbiased out-of-fold scores for all events

## 3. Apply the trained model to ntuples

```bash
cd /path/to/fcc-ee
python3 run_lvqq.py apply
```

Scored ntuples are written to:

```text
output/h_hww_lvqq/bdt_scored/ecm240/
```

A new branch called `bdt_score` is added.

## 4. Run the profile-likelihood fit

```bash
cd /path/to/fcc-ee
python3 run_lvqq.py fit
```

The default output file `fit_results.json` reports:
- `relative_uncertainty_pct`: main result with MC-stat nuisance parameters
- `physics_only_rel_uncertainty_pct`: floor without Barlow-Beeston MC-stat terms
- `counting_scan_results`: true 1-bin cut-and-count scan used only for comparison

## Default feature set

The shared feature list is defined in `ml_config.py`.
