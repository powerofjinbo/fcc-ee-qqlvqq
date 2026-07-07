# finalfable — FCC-ee H→WW*(ℓνqq̄) expected sensitivity

Final release of the semi-leptonic Z(qq̄)H(WW*→ℓνqq̄′) analysis at √s = 240 GeV,
Winter2023 IDEA samples, ℒ = 10.8 ab⁻¹ (four interaction points), full MC
statistics for all signal and background samples (verified: eventsProcessed ==
N_gen for all 32 samples).

## Headline result

| Quantity | Value |
|---|---|
| δμ/μ (20-bin BDT shape fit, Asimov) | **0.595 %** (μ = 1 ± 0.00595) |
| Statistical floor (no MC-template nuisances) | 0.564 % |
| Best single-bin counting reference | 0.616 % @ BDT > 0.70 |
| S / B after baseline selection | 38 408.6 / 70 879.6 (S/B = 0.54) |
| BDT test / train / out-of-fold AUC | 0.9742 / 0.9810 / 0.9750 |

Fit model: 20 uniform BDT-score bins; 1% flat normalisation nuisance per
background group (WW, ZZ, qq̄, ZH-other); shared per-bin MC statistical
nuisances (HistFactory staterror); MINUIT/HESSE errors validated with an
explicit profile-likelihood scan of μ.

## Selection (6 hard cuts)

1. ≥1 lepton with 10 < p < 60 GeV
2. Selected-lepton isolation I < 0.20
3. Veto additional isolated leptons with p > 20 GeV
4. 10 < E_miss < 55 GeV
5. Exactly 4 Durham jets and √d34 > 14 GeV
6. min jet constituent multiplicity > 8

No hard windows on m_Z,cand or p_Z,cand: both enter the BDT. This design is
supported by full-fit window scans (`zcand_window_scan_finalfable.csv`): all
41 p_Z windows and all 22 m_Z windows degrade the fit relative to no window.

## Files

- `FCC_ee_qqlvqq_finalfable.pdf` / `.zip` — analysis note (source + figures)
- `HWW_lvqq_slides_finalfable.pdf` / `fcc_ee_presentation_finalfable.zip` — slides
- `fit_results_finalfable.json` — full fit output (incl. counting scan, profile scan)
- `training_metrics_finalfable.json` — BDT training metrics
- `cutflow_finalfable.txt` / `cutflow_efficiency_finalfable.txt` — cutflow tables
- `zcand_window_scan_finalfable.csv` — cut-design window scans

Reproduce: `./run_v_fable_pipeline.sh` (local) or `./submit_v_fable_chain.sh`
(Slurm chain); analysis outputs land under the `v_fable` tag directories.
