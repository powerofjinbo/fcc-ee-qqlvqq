# FCC lvqq Learning-Order Slides

## Audience

- Primary audience: the repository author, studying the FCC lvqq pipeline in depth.
- Secondary use: a compact explanation deck for meetings with advisors/collaborators.

## Objective

- Turn the repository into a learnable sequence rather than a flat list of scripts.
- Make the study order follow dependency structure:
  `driver -> event selection -> validation plots -> ML training -> statistical fit -> paper`.
- Keep each slide actionable:
  what to read, what question to answer, and what command to run.

## Narrative Arc

1. Start from the full map.
2. Clarify repo layers and the role of `functions/` and `paper/`.
3. Walk through the pipeline day by day.
4. End with a self-test checklist that matches the most important conceptual gaps.

## Visual System

- Format: 16:9 editable PPTX.
- Style: light academic deck with warm paper background and deep teal accent.
- Typography: `PingFang SC` for Chinese readability, `Menlo` for code-like labels.
- Layout language: strong header rail, large title block, three-card study panels, selective metric slides.

## Slide List

1. Cover: study objective and core principle.
2. Overview: one entry point, four layers, seven study days.
3. Repo map: top level, `functions/` + `utils.h`, and `paper/`.
4. Day 1: `run_lvqq.py` and `ml_config.py`.
5. Day 2: `h_hww_lvqq.py` preselection (`cut1`-`cut4`).
6. Day 3: `h_hww_lvqq.py` jet reconstruction, pairing, and `cut5`-`cut7`.
7. Day 4: `plots_lvqq.py` as validation, not decoration.
8. Day 5: `train_xgboost_bdt.py` data loading, weights, and splits.
9. Day 6: overfitting control and 5-fold scoring.
10. Day 7: `fit`, `apply`, and `paper`.
11. Final checklist: the questions the user must be able to answer aloud.

## Source Plan

- Repository scripts:
  - `run_lvqq.py`
  - `h_hww_lvqq.py`
  - `ml_config.py`
  - `plots_lvqq.py`
  - `ml/train_xgboost_bdt.py`
  - `ml/apply_xgboost_bdt.py`
  - `ml/fit_profile_likelihood.py`
  - `paper/generate_supporting_figures.py`
  - `paper/sync_paper_figures.py`
  - `paper/main.tex`
- Existing repo understanding from previous study notes and code inspection.

## Editability Plan

- All visible text is authored as editable PowerPoint text boxes.
- The deck is built from a local JS builder so the slide structure remains modifiable.
- Final artifact: `docs/learning_order_slides/outputs/output.pptx`
