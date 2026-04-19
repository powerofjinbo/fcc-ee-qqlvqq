# Annotated rewrite generated for: ml/fit_profile_likelihood.py
# L1 [Original comment]: #!/usr/bin/env python3
#!/usr/bin/env python3
# L2 [Executable statement]: """Profile likelihood fit for sigma_ZH x BR(H->WW*) measurement.
"""Profile likelihood fit for sigma_ZH x BR(H->WW*) measurement.
# L3 [Blank separator]: 

# L4 [Executable statement]: Methodology follows Jan Eysermans et al. (DOI: 10.17181/9v8ey-n6k50):
Methodology follows Jan Eysermans et al. (DOI: 10.17181/9v8ey-n6k50):
# L5 [Executable statement]: - Template fit to BDT score distribution
- Template fit to BDT score distribution
# L6 [Executable statement]: - Signal strength mu = (sigma x BR)_obs / (sigma x BR)_SM
- Signal strength mu = (sigma x BR)_obs / (sigma x BR)_SM
# L7 [Executable statement]: - 1% flat normalization systematic on each background process
- 1% flat normalization systematic on each background process
# L8 [Executable statement]: - Uses pyhf for the statistical model
- Uses pyhf for the statistical model
# L9 [Blank separator]: 

# L10 [Executable statement]: Inputs:
Inputs:
# L11 [Executable statement]:   - BDT kfold_scores.csv (preferred, from train_xgboost_bdt.py)
  - BDT kfold_scores.csv (preferred, from train_xgboost_bdt.py)
# L12 [Executable statement]:   - Or: test_scores.csv (fallback, with weight rescaling by 1/test_frac)
  - Or: test_scores.csv (fallback, with weight rescaling by 1/test_frac)
# L13 [Blank separator]: 

# L14 [Executable statement]: Outputs:
Outputs:
# L15 [Executable statement]:   - Expected mu_hat, sigma(mu) from Asimov dataset
  - Expected mu_hat, sigma(mu) from Asimov dataset
# L16 [Executable statement]:   - Expected relative uncertainty on sigma_ZH x BR(H->WW*)
  - Expected relative uncertainty on sigma_ZH x BR(H->WW*)
# L17 [Executable statement]: """
"""
# L18 [Blank separator]: 

# L19 [Import statement]: import argparse
import argparse
# L20 [Import statement]: import json
import json
# L21 [Import statement]: import sys
import sys
# L22 [Import statement]: from pathlib import Path
from pathlib import Path
# L23 [Blank separator]: 

# L24 [Import statement]: import numpy as np
import numpy as np
# L25 [Import statement]: import pandas as pd
import pandas as pd
# L26 [Blank separator]: 

# L27 [Executable statement]: THIS_DIR = Path(__file__).resolve().parent
THIS_DIR = Path(__file__).resolve().parent
# L28 [Executable statement]: ANALYSIS_DIR = THIS_DIR.parent
ANALYSIS_DIR = THIS_DIR.parent
# L29 [Executable statement]: sys.path.insert(0, str(ANALYSIS_DIR))
sys.path.insert(0, str(ANALYSIS_DIR))
# L30 [Blank separator]: 

# L31 [Import statement]: from ml_config import BACKGROUND_SAMPLES, DEFAULT_MODEL_DIR, SIGNAL_SAMPLES
from ml_config import BACKGROUND_SAMPLES, DEFAULT_MODEL_DIR, SIGNAL_SAMPLES
# L32 [Blank separator]: 

# L33 [Blank separator]: 

# L34 [Function definition]: def load_scores(scores_path):
def load_scores(scores_path):
# L35 [Executable statement]:     """Load BDT scores from CSV."""
    """Load BDT scores from CSV."""
# L36 [Executable statement]:     df = pd.read_csv(scores_path)
    df = pd.read_csv(scores_path)
# L37 [Function return]:     return df
    return df
# L38 [Blank separator]: 

# L39 [Blank separator]: 

# L40 [Function definition]: def build_templates(df, nbins=20, bdt_cut=None, score_range=(0, 1)):
def build_templates(df, nbins=20, bdt_cut=None, score_range=(0, 1)):
# L41 [Executable statement]:     """Build signal and background histograms from BDT scores.
    """Build signal and background histograms from BDT scores.
# L42 [Blank separator]: 

# L43 [Executable statement]:     Groups backgrounds by physics process type for independent normalization.
    Groups backgrounds by physics process type for independent normalization.
# L44 [Executable statement]:     """
    """
# L45 [Conditional block]:     if bdt_cut is not None:
    if bdt_cut is not None:
# L46 [Executable statement]:         df = df[df["bdt_score"] >= bdt_cut].copy()
        df = df[df["bdt_score"] >= bdt_cut].copy()
# L47 [Blank separator]: 

# L48 [Executable statement]:     bins = np.linspace(score_range[0], score_range[1], nbins + 1)
    bins = np.linspace(score_range[0], score_range[1], nbins + 1)
# L49 [Blank separator]: 

# L50 [Original comment]:     # Signal template (with MC stat errors)
    # Signal template (with MC stat errors)
# L51 [Executable statement]:     sig_mask = df["y_true"] == 1
    sig_mask = df["y_true"] == 1
# L52 [Executable statement]:     sig_hist, _ = np.histogram(
    sig_hist, _ = np.histogram(
# L53 [Executable statement]:         df.loc[sig_mask, "bdt_score"],
        df.loc[sig_mask, "bdt_score"],
# L54 [Executable statement]:         bins=bins,
        bins=bins,
# L55 [Executable statement]:         weights=df.loc[sig_mask, "phys_weight"],
        weights=df.loc[sig_mask, "phys_weight"],
# L56 [Executable statement]:     )
    )
# L57 [Executable statement]:     sig_w2, _ = np.histogram(
    sig_w2, _ = np.histogram(
# L58 [Executable statement]:         df.loc[sig_mask, "bdt_score"],
        df.loc[sig_mask, "bdt_score"],
# L59 [Executable statement]:         bins=bins,
        bins=bins,
# L60 [Executable statement]:         weights=df.loc[sig_mask, "phys_weight"] ** 2,
        weights=df.loc[sig_mask, "phys_weight"] ** 2,
# L61 [Executable statement]:     )
    )
# L62 [Executable statement]:     sig_err = np.sqrt(sig_w2)
    sig_err = np.sqrt(sig_w2)
# L63 [Blank separator]: 

# L64 [Original comment]:     # Group backgrounds by process type for separate normalization systematics
    # Group backgrounds by process type for separate normalization systematics
# L65 [Executable statement]:     bkg_groups = {
    bkg_groups = {
# L66 [Executable statement]:         "WW": ["p8_ee_WW_ecm240"],
        "WW": ["p8_ee_WW_ecm240"],
# L67 [Executable statement]:         "ZZ": ["p8_ee_ZZ_ecm240"],
        "ZZ": ["p8_ee_ZZ_ecm240"],
# L68 [Executable statement]:         "qq": [s for s in BACKGROUND_SAMPLES if s.startswith("wz3p6_ee_") and "tautau" not in s],
        "qq": [s for s in BACKGROUND_SAMPLES if s.startswith("wz3p6_ee_") and "tautau" not in s],
# L69 [Executable statement]:         "tautau": ["wz3p6_ee_tautau_ecm240"],
        "tautau": ["wz3p6_ee_tautau_ecm240"],
# L70 [Executable statement]:         "ZH_other": [
        "ZH_other": [
# L71 [Executable statement]:             s for s in BACKGROUND_SAMPLES
            s for s in BACKGROUND_SAMPLES
# L72 [Conditional block]:             if s.startswith((
            if s.startswith((
# L73 [Executable statement]:                 "wzp6_ee_qqH_H",
                "wzp6_ee_qqH_H",
# L74 [Executable statement]:                 "wzp6_ee_bbH_H",
                "wzp6_ee_bbH_H",
# L75 [Executable statement]:                 "wzp6_ee_ccH_H",
                "wzp6_ee_ccH_H",
# L76 [Executable statement]:                 "wzp6_ee_ssH_H",
                "wzp6_ee_ssH_H",
# L77 [Executable statement]:             ))
            ))
# L78 [Executable statement]:         ],
        ],
# L79 [Executable statement]:     }
    }
# L80 [Blank separator]: 

# L81 [Executable statement]:     bkg_hists = {}
    bkg_hists = {}
# L82 [Executable statement]:     bkg_errs = {}
    bkg_errs = {}
# L83 [Loop over iterable]:     for group_name, samples in bkg_groups.items():
    for group_name, samples in bkg_groups.items():
# L84 [Executable statement]:         mask = df["sample_name"].isin(samples) & (df["y_true"] == 0)
        mask = df["sample_name"].isin(samples) & (df["y_true"] == 0)
# L85 [Conditional block]:         if mask.sum() == 0:
        if mask.sum() == 0:
# L86 [Executable statement]:             continue
            continue
# L87 [Executable statement]:         h, _ = np.histogram(
        h, _ = np.histogram(
# L88 [Executable statement]:             df.loc[mask, "bdt_score"],
            df.loc[mask, "bdt_score"],
# L89 [Executable statement]:             bins=bins,
            bins=bins,
# L90 [Executable statement]:             weights=df.loc[mask, "phys_weight"],
            weights=df.loc[mask, "phys_weight"],
# L91 [Executable statement]:         )
        )
# L92 [Executable statement]:         w2, _ = np.histogram(
        w2, _ = np.histogram(
# L93 [Executable statement]:             df.loc[mask, "bdt_score"],
            df.loc[mask, "bdt_score"],
# L94 [Executable statement]:             bins=bins,
            bins=bins,
# L95 [Executable statement]:             weights=df.loc[mask, "phys_weight"] ** 2,
            weights=df.loc[mask, "phys_weight"] ** 2,
# L96 [Executable statement]:         )
        )
# L97 [Conditional block]:         if h.sum() > 0:
        if h.sum() > 0:
# L98 [Executable statement]:             bkg_hists[group_name] = h
            bkg_hists[group_name] = h
# L99 [Executable statement]:             bkg_errs[group_name] = np.sqrt(w2)
            bkg_errs[group_name] = np.sqrt(w2)
# L100 [Blank separator]: 

# L101 [Function return]:     return sig_hist, sig_err, bkg_hists, bkg_errs, bins
    return sig_hist, sig_err, bkg_hists, bkg_errs, bins
# L102 [Blank separator]: 

# L103 [Blank separator]: 

# L104 [Function definition]: def build_pyhf_model(sig_hist, sig_err, bkg_hists, bkg_errs, norm_uncertainty=0.01, use_staterror=True):
def build_pyhf_model(sig_hist, sig_err, bkg_hists, bkg_errs, norm_uncertainty=0.01, use_staterror=True):
# L105 [Executable statement]:     """Build a pyhf model with signal + backgrounds + normalization + MC stat.
    """Build a pyhf model with signal + backgrounds + normalization + MC stat.
# L106 [Blank separator]: 

# L107 [Executable statement]:     Each background group gets an independent normalization uncertainty.
    Each background group gets an independent normalization uncertainty.
# L108 [Executable statement]:     All samples get Barlow-Beeston MC statistical uncertainties (staterror).
    All samples get Barlow-Beeston MC statistical uncertainties (staterror).
# L109 [Executable statement]:     Signal is the POI (mu).
    Signal is the POI (mu).
# L110 [Executable statement]:     """
    """
# L111 [Import statement]:     import pyhf
    import pyhf
# L112 [Blank separator]: 

# L113 [Original comment]:     # Ensure no negative/zero bins (pyhf requires positive expected rates)
    # Ensure no negative/zero bins (pyhf requires positive expected rates)
# L114 [Executable statement]:     sig_hist = np.maximum(sig_hist, 1e-6)
    sig_hist = np.maximum(sig_hist, 1e-6)
# L115 [Executable statement]:     sig_err = np.maximum(sig_err, 1e-6)
    sig_err = np.maximum(sig_err, 1e-6)
# L116 [Blank separator]: 

# L117 [Executable statement]:     samples = []
    samples = []
# L118 [Blank separator]: 

# L119 [Original comment]:     # Signal sample with MC stat uncertainty
    # Signal sample with MC stat uncertainty
# L120 [Executable statement]:     sig_modifiers = [
    sig_modifiers = [
# L121 [Executable statement]:         {"name": "mu", "type": "normfactor", "data": None},
        {"name": "mu", "type": "normfactor", "data": None},
# L122 [Executable statement]:     ]
    ]
# L123 [Conditional block]:     if use_staterror:
    if use_staterror:
# L124 [Executable statement]:         sig_modifiers.append({"name": "staterror_sig", "type": "staterror", "data": sig_err.tolist()})
        sig_modifiers.append({"name": "staterror_sig", "type": "staterror", "data": sig_err.tolist()})
# L125 [Executable statement]:     samples.append({
    samples.append({
# L126 [Executable statement]:         "name": "signal",
        "name": "signal",
# L127 [Executable statement]:         "data": sig_hist.tolist(),
        "data": sig_hist.tolist(),
# L128 [Executable statement]:         "modifiers": sig_modifiers,
        "modifiers": sig_modifiers,
# L129 [Executable statement]:     })
    })
# L130 [Blank separator]: 

# L131 [Original comment]:     # Background samples with normalization + MC stat systematics
    # Background samples with normalization + MC stat systematics
# L132 [Loop over iterable]:     for group_name, hist in bkg_hists.items():
    for group_name, hist in bkg_hists.items():
# L133 [Executable statement]:         hist = np.maximum(hist, 1e-6)
        hist = np.maximum(hist, 1e-6)
# L134 [Executable statement]:         err = np.maximum(bkg_errs.get(group_name, np.zeros_like(hist)), 1e-6)
        err = np.maximum(bkg_errs.get(group_name, np.zeros_like(hist)), 1e-6)
# L135 [Executable statement]:         modifiers = [
        modifiers = [
# L136 [Executable statement]:             {
            {
# L137 [Executable statement]:                 "name": f"norm_{group_name}",
                "name": f"norm_{group_name}",
# L138 [Executable statement]:                 "type": "normsys",
                "type": "normsys",
# L139 [Executable statement]:                 "data": {"hi": 1.0 + norm_uncertainty, "lo": 1.0 - norm_uncertainty},
                "data": {"hi": 1.0 + norm_uncertainty, "lo": 1.0 - norm_uncertainty},
# L140 [Executable statement]:             },
            },
# L141 [Executable statement]:         ]
        ]
# L142 [Conditional block]:         if use_staterror:
        if use_staterror:
# L143 [Executable statement]:             modifiers.append({"name": f"staterror_{group_name}", "type": "staterror", "data": err.tolist()})
            modifiers.append({"name": f"staterror_{group_name}", "type": "staterror", "data": err.tolist()})
# L144 [Executable statement]:         samples.append({
        samples.append({
# L145 [Executable statement]:             "name": group_name,
            "name": group_name,
# L146 [Executable statement]:             "data": hist.tolist(),
            "data": hist.tolist(),
# L147 [Executable statement]:             "modifiers": modifiers,
            "modifiers": modifiers,
# L148 [Executable statement]:         })
        })
# L149 [Blank separator]: 

# L150 [Executable statement]:     spec = {
    spec = {
# L151 [Executable statement]:         "version": "1.0.0",
        "version": "1.0.0",
# L152 [Executable statement]:         "channels": [
        "channels": [
# L153 [Executable statement]:             {
            {
# L154 [Executable statement]:                 "name": "bdt_score",
                "name": "bdt_score",
# L155 [Executable statement]:                 "samples": samples,
                "samples": samples,
# L156 [Executable statement]:             }
            }
# L157 [Executable statement]:         ],
        ],
# L158 [Executable statement]:         "measurements": [
        "measurements": [
# L159 [Executable statement]:             {
            {
# L160 [Executable statement]:                 "name": "signal_strength",
                "name": "signal_strength",
# L161 [Executable statement]:                 "config": {
                "config": {
# L162 [Executable statement]:                     "poi": "mu",
                    "poi": "mu",
# L163 [Executable statement]:                     "parameters": [
                    "parameters": [
# L164 [Executable statement]:                         {"name": "mu", "bounds": [[0.0, 5.0]], "inits": [1.0]},
                        {"name": "mu", "bounds": [[0.0, 5.0]], "inits": [1.0]},
# L165 [Executable statement]:                     ],
                    ],
# L166 [Executable statement]:                 },
                },
# L167 [Executable statement]:             }
            }
# L168 [Executable statement]:         ],
        ],
# L169 [Executable statement]:         "observations": [
        "observations": [
# L170 [Executable statement]:             {
            {
# L171 [Executable statement]:                 "name": "bdt_score",
                "name": "bdt_score",
# L172 [Executable statement]:                 "data": [],  # filled by Asimov or observed
                "data": [],  # filled by Asimov or observed
# L173 [Executable statement]:             }
            }
# L174 [Executable statement]:         ],
        ],
# L175 [Executable statement]:     }
    }
# L176 [Blank separator]: 

# L177 [Function return]:     return spec
    return spec
# L178 [Blank separator]: 

# L179 [Blank separator]: 

# L180 [Function definition]: def fit_asimov(spec, sig_hist, bkg_hists):
def fit_asimov(spec, sig_hist, bkg_hists):
# L181 [Executable statement]:     """Run Asimov fit: generate expected data at mu=1 and fit."""
    """Run Asimov fit: generate expected data at mu=1 and fit."""
# L182 [Import statement]:     import pyhf
    import pyhf
# L183 [Executable statement]:     pyhf.set_backend("numpy")
    pyhf.set_backend("numpy")
# L184 [Blank separator]: 

# L185 [Original comment]:     # Build Asimov data (sum of signal + all backgrounds at nominal)
    # Build Asimov data (sum of signal + all backgrounds at nominal)
# L186 [Executable statement]:     total = sig_hist.copy()
    total = sig_hist.copy()
# L187 [Loop over iterable]:     for h in bkg_hists.values():
    for h in bkg_hists.values():
# L188 [Executable statement]:         total += h
        total += h
# L189 [Executable statement]:     spec["observations"][0]["data"] = total.tolist()
    spec["observations"][0]["data"] = total.tolist()
# L190 [Blank separator]: 

# L191 [Executable statement]:     ws = pyhf.Workspace(spec)
    ws = pyhf.Workspace(spec)
# L192 [Executable statement]:     model = ws.model()
    model = ws.model()
# L193 [Executable statement]:     data = total.tolist() + model.config.auxdata
    data = total.tolist() + model.config.auxdata
# L194 [Blank separator]: 

# L195 [Original comment]:     # MLE fit
    # MLE fit
# L196 [Executable statement]:     bestfit, twice_nll_val = pyhf.infer.mle.fit(
    bestfit, twice_nll_val = pyhf.infer.mle.fit(
# L197 [Executable statement]:         data, model, return_fitted_val=True
        data, model, return_fitted_val=True
# L198 [Executable statement]:     )
    )
# L199 [Executable statement]:     bestfit = np.asarray(bestfit)
    bestfit = np.asarray(bestfit)
# L200 [Blank separator]: 

# L201 [Original comment]:     # Compute uncertainties via numerical Hessian of NLL
    # Compute uncertainties via numerical Hessian of NLL
# L202 [Function definition]:     def nll_func(pars):
    def nll_func(pars):
# L203 [Executable statement]:         pars_tensor = pyhf.tensorlib.astensor(pars)
        pars_tensor = pyhf.tensorlib.astensor(pars)
# L204 [Executable statement]:         val = pyhf.infer.mle.twice_nll(pars_tensor, data, model)
        val = pyhf.infer.mle.twice_nll(pars_tensor, data, model)
# L205 [Function return]:         return float(np.asarray(val).item()) / 2.0
        return float(np.asarray(val).item()) / 2.0
# L206 [Blank separator]: 

# L207 [Executable statement]:     n = len(bestfit)
    n = len(bestfit)
# L208 [Executable statement]:     eps = 1e-4
    eps = 1e-4
# L209 [Executable statement]:     hessian = np.zeros((n, n))
    hessian = np.zeros((n, n))
# L210 [Executable statement]:     f0 = nll_func(bestfit)
    f0 = nll_func(bestfit)
# L211 [Loop over iterable]:     for i in range(n):
    for i in range(n):
# L212 [Loop over iterable]:         for j in range(i, n):
        for j in range(i, n):
# L213 [Executable statement]:             pars_pp = bestfit.copy()
            pars_pp = bestfit.copy()
# L214 [Executable statement]:             pars_pp[i] += eps
            pars_pp[i] += eps
# L215 [Executable statement]:             pars_pp[j] += eps
            pars_pp[j] += eps
# L216 [Executable statement]:             pars_pm = bestfit.copy()
            pars_pm = bestfit.copy()
# L217 [Executable statement]:             pars_pm[i] += eps
            pars_pm[i] += eps
# L218 [Executable statement]:             pars_pm[j] -= eps
            pars_pm[j] -= eps
# L219 [Executable statement]:             pars_mp = bestfit.copy()
            pars_mp = bestfit.copy()
# L220 [Executable statement]:             pars_mp[i] -= eps
            pars_mp[i] -= eps
# L221 [Executable statement]:             pars_mp[j] += eps
            pars_mp[j] += eps
# L222 [Executable statement]:             pars_mm = bestfit.copy()
            pars_mm = bestfit.copy()
# L223 [Executable statement]:             pars_mm[i] -= eps
            pars_mm[i] -= eps
# L224 [Executable statement]:             pars_mm[j] -= eps
            pars_mm[j] -= eps
# L225 [Executable statement]:             hessian[i, j] = (nll_func(pars_pp) - nll_func(pars_pm) - nll_func(pars_mp) + nll_func(pars_mm)) / (4 * eps * eps)
            hessian[i, j] = (nll_func(pars_pp) - nll_func(pars_pm) - nll_func(pars_mp) + nll_func(pars_mm)) / (4 * eps * eps)
# L226 [Executable statement]:             hessian[j, i] = hessian[i, j]
            hessian[j, i] = hessian[i, j]
# L227 [Blank separator]: 

# L228 [Exception handling start]:     try:
    try:
# L229 [Executable statement]:         cov = np.linalg.inv(hessian)
        cov = np.linalg.inv(hessian)
# L230 [Executable statement]:         errors = np.sqrt(np.maximum(np.diag(cov), 0))
        errors = np.sqrt(np.maximum(np.diag(cov), 0))
# L231 [Exception handler]:     except np.linalg.LinAlgError:
    except np.linalg.LinAlgError:
# L232 [Executable statement]:         errors = np.zeros(n)
        errors = np.zeros(n)
# L233 [Blank separator]: 

# L234 [Executable statement]:     mu_idx = model.config.poi_index
    mu_idx = model.config.poi_index
# L235 [Executable statement]:     mu_hat = float(bestfit[mu_idx])
    mu_hat = float(bestfit[mu_idx])
# L236 [Executable statement]:     mu_err = float(errors[mu_idx])
    mu_err = float(errors[mu_idx])
# L237 [Blank separator]: 

# L238 [Original comment]:     # All parameter results
    # All parameter results
# L239 [Executable statement]:     par_names = model.config.par_names
    par_names = model.config.par_names
# L240 [Executable statement]:     fit_results = {}
    fit_results = {}
# L241 [Loop over iterable]:     for i, name in enumerate(par_names):
    for i, name in enumerate(par_names):
# L242 [Executable statement]:         fit_results[name] = {
        fit_results[name] = {
# L243 [Executable statement]:             "value": float(bestfit[i]),
            "value": float(bestfit[i]),
# L244 [Executable statement]:             "error": float(errors[i]),
            "error": float(errors[i]),
# L245 [Executable statement]:         }
        }
# L246 [Blank separator]: 

# L247 [Function return]:     return mu_hat, mu_err, fit_results
    return mu_hat, mu_err, fit_results
# L248 [Blank separator]: 

# L249 [Blank separator]: 

# L250 [Function definition]: def scan_bdt_cut(df, cuts=None, fit_nbins=1, norm_uncertainty=0.01, use_staterror=True):
def scan_bdt_cut(df, cuts=None, fit_nbins=1, norm_uncertainty=0.01, use_staterror=True):
# L251 [Executable statement]:     """Scan BDT cuts for a fixed fit granularity.
    """Scan BDT cuts for a fixed fit granularity.
# L252 [Blank separator]: 

# L253 [Executable statement]:     The paper comparison between "counting" and "shape" fits should use a true
    The paper comparison between "counting" and "shape" fits should use a true
# L254 [Executable statement]:     single-bin model after the threshold cut. `fit_nbins=1` implements that
    single-bin model after the threshold cut. `fit_nbins=1` implements that
# L255 [Executable statement]:     counting baseline, while larger values can be used for shape studies.
    counting baseline, while larger values can be used for shape studies.
# L256 [Executable statement]:     """
    """
# L257 [Import statement]:     import pyhf
    import pyhf
# L258 [Blank separator]: 

# L259 [Conditional block]:     if cuts is None:
    if cuts is None:
# L260 [Executable statement]:         coarse_cuts = np.arange(0.0, 0.90, 0.05)
        coarse_cuts = np.arange(0.0, 0.90, 0.05)
# L261 [Executable statement]:         fine_cuts = np.arange(0.90, 1.00, 0.01)
        fine_cuts = np.arange(0.90, 1.00, 0.01)
# L262 [Executable statement]:         cuts = np.unique(np.round(np.concatenate([coarse_cuts, fine_cuts]), 2))
        cuts = np.unique(np.round(np.concatenate([coarse_cuts, fine_cuts]), 2))
# L263 [Blank separator]: 

# L264 [Executable statement]:     results = []
    results = []
# L265 [Loop over iterable]:     for cut in cuts:
    for cut in cuts:
# L266 [Executable statement]:         sig_hist, sig_err, bkg_hists, bkg_errs, bins = build_templates(
        sig_hist, sig_err, bkg_hists, bkg_errs, bins = build_templates(
# L267 [Executable statement]:             df, nbins=fit_nbins, bdt_cut=cut,
            df, nbins=fit_nbins, bdt_cut=cut,
# L268 [Executable statement]:         )
        )
# L269 [Blank separator]: 

# L270 [Executable statement]:         n_sig = sig_hist.sum()
        n_sig = sig_hist.sum()
# L271 [Executable statement]:         n_bkg = sum(h.sum() for h in bkg_hists.values())
        n_bkg = sum(h.sum() for h in bkg_hists.values())
# L272 [Blank separator]: 

# L273 [Conditional block]:         if n_sig < 1 or n_bkg < 1:
        if n_sig < 1 or n_bkg < 1:
# L274 [Executable statement]:             continue
            continue
# L275 [Blank separator]: 

# L276 [Executable statement]:         spec = build_pyhf_model(sig_hist, sig_err, bkg_hists, bkg_errs, norm_uncertainty, use_staterror=use_staterror)
        spec = build_pyhf_model(sig_hist, sig_err, bkg_hists, bkg_errs, norm_uncertainty, use_staterror=use_staterror)
# L277 [Blank separator]: 

# L278 [Exception handling start]:         try:
        try:
# L279 [Executable statement]:             mu_hat, mu_err, _ = fit_asimov(spec, sig_hist, bkg_hists)
            mu_hat, mu_err, _ = fit_asimov(spec, sig_hist, bkg_hists)
# L280 [Executable statement]:             rel_err = mu_err / mu_hat if mu_hat > 0 else float("inf")
            rel_err = mu_err / mu_hat if mu_hat > 0 else float("inf")
# L281 [Exception handler]:         except Exception as e:
        except Exception as e:
# L282 [Runtime log output]:             print(f"  cut={cut:.2f}: fit failed ({e})")
            print(f"  cut={cut:.2f}: fit failed ({e})")
# L283 [Executable statement]:             continue
            continue
# L284 [Blank separator]: 

# L285 [Executable statement]:         results.append({
        results.append({
# L286 [Executable statement]:             "bdt_cut": float(cut),
            "bdt_cut": float(cut),
# L287 [Executable statement]:             "fit_nbins": int(fit_nbins),
            "fit_nbins": int(fit_nbins),
# L288 [Executable statement]:             "n_sig": float(n_sig),
            "n_sig": float(n_sig),
# L289 [Executable statement]:             "n_bkg": float(n_bkg),
            "n_bkg": float(n_bkg),
# L290 [Executable statement]:             "s_over_b": float(n_sig / n_bkg) if n_bkg > 0 else 0,
            "s_over_b": float(n_sig / n_bkg) if n_bkg > 0 else 0,
# L291 [Executable statement]:             "s_over_sqrt_b": float(n_sig / np.sqrt(n_bkg)) if n_bkg > 0 else 0,
            "s_over_sqrt_b": float(n_sig / np.sqrt(n_bkg)) if n_bkg > 0 else 0,
# L292 [Executable statement]:             "mu_hat": mu_hat,
            "mu_hat": mu_hat,
# L293 [Executable statement]:             "mu_err": mu_err,
            "mu_err": mu_err,
# L294 [Executable statement]:             "rel_uncertainty": rel_err,
            "rel_uncertainty": rel_err,
# L295 [Executable statement]:         })
        })
# L296 [Blank separator]: 

# L297 [Runtime log output]:         print(f"  cut={cut:.2f}: S={n_sig:.0f}, B={n_bkg:.0f}, "
        print(f"  cut={cut:.2f}: S={n_sig:.0f}, B={n_bkg:.0f}, "
# L298 [Executable statement]:               f"S/√B={n_sig/np.sqrt(n_bkg):.1f}, δμ/μ={rel_err*100:.2f}%")
              f"S/√B={n_sig/np.sqrt(n_bkg):.1f}, δμ/μ={rel_err*100:.2f}%")
# L299 [Blank separator]: 

# L300 [Function return]:     return results
    return results
# L301 [Blank separator]: 

# L302 [Blank separator]: 

# L303 [Function definition]: def make_fit_plots(output_dir, scan_results, best_result, sig_hist, bkg_hists, bins, shape_rel_unc_pct=None):
def make_fit_plots(output_dir, scan_results, best_result, sig_hist, bkg_hists, bins, shape_rel_unc_pct=None):
# L304 [Executable statement]:     """Generate fit diagnostic plots."""
    """Generate fit diagnostic plots."""
# L305 [Import statement]:     import matplotlib
    import matplotlib
# L306 [Executable statement]:     matplotlib.use("Agg")
    matplotlib.use("Agg")
# L307 [Import statement]:     import matplotlib.pyplot as plt
    import matplotlib.pyplot as plt
# L308 [Import statement]:     from matplotlib.ticker import LogLocator, NullFormatter
    from matplotlib.ticker import LogLocator, NullFormatter
# L309 [Blank separator]: 

# L310 [Executable statement]:     plots_dir = output_dir / "plots"
    plots_dir = output_dir / "plots"
# L311 [Executable statement]:     plots_dir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)
# L312 [Blank separator]: 

# L313 [Original comment]:     # 1. BDT cut optimization scan
    # 1. BDT cut optimization scan
# L314 [Conditional block]:     if len(scan_results) > 1:
    if len(scan_results) > 1:
# L315 [Executable statement]:         fig, ax = plt.subplots(figsize=(6.0, 4.6))
        fig, ax = plt.subplots(figsize=(6.0, 4.6))
# L316 [Blank separator]: 

# L317 [Executable statement]:         plot_results = [r for r in scan_results if r["bdt_cut"] >= 0.05]
        plot_results = [r for r in scan_results if r["bdt_cut"] >= 0.05]
# L318 [Executable statement]:         cuts = [r["bdt_cut"] for r in plot_results]
        cuts = [r["bdt_cut"] for r in plot_results]
# L319 [Executable statement]:         rel_unc = [r["rel_uncertainty"] * 100 for r in plot_results]
        rel_unc = [r["rel_uncertainty"] * 100 for r in plot_results]
# L320 [Blank separator]: 

# L321 [Executable statement]:         ax.plot(cuts, rel_unc, color="#2C7FB8", marker="o", markersize=4.5, linewidth=2.0)
        ax.plot(cuts, rel_unc, color="#2C7FB8", marker="o", markersize=4.5, linewidth=2.0)
# L322 [Executable statement]:         ax.set_xlabel("BDT score threshold")
        ax.set_xlabel("BDT score threshold")
# L323 [Executable statement]:         ax.set_ylabel(r"Expected $\delta\mu/\mu$ [%]")
        ax.set_ylabel(r"Expected $\delta\mu/\mu$ [%]")
# L324 [Executable statement]:         ax.set_title("1-bin counting reference scan")
        ax.set_title("1-bin counting reference scan")
# L325 [Executable statement]:         ax.grid(True, alpha=0.25)
        ax.grid(True, alpha=0.25)
# L326 [Executable statement]:         ax.set_xlim(0.05, 1.0)
        ax.set_xlim(0.05, 1.0)
# L327 [Blank separator]: 

# L328 [Conditional block]:         if shape_rel_unc_pct is not None:
        if shape_rel_unc_pct is not None:
# L329 [Executable statement]:             ax.axhline(
            ax.axhline(
# L330 [Executable statement]:                 shape_rel_unc_pct,
                shape_rel_unc_pct,
# L331 [Executable statement]:                 color="#333333",
                color="#333333",
# L332 [Executable statement]:                 linestyle=(0, (4, 3)),
                linestyle=(0, (4, 3)),
# L333 [Executable statement]:                 linewidth=1.4,
                linewidth=1.4,
# L334 [Executable statement]:                 label=f"20-bin shape fit: {shape_rel_unc_pct:.2f}%",
                label=f"20-bin shape fit: {shape_rel_unc_pct:.2f}%",
# L335 [Executable statement]:             )
            )
# L336 [Blank separator]: 

# L337 [Conditional block]:         if best_result:
        if best_result:
# L338 [Executable statement]:             best_cut = best_result["bdt_cut"]
            best_cut = best_result["bdt_cut"]
# L339 [Executable statement]:             best_unc = best_result["rel_uncertainty"] * 100
            best_unc = best_result["rel_uncertainty"] * 100
# L340 [Executable statement]:             ax.axvline(best_cut, color="#D64F4F", linestyle="--", linewidth=1.4)
            ax.axvline(best_cut, color="#D64F4F", linestyle="--", linewidth=1.4)
# L341 [Executable statement]:             ax.scatter([best_cut], [best_unc], color="#D64F4F", zorder=5)
            ax.scatter([best_cut], [best_unc], color="#D64F4F", zorder=5)
# L342 [Executable statement]:             ax.annotate(
            ax.annotate(
# L343 [Executable statement]:                 f"Best counting:\n{best_unc:.2f}% @ {best_cut:.2f}",
                f"Best counting:\n{best_unc:.2f}% @ {best_cut:.2f}",
# L344 [Executable statement]:                 xy=(best_cut, best_unc),
                xy=(best_cut, best_unc),
# L345 [Executable statement]:                 xytext=(-74, 22),
                xytext=(-74, 22),
# L346 [Executable statement]:                 textcoords="offset points",
                textcoords="offset points",
# L347 [Executable statement]:                 fontsize=9,
                fontsize=9,
# L348 [Executable statement]:                 bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": "#D64F4F", "alpha": 0.92},
                bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": "#D64F4F", "alpha": 0.92},
# L349 [Executable statement]:                 arrowprops={"arrowstyle": "->", "color": "#D64F4F", "lw": 1.1},
                arrowprops={"arrowstyle": "->", "color": "#D64F4F", "lw": 1.1},
# L350 [Executable statement]:             )
            )
# L351 [Blank separator]: 

# L352 [Executable statement]:         ax.legend(frameon=False, fontsize=9, loc="upper right")
        ax.legend(frameon=False, fontsize=9, loc="upper right")
# L353 [Executable statement]:         fig.tight_layout()
        fig.tight_layout()
# L354 [Executable statement]:         fig.savefig(plots_dir / "bdt_cut_scan.pdf", dpi=150)
        fig.savefig(plots_dir / "bdt_cut_scan.pdf", dpi=150)
# L355 [Executable statement]:         fig.savefig(plots_dir / "bdt_cut_scan.png", dpi=150)
        fig.savefig(plots_dir / "bdt_cut_scan.png", dpi=150)
# L356 [Executable statement]:         plt.close(fig)
        plt.close(fig)
# L357 [Blank separator]: 

# L358 [Original comment]:     # 2. Template shapes at best working point
    # 2. Template shapes at best working point
# L359 [Executable statement]:     fig, (ax_top, ax_bottom) = plt.subplots(
    fig, (ax_top, ax_bottom) = plt.subplots(
# L360 [Executable statement]:         2,
        2,
# L361 [Executable statement]:         1,
        1,
# L362 [Executable statement]:         figsize=(7.5, 6.8),
        figsize=(7.5, 6.8),
# L363 [Executable statement]:         sharex=True,
        sharex=True,
# L364 [Executable statement]:         gridspec_kw={"height_ratios": [2.5, 1.8], "hspace": 0.05},
        gridspec_kw={"height_ratios": [2.5, 1.8], "hspace": 0.05},
# L365 [Executable statement]:     )
    )
# L366 [Executable statement]:     bin_centers = 0.5 * (bins[:-1] + bins[1:])
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
# L367 [Executable statement]:     bin_width = bins[1] - bins[0]
    bin_width = bins[1] - bins[0]
# L368 [Blank separator]: 

# L369 [Original comment]:     # Stack backgrounds
    # Stack backgrounds
# L370 [Executable statement]:     bkg_labels = list(bkg_hists.keys())
    bkg_labels = list(bkg_hists.keys())
# L371 [Executable statement]:     bkg_arrays = [bkg_hists[k] for k in bkg_labels]
    bkg_arrays = [bkg_hists[k] for k in bkg_labels]
# L372 [Executable statement]:     colors = ["#5B7BD5", "#D65F5F", "#4CAF50", "#F1C84B", "#F39C5A"]
    colors = ["#5B7BD5", "#D65F5F", "#4CAF50", "#F1C84B", "#F39C5A"]
# L373 [Blank separator]: 

# L374 [Executable statement]:     ax_top.hist(
    ax_top.hist(
# L375 [Executable statement]:         [bin_centers] * len(bkg_arrays),
        [bin_centers] * len(bkg_arrays),
# L376 [Executable statement]:         bins=bins,
        bins=bins,
# L377 [Executable statement]:         weights=bkg_arrays,
        weights=bkg_arrays,
# L378 [Executable statement]:         stacked=True,
        stacked=True,
# L379 [Executable statement]:         label=[f"Bkg: {l}" for l in bkg_labels],
        label=[f"Bkg: {l}" for l in bkg_labels],
# L380 [Executable statement]:         color=colors[:len(bkg_arrays)],
        color=colors[:len(bkg_arrays)],
# L381 [Executable statement]:         alpha=0.88,
        alpha=0.88,
# L382 [Executable statement]:     )
    )
# L383 [Blank separator]: 

# L384 [Executable statement]:     total_bkg = np.sum(np.asarray(bkg_arrays), axis=0)
    total_bkg = np.sum(np.asarray(bkg_arrays), axis=0)
# L385 [Executable statement]:     ax_top.step(
    ax_top.step(
# L386 [Executable statement]:         bins[:-1],
        bins[:-1],
# L387 [Executable statement]:         total_bkg,
        total_bkg,
# L388 [Executable statement]:         where="post",
        where="post",
# L389 [Executable statement]:         color="#22313F",
        color="#22313F",
# L390 [Executable statement]:         linewidth=1.2,
        linewidth=1.2,
# L391 [Executable statement]:         alpha=0.95,
        alpha=0.95,
# L392 [Executable statement]:         label="Total background",
        label="Total background",
# L393 [Executable statement]:     )
    )
# L394 [Blank separator]: 

# L395 [Original comment]:     # Signal overlay (scaled for visibility)
    # Signal overlay (scaled for visibility)
# L396 [Executable statement]:     sig_scale = max(1, int(sum(h.sum() for h in bkg_hists.values()) / sig_hist.sum() / 5)) if sig_hist.sum() > 0 else 1
    sig_scale = max(1, int(sum(h.sum() for h in bkg_hists.values()) / sig_hist.sum() / 5)) if sig_hist.sum() > 0 else 1
# L397 [Executable statement]:     ax_top.step(
    ax_top.step(
# L398 [Executable statement]:         bins[:-1],
        bins[:-1],
# L399 [Executable statement]:         sig_hist * sig_scale,
        sig_hist * sig_scale,
# L400 [Executable statement]:         where="post",
        where="post",
# L401 [Executable statement]:         color="black",
        color="black",
# L402 [Executable statement]:         linewidth=2.0,
        linewidth=2.0,
# L403 [Executable statement]:         label=f"Signal (x{sig_scale})",
        label=f"Signal (x{sig_scale})",
# L404 [Executable statement]:     )
    )
# L405 [Blank separator]: 

# L406 [Executable statement]:     ax_top.set_ylabel(f"Events / {bin_width:.2f}")
    ax_top.set_ylabel(f"Events / {bin_width:.2f}")
# L407 [Executable statement]:     ax_top.set_title("BDT score templates and background composition")
    ax_top.set_title("BDT score templates and background composition")
# L408 [Executable statement]:     ax_top.legend(fontsize=8.7, ncol=2, frameon=False, loc="upper center")
    ax_top.legend(fontsize=8.7, ncol=2, frameon=False, loc="upper center")
# L409 [Executable statement]:     ax_top.text(0.03, 0.95, r'$\mathbf{FCC\text{-}ee}$ Simulation',
    ax_top.text(0.03, 0.95, r'$\mathbf{FCC\text{-}ee}$ Simulation',
# L410 [Executable statement]:                 transform=ax_top.transAxes, fontsize=10, va='top', fontstyle='italic')
                transform=ax_top.transAxes, fontsize=10, va='top', fontstyle='italic')
# L411 [Executable statement]:     ax_top.text(0.03, 0.89, r'$\sqrt{s}=240$ GeV, $10.8\,\mathrm{ab}^{-1}$',
    ax_top.text(0.03, 0.89, r'$\sqrt{s}=240$ GeV, $10.8\,\mathrm{ab}^{-1}$',
# L412 [Executable statement]:                 transform=ax_top.transAxes, fontsize=9, va='top')
                transform=ax_top.transAxes, fontsize=9, va='top')
# L413 [Executable statement]:     ax_top.set_yscale("log")
    ax_top.set_yscale("log")
# L414 [Executable statement]:     ax_top.set_ylim(bottom=0.1)
    ax_top.set_ylim(bottom=0.1)
# L415 [Executable statement]:     ax_top.yaxis.set_major_locator(LogLocator(base=10.0, numticks=12))
    ax_top.yaxis.set_major_locator(LogLocator(base=10.0, numticks=12))
# L416 [Executable statement]:     ax_top.yaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2, 10), numticks=120))
    ax_top.yaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2, 10), numticks=120))
# L417 [Executable statement]:     ax_top.yaxis.set_minor_formatter(NullFormatter())
    ax_top.yaxis.set_minor_formatter(NullFormatter())
# L418 [Executable statement]:     ax_top.grid(axis="y", which="major", alpha=0.24, linewidth=0.8)
    ax_top.grid(axis="y", which="major", alpha=0.24, linewidth=0.8)
# L419 [Executable statement]:     ax_top.grid(axis="y", which="minor", alpha=0.14, linewidth=0.55)
    ax_top.grid(axis="y", which="minor", alpha=0.14, linewidth=0.55)
# L420 [Executable statement]:     ax_top.tick_params(axis="y", which="major", labelsize=9)
    ax_top.tick_params(axis="y", which="major", labelsize=9)
# L421 [Executable statement]:     ax_top.tick_params(axis="y", which="minor", length=2.5)
    ax_top.tick_params(axis="y", which="minor", length=2.5)
# L422 [Blank separator]: 

# L423 [Original comment]:     # Sub-dominant background yields panel (excluding WW)
    # Sub-dominant background yields panel (excluding WW)
# L424 [Executable statement]:     subdominant = [
    subdominant = [
# L425 [Executable statement]:         (label, arr, color)
        (label, arr, color)
# L426 [Loop over iterable]:         for label, arr, color in zip(bkg_labels, bkg_arrays, colors)
        for label, arr, color in zip(bkg_labels, bkg_arrays, colors)
# L427 [Conditional block]:         if label != "WW"
        if label != "WW"
# L428 [Executable statement]:     ]
    ]
# L429 [Executable statement]:     ax_bottom.hist(
    ax_bottom.hist(
# L430 [Executable statement]:         [bin_centers] * len(subdominant),
        [bin_centers] * len(subdominant),
# L431 [Executable statement]:         bins=bins,
        bins=bins,
# L432 [Executable statement]:         weights=[arr for _, arr, _ in subdominant],
        weights=[arr for _, arr, _ in subdominant],
# L433 [Executable statement]:         stacked=True,
        stacked=True,
# L434 [Executable statement]:         label=[l for l, _, _ in subdominant],
        label=[l for l, _, _ in subdominant],
# L435 [Executable statement]:         color=[c for _, _, c in subdominant],
        color=[c for _, _, c in subdominant],
# L436 [Executable statement]:         alpha=0.88,
        alpha=0.88,
# L437 [Executable statement]:     )
    )
# L438 [Executable statement]:     ax_bottom.set_xlabel("BDT score")
    ax_bottom.set_xlabel("BDT score")
# L439 [Executable statement]:     ax_bottom.set_ylabel(f"Events / {bin_width:.2f}")
    ax_bottom.set_ylabel(f"Events / {bin_width:.2f}")
# L440 [Executable statement]:     ax_bottom.set_xlim(0.0, 1.0)
    ax_bottom.set_xlim(0.0, 1.0)
# L441 [Executable statement]:     ax_bottom.set_yscale("log")
    ax_bottom.set_yscale("log")
# L442 [Executable statement]:     ax_bottom.set_ylim(bottom=0.1)
    ax_bottom.set_ylim(bottom=0.1)
# L443 [Executable statement]:     ax_bottom.legend(fontsize=7, ncol=2, frameon=False, loc="upper right")
    ax_bottom.legend(fontsize=7, ncol=2, frameon=False, loc="upper right")
# L444 [Executable statement]:     ax_bottom.grid(axis="y", which="major", alpha=0.24)
    ax_bottom.grid(axis="y", which="major", alpha=0.24)
# L445 [Executable statement]:     ax_bottom.text(
    ax_bottom.text(
# L446 [Executable statement]:         0.02,
        0.02,
# L447 [Executable statement]:         0.95,
        0.95,
# L448 [Executable statement]:         "Sub-dominant backgrounds (excl. WW)",
        "Sub-dominant backgrounds (excl. WW)",
# L449 [Executable statement]:         transform=ax_bottom.transAxes,
        transform=ax_bottom.transAxes,
# L450 [Executable statement]:         fontsize=8,
        fontsize=8,
# L451 [Executable statement]:         va="top",
        va="top",
# L452 [Executable statement]:     )
    )
# L453 [Executable statement]:     fig.tight_layout()
    fig.tight_layout()
# L454 [Executable statement]:     fig.savefig(plots_dir / "fit_templates.pdf", dpi=150)
    fig.savefig(plots_dir / "fit_templates.pdf", dpi=150)
# L455 [Executable statement]:     fig.savefig(plots_dir / "fit_templates.png", dpi=150)
    fig.savefig(plots_dir / "fit_templates.png", dpi=150)
# L456 [Executable statement]:     plt.close(fig)
    plt.close(fig)
# L457 [Blank separator]: 

# L458 [Original comment]:     # 3. Rank-ordered BDT bins (highest score to lowest score)
    # 3. Rank-ordered BDT bins (highest score to lowest score)
# L459 [Executable statement]:     rank_order = np.arange(len(sig_hist))[::-1]
    rank_order = np.arange(len(sig_hist))[::-1]
# L460 [Executable statement]:     rank_bins = np.arange(1, len(sig_hist) + 1)
    rank_bins = np.arange(1, len(sig_hist) + 1)
# L461 [Executable statement]:     sig_rank = sig_hist[rank_order]
    sig_rank = sig_hist[rank_order]
# L462 [Executable statement]:     bkg_rank_arrays = [arr[rank_order] for arr in bkg_arrays]
    bkg_rank_arrays = [arr[rank_order] for arr in bkg_arrays]
# L463 [Executable statement]:     total_rank = np.sum(np.asarray(bkg_rank_arrays), axis=0)
    total_rank = np.sum(np.asarray(bkg_rank_arrays), axis=0)
# L464 [Blank separator]: 

# L465 [Executable statement]:     fig, (ax_top, ax_bottom) = plt.subplots(
    fig, (ax_top, ax_bottom) = plt.subplots(
# L466 [Executable statement]:         2,
        2,
# L467 [Executable statement]:         1,
        1,
# L468 [Executable statement]:         figsize=(7.4, 6.6),
        figsize=(7.4, 6.6),
# L469 [Executable statement]:         sharex=True,
        sharex=True,
# L470 [Executable statement]:         gridspec_kw={"height_ratios": [3.0, 1.15], "hspace": 0.05},
        gridspec_kw={"height_ratios": [3.0, 1.15], "hspace": 0.05},
# L471 [Executable statement]:     )
    )
# L472 [Blank separator]: 

# L473 [Executable statement]:     cumulative = np.zeros_like(rank_bins, dtype=float)
    cumulative = np.zeros_like(rank_bins, dtype=float)
# L474 [Loop over iterable]:     for label, arr, color in zip(bkg_labels, bkg_rank_arrays, colors):
    for label, arr, color in zip(bkg_labels, bkg_rank_arrays, colors):
# L475 [Executable statement]:         ax_top.bar(
        ax_top.bar(
# L476 [Executable statement]:             rank_bins,
            rank_bins,
# L477 [Executable statement]:             arr,
            arr,
# L478 [Executable statement]:             bottom=cumulative,
            bottom=cumulative,
# L479 [Executable statement]:             width=0.90,
            width=0.90,
# L480 [Executable statement]:             color=color,
            color=color,
# L481 [Executable statement]:             alpha=0.88,
            alpha=0.88,
# L482 [Executable statement]:             label=f"Bkg: {label}",
            label=f"Bkg: {label}",
# L483 [Executable statement]:             linewidth=0.0,
            linewidth=0.0,
# L484 [Executable statement]:         )
        )
# L485 [Executable statement]:         cumulative += arr
        cumulative += arr
# L486 [Blank separator]: 

# L487 [Executable statement]:     sig_scale_rank = sig_scale
    sig_scale_rank = sig_scale
# L488 [Executable statement]:     ax_top.step(
    ax_top.step(
# L489 [Executable statement]:         np.r_[rank_bins, rank_bins[-1] + 1] - 0.5,
        np.r_[rank_bins, rank_bins[-1] + 1] - 0.5,
# L490 [Executable statement]:         np.r_[sig_rank * sig_scale_rank, sig_rank[-1] * sig_scale_rank],
        np.r_[sig_rank * sig_scale_rank, sig_rank[-1] * sig_scale_rank],
# L491 [Executable statement]:         where="post",
        where="post",
# L492 [Executable statement]:         color="black",
        color="black",
# L493 [Executable statement]:         linewidth=2.0,
        linewidth=2.0,
# L494 [Executable statement]:         label=f"Signal (x{sig_scale_rank})",
        label=f"Signal (x{sig_scale_rank})",
# L495 [Executable statement]:     )
    )
# L496 [Executable statement]:     ax_top.set_ylabel("Events / rank bin")
    ax_top.set_ylabel("Events / rank bin")
# L497 [Executable statement]:     ax_top.set_title("Rank-ordered BDT bins")
    ax_top.set_title("Rank-ordered BDT bins")
# L498 [Executable statement]:     ax_top.set_yscale("log")
    ax_top.set_yscale("log")
# L499 [Executable statement]:     ax_top.set_ylim(bottom=0.1)
    ax_top.set_ylim(bottom=0.1)
# L500 [Executable statement]:     ax_top.yaxis.set_major_locator(LogLocator(base=10.0, numticks=12))
    ax_top.yaxis.set_major_locator(LogLocator(base=10.0, numticks=12))
# L501 [Executable statement]:     ax_top.yaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2, 10), numticks=120))
    ax_top.yaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2, 10), numticks=120))
# L502 [Executable statement]:     ax_top.yaxis.set_minor_formatter(NullFormatter())
    ax_top.yaxis.set_minor_formatter(NullFormatter())
# L503 [Executable statement]:     ax_top.grid(axis="y", which="major", alpha=0.24, linewidth=0.8)
    ax_top.grid(axis="y", which="major", alpha=0.24, linewidth=0.8)
# L504 [Executable statement]:     ax_top.grid(axis="y", which="minor", alpha=0.14, linewidth=0.55)
    ax_top.grid(axis="y", which="minor", alpha=0.14, linewidth=0.55)
# L505 [Executable statement]:     ax_top.tick_params(axis="y", which="major", labelsize=9)
    ax_top.tick_params(axis="y", which="major", labelsize=9)
# L506 [Executable statement]:     ax_top.tick_params(axis="y", which="minor", length=2.5)
    ax_top.tick_params(axis="y", which="minor", length=2.5)
# L507 [Executable statement]:     ax_top.legend(fontsize=8.6, ncol=2, frameon=False, loc="upper center")
    ax_top.legend(fontsize=8.6, ncol=2, frameon=False, loc="upper center")
# L508 [Executable statement]:     ax_top.text(
    ax_top.text(
# L509 [Executable statement]:         0.03,
        0.03,
# L510 [Executable statement]:         0.95,
        0.95,
# L511 [Executable statement]:         r'$\mathbf{FCC\text{-}ee}$ Simulation',
        r'$\mathbf{FCC\text{-}ee}$ Simulation',
# L512 [Executable statement]:         transform=ax_top.transAxes,
        transform=ax_top.transAxes,
# L513 [Executable statement]:         fontsize=10,
        fontsize=10,
# L514 [Executable statement]:         va='top',
        va='top',
# L515 [Executable statement]:         fontstyle='italic',
        fontstyle='italic',
# L516 [Executable statement]:     )
    )
# L517 [Executable statement]:     ax_top.text(
    ax_top.text(
# L518 [Executable statement]:         0.03,
        0.03,
# L519 [Executable statement]:         0.89,
        0.89,
# L520 [Executable statement]:         r'$\sqrt{s}=240$ GeV, $10.8\,\mathrm{ab}^{-1}$',
        r'$\sqrt{s}=240$ GeV, $10.8\,\mathrm{ab}^{-1}$',
# L521 [Executable statement]:         transform=ax_top.transAxes,
        transform=ax_top.transAxes,
# L522 [Executable statement]:         fontsize=9,
        fontsize=9,
# L523 [Executable statement]:         va='top',
        va='top',
# L524 [Executable statement]:     )
    )
# L525 [Blank separator]: 

# L526 [Executable statement]:     purity = np.divide(sig_rank, sig_rank + total_rank, out=np.zeros_like(sig_rank), where=(sig_rank + total_rank) > 0)
    purity = np.divide(sig_rank, sig_rank + total_rank, out=np.zeros_like(sig_rank), where=(sig_rank + total_rank) > 0)
# L527 [Executable statement]:     ax_bottom.plot(rank_bins, purity, color="#2C7FB8", marker="o", markersize=3.8, linewidth=1.8)
    ax_bottom.plot(rank_bins, purity, color="#2C7FB8", marker="o", markersize=3.8, linewidth=1.8)
# L528 [Executable statement]:     ax_bottom.set_ylabel(r"$S/(S+B)$")
    ax_bottom.set_ylabel(r"$S/(S+B)$")
# L529 [Executable statement]:     ax_bottom.set_xlabel("BDT rank bin (1 = highest score)")
    ax_bottom.set_xlabel("BDT rank bin (1 = highest score)")
# L530 [Executable statement]:     ax_bottom.set_ylim(0.0, min(1.0, max(0.15, purity.max() * 1.25 if len(purity) else 0.15)))
    ax_bottom.set_ylim(0.0, min(1.0, max(0.15, purity.max() * 1.25 if len(purity) else 0.15)))
# L531 [Executable statement]:     ax_bottom.set_xlim(0.5, len(rank_bins) + 0.5)
    ax_bottom.set_xlim(0.5, len(rank_bins) + 0.5)
# L532 [Executable statement]:     ax_bottom.set_xticks(rank_bins[::2] if len(rank_bins) > 10 else rank_bins)
    ax_bottom.set_xticks(rank_bins[::2] if len(rank_bins) > 10 else rank_bins)
# L533 [Executable statement]:     ax_bottom.grid(axis="y", alpha=0.22)
    ax_bottom.grid(axis="y", alpha=0.22)
# L534 [Executable statement]:     ax_bottom.text(
    ax_bottom.text(
# L535 [Executable statement]:         0.02,
        0.02,
# L536 [Executable statement]:         0.92,
        0.92,
# L537 [Executable statement]:         "Signal purity by ranked bin",
        "Signal purity by ranked bin",
# L538 [Executable statement]:         transform=ax_bottom.transAxes,
        transform=ax_bottom.transAxes,
# L539 [Executable statement]:         fontsize=9,
        fontsize=9,
# L540 [Executable statement]:         va="top",
        va="top",
# L541 [Executable statement]:     )
    )
# L542 [Blank separator]: 

# L543 [Executable statement]:     fig.tight_layout()
    fig.tight_layout()
# L544 [Executable statement]:     fig.savefig(plots_dir / "bdt_score_rank.pdf", dpi=150)
    fig.savefig(plots_dir / "bdt_score_rank.pdf", dpi=150)
# L545 [Executable statement]:     fig.savefig(plots_dir / "bdt_score_rank.png", dpi=150)
    fig.savefig(plots_dir / "bdt_score_rank.png", dpi=150)
# L546 [Executable statement]:     plt.close(fig)
    plt.close(fig)
# L547 [Blank separator]: 

# L548 [Runtime log output]:     print(f"  Fit plots saved to {plots_dir}/")
    print(f"  Fit plots saved to {plots_dir}/")
# L549 [Blank separator]: 

# L550 [Blank separator]: 

# L551 [Function definition]: def main():
def main():
# L552 [Executable statement]:     parser = argparse.ArgumentParser(description="Profile likelihood fit for H->WW* measurement")
    parser = argparse.ArgumentParser(description="Profile likelihood fit for H->WW* measurement")
# L553 [Executable statement]:     parser.add_argument("--scores", type=str, default=None,
    parser.add_argument("--scores", type=str, default=None,
# L554 [Executable statement]:                        help="Path to test_scores.csv from BDT training")
                       help="Path to test_scores.csv from BDT training")
# L555 [Executable statement]:     parser.add_argument("--model-dir", type=str, default=None,
    parser.add_argument("--model-dir", type=str, default=None,
# L556 [Executable statement]:                        help="Model directory (default: ml/models/xgboost_bdt)")
                       help="Model directory (default: ml/models/xgboost_bdt)")
# L557 [Executable statement]:     parser.add_argument("--nbins", type=int, default=20,
    parser.add_argument("--nbins", type=int, default=20,
# L558 [Executable statement]:                        help="Number of BDT score bins for template fit")
                       help="Number of BDT score bins for template fit")
# L559 [Executable statement]:     parser.add_argument("--norm-unc", type=float, default=0.01,
    parser.add_argument("--norm-unc", type=float, default=0.01,
# L560 [Executable statement]:                        help="Background normalization uncertainty (default: 1%%)")
                       help="Background normalization uncertainty (default: 1%%)")
# L561 [Executable statement]:     parser.add_argument("--bdt-cut", type=float, default=None,
    parser.add_argument("--bdt-cut", type=float, default=None,
# L562 [Executable statement]:                        help="Fixed BDT score cut (if None, scans for optimal)")
                       help="Fixed BDT score cut (if None, scans for optimal)")
# L563 [Executable statement]:     parser.add_argument("--no-scan", action="store_true",
    parser.add_argument("--no-scan", action="store_true",
# L564 [Executable statement]:                        help="Skip BDT cut scan, use --bdt-cut or 0.0")
                       help="Skip BDT cut scan, use --bdt-cut or 0.0")
# L565 [Executable statement]:     parser.add_argument("--no-plots", action="store_true",
    parser.add_argument("--no-plots", action="store_true",
# L566 [Executable statement]:                        help="Skip diagnostic plots")
                       help="Skip diagnostic plots")
# L567 [Executable statement]:     parser.add_argument("--no-staterror", action="store_true",
    parser.add_argument("--no-staterror", action="store_true",
# L568 [Executable statement]:                        help="Disable Barlow-Beeston MC stat uncertainty (show physics-only precision)")
                       help="Disable Barlow-Beeston MC stat uncertainty (show physics-only precision)")
# L569 [Executable statement]:     args = parser.parse_args()
    args = parser.parse_args()
# L570 [Blank separator]: 

# L571 [Original comment]:     # Locate scores file
    # Locate scores file
# L572 [Conditional block]:     if args.scores:
    if args.scores:
# L573 [Executable statement]:         scores_path = Path(args.scores)
        scores_path = Path(args.scores)
# L574 [Else-if conditional]:     elif args.model_dir:
    elif args.model_dir:
# L575 [Executable statement]:         model_dir = Path(args.model_dir)
        model_dir = Path(args.model_dir)
# L576 [Original comment]:         # Prefer kfold_scores.csv (all events, no scaling needed)
        # Prefer kfold_scores.csv (all events, no scaling needed)
# L577 [Executable statement]:         kfold_path = model_dir / "kfold_scores.csv"
        kfold_path = model_dir / "kfold_scores.csv"
# L578 [Executable statement]:         test_path = model_dir / "test_scores.csv"
        test_path = model_dir / "test_scores.csv"
# L579 [Conditional block]:         if kfold_path.exists():
        if kfold_path.exists():
# L580 [Executable statement]:             scores_path = kfold_path
            scores_path = kfold_path
# L581 [Else branch]:         else:
        else:
# L582 [Executable statement]:             scores_path = test_path
            scores_path = test_path
# L583 [Else branch]:     else:
    else:
# L584 [Executable statement]:         model_dir = ANALYSIS_DIR / DEFAULT_MODEL_DIR
        model_dir = ANALYSIS_DIR / DEFAULT_MODEL_DIR
# L585 [Executable statement]:         scores_path = model_dir / "test_scores.csv"
        scores_path = model_dir / "test_scores.csv"
# L586 [Conditional block]:         if not scores_path.exists():
        if not scores_path.exists():
# L587 [Executable statement]:             scores_path = THIS_DIR / "models" / "xgboost_bdt_v6" / "test_scores.csv"
            scores_path = THIS_DIR / "models" / "xgboost_bdt_v6" / "test_scores.csv"
# L588 [Blank separator]: 

# L589 [Runtime log output]:     print(f"Loading scores from {scores_path}")
    print(f"Loading scores from {scores_path}")
# L590 [Executable statement]:     df = load_scores(scores_path)
    df = load_scores(scores_path)
# L591 [Runtime log output]:     print(f"  {len(df)} events loaded ({(df['y_true']==1).sum()} signal, {(df['y_true']==0).sum()} background)")
    print(f"  {len(df)} events loaded ({(df['y_true']==1).sum()} signal, {(df['y_true']==0).sum()} background)")
# L592 [Blank separator]: 

# L593 [Executable statement]:     output_dir = scores_path.parent
    output_dir = scores_path.parent
# L594 [Blank separator]: 

# L595 [Original comment]:     # Weight scaling depends on input file type:
    # Weight scaling depends on input file type:
# L596 [Original comment]:     # - kfold_scores.csv: ALL events scored, no scaling needed
    # - kfold_scores.csv: ALL events scored, no scaling needed
# L597 [Original comment]:     # - test_scores.csv: only test fraction, scale by 1/test_frac
    # - test_scores.csv: only test fraction, scale by 1/test_frac
# L598 [Conditional block]:     if "kfold" in scores_path.name:
    if "kfold" in scores_path.name:
# L599 [Runtime log output]:         print("  Using k-fold scores (all events, no scaling)")
        print("  Using k-fold scores (all events, no scaling)")
# L600 [Else branch]:     else:
    else:
# L601 [Executable statement]:         test_frac = 0.30  # must match --test-size in train_xgboost_bdt.py
        test_frac = 0.30  # must match --test-size in train_xgboost_bdt.py
# L602 [Executable statement]:         df["phys_weight"] = df["phys_weight"] / test_frac
        df["phys_weight"] = df["phys_weight"] / test_frac
# L603 [Runtime log output]:         print(f"  Scaling weights by 1/{test_frac} for test-set-only scores")
        print(f"  Scaling weights by 1/{test_frac} for test-set-only scores")
# L604 [Blank separator]: 

# L605 [Executable statement]:     use_staterr = not args.no_staterror
    use_staterr = not args.no_staterror
# L606 [Blank separator]: 

# L607 [Original comment]:     # Single-bin counting scan for the cut-and-count reference.
    # Single-bin counting scan for the cut-and-count reference.
# L608 [Conditional block]:     if not args.no_scan:
    if not args.no_scan:
# L609 [Runtime log output]:         print("\nScanning BDT score cuts (1-bin counting reference):")
        print("\nScanning BDT score cuts (1-bin counting reference):")
# L610 [Executable statement]:         scan_results = scan_bdt_cut(
        scan_results = scan_bdt_cut(
# L611 [Executable statement]:             df,
            df,
# L612 [Executable statement]:             fit_nbins=1,
            fit_nbins=1,
# L613 [Executable statement]:             norm_uncertainty=args.norm_unc,
            norm_uncertainty=args.norm_unc,
# L614 [Executable statement]:             use_staterror=use_staterr,
            use_staterror=use_staterr,
# L615 [Executable statement]:         )
        )
# L616 [Blank separator]: 

# L617 [Conditional block]:         if not scan_results:
        if not scan_results:
# L618 [Runtime log output]:             print("ERROR: All BDT cuts failed. Check input data.")
            print("ERROR: All BDT cuts failed. Check input data.")
# L619 [Return from function]:             return
            return
# L620 [Blank separator]: 

# L621 [Executable statement]:         best_counting = min(scan_results, key=lambda r: r["rel_uncertainty"])
        best_counting = min(scan_results, key=lambda r: r["rel_uncertainty"])
# L622 [Runtime log output]:         print(f"\n  Best 1-bin counting cut: {best_counting['bdt_cut']:.2f}")
        print(f"\n  Best 1-bin counting cut: {best_counting['bdt_cut']:.2f}")
# L623 [Runtime log output]:         print(f"  S={best_counting['n_sig']:.0f}, B={best_counting['n_bkg']:.0f}")
        print(f"  S={best_counting['n_sig']:.0f}, B={best_counting['n_bkg']:.0f}")
# L624 [Runtime log output]:         print(f"  Expected δμ/μ = {best_counting['rel_uncertainty']*100:.2f}%")
        print(f"  Expected δμ/μ = {best_counting['rel_uncertainty']*100:.2f}%")
# L625 [Else branch]:     else:
    else:
# L626 [Executable statement]:         scan_results = []
        scan_results = []
# L627 [Executable statement]:         best_counting = None
        best_counting = None
# L628 [Blank separator]: 

# L629 [Original comment]:     # The headline result is the full 20-bin shape fit. By default we keep the
    # The headline result is the full 20-bin shape fit. By default we keep the
# L630 [Original comment]:     # full BDT score range unless the caller explicitly requests a threshold.
    # full BDT score range unless the caller explicitly requests a threshold.
# L631 [Executable statement]:     bdt_cut = args.bdt_cut if args.bdt_cut is not None else 0.0
    bdt_cut = args.bdt_cut if args.bdt_cut is not None else 0.0
# L632 [Blank separator]: 

# L633 [Original comment]:     # Final fit at chosen working point
    # Final fit at chosen working point
# L634 [Runtime log output]:     print(f"\nFinal {args.nbins}-bin shape fit at BDT cut = {bdt_cut:.2f}:")
    print(f"\nFinal {args.nbins}-bin shape fit at BDT cut = {bdt_cut:.2f}:")
# L635 [Executable statement]:     sig_hist, sig_err, bkg_hists, bkg_errs, bins = build_templates(df, nbins=args.nbins, bdt_cut=bdt_cut)
    sig_hist, sig_err, bkg_hists, bkg_errs, bins = build_templates(df, nbins=args.nbins, bdt_cut=bdt_cut)
# L636 [Blank separator]: 

# L637 [Executable statement]:     n_sig = sig_hist.sum()
    n_sig = sig_hist.sum()
# L638 [Executable statement]:     n_bkg = sum(h.sum() for h in bkg_hists.values())
    n_bkg = sum(h.sum() for h in bkg_hists.values())
# L639 [Runtime log output]:     print(f"  Signal events: {n_sig:.0f}")
    print(f"  Signal events: {n_sig:.0f}")
# L640 [Runtime log output]:     print(f"  Background events: {n_bkg:.0f}")
    print(f"  Background events: {n_bkg:.0f}")
# L641 [Loop over iterable]:     for name, h in bkg_hists.items():
    for name, h in bkg_hists.items():
# L642 [Runtime log output]:         print(f"    {name}: {h.sum():.0f}")
        print(f"    {name}: {h.sum():.0f}")
# L643 [Blank separator]: 

# L644 [Executable statement]:     spec = build_pyhf_model(sig_hist, sig_err, bkg_hists, bkg_errs, args.norm_unc, use_staterror=use_staterr)
    spec = build_pyhf_model(sig_hist, sig_err, bkg_hists, bkg_errs, args.norm_unc, use_staterror=use_staterr)
# L645 [Executable statement]:     mu_hat, mu_err, fit_results = fit_asimov(spec, sig_hist, bkg_hists)
    mu_hat, mu_err, fit_results = fit_asimov(spec, sig_hist, bkg_hists)
# L646 [Blank separator]: 

# L647 [Executable statement]:     rel_unc = mu_err / mu_hat if mu_hat > 0 else float("inf")
    rel_unc = mu_err / mu_hat if mu_hat > 0 else float("inf")
# L648 [Executable statement]:     physics_only_mu_hat = None
    physics_only_mu_hat = None
# L649 [Executable statement]:     physics_only_mu_err = None
    physics_only_mu_err = None
# L650 [Executable statement]:     physics_only_rel_unc = None
    physics_only_rel_unc = None
# L651 [Conditional block]:     if use_staterr:
    if use_staterr:
# L652 [Executable statement]:         physics_spec = build_pyhf_model(
        physics_spec = build_pyhf_model(
# L653 [Executable statement]:             sig_hist, sig_err, bkg_hists, bkg_errs, args.norm_unc, use_staterror=False,
            sig_hist, sig_err, bkg_hists, bkg_errs, args.norm_unc, use_staterror=False,
# L654 [Executable statement]:         )
        )
# L655 [Executable statement]:         physics_only_mu_hat, physics_only_mu_err, _ = fit_asimov(physics_spec, sig_hist, bkg_hists)
        physics_only_mu_hat, physics_only_mu_err, _ = fit_asimov(physics_spec, sig_hist, bkg_hists)
# L656 [Executable statement]:         physics_only_rel_unc = (
        physics_only_rel_unc = (
# L657 [Executable statement]:             physics_only_mu_err / physics_only_mu_hat if physics_only_mu_hat > 0 else float("inf")
            physics_only_mu_err / physics_only_mu_hat if physics_only_mu_hat > 0 else float("inf")
# L658 [Executable statement]:         )
        )
# L659 [Blank separator]: 

# L660 [Runtime log output]:     print(f"\n  === RESULT ===")
    print(f"\n  === RESULT ===")
# L661 [Runtime log output]:     print(f"  mu_hat = {mu_hat:.4f} +/- {mu_err:.4f}")
    print(f"  mu_hat = {mu_hat:.4f} +/- {mu_err:.4f}")
# L662 [Runtime log output]:     print(f"  Relative uncertainty: {rel_unc*100:.2f}%")
    print(f"  Relative uncertainty: {rel_unc*100:.2f}%")
# L663 [Runtime log output]:     print(f"  => Expected precision on sigma_ZH x BR(H->WW*): {rel_unc*100:.2f}%")
    print(f"  => Expected precision on sigma_ZH x BR(H->WW*): {rel_unc*100:.2f}%")
# L664 [Conditional block]:     if physics_only_rel_unc is not None:
    if physics_only_rel_unc is not None:
# L665 [Runtime log output]:         print(f"  Physics-only floor (no MC stat nuisance terms): {physics_only_rel_unc*100:.2f}%")
        print(f"  Physics-only floor (no MC stat nuisance terms): {physics_only_rel_unc*100:.2f}%")
# L666 [Blank separator]: 

# L667 [Original comment]:     # Save results
    # Save results
# L668 [Executable statement]:     result = {
    result = {
# L669 [Executable statement]:         "bdt_cut": bdt_cut,
        "bdt_cut": bdt_cut,
# L670 [Executable statement]:         "nbins": args.nbins,
        "nbins": args.nbins,
# L671 [Executable statement]:         "scan_mode": "counting_1bin",
        "scan_mode": "counting_1bin",
# L672 [Executable statement]:         "norm_uncertainty": args.norm_unc,
        "norm_uncertainty": args.norm_unc,
# L673 [Executable statement]:         "n_signal": float(n_sig),
        "n_signal": float(n_sig),
# L674 [Executable statement]:         "n_background": float(n_bkg),
        "n_background": float(n_bkg),
# L675 [Executable statement]:         "mu_hat": mu_hat,
        "mu_hat": mu_hat,
# L676 [Executable statement]:         "mu_err": mu_err,
        "mu_err": mu_err,
# L677 [Executable statement]:         "relative_uncertainty_pct": rel_unc * 100,
        "relative_uncertainty_pct": rel_unc * 100,
# L678 [Executable statement]:         "fit_parameters": fit_results,
        "fit_parameters": fit_results,
# L679 [Executable statement]:         "bkg_yields": {k: float(v.sum()) for k, v in bkg_hists.items()},
        "bkg_yields": {k: float(v.sum()) for k, v in bkg_hists.items()},
# L680 [Executable statement]:     }
    }
# L681 [Blank separator]: 

# L682 [Conditional block]:     if physics_only_rel_unc is not None:
    if physics_only_rel_unc is not None:
# L683 [Executable statement]:         result["physics_only_mu_hat"] = physics_only_mu_hat
        result["physics_only_mu_hat"] = physics_only_mu_hat
# L684 [Executable statement]:         result["physics_only_mu_err"] = physics_only_mu_err
        result["physics_only_mu_err"] = physics_only_mu_err
# L685 [Executable statement]:         result["physics_only_rel_uncertainty_pct"] = physics_only_rel_unc * 100
        result["physics_only_rel_uncertainty_pct"] = physics_only_rel_unc * 100
# L686 [Executable statement]:         result["physics_only_note"] = (
        result["physics_only_note"] = (
# L687 [Executable statement]:             "Shape-fit precision with the same normalization systematics but without "
            "Shape-fit precision with the same normalization systematics but without "
# L688 [Executable statement]:             "Barlow-Beeston MC-stat nuisance terms."
            "Barlow-Beeston MC-stat nuisance terms."
# L689 [Executable statement]:         )
        )
# L690 [Blank separator]: 

# L691 [Conditional block]:     if scan_results:
    if scan_results:
# L692 [Executable statement]:         result["counting_scan_results"] = scan_results
        result["counting_scan_results"] = scan_results
# L693 [Blank separator]: 

# L694 [Executable statement]:     result_path = output_dir / "fit_results.json"
    result_path = output_dir / "fit_results.json"
# L695 [Context manager block]:     with open(result_path, "w") as f:
    with open(result_path, "w") as f:
# L696 [Executable statement]:         json.dump(result, f, indent=2)
        json.dump(result, f, indent=2)
# L697 [Runtime log output]:     print(f"\n  Results saved to {result_path}")
    print(f"\n  Results saved to {result_path}")
# L698 [Blank separator]: 

# L699 [Original comment]:     # Plots
    # Plots
# L700 [Conditional block]:     if not args.no_plots:
    if not args.no_plots:
# L701 [Executable statement]:         make_fit_plots(
        make_fit_plots(
# L702 [Executable statement]:             output_dir,
            output_dir,
# L703 [Executable statement]:             scan_results,
            scan_results,
# L704 [Executable statement]:             best_counting,
            best_counting,
# L705 [Executable statement]:             sig_hist,
            sig_hist,
# L706 [Executable statement]:             bkg_hists,
            bkg_hists,
# L707 [Executable statement]:             bins,
            bins,
# L708 [Executable statement]:             shape_rel_unc_pct=rel_unc * 100,
            shape_rel_unc_pct=rel_unc * 100,
# L709 [Executable statement]:         )
        )
# L710 [Blank separator]: 

# L711 [Blank separator]: 

# L712 [Conditional block]: if __name__ == "__main__":
if __name__ == "__main__":
# L713 [Executable statement]:     main()
    main()
