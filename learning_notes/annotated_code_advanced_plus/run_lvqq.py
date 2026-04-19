#!/usr/bin/env python3
# Workflow orchestrator for the full lvqq chain:
# histmaker -> treemaker -> BDT training -> score-table fit -> scored-ROOT export -> plots/paper sync.
#
# This file wires physics selection, ML training/inference, and statistical fit.
# It does not define physics formulas itself; it controls execution order and reproducibility.

"""Unified driver for the lvqq analysis workflow."""

# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
from __future__ import annotations

# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import argparse
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import os
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import shlex
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
import subprocess
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
from collections.abc import Callable
# [Context] Import dependencies for ROOT I/O, pandas/numpy processing, ML, and statistics.
from pathlib import Path


# [Workflow] Configuration binding; this line defines a stable contract across modules.
ANALYSIS_DIR = Path(__file__).resolve().parent
# [Workflow] Configuration binding; this line defines a stable contract across modules.
SETUP_SH = Path("/home/submit/jinboz1/tutorials/FCCAnalyses/setup.sh")
# [Workflow] Configuration binding; this line defines a stable contract across modules.
MODEL_DIR = "ml/models/xgboost_bdt_v6"


# [Workflow] Parse and validate fractions so experiments can be rerun with reproducible CLI knobs.
# Physical interpretation:
# - fractions rescale only effective background exposure from each process family.
# - they emulate alternate control-region calibrations or sensitivity scans.
def parse_fraction(value: str) -> float:
# [Context] Supporting line for the active lvqq analysis stage.
    try:
# [Context] Supporting line for the active lvqq analysis stage.
        fraction = float(value)
# [Context] Supporting line for the active lvqq analysis stage.
    except ValueError as exc:
# [Context] Supporting line for the active lvqq analysis stage.
        raise argparse.ArgumentTypeError("background fraction must be a float in (0, 1]") from exc
# [Context] Supporting line for the active lvqq analysis stage.
    if not (0.0 < fraction <= 1.0):
# [Context] Supporting line for the active lvqq analysis stage.
        raise argparse.ArgumentTypeError("background fraction must be in (0, 1]")
# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return fraction


# [Physics] Baseline background priors used when no override is provided.
def default_background_fractions() -> dict[str, float]:
# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return {"ww": 1.0, "zz": 1.0, "qq": 1.0, "tautau": 1.0}


# [I/O] Wrap command execution so setup and environment interpolation are consistent across all stages.
def run_bash(command: str, *, needs_setup: bool = False, extra_env: dict[str, str] | None = None) -> None:
    # [Workflow] Thin subprocess wrapper guarantees identical execution context.
    # `needs_setup=True` reproduces interactive `source`-based environment for FCCAnalyses binaries.
# [Workflow] Copy exactly the curated deliverables to paper directories.
    env = os.environ.copy()
# [Context] Supporting line for the active lvqq analysis stage.
    if extra_env:
# [Context] Supporting line for the active lvqq analysis stage.
        env.update(extra_env)

# [Context] Supporting line for the active lvqq analysis stage.
    shell_cmd = f'cd "{ANALYSIS_DIR}" && {command}'
# [Context] Supporting line for the active lvqq analysis stage.
    if needs_setup:
# [Context] Supporting line for the active lvqq analysis stage.
        shell_cmd = f'source "{SETUP_SH}" >/dev/null 2>&1 && {shell_cmd}'

# [Context] Supporting line for the active lvqq analysis stage.
    subprocess.run(["bash", "-lc", shell_cmd], check=True, env=env)


# [Workflow] Run histogram workflow for cutflow and shape outputs.
def step_histmaker() -> None:
# [Context] Supporting line for the active lvqq analysis stage.
    run_bash("fccanalysis run h_hww_lvqq.py", needs_setup=True, extra_env={"LVQQ_MODE": "histmaker"})


# [Workflow] Run treemaker to produce per-event branches for ML.
def step_treemaker() -> None:
# [Context] Supporting line for the active lvqq analysis stage.
    run_bash("fccanalysis run h_hww_lvqq.py", needs_setup=True, extra_env={"LVQQ_MODE": "treemaker"})


# [ML] Train BDT from prepared features.
def step_train() -> None:
# [Context] Supporting line for the active lvqq analysis stage.
    run_bash("python3 ml/train_xgboost_bdt.py")


# [ML] Apply trained BDT to all requested samples.
# This is the scored-ROOT export branch, not the default score source of the statistical fit.
def step_apply() -> None:
# [Context] Supporting line for the active lvqq analysis stage.
    run_bash("python3 ml/apply_xgboost_bdt.py")


# [Stats] Execute profile likelihood extraction of sigmaZH x BR(H->WW*).
def step_fit() -> None:
# [Stats] Default fit consumes CSV scores from training artifacts (`kfold_scores.csv` or `test_scores.csv`).
# Running fit before apply therefore shortens time-to-result without changing the statistical input.
# [Context] Supporting line for the active lvqq analysis stage.
    run_bash(f"python3 ml/fit_profile_likelihood.py --model-dir {MODEL_DIR}")


# [ML] Regenerate ROC diagnostic plot(s).
def step_roc_plot() -> None:
# [Context] Supporting line for the active lvqq analysis stage.
    run_bash("python3 ml/regenerate_roc.py")


# [Physics] Produce supplemental plots that check reconstruction and topology assumptions.
def step_supporting_figures() -> None:
# [Context] Supporting line for the active lvqq analysis stage.
    run_bash("python3 paper/generate_supporting_figures.py")


# [Workflow] Move selected outputs into paper directory.
def step_sync_paper_figures() -> None:
# [Context] Supporting line for the active lvqq analysis stage.
    run_bash("python3 paper/sync_paper_figures.py")


# [Workflow] run_lvqq.py function step_plots: modularize one operation for deterministic pipeline control.
def step_plots() -> None:
    # Ploting step is intentionally coupled after fit outputs exist:
    # - ROC/fit diagnostics and supporting figures are generated from the same model artifacts.
    # - paper sync is a purely file-management step, no physics recomputation.
# [Context] Supporting line for the active lvqq analysis stage.
    run_bash("python3 plots_lvqq.py", needs_setup=True)
# [Context] Supporting line for the active lvqq analysis stage.
    step_roc_plot()
# [Context] Supporting line for the active lvqq analysis stage.
    step_supporting_figures()
# [Context] Supporting line for the active lvqq analysis stage.
    step_sync_paper_figures()


# [Workflow] run_lvqq.py function step_paper: modularize one operation for deterministic pipeline control.
def step_paper() -> None:
# [Context] Supporting line for the active lvqq analysis stage.
    step_roc_plot()
# [Context] Supporting line for the active lvqq analysis stage.
    step_supporting_figures()
# [Context] Supporting line for the active lvqq analysis stage.
    step_sync_paper_figures()
# [Context] Supporting line for the active lvqq analysis stage.
    run_bash('cd paper && tectonic main.tex')


# [Workflow] Build reproducible batch submission with logs and tuned scheduler resources.
def submit_to_slurm(args: argparse.Namespace) -> None:
# [Context] Supporting line for the active lvqq analysis stage.
    log_dir = ANALYSIS_DIR / "logs" / "slurm"
# [Context] Supporting line for the active lvqq analysis stage.
    log_dir.mkdir(parents=True, exist_ok=True)

# [Context] Supporting line for the active lvqq analysis stage.
    rerun_cmd = [
# [Context] Supporting line for the active lvqq analysis stage.
        "python3",
# [Context] Supporting line for the active lvqq analysis stage.
        str(ANALYSIS_DIR / "run_lvqq.py"),
# [Context] Supporting line for the active lvqq analysis stage.
        args.target,
# [Context] Supporting line for the active lvqq analysis stage.
    ]
# [Context] Supporting line for the active lvqq analysis stage.
    if args.background_fraction is not None:
# [Context] Supporting line for the active lvqq analysis stage.
        rerun_cmd.extend(["--background-fraction", str(args.background_fraction)])
# [Context] Supporting line for the active lvqq analysis stage.
    if args.ww_fraction is not None:
# [Context] Supporting line for the active lvqq analysis stage.
        rerun_cmd.extend(["--ww-fraction", str(args.ww_fraction)])
# [Context] Supporting line for the active lvqq analysis stage.
    if args.zz_fraction is not None:
# [Context] Supporting line for the active lvqq analysis stage.
        rerun_cmd.extend(["--zz-fraction", str(args.zz_fraction)])
# [Context] Supporting line for the active lvqq analysis stage.
    if args.qq_fraction is not None:
# [Context] Supporting line for the active lvqq analysis stage.
        rerun_cmd.extend(["--qq-fraction", str(args.qq_fraction)])
# [Context] Supporting line for the active lvqq analysis stage.
    if args.tautau_fraction is not None:
# [Context] Supporting line for the active lvqq analysis stage.
        rerun_cmd.extend(["--tautau-fraction", str(args.tautau_fraction)])

# [Context] Supporting line for the active lvqq analysis stage.
    submit_cmd = [
# [Context] Supporting line for the active lvqq analysis stage.
        "sbatch",
# [Context] Supporting line for the active lvqq analysis stage.
        "--parsable",
# [Context] Supporting line for the active lvqq analysis stage.
        f"--job-name=lvqq_{args.target}",
# [Context] Supporting line for the active lvqq analysis stage.
        f"--partition={args.slurm_partition}",
# [Context] Supporting line for the active lvqq analysis stage.
        f"--cpus-per-task={args.slurm_cpus}",
# [Context] Supporting line for the active lvqq analysis stage.
        f"--mem={args.slurm_mem}",
# [Context] Supporting line for the active lvqq analysis stage.
        f"--time={args.slurm_time}",
# [Context] Supporting line for the active lvqq analysis stage.
        f"--chdir={ANALYSIS_DIR}",
# [Context] Supporting line for the active lvqq analysis stage.
        f"--output={log_dir / '%x-%j.out'}",
# [Context] Supporting line for the active lvqq analysis stage.
        f"--error={log_dir / '%x-%j.err'}",
# [Context] Supporting line for the active lvqq analysis stage.
        "--wrap",
# [Context] Supporting line for the active lvqq analysis stage.
        shlex.join(rerun_cmd),
# [Context] Supporting line for the active lvqq analysis stage.
    ]

# [Context] Supporting line for the active lvqq analysis stage.
    result = subprocess.run(submit_cmd, check=True, text=True, capture_output=True)
# [Context] Supporting line for the active lvqq analysis stage.
    print(f"Submitted Slurm job {result.stdout.strip()}")
# [Context] Supporting line for the active lvqq analysis stage.
    print(f"Logs: {log_dir}")


# [Workflow] run_lvqq.py function run_sequence: modularize one operation for deterministic pipeline control.
def run_sequence(name: str, steps: list[tuple[str, Callable[[], None]]]) -> None:
# [Context] Supporting line for the active lvqq analysis stage.
    for label, fn in steps:
# [Context] Supporting line for the active lvqq analysis stage.
        print(f"\n==> {name}: {label}")
# [Context] Supporting line for the active lvqq analysis stage.
        fn()


# [Workflow] run_lvqq.py function parse_args: modularize one operation for deterministic pipeline control.
def parse_args() -> argparse.Namespace:
    # CLI supports both full end-to-end runs and targeted steps.
    # For scientific debugging, typical pattern is: histmaker->treemaker->train->fit.
# [Context] Supporting line for the active lvqq analysis stage.
    parser = argparse.ArgumentParser(description=__doc__)
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument(
# [Context] Supporting line for the active lvqq analysis stage.
        "target",
# [Context] Supporting line for the active lvqq analysis stage.
        nargs="?",
# [Context] Supporting line for the active lvqq analysis stage.
        default="all",
# [Context] Supporting line for the active lvqq analysis stage.
        choices=["histmaker", "treemaker", "train", "apply", "fit", "plots", "paper", "stage1", "ml", "all"],
# [Context] Supporting line for the active lvqq analysis stage.
        help="Workflow target to run",
# [Context] Supporting line for the active lvqq analysis stage.
    )
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument(
# [Context] Supporting line for the active lvqq analysis stage.
        "--background-fraction",
# [Context] Supporting line for the active lvqq analysis stage.
        type=parse_fraction,
# [Context] Supporting line for the active lvqq analysis stage.
        default=None,
# [Context] Supporting line for the active lvqq analysis stage.
        help="Global override for all reducible backgrounds (WW/ZZ/qq/tautau).",
# [Context] Supporting line for the active lvqq analysis stage.
    )
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument("--ww-fraction", type=parse_fraction, default=None)
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument("--zz-fraction", type=parse_fraction, default=None)
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument("--qq-fraction", type=parse_fraction, default=None)
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument("--tautau-fraction", type=parse_fraction, default=None)
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument(
# [Context] Supporting line for the active lvqq analysis stage.
        "--slurm",
# [Context] Supporting line for the active lvqq analysis stage.
        action="store_true",
# [Context] Supporting line for the active lvqq analysis stage.
        help="Submit the requested workflow target to Slurm instead of running locally.",
# [Context] Supporting line for the active lvqq analysis stage.
    )
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument("--slurm-partition", default="submit")
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument("--slurm-cpus", type=int, default=16)
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument("--slurm-mem", default="48G")
# [Context] Supporting line for the active lvqq analysis stage.
    parser.add_argument("--slurm-time", default="2-00:00:00")
# [Workflow] Return value hands the constructed object/metric to the next module stage.
    return parser.parse_args()


# [Workflow] run_lvqq.py function main: modularize one operation for deterministic pipeline control.
def main() -> None:
# [Context] Supporting line for the active lvqq analysis stage.
    if not SETUP_SH.exists():
# [Context] Supporting line for the active lvqq analysis stage.
        raise SystemExit(f"Missing FCCAnalyses setup script: {SETUP_SH}")

# [Context] Supporting line for the active lvqq analysis stage.
    args = parse_args()
# [Context] Supporting line for the active lvqq analysis stage.
    if args.background_fraction is not None:
# [Context] Supporting line for the active lvqq analysis stage.
        os.environ["LVQQ_BACKGROUND_FRACTION"] = str(args.background_fraction)
# [Context] Supporting line for the active lvqq analysis stage.
    else:
# [Context] Supporting line for the active lvqq analysis stage.
        os.environ.pop("LVQQ_BACKGROUND_FRACTION", None)
# [Context] Supporting line for the active lvqq analysis stage.
    if args.ww_fraction is not None:
# [Context] Supporting line for the active lvqq analysis stage.
        os.environ["LVQQ_WW_FRACTION"] = str(args.ww_fraction)
# [Context] Supporting line for the active lvqq analysis stage.
    else:
# [Context] Supporting line for the active lvqq analysis stage.
        os.environ.pop("LVQQ_WW_FRACTION", None)
# [Context] Supporting line for the active lvqq analysis stage.
    if args.zz_fraction is not None:
# [Context] Supporting line for the active lvqq analysis stage.
        os.environ["LVQQ_ZZ_FRACTION"] = str(args.zz_fraction)
# [Context] Supporting line for the active lvqq analysis stage.
    else:
# [Context] Supporting line for the active lvqq analysis stage.
        os.environ.pop("LVQQ_ZZ_FRACTION", None)
# [Context] Supporting line for the active lvqq analysis stage.
    if args.qq_fraction is not None:
# [Context] Supporting line for the active lvqq analysis stage.
        os.environ["LVQQ_QQ_FRACTION"] = str(args.qq_fraction)
# [Context] Supporting line for the active lvqq analysis stage.
    else:
# [Context] Supporting line for the active lvqq analysis stage.
        os.environ.pop("LVQQ_QQ_FRACTION", None)
# [Context] Supporting line for the active lvqq analysis stage.
    if args.tautau_fraction is not None:
# [Context] Supporting line for the active lvqq analysis stage.
        os.environ["LVQQ_TAUTAU_FRACTION"] = str(args.tautau_fraction)
# [Context] Supporting line for the active lvqq analysis stage.
    else:
# [Context] Supporting line for the active lvqq analysis stage.
        os.environ.pop("LVQQ_TAUTAU_FRACTION", None)

# [Context] Supporting line for the active lvqq analysis stage.
    active_fractions = default_background_fractions()
# [Context] Supporting line for the active lvqq analysis stage.
    if args.background_fraction is not None:
# [Context] Supporting line for the active lvqq analysis stage.
        active_fractions = {key: args.background_fraction for key in active_fractions}
# [Context] Supporting line for the active lvqq analysis stage.
    for key, value in {
# [Context] Supporting line for the active lvqq analysis stage.
        "ww": args.ww_fraction,
# [Context] Supporting line for the active lvqq analysis stage.
        "zz": args.zz_fraction,
# [Context] Supporting line for the active lvqq analysis stage.
        "qq": args.qq_fraction,
# [Context] Supporting line for the active lvqq analysis stage.
        "tautau": args.tautau_fraction,
# [Context] Supporting line for the active lvqq analysis stage.
    }.items():
# [Context] Supporting line for the active lvqq analysis stage.
        if value is not None:
# [Context] Supporting line for the active lvqq analysis stage.
            active_fractions[key] = value

# [Context] Supporting line for the active lvqq analysis stage.
    print(
# [Context] Supporting line for the active lvqq analysis stage.
        "Background fractions:"
# [Context] Supporting line for the active lvqq analysis stage.
        f" WW={active_fractions['ww']:.6g},"
# [Context] Supporting line for the active lvqq analysis stage.
        f" ZZ={active_fractions['zz']:.6g},"
# [Context] Supporting line for the active lvqq analysis stage.
        f" qq={active_fractions['qq']:.6g},"
# [Context] Supporting line for the active lvqq analysis stage.
        f" tautau={active_fractions['tautau']:.6g}"
# [Context] Supporting line for the active lvqq analysis stage.
    )

# [Context] Supporting line for the active lvqq analysis stage.
    if args.slurm:
# [Context] Supporting line for the active lvqq analysis stage.
        submit_to_slurm(args)
# [Workflow] Return value hands the constructed object/metric to the next module stage.
        return

# [Context] Supporting line for the active lvqq analysis stage.
    mapping: dict[str, list[tuple[str, Callable[[], None]]]] = {
# [Context] Supporting line for the active lvqq analysis stage.
        "histmaker": [("histmaker", step_histmaker)],
# [Context] Supporting line for the active lvqq analysis stage.
        "treemaker": [("treemaker", step_treemaker)],
# [Context] Supporting line for the active lvqq analysis stage.
        "train": [("train", step_train)],
# [Context] Supporting line for the active lvqq analysis stage.
        "apply": [("apply", step_apply)],
# [Context] Supporting line for the active lvqq analysis stage.
        "fit": [("fit", step_fit)],
# [Context] Supporting line for the active lvqq analysis stage.
        "plots": [("plots", step_plots)],
# [Context] Supporting line for the active lvqq analysis stage.
        "paper": [("paper", step_paper)],
# [Context] Supporting line for the active lvqq analysis stage.
        "stage1": [("histmaker", step_histmaker), ("treemaker", step_treemaker)],
# [Workflow] Default ML path is ordered for fastest useful answer:
# `train` writes CSV scores immediately, so `fit` can finish before the optional full ROOT re-scoring pass.
# [Context] Supporting line for the active lvqq analysis stage.
        "ml": [("train", step_train), ("fit", step_fit), ("apply", step_apply)],
# [Context] Supporting line for the active lvqq analysis stage.
        "all": [
# [Context] Supporting line for the active lvqq analysis stage.
            ("histmaker", step_histmaker),
# [Context] Supporting line for the active lvqq analysis stage.
            ("treemaker", step_treemaker),
# [Context] Supporting line for the active lvqq analysis stage.
            ("train", step_train),
# [Context] Supporting line for the active lvqq analysis stage.
            ("fit", step_fit),
# [Context] Supporting line for the active lvqq analysis stage.
            ("apply", step_apply),
# [Context] Supporting line for the active lvqq analysis stage.
            ("plots", step_plots),
# [Context] Supporting line for the active lvqq analysis stage.
            ("paper", step_paper),
# [Context] Supporting line for the active lvqq analysis stage.
        ],
# [Context] Supporting line for the active lvqq analysis stage.
    }

# [Context] Supporting line for the active lvqq analysis stage.
    run_sequence(args.target, mapping[args.target])
# [Context] Supporting line for the active lvqq analysis stage.
    print("\nWorkflow completed.")


# [Context] Supporting line for the active lvqq analysis stage.
if __name__ == "__main__":
# [Context] Supporting line for the active lvqq analysis stage.
    main()
