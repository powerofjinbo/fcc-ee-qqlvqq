# `Z(qq)WW(lvqq)` Standard Analysis Flow

This directory contains the standard FCC-ee semi-leptonic `H -> WW* -> lvqq`
analysis workflow.

## Standard entry points

You only need to interact with one script in normal use:

- `run_lvqq.py`
  - Unified driver for the full workflow.
  - Can run the whole chain or individual stages:
    `all`, `stage1`, `ml`, `histmaker`, `treemaker`, `train`, `apply`,
    `fit`, `plots`, `paper`.

- `h_hww_lvqq.py`
  - Unified FCCAnalyses analysis module.
  - `LVQQ_MODE=histmaker` writes histograms to
    `output/h_hww_lvqq/histmaker/ecm240/`.
  - `LVQQ_MODE=treemaker` writes flat ML ntuples to
    `output/h_hww_lvqq/treemaker/ecm240/`.

- `ml_config.py`
  - Shared analysis configuration for the ML workflow.
  - Defines the feature list, signal/background sample lists, and default
    output locations.
  - The default background setup keeps signal, `ZH(other)`, and the large
    reducible backgrounds all at full statistics.
  - A global `LVQQ_BACKGROUND_FRACTION` override is still available for quick
    reduced-stat runs, and the per-group overrides `LVQQ_WW_FRACTION`,
    `LVQQ_ZZ_FRACTION`, `LVQQ_QQ_FRACTION`, and `LVQQ_TAUTAU_FRACTION` can be
    used when needed.

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
    `ml/models/xgboost_bdt_v6/plots/`.

- `paper/main.tex`
  - The note/paper source.
  - Uses the plots and numbers produced by the workflow.

## Repository layout

The repository is easier to understand if you group it into four layers:

- Top level orchestration and event selection
  - `run_lvqq.py`: the only normal user entry point.
  - `h_hww_lvqq.py`: the FCCAnalyses event-selection graph.
  - `ml_config.py`: shared sample lists, feature lists, and default paths.
  - `plots_lvqq.py`: cutflow tables and paper-style kinematic plots from the
    histogram outputs.

- `ml/`
  - The classifier and statistical-inference layer.
  - Training, model application, ROC reproduction, and the profile-likelihood
    fit live here.

- `functions/`
  - C++ helper headers loaded by the FCCAnalyses graph.
  - These are low-level physics/helper routines used inside
    `df.Define(...)` and `df.Filter(...)`.
  - See [`functions/README.md`](functions/README.md).

- `paper/`
  - The presentation/publication layer.
  - This directory turns finished plots and fit outputs into the final note.
  - See [`paper/README.md`](paper/README.md).

There is also one important root-level helper file:

- `utils.h`
  - lvqq-specific C++ utilities such as jet pairing and event-shape helpers.
  - It is loaded together with the headers in `functions/` by
    `h_hww_lvqq.py`.

Generated outputs are intentionally kept out of git:

- `output/`: FCCAnalyses histmaker/treemaker/scored ROOT outputs
- `plots_lvqq/`: rendered cutflow and validation plots
- `ml/models/`: trained-model artifacts and fit outputs
- `logs/`, `tmp/`: local runtime artifacts

If your local checkout also contains study material such as `learning_notes/`
or presentation material such as `deliverables/`, those are not part of the
core analysis pipeline.

## Optional utility

- `ml/regenerate_roc.py`
  - Convenience script to remake the ROC plot from saved outputs.
  - Not required for the standard end-to-end workflow.

## Standard run order

1. `python3 run_lvqq.py histmaker`
2. `python3 run_lvqq.py treemaker`
3. `python3 run_lvqq.py train`
4. `python3 run_lvqq.py apply`
5. `python3 run_lvqq.py fit`
6. `python3 run_lvqq.py plots`
7. `python3 run_lvqq.py paper`

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

To override all reducible backgrounds with one common fraction:

```bash
python3 run_lvqq.py all --background-fraction 0.1
```

To override only one background class:

```bash
python3 run_lvqq.py all --ww-fraction 0.5 --zz-fraction 0.3 --qq-fraction 0.1 --tautau-fraction 0.1
```

Useful shorter variants:

```bash
python3 run_lvqq.py stage1   # histmaker + treemaker
python3 run_lvqq.py ml       # train + apply + fit
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
