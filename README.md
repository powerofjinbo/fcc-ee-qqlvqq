# `Z(qq)WW(lvqq)` Standard Analysis Flow

This directory contains the standard FCC-ee semi-leptonic `H -> WW* -> lvqq`
analysis workflow.

## Current version: v_fable

The nominal selection (single source of truth: `CUTFLOW_STAGES` in
`ml_config.py`) has 6 hard cuts:

1. `>= 1` lepton with `10 < p < 60 GeV`
2. selected-lepton isolation `I < 0.20`
3. veto extra isolated leptons with `p > 20 GeV`
4. `10 < E_miss < 55 GeV`
5. exclusive `N=4` Durham jets and `sqrt(d34) > 14 GeV`
6. `min jet Nconst > 8`

There is NO hard window on `Zcand_m` or `Zcand_p`: both are BDT inputs.
Full profile-likelihood window scans (`ml/scan_zcand_windows.py`) showed
every candidate window on either variable degrades the 20-bin shape-fit
precision relative to no window (e.g. the former `40 < pZ < 60` cut:
0.731% vs 0.595% without it). The BDT trains on the 26-feature core list;
the treemaker keeps all extra branches so future retrainings do not need a
treemaker rerun. The fit uses out-of-fold (`kfold_scores.csv`) scores, one
shared staterror per channel, and MINUIT errors validated by a
profile-likelihood scan.

Full-statistics run (recommended, survives SSH disconnects):

```bash
./submit_v_fable_chain.sh          # Slurm dependency chain, or:
mkdir -p logs/v_fable
nohup ./run_v_fable_pipeline.sh > logs/v_fable/pipeline.log 2>&1 &   # local
```

## Standard entry points

You only need to interact with one script in normal use:

- `run_lvqq.py`
  - Unified driver for the full workflow.
  - Can run the whole chain or individual stages:
    `all`, `stage1`, `ml`, `histmaker`, `treemaker`, `scanmaker`, `cutscan`,
    `scans`, `train`, `apply`, `fit`, `plots`, `paper`.

- `h_hww_lvqq.py`
  - Unified FCCAnalyses analysis module.
  - `LVQQ_MODE=histmaker` writes histograms to
    `output/h_hww_lvqq/histmaker/ecm240/`.
  - `LVQQ_MODE=treemaker` writes flat ML ntuples to
    `output/h_hww_lvqq/treemaker/ecm240/`.
  - `LVQQ_MODE=scanmaker` writes loose cut-scan ntuples to
    `output/h_hww_lvqq/scanmaker/ecm240/`.

- `ml_config.py`
  - Shared analysis configuration for the ML workflow.
  - Defines the feature list, signal/background sample lists, and default
    output locations.
  - The default background setup keeps signal, `ZH(other)`, and the large
    reducible backgrounds all at full statistics.
  - A global `LVQQ_BACKGROUND_FRACTION` override is still available for quick
    reduced-stat runs over all backgrounds, and the per-group overrides
    `LVQQ_WW_FRACTION`, `LVQQ_ZZ_FRACTION`, `LVQQ_QQ_FRACTION`,
    `LVQQ_TAUTAU_FRACTION`, and `LVQQ_ZH_OTHER_FRACTION` can be used when
    needed.

- `plots_lvqq.py`
  - Reads the histmaker ROOT files and produces cutflow tables plus the
    paper-style kinematic plots in `plots_lvqq/`.
  - The `plots` workflow step also refreshes the paper ROC figure
    `roc_curve.*` together with the support figures `pairing_validation.*`
    and `feynman_diagram.*`.

- `ml/train_xgboost_bdt.py`
  - Trains the XGBoost BDT from the treemaker ntuples.
  - Produces the trained model, diagnostics, and `kfold_scores.csv`.

- `ml/apply_xgboost_bdt.py`
  - Applies the trained BDT to the treemaker ntuples.
  - Writes scored ROOT files with a `bdt_score` branch to
    `output/h_hww_lvqq/bdt_scored/ecm240/`.

- `ml/fit_profile_likelihood.py`
  - Builds the binned signal/background templates from the BDT scores and
    runs the `pyhf` profile-likelihood fit.
  - Produces `fit_results.json` and the fit plots under
    `ml/models/xgboost_bdt_<tag>/plots/` (e.g. `ml/models/xgboost_bdt_v_fable/plots/`).

- `ml/scan_preselection_cuts.py`
  - Reads loose scanmaker ntuples and scans lepton, isolation, MET,
    missing-direction, `sqrt(d34)`, and asymmetric recoil-window thresholds.
  - Produces CSV summaries and scan plots under `cut_scans_v_fable_baseline/`.

- `paper/main.tex`
  - The note/paper source.
  - Uses the plots and numbers produced by the workflow.

## Optional utility

- `ml/regenerate_roc.py`
  - Convenience script to remake the ROC plot from saved outputs.
  - Invoked automatically by the `plots` and `paper` targets of
    `run_lvqq.py` (step_roc_plot); do not delete.

## Standard run order

1. `python3 run_lvqq.py histmaker`
2. `python3 run_lvqq.py treemaker`
3. `python3 run_lvqq.py train`
4. `python3 run_lvqq.py apply`
5. `python3 run_lvqq.py fit`
6. `python3 run_lvqq.py plots`
7. `python3 run_lvqq.py paper`

## Cut-scan workflow

For preselection optimization studies, first make the loose scan ntuples and
then run the offline scans:

```bash
python3 run_lvqq.py scans
```

For quick development, use a reduced background fraction. Signal remains at
full statistics:

```bash
python3 run_lvqq.py scans --background-fraction 0.05
```

For a very fast smoke test, reduce signal and all backgrounds:

```bash
python3 run_lvqq.py scans --signal-fraction 0.01 --background-fraction 0.0001
```

The scan stage writes ROOT files to `output/h_hww_lvqq/scanmaker/ecm240/` and
CSV/plot outputs to `cut_scans_v_fable_baseline/`. The nominal `treemaker` output remains the
baseline-selected ntuple used for BDT training and fitting.

## One-command run

From this directory:

```bash
python3 run_lvqq.py all
```

The default background configuration corresponds to:
- signal: `100%`
- `ZH(other)`: `100%`
- `WW`: `100%`
- `ZZ`: `100%`
- `tautau`: `100%`
- `qq`: `100%`

To override all backgrounds with one common fraction while keeping signal at
full statistics:

```bash
python3 run_lvqq.py all --background-fraction 0.1
```

To override only one background class:

```bash
python3 run_lvqq.py all --ww-fraction 0.5 --zz-fraction 0.3 --qq-fraction 0.1 --tautau-fraction 0.1
```

To include `ZH(other)` in a reduced-stat test explicitly:

```bash
python3 run_lvqq.py scans --background-fraction 0.0001
```

Useful shorter variants:

```bash
python3 run_lvqq.py stage1   # histmaker + treemaker
python3 run_lvqq.py ml       # train + apply + fit
python3 run_lvqq.py scans    # loose scanmaker + preselection cut scans
```

## Batch running on subMIT

For long full-stat runs, use Slurm instead of keeping the job on the login node:

```bash
python3 run_lvqq.py all --slurm
```

This submits the same workflow to the `submit` partition and writes logs under
`logs/slurm/`. A quick batch-node probe confirms the Slurm workers can see both
`/ceph/submit/...` and your local FCCAnalyses setup area, so the standard
workflow paths are valid there.
