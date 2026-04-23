# `functions/`

This directory contains C++ helper headers used by the FCCAnalyses event graph.
They are not Python utilities.

The analysis module [`h_hww_lvqq.py`](../h_hww_lvqq.py) loads them through
`includePaths`, so the functions defined here can be called inside
`df.Define(...)` and `df.Filter(...)` expressions during the RDataFrame stage.

Current contents:

- `functions.h`
  - General reconstructed-object helpers.
  - Examples: Lorentz-vector builders, missing-energy helpers, isolation, and
    resonance-building utilities.

- `functions_gen.h`
  - Generator-level / truth-matching helpers.
  - Used when the analysis needs MC-particle-side utilities.

Related file:

- `../utils.h`
  - Analysis-specific C++ helpers for the lvqq channel.
  - This includes the jet-pairing and event-shape helpers used by
    `h_hww_lvqq.py`, such as `pairing_Zpriority_4jets`, `totalJetMass`,
    `computeThrust`, and `angleLeptonMiss`.
  - Conceptually this file belongs next to the other C++ helpers, but it is
    currently kept at the repository root to avoid changing the working
    FCCAnalyses include-path setup.

Mental model:

- `functions/` = reusable low-level C++ physics/helper layer
- `h_hww_lvqq.py` = channel analysis graph that calls these helpers
- `ml/` = downstream ML and statistical inference
