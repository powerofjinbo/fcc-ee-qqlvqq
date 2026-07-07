# v9 Integrated Off-Shell Leptonic-W Plan

## Motivation

The nominal lvqq reconstruction currently treats the event as

```text
e+e- -> ZH
Z -> qq
H -> W W*
W_lep -> l nu is treated as the on-shell-like W
W_had -> qq is treated as the off-shell W*
```

This is a useful baseline, but the generator final state is only `lvqq`.
Event-by-event, we cannot assume that the leptonic `lv` system always comes
from the on-shell W.  The complementary signal branch is

```text
W_lep -> l nu may be off-shell
W_had -> qq may be on-shell
```

For v9 this is integrated into the nominal workflow as diagnostic and BDT
information.  The hard-cut sequence stays the Sara/Jan 8-cut baseline; the
on-shell/off-shell ambiguity is learned by the BDT and checked with validation
plots rather than imposed as a new hard W-mass cut.

## Key Reconstruction Issue

After the production-Z jets are chosen, the remaining two jets form the
hadronic W candidate.  If the hadronic W is on-shell, its mass can be close to
80 GeV, which is not very far from the Z mass.  Therefore the current
Z-priority pairing can confuse the production Z and the hadronic W more often
than in the nominal hadronic-off-shell interpretation.

Recommended strategy:

1. Keep the current Z-priority pairing as the baseline candidate.
2. Add an alternative Z/W pairing hypothesis that minimizes a two-boson score:

```text
chi2_ZW = ((m_jj_Z - mZ) / sigmaZ)^2 + ((m_jj_W - mW) / sigmaW)^2
```

3. Store both hypotheses as diagnostic/BDT features before deciding whether to
use one hard pairing rule.

## Proposed Cut Strategy

The v9 nominal hard selection remains the current 8-cut baseline, with no hard
W-mass, Higgs-candidate-mass, or recoil-mass window:

```text
Cut1: >=1 lepton with 10 < p_l < 60 GeV
Cut2: selected lepton isolation I < 0.20
Cut3: veto additional lepton with p > 20 GeV
Cut4: 10 < E_miss < 55 GeV
Cut5: exclusive 4 jets + sqrt(d34) > 14 GeV
Cut6: min_jet_nconst > 8
Cut7: 85 < m_Zcand < 95 GeV
Cut8: 40 < p_Zcand < 60 GeV
```

Keep these as scan/BDT-shape candidates only:

```text
Wlep_m upper window:       Wlep_m < 50, 60, 70, 80 GeV
Whad_m on-shell window:    60 < Whad_m < 95 GeV, or 65 < Whad_m < 90 GeV
deltaW_onShell:            abs(Wlep_m-mW) - abs(Whad_m-mW) > 0, 5, 10 GeV
pairing ambiguity:         chi2_ZW or abs(mZcand-mZ)-abs(Whad_m-mW)
```

Do not make these hard cuts until scan and BDT/fit checks show they improve the
final expected precision.  In particular, `Wlep_m` uses missing momentum and may
be resolution-sensitive.

## New Variables To Add

Minimal branch variables:

```text
Wlep_m
Wlep_p
Whad_m / Wstar_m
Whad_p / Wstar_p
abs_Wlep_mW = abs(Wlep_m - 80.379)
abs_Whad_mW = abs(Whad_m - 80.379)
deltaW_onShell = abs_Wlep_mW - abs_Whad_mW
mW_min = min(Wlep_m, Whad_m)
mW_max = max(Wlep_m, Whad_m)
Hcand_m
recoil_m
angleLepMiss
deltaR_Whad_jj
angle_Whad_jj
```

Alternative-pairing variables:

```text
Zcand_m_Zpriority
Whad_m_Zpriority
Zcand_m_ZWchi2
Whad_m_ZWchi2
chi2_ZW
delta_pairing_Z_mass = abs(Zcand_m_Zpriority - Zcand_m_ZWchi2)
```

Generator-truth validation variables, if accessible:

```text
truth_Wlep_mass
truth_Whad_mass
truth_leptonic_W_is_offshell
truth_hadronic_W_is_onshell
```

Truth flags should be used only for validation/category studies, not as BDT
input features.

## v9 BDT Strategy

Implement the inclusive BDT first, then compare category options only if the
inclusive v9 BDT shows stable train/test behavior:

1. Inclusive v9 BDT

Train one BDT on the current signal definition, with the new W-assignment
features included.  This is now the v9 nominal direction.

2. Optional two-category BDT / simultaneous fit

Split signal-like events into two reconstructed categories:

```text
Category A: deltaW_onShell < 0
  leptonic W is more on-shell-like
  current nominal interpretation

Category B: deltaW_onShell > 0
  hadronic W is more on-shell-like
  off-shell leptonic-W interpretation
```

Train separate BDTs or fit separate BDT-score templates in the two categories.

3. Multi-class diagnostic BDT

Train a diagnostic classifier with classes:

```text
signal_leptonic_on_shell
signal_leptonic_off_shell
background
```

Only do this if truth-level branch labels are robust.

## Fit Strategy

The safest final statistical comparison is:

```text
Model 1: current inclusive BDT fit
Model 2: inclusive BDT fit with off-shell variables
Model 3: two-category simultaneous fit
         channel A = leptonic-on-shell-like
         channel B = leptonic-off-shell-like
```

For each model, compare:

```text
final delta_mu / mu
signal yield retained
background yield retained
S/B
BDT train/test AUC
overtraining plot
BDT-score template stability
bin-by-bin MC statistical uncertainties
background composition after selection
```

## Validation Plots

Required before showing this branch:

```text
Wlep_m
Whad_m / Wstar_m
deltaW_onShell
abs_Wlep_mW
abs_Whad_mW
Zcand_m under Z-priority pairing
Zcand_m under ZW-chi2 pairing
Whad_m under both pairings
Hcand_m split by deltaW_onShell sign
BDT score split by reconstructed W-assignment category
cutflow for Category A and Category B
```

## Recommended Execution Order

1. Add the new reconstruction variables and alternative-pairing diagnostics.
2. Run a light v9 smoke sample first, then the desired full v9 production.
3. Produce cut-by-stage and normalized diagnostics for the new W variables.
4. Train the inclusive v9 BDT with the new variables.
5. Run the v9 profile-likelihood fit.
6. Compare inclusive v9 with optional two-category studies only after the
   inclusive result is stable.

## Current Recommendation

Do not add an immediate hard cut on `Wlep_m` or `Whad_m`.  In v9 these enter as
BDT features and category diagnostics.  If we later split categories, the first
candidate split is

```text
deltaW_onShell = abs(Wlep_m - mW) - abs(Whad_m - mW)
```

because it directly captures whether the leptonic or hadronic W candidate is
more on-shell-like while preserving signal statistics.
