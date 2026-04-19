# Annotated rewrite generated for: run_lvqq.py
# L1 [Original comment]: #!/usr/bin/env python3
#!/usr/bin/env python3
# L2 [Executable statement]: """Unified driver for the lvqq analysis workflow."""
"""Unified driver for the lvqq analysis workflow."""
# L3 [Blank separator]: 

# L4 [Import statement]: from __future__ import annotations
from __future__ import annotations
# L5 [Blank separator]: 

# L6 [Import statement]: import argparse
import argparse
# L7 [Import statement]: import os
import os
# L8 [Import statement]: import shlex
import shlex
# L9 [Import statement]: import subprocess
import subprocess
# L10 [Import statement]: from collections.abc import Callable
from collections.abc import Callable
# L11 [Import statement]: from pathlib import Path
from pathlib import Path
# L12 [Blank separator]: 

# L13 [Blank separator]: 

# L14 [Executable statement]: ANALYSIS_DIR = Path(__file__).resolve().parent
ANALYSIS_DIR = Path(__file__).resolve().parent
# L15 [Executable statement]: SETUP_SH = Path("/home/submit/jinboz1/tutorials/FCCAnalyses/setup.sh")
SETUP_SH = Path("/home/submit/jinboz1/tutorials/FCCAnalyses/setup.sh")
# L16 [Executable statement]: MODEL_DIR = "ml/models/xgboost_bdt_v6"
MODEL_DIR = "ml/models/xgboost_bdt_v6"
# L17 [Blank separator]: 

# L18 [Blank separator]: 

# L19 [Function definition]: def parse_fraction(value: str) -> float:
def parse_fraction(value: str) -> float:
# L20 [Exception handling start]:     try:
    try:
# L21 [Executable statement]:         fraction = float(value)
        fraction = float(value)
# L22 [Exception handler]:     except ValueError as exc:
    except ValueError as exc:
# L23 [Executable statement]:         raise argparse.ArgumentTypeError("background fraction must be a float in (0, 1]") from exc
        raise argparse.ArgumentTypeError("background fraction must be a float in (0, 1]") from exc
# L24 [Conditional block]:     if not (0.0 < fraction <= 1.0):
    if not (0.0 < fraction <= 1.0):
# L25 [Executable statement]:         raise argparse.ArgumentTypeError("background fraction must be in (0, 1]")
        raise argparse.ArgumentTypeError("background fraction must be in (0, 1]")
# L26 [Function return]:     return fraction
    return fraction
# L27 [Blank separator]: 

# L28 [Blank separator]: 

# L29 [Function definition]: def default_background_fractions() -> dict[str, float]:
def default_background_fractions() -> dict[str, float]:
# L30 [Function return]:     return {"ww": 1.0, "zz": 1.0, "qq": 1.0, "tautau": 1.0}
    return {"ww": 1.0, "zz": 1.0, "qq": 1.0, "tautau": 1.0}
# L31 [Blank separator]: 

# L32 [Blank separator]: 

# L33 [Function definition]: def run_bash(command: str, *, needs_setup: bool = False, extra_env: dict[str, str] | None = None) -> None:
def run_bash(command: str, *, needs_setup: bool = False, extra_env: dict[str, str] | None = None) -> None:
# L34 [Executable statement]:     env = os.environ.copy()
    env = os.environ.copy()
# L35 [Conditional block]:     if extra_env:
    if extra_env:
# L36 [Executable statement]:         env.update(extra_env)
        env.update(extra_env)
# L37 [Blank separator]: 

# L38 [Executable statement]:     shell_cmd = f'cd "{ANALYSIS_DIR}" && {command}'
    shell_cmd = f'cd "{ANALYSIS_DIR}" && {command}'
# L39 [Conditional block]:     if needs_setup:
    if needs_setup:
# L40 [Executable statement]:         shell_cmd = f'source "{SETUP_SH}" >/dev/null 2>&1 && {shell_cmd}'
        shell_cmd = f'source "{SETUP_SH}" >/dev/null 2>&1 && {shell_cmd}'
# L41 [Blank separator]: 

# L42 [Executable statement]:     subprocess.run(["bash", "-lc", shell_cmd], check=True, env=env)
    subprocess.run(["bash", "-lc", shell_cmd], check=True, env=env)
# L43 [Blank separator]: 

# L44 [Blank separator]: 

# L45 [Function definition]: def step_histmaker() -> None:
def step_histmaker() -> None:
# L46 [Executable statement]:     run_bash("fccanalysis run h_hww_lvqq.py", needs_setup=True, extra_env={"LVQQ_MODE": "histmaker"})
    run_bash("fccanalysis run h_hww_lvqq.py", needs_setup=True, extra_env={"LVQQ_MODE": "histmaker"})
# L47 [Blank separator]: 

# L48 [Blank separator]: 

# L49 [Function definition]: def step_treemaker() -> None:
def step_treemaker() -> None:
# L50 [Executable statement]:     run_bash("fccanalysis run h_hww_lvqq.py", needs_setup=True, extra_env={"LVQQ_MODE": "treemaker"})
    run_bash("fccanalysis run h_hww_lvqq.py", needs_setup=True, extra_env={"LVQQ_MODE": "treemaker"})
# L51 [Blank separator]: 

# L52 [Blank separator]: 

# L53 [Function definition]: def step_train() -> None:
def step_train() -> None:
# L54 [Executable statement]:     run_bash("python3 ml/train_xgboost_bdt.py")
    run_bash("python3 ml/train_xgboost_bdt.py")
# L55 [Blank separator]: 

# L56 [Blank separator]: 

# L57 [Function definition]: def step_apply() -> None:
def step_apply() -> None:
# L58 [Executable statement]:     run_bash("python3 ml/apply_xgboost_bdt.py")
    run_bash("python3 ml/apply_xgboost_bdt.py")
# L59 [Blank separator]: 

# L60 [Blank separator]: 

# L61 [Function definition]: def step_fit() -> None:
def step_fit() -> None:
# L62 [Executable statement]:     run_bash(f"python3 ml/fit_profile_likelihood.py --model-dir {MODEL_DIR}")
    run_bash(f"python3 ml/fit_profile_likelihood.py --model-dir {MODEL_DIR}")
# L63 [Blank separator]: 

# L64 [Blank separator]: 

# L65 [Function definition]: def step_roc_plot() -> None:
def step_roc_plot() -> None:
# L66 [Executable statement]:     run_bash("python3 ml/regenerate_roc.py")
    run_bash("python3 ml/regenerate_roc.py")
# L67 [Blank separator]: 

# L68 [Blank separator]: 

# L69 [Function definition]: def step_supporting_figures() -> None:
def step_supporting_figures() -> None:
# L70 [Executable statement]:     run_bash("python3 paper/generate_supporting_figures.py")
    run_bash("python3 paper/generate_supporting_figures.py")
# L71 [Blank separator]: 

# L72 [Blank separator]: 

# L73 [Function definition]: def step_sync_paper_figures() -> None:
def step_sync_paper_figures() -> None:
# L74 [Executable statement]:     run_bash("python3 paper/sync_paper_figures.py")
    run_bash("python3 paper/sync_paper_figures.py")
# L75 [Blank separator]: 

# L76 [Blank separator]: 

# L77 [Function definition]: def step_plots() -> None:
def step_plots() -> None:
# L78 [Executable statement]:     run_bash("python3 plots_lvqq.py", needs_setup=True)
    run_bash("python3 plots_lvqq.py", needs_setup=True)
# L79 [Executable statement]:     step_roc_plot()
    step_roc_plot()
# L80 [Executable statement]:     step_supporting_figures()
    step_supporting_figures()
# L81 [Executable statement]:     step_sync_paper_figures()
    step_sync_paper_figures()
# L82 [Blank separator]: 

# L83 [Blank separator]: 

# L84 [Function definition]: def step_paper() -> None:
def step_paper() -> None:
# L85 [Executable statement]:     step_roc_plot()
    step_roc_plot()
# L86 [Executable statement]:     step_supporting_figures()
    step_supporting_figures()
# L87 [Executable statement]:     step_sync_paper_figures()
    step_sync_paper_figures()
# L88 [Executable statement]:     run_bash('cd paper && tectonic main.tex')
    run_bash('cd paper && tectonic main.tex')
# L89 [Blank separator]: 

# L90 [Blank separator]: 

# L91 [Function definition]: def submit_to_slurm(args: argparse.Namespace) -> None:
def submit_to_slurm(args: argparse.Namespace) -> None:
# L92 [Executable statement]:     log_dir = ANALYSIS_DIR / "logs" / "slurm"
    log_dir = ANALYSIS_DIR / "logs" / "slurm"
# L93 [Executable statement]:     log_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
# L94 [Blank separator]: 

# L95 [Executable statement]:     rerun_cmd = [
    rerun_cmd = [
# L96 [Executable statement]:         "python3",
        "python3",
# L97 [Executable statement]:         str(ANALYSIS_DIR / "run_lvqq.py"),
        str(ANALYSIS_DIR / "run_lvqq.py"),
# L98 [Executable statement]:         args.target,
        args.target,
# L99 [Executable statement]:     ]
    ]
# L100 [Conditional block]:     if args.background_fraction is not None:
    if args.background_fraction is not None:
# L101 [Executable statement]:         rerun_cmd.extend(["--background-fraction", str(args.background_fraction)])
        rerun_cmd.extend(["--background-fraction", str(args.background_fraction)])
# L102 [Conditional block]:     if args.ww_fraction is not None:
    if args.ww_fraction is not None:
# L103 [Executable statement]:         rerun_cmd.extend(["--ww-fraction", str(args.ww_fraction)])
        rerun_cmd.extend(["--ww-fraction", str(args.ww_fraction)])
# L104 [Conditional block]:     if args.zz_fraction is not None:
    if args.zz_fraction is not None:
# L105 [Executable statement]:         rerun_cmd.extend(["--zz-fraction", str(args.zz_fraction)])
        rerun_cmd.extend(["--zz-fraction", str(args.zz_fraction)])
# L106 [Conditional block]:     if args.qq_fraction is not None:
    if args.qq_fraction is not None:
# L107 [Executable statement]:         rerun_cmd.extend(["--qq-fraction", str(args.qq_fraction)])
        rerun_cmd.extend(["--qq-fraction", str(args.qq_fraction)])
# L108 [Conditional block]:     if args.tautau_fraction is not None:
    if args.tautau_fraction is not None:
# L109 [Executable statement]:         rerun_cmd.extend(["--tautau-fraction", str(args.tautau_fraction)])
        rerun_cmd.extend(["--tautau-fraction", str(args.tautau_fraction)])
# L110 [Blank separator]: 

# L111 [Executable statement]:     submit_cmd = [
    submit_cmd = [
# L112 [Executable statement]:         "sbatch",
        "sbatch",
# L113 [Executable statement]:         "--parsable",
        "--parsable",
# L114 [Executable statement]:         f"--job-name=lvqq_{args.target}",
        f"--job-name=lvqq_{args.target}",
# L115 [Executable statement]:         f"--partition={args.slurm_partition}",
        f"--partition={args.slurm_partition}",
# L116 [Executable statement]:         f"--cpus-per-task={args.slurm_cpus}",
        f"--cpus-per-task={args.slurm_cpus}",
# L117 [Executable statement]:         f"--mem={args.slurm_mem}",
        f"--mem={args.slurm_mem}",
# L118 [Executable statement]:         f"--time={args.slurm_time}",
        f"--time={args.slurm_time}",
# L119 [Executable statement]:         f"--chdir={ANALYSIS_DIR}",
        f"--chdir={ANALYSIS_DIR}",
# L120 [Executable statement]:         f"--output={log_dir / '%x-%j.out'}",
        f"--output={log_dir / '%x-%j.out'}",
# L121 [Executable statement]:         f"--error={log_dir / '%x-%j.err'}",
        f"--error={log_dir / '%x-%j.err'}",
# L122 [Executable statement]:         "--wrap",
        "--wrap",
# L123 [Executable statement]:         shlex.join(rerun_cmd),
        shlex.join(rerun_cmd),
# L124 [Executable statement]:     ]
    ]
# L125 [Blank separator]: 

# L126 [Executable statement]:     result = subprocess.run(submit_cmd, check=True, text=True, capture_output=True)
    result = subprocess.run(submit_cmd, check=True, text=True, capture_output=True)
# L127 [Runtime log output]:     print(f"Submitted Slurm job {result.stdout.strip()}")
    print(f"Submitted Slurm job {result.stdout.strip()}")
# L128 [Runtime log output]:     print(f"Logs: {log_dir}")
    print(f"Logs: {log_dir}")
# L129 [Blank separator]: 

# L130 [Blank separator]: 

# L131 [Function definition]: def run_sequence(name: str, steps: list[tuple[str, Callable[[], None]]]) -> None:
def run_sequence(name: str, steps: list[tuple[str, Callable[[], None]]]) -> None:
# L132 [Loop over iterable]:     for label, fn in steps:
    for label, fn in steps:
# L133 [Runtime log output]:         print(f"\n==> {name}: {label}")
        print(f"\n==> {name}: {label}")
# L134 [Executable statement]:         fn()
        fn()
# L135 [Blank separator]: 

# L136 [Blank separator]: 

# L137 [Function definition]: def parse_args() -> argparse.Namespace:
def parse_args() -> argparse.Namespace:
# L138 [Executable statement]:     parser = argparse.ArgumentParser(description=__doc__)
    parser = argparse.ArgumentParser(description=__doc__)
# L139 [Executable statement]:     parser.add_argument(
    parser.add_argument(
# L140 [Executable statement]:         "target",
        "target",
# L141 [Executable statement]:         nargs="?",
        nargs="?",
# L142 [Executable statement]:         default="all",
        default="all",
# L143 [Executable statement]:         choices=["histmaker", "treemaker", "train", "apply", "fit", "plots", "paper", "stage1", "ml", "all"],
        choices=["histmaker", "treemaker", "train", "apply", "fit", "plots", "paper", "stage1", "ml", "all"],
# L144 [Executable statement]:         help="Workflow target to run",
        help="Workflow target to run",
# L145 [Executable statement]:     )
    )
# L146 [Executable statement]:     parser.add_argument(
    parser.add_argument(
# L147 [Executable statement]:         "--background-fraction",
        "--background-fraction",
# L148 [Executable statement]:         type=parse_fraction,
        type=parse_fraction,
# L149 [Executable statement]:         default=None,
        default=None,
# L150 [Executable statement]:         help="Global override for all reducible backgrounds (WW/ZZ/qq/tautau).",
        help="Global override for all reducible backgrounds (WW/ZZ/qq/tautau).",
# L151 [Executable statement]:     )
    )
# L152 [Executable statement]:     parser.add_argument("--ww-fraction", type=parse_fraction, default=None)
    parser.add_argument("--ww-fraction", type=parse_fraction, default=None)
# L153 [Executable statement]:     parser.add_argument("--zz-fraction", type=parse_fraction, default=None)
    parser.add_argument("--zz-fraction", type=parse_fraction, default=None)
# L154 [Executable statement]:     parser.add_argument("--qq-fraction", type=parse_fraction, default=None)
    parser.add_argument("--qq-fraction", type=parse_fraction, default=None)
# L155 [Executable statement]:     parser.add_argument("--tautau-fraction", type=parse_fraction, default=None)
    parser.add_argument("--tautau-fraction", type=parse_fraction, default=None)
# L156 [Executable statement]:     parser.add_argument(
    parser.add_argument(
# L157 [Executable statement]:         "--slurm",
        "--slurm",
# L158 [Executable statement]:         action="store_true",
        action="store_true",
# L159 [Executable statement]:         help="Submit the requested workflow target to Slurm instead of running locally.",
        help="Submit the requested workflow target to Slurm instead of running locally.",
# L160 [Executable statement]:     )
    )
# L161 [Executable statement]:     parser.add_argument("--slurm-partition", default="submit")
    parser.add_argument("--slurm-partition", default="submit")
# L162 [Executable statement]:     parser.add_argument("--slurm-cpus", type=int, default=16)
    parser.add_argument("--slurm-cpus", type=int, default=16)
# L163 [Executable statement]:     parser.add_argument("--slurm-mem", default="48G")
    parser.add_argument("--slurm-mem", default="48G")
# L164 [Executable statement]:     parser.add_argument("--slurm-time", default="2-00:00:00")
    parser.add_argument("--slurm-time", default="2-00:00:00")
# L165 [Function return]:     return parser.parse_args()
    return parser.parse_args()
# L166 [Blank separator]: 

# L167 [Blank separator]: 

# L168 [Function definition]: def main() -> None:
def main() -> None:
# L169 [Conditional block]:     if not SETUP_SH.exists():
    if not SETUP_SH.exists():
# L170 [Executable statement]:         raise SystemExit(f"Missing FCCAnalyses setup script: {SETUP_SH}")
        raise SystemExit(f"Missing FCCAnalyses setup script: {SETUP_SH}")
# L171 [Blank separator]: 

# L172 [Executable statement]:     args = parse_args()
    args = parse_args()
# L173 [Conditional block]:     if args.background_fraction is not None:
    if args.background_fraction is not None:
# L174 [Executable statement]:         os.environ["LVQQ_BACKGROUND_FRACTION"] = str(args.background_fraction)
        os.environ["LVQQ_BACKGROUND_FRACTION"] = str(args.background_fraction)
# L175 [Else branch]:     else:
    else:
# L176 [Executable statement]:         os.environ.pop("LVQQ_BACKGROUND_FRACTION", None)
        os.environ.pop("LVQQ_BACKGROUND_FRACTION", None)
# L177 [Conditional block]:     if args.ww_fraction is not None:
    if args.ww_fraction is not None:
# L178 [Executable statement]:         os.environ["LVQQ_WW_FRACTION"] = str(args.ww_fraction)
        os.environ["LVQQ_WW_FRACTION"] = str(args.ww_fraction)
# L179 [Else branch]:     else:
    else:
# L180 [Executable statement]:         os.environ.pop("LVQQ_WW_FRACTION", None)
        os.environ.pop("LVQQ_WW_FRACTION", None)
# L181 [Conditional block]:     if args.zz_fraction is not None:
    if args.zz_fraction is not None:
# L182 [Executable statement]:         os.environ["LVQQ_ZZ_FRACTION"] = str(args.zz_fraction)
        os.environ["LVQQ_ZZ_FRACTION"] = str(args.zz_fraction)
# L183 [Else branch]:     else:
    else:
# L184 [Executable statement]:         os.environ.pop("LVQQ_ZZ_FRACTION", None)
        os.environ.pop("LVQQ_ZZ_FRACTION", None)
# L185 [Conditional block]:     if args.qq_fraction is not None:
    if args.qq_fraction is not None:
# L186 [Executable statement]:         os.environ["LVQQ_QQ_FRACTION"] = str(args.qq_fraction)
        os.environ["LVQQ_QQ_FRACTION"] = str(args.qq_fraction)
# L187 [Else branch]:     else:
    else:
# L188 [Executable statement]:         os.environ.pop("LVQQ_QQ_FRACTION", None)
        os.environ.pop("LVQQ_QQ_FRACTION", None)
# L189 [Conditional block]:     if args.tautau_fraction is not None:
    if args.tautau_fraction is not None:
# L190 [Executable statement]:         os.environ["LVQQ_TAUTAU_FRACTION"] = str(args.tautau_fraction)
        os.environ["LVQQ_TAUTAU_FRACTION"] = str(args.tautau_fraction)
# L191 [Else branch]:     else:
    else:
# L192 [Executable statement]:         os.environ.pop("LVQQ_TAUTAU_FRACTION", None)
        os.environ.pop("LVQQ_TAUTAU_FRACTION", None)
# L193 [Blank separator]: 

# L194 [Executable statement]:     active_fractions = default_background_fractions()
    active_fractions = default_background_fractions()
# L195 [Conditional block]:     if args.background_fraction is not None:
    if args.background_fraction is not None:
# L196 [Executable statement]:         active_fractions = {key: args.background_fraction for key in active_fractions}
        active_fractions = {key: args.background_fraction for key in active_fractions}
# L197 [Loop over iterable]:     for key, value in {
    for key, value in {
# L198 [Executable statement]:         "ww": args.ww_fraction,
        "ww": args.ww_fraction,
# L199 [Executable statement]:         "zz": args.zz_fraction,
        "zz": args.zz_fraction,
# L200 [Executable statement]:         "qq": args.qq_fraction,
        "qq": args.qq_fraction,
# L201 [Executable statement]:         "tautau": args.tautau_fraction,
        "tautau": args.tautau_fraction,
# L202 [Executable statement]:     }.items():
    }.items():
# L203 [Conditional block]:         if value is not None:
        if value is not None:
# L204 [Executable statement]:             active_fractions[key] = value
            active_fractions[key] = value
# L205 [Blank separator]: 

# L206 [Runtime log output]:     print(
    print(
# L207 [Executable statement]:         "Background fractions:"
        "Background fractions:"
# L208 [Executable statement]:         f" WW={active_fractions['ww']:.6g},"
        f" WW={active_fractions['ww']:.6g},"
# L209 [Executable statement]:         f" ZZ={active_fractions['zz']:.6g},"
        f" ZZ={active_fractions['zz']:.6g},"
# L210 [Executable statement]:         f" qq={active_fractions['qq']:.6g},"
        f" qq={active_fractions['qq']:.6g},"
# L211 [Executable statement]:         f" tautau={active_fractions['tautau']:.6g}"
        f" tautau={active_fractions['tautau']:.6g}"
# L212 [Executable statement]:     )
    )
# L213 [Blank separator]: 

# L214 [Conditional block]:     if args.slurm:
    if args.slurm:
# L215 [Executable statement]:         submit_to_slurm(args)
        submit_to_slurm(args)
# L216 [Return from function]:         return
        return
# L217 [Blank separator]: 

# L218 [Executable statement]:     mapping: dict[str, list[tuple[str, Callable[[], None]]]] = {
    mapping: dict[str, list[tuple[str, Callable[[], None]]]] = {
# L219 [Executable statement]:         "histmaker": [("histmaker", step_histmaker)],
        "histmaker": [("histmaker", step_histmaker)],
# L220 [Executable statement]:         "treemaker": [("treemaker", step_treemaker)],
        "treemaker": [("treemaker", step_treemaker)],
# L221 [Executable statement]:         "train": [("train", step_train)],
        "train": [("train", step_train)],
# L222 [Executable statement]:         "apply": [("apply", step_apply)],
        "apply": [("apply", step_apply)],
# L223 [Executable statement]:         "fit": [("fit", step_fit)],
        "fit": [("fit", step_fit)],
# L224 [Executable statement]:         "plots": [("plots", step_plots)],
        "plots": [("plots", step_plots)],
# L225 [Executable statement]:         "paper": [("paper", step_paper)],
        "paper": [("paper", step_paper)],
# L226 [Executable statement]:         "stage1": [("histmaker", step_histmaker), ("treemaker", step_treemaker)],
        "stage1": [("histmaker", step_histmaker), ("treemaker", step_treemaker)],
# L227 [Executable statement]:         "ml": [("train", step_train), ("apply", step_apply), ("fit", step_fit)],
        "ml": [("train", step_train), ("apply", step_apply), ("fit", step_fit)],
# L228 [Executable statement]:         "all": [
        "all": [
# L229 [Executable statement]:             ("histmaker", step_histmaker),
            ("histmaker", step_histmaker),
# L230 [Executable statement]:             ("treemaker", step_treemaker),
            ("treemaker", step_treemaker),
# L231 [Executable statement]:             ("train", step_train),
            ("train", step_train),
# L232 [Executable statement]:             ("apply", step_apply),
            ("apply", step_apply),
# L233 [Executable statement]:             ("fit", step_fit),
            ("fit", step_fit),
# L234 [Executable statement]:             ("plots", step_plots),
            ("plots", step_plots),
# L235 [Executable statement]:             ("paper", step_paper),
            ("paper", step_paper),
# L236 [Executable statement]:         ],
        ],
# L237 [Executable statement]:     }
    }
# L238 [Blank separator]: 

# L239 [Executable statement]:     run_sequence(args.target, mapping[args.target])
    run_sequence(args.target, mapping[args.target])
# L240 [Runtime log output]:     print("\nWorkflow completed.")
    print("\nWorkflow completed.")
# L241 [Blank separator]: 

# L242 [Blank separator]: 

# L243 [Conditional block]: if __name__ == "__main__":
if __name__ == "__main__":
# L244 [Executable statement]:     main()
    main()
