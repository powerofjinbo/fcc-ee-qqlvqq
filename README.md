# FCC-ee `Z(qq)WW(lvqq)` Analysis

This repository contains the FCC-ee semi-leptonic Higgs analysis

- `e+e- -> ZH`
- `Z -> q qbar`
- `H -> WW* -> l nu q qbar'`

The code is organized as a single analysis workflow driven by `run_lvqq.py`.

## Repository layout

- `run_lvqq.py`
  Unified driver for the workflow.
- `h_hww_lvqq.py`
  FCCAnalyses analysis module for both `histmaker` and `treemaker`.
- `ml_config.py`
  Shared configuration: samples, mixed background fractions, ML features.
- `utils.h`
  Channel-specific C++ helpers, including the 4-jet Z-priority pairing.
- `functions/`
  Common FCC helper headers required by the analysis module.
- `ml/`
  XGBoost training, score application, and `pyhf` fit code.
- `plots_lvqq.py`
  Cutflow and kinematic plotting.
- `paper/`
  Note source and helper script for support figures.

## Default sample configuration

The default mixed-statistics setup is:

- signal: `100%`
- `ZH(other)`: `100%`
- `WW`: `10%`
- `ZZ`: `10%`
- `tautau`: `10%`
- `qq`: `5%`

## Standard workflow

```bash
python3 run_lvqq.py histmaker
python3 run_lvqq.py treemaker
python3 run_lvqq.py train
python3 run_lvqq.py apply
python3 run_lvqq.py fit
python3 run_lvqq.py plots
python3 run_lvqq.py paper
```

or in one shot:

```bash
python3 run_lvqq.py all
```

## Environment assumptions

This analysis is currently configured for the FCC-ee subMIT environment:

- Delphes samples from `/ceph/submit/.../winter2023/IDEA/`
- FCCAnalyses setup script from `FCCANALYSES_SETUP_SH`

If `FCCANALYSES_SETUP_SH` is not set, `run_lvqq.py` falls back to:

```text
/home/submit/jinboz1/tutorials/FCCAnalyses/setup.sh
```

## Notes

- Generated outputs such as `output/`, `plots_lvqq/`, `logs/`, and `ml/models/`
  are intentionally excluded from version control.
- The paper depends on plots produced by the workflow; run the pipeline before
  compiling `paper/main.tex`.
