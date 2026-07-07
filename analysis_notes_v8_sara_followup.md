# v9 Sara Follow-Up Notes

## Cut-strength presentation

Each per-cut strength table now reports the counting precision proxy

```text
delta_mu / mu ~= sqrt(S + B) / S
```

immediately before and after the cut, plus the relative improvement caused by
that cut. This is not the final profile-likelihood precision; it is a simple
cut-by-cut diagnostic for explaining why a cut helps or hurts the selection.

Cut2 should be discussed with normalized plots as well as absolute-yield plots:
the absolute plot shows total expected yields, while the normalized plot makes
the strong qq rejection visually obvious. In v9, Cut2 keeps only about 5.7% of
the qq background that survives Cut1, corresponding to about 94.3% qq rejection
at this step.

The former hard Z-mass window,

```text
85 < Zcand_m < 95 GeV
```

is removed from the nominal cut chain because it improves purity but worsens
the counting precision proxy by losing too much signal.  `Zcand_m`/`Zcand_dm`
should remain as diagnostic and BDT-shape inputs.  The former Cut8
`40 < Zcand_p < 60 GeV` is now Cut7.

## Cut3 extra-lepton momentum

The nominal Cut3 is an extra-lepton veto:

```text
n_extra_iso_leptons_p20 == 0
```

A new histogram branch, `extra_iso_lepton_p_after_cut2`, has been added for the
momentum spectrum of additional isolated leptons after Cut2. This plot is meant
to justify the `p > 20 GeV` veto threshold. It will appear after rerunning
histmaker/plots with the updated code.

## On-shell versus off-shell W assignment

The final generated topology is `lvqq`, but event-by-event we cannot assume that
the leptonic `lv` system always comes from the on-shell W. In the v9 analysis,
we keep the hard cuts simple and integrate this ambiguity as BDT/diagnostic
information:

```text
H -> W W*
selected lepton + missing momentum -> W_lep candidate
remaining non-Z jet pair -> W* candidate
```

The complementary interpretation is explicitly retained:

```text
leptonic system may be W*
hadronic non-Z jet pair may be on-shell W
```

Integrated v9 implementation:

1. Keep the current Z-priority jet pairing for the production Z.
2. Add an alternative Z/W chi2 pairing as a diagnostic/BDT hypothesis.
3. Add `Wlep_m`, `Whad_m`, `abs_Wlep_mW`, `abs_Whad_mW`,
   `deltaW_onShell`, `lepW_offshell_like`, and alternative-pairing variables to
   the treemaker.
4. Let the inclusive v9 BDT learn this ambiguity first; only split into
   categories later if the inclusive BDT/fit diagnostics support it.

No hard W-mass cut is added in v9.  That avoids baking in the assumption that
the leptonic W is always on-shell.
