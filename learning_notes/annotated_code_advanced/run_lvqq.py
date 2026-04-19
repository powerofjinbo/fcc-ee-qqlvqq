#!/usr/bin/env python3
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
"""Unified driver for the lvqq analysis workflow."""

# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
from __future__ import annotations

# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
import argparse
# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
import os
# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
import shlex
# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
import subprocess
# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
from collections.abc import Callable
# [Context] Importing dependencies for analysis infrastructure, ROOT I/O, and ML/statistical tooling required by this module.
from pathlib import Path


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
ANALYSIS_DIR = Path(__file__).resolve().parent
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
SETUP_SH = Path("/home/submit/jinboz1/tutorials/FCCAnalyses/setup.sh")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
MODEL_DIR = "ml/models/xgboost_bdt_v6"


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def parse_fraction(value: str) -> float:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    try:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        fraction = float(value)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    except ValueError as exc:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        raise argparse.ArgumentTypeError("background fraction must be a float in (0, 1]") from exc
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if not (0.0 < fraction <= 1.0):
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        raise argparse.ArgumentTypeError("background fraction must be in (0, 1]")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    return fraction


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def default_background_fractions() -> dict[str, float]:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    return {"ww": 1.0, "zz": 1.0, "qq": 1.0, "tautau": 1.0}


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def run_bash(command: str, *, needs_setup: bool = False, extra_env: dict[str, str] | None = None) -> None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    env = os.environ.copy()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if extra_env:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        env.update(extra_env)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    shell_cmd = f'cd "{ANALYSIS_DIR}" && {command}'
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if needs_setup:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        shell_cmd = f'source "{SETUP_SH}" >/dev/null 2>&1 && {shell_cmd}'

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    subprocess.run(["bash", "-lc", shell_cmd], check=True, env=env)


# [Workflow] Encapsulated execution unit so each pipeline stage can be rerun independently or chained from the same driver.
def step_histmaker() -> None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    run_bash("fccanalysis run h_hww_lvqq.py", needs_setup=True, extra_env={"LVQQ_MODE": "histmaker"})


# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
def step_treemaker() -> None:
# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
    run_bash("fccanalysis run h_hww_lvqq.py", needs_setup=True, extra_env={"LVQQ_MODE": "treemaker"})


# [Workflow] Encapsulated execution unit so each pipeline stage can be rerun independently or chained from the same driver.
def step_train() -> None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    run_bash("python3 ml/train_xgboost_bdt.py")


# [Workflow] Encapsulated execution unit so each pipeline stage can be rerun independently or chained from the same driver.
def step_apply() -> None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    run_bash("python3 ml/apply_xgboost_bdt.py")


# [ML] Core model operation is tree-based boosted classification; this captures non-linear kinematic correlations in lvqq features.
def step_fit() -> None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    run_bash(f"python3 ml/fit_profile_likelihood.py --model-dir {MODEL_DIR}")


# [Workflow] Encapsulated execution unit so each pipeline stage can be rerun independently or chained from the same driver.
def step_roc_plot() -> None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    run_bash("python3 ml/regenerate_roc.py")


# [Workflow] Encapsulated execution unit so each pipeline stage can be rerun independently or chained from the same driver.
def step_supporting_figures() -> None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    run_bash("python3 paper/generate_supporting_figures.py")


# [Workflow] Encapsulated execution unit so each pipeline stage can be rerun independently or chained from the same driver.
def step_sync_paper_figures() -> None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    run_bash("python3 paper/sync_paper_figures.py")


# [Workflow] Encapsulated execution unit so each pipeline stage can be rerun independently or chained from the same driver.
def step_plots() -> None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    run_bash("python3 plots_lvqq.py", needs_setup=True)
# [Workflow] Encapsulated execution unit so each pipeline stage can be rerun independently or chained from the same driver.
    step_roc_plot()
# [Workflow] Encapsulated execution unit so each pipeline stage can be rerun independently or chained from the same driver.
    step_supporting_figures()
# [Workflow] Encapsulated execution unit so each pipeline stage can be rerun independently or chained from the same driver.
    step_sync_paper_figures()


# [Workflow] Encapsulated execution unit so each pipeline stage can be rerun independently or chained from the same driver.
def step_paper() -> None:
# [Workflow] Encapsulated execution unit so each pipeline stage can be rerun independently or chained from the same driver.
    step_roc_plot()
# [Workflow] Encapsulated execution unit so each pipeline stage can be rerun independently or chained from the same driver.
    step_supporting_figures()
# [Workflow] Encapsulated execution unit so each pipeline stage can be rerun independently or chained from the same driver.
    step_sync_paper_figures()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    run_bash('cd paper && tectonic main.tex')


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def submit_to_slurm(args: argparse.Namespace) -> None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    log_dir = ANALYSIS_DIR / "logs" / "slurm"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    log_dir.mkdir(parents=True, exist_ok=True)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    rerun_cmd = [
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "python3",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        str(ANALYSIS_DIR / "run_lvqq.py"),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        args.target,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ]
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if args.background_fraction is not None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        rerun_cmd.extend(["--background-fraction", str(args.background_fraction)])
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if args.ww_fraction is not None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        rerun_cmd.extend(["--ww-fraction", str(args.ww_fraction)])
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if args.zz_fraction is not None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        rerun_cmd.extend(["--zz-fraction", str(args.zz_fraction)])
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if args.qq_fraction is not None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        rerun_cmd.extend(["--qq-fraction", str(args.qq_fraction)])
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if args.tautau_fraction is not None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        rerun_cmd.extend(["--tautau-fraction", str(args.tautau_fraction)])

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    submit_cmd = [
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "sbatch",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "--parsable",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        f"--job-name=lvqq_{args.target}",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        f"--partition={args.slurm_partition}",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        f"--cpus-per-task={args.slurm_cpus}",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        f"--mem={args.slurm_mem}",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        f"--time={args.slurm_time}",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        f"--chdir={ANALYSIS_DIR}",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        f"--output={log_dir / '%x-%j.out'}",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        f"--error={log_dir / '%x-%j.err'}",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "--wrap",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        shlex.join(rerun_cmd),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    ]

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    result = subprocess.run(submit_cmd, check=True, text=True, capture_output=True)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print(f"Submitted Slurm job {result.stdout.strip()}")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print(f"Logs: {log_dir}")


# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
def run_sequence(name: str, steps: list[tuple[str, Callable[[], None]]]) -> None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for label, fn in steps:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        print(f"\n==> {name}: {label}")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        fn()


# [Workflow] Argument parser: expose knobs for reproducibility (seed), split fractions, model options, and outputs.
def parse_args() -> argparse.Namespace:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    parser = argparse.ArgumentParser(description=__doc__)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    parser.add_argument(
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "target",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        nargs="?",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        default="all",
# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
        choices=["histmaker", "treemaker", "train", "apply", "fit", "plots", "paper", "stage1", "ml", "all"],
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        help="Workflow target to run",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    )
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    parser.add_argument(
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "--background-fraction",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        type=parse_fraction,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        default=None,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        help="Global override for all reducible backgrounds (WW/ZZ/qq/tautau).",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    )
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    parser.add_argument("--ww-fraction", type=parse_fraction, default=None)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    parser.add_argument("--zz-fraction", type=parse_fraction, default=None)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    parser.add_argument("--qq-fraction", type=parse_fraction, default=None)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    parser.add_argument("--tautau-fraction", type=parse_fraction, default=None)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    parser.add_argument(
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "--slurm",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        action="store_true",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        help="Submit the requested workflow target to Slurm instead of running locally.",
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    )
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    parser.add_argument("--slurm-partition", default="submit")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    parser.add_argument("--slurm-cpus", type=int, default=16)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    parser.add_argument("--slurm-mem", default="48G")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    parser.add_argument("--slurm-time", default="2-00:00:00")
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    return parser.parse_args()


# [Workflow] Main orchestrator for this module; executes the full chain for this script only.
def main() -> None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if not SETUP_SH.exists():
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        raise SystemExit(f"Missing FCCAnalyses setup script: {SETUP_SH}")

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    args = parse_args()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if args.background_fraction is not None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        os.environ["LVQQ_BACKGROUND_FRACTION"] = str(args.background_fraction)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    else:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        os.environ.pop("LVQQ_BACKGROUND_FRACTION", None)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if args.ww_fraction is not None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        os.environ["LVQQ_WW_FRACTION"] = str(args.ww_fraction)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    else:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        os.environ.pop("LVQQ_WW_FRACTION", None)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if args.zz_fraction is not None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        os.environ["LVQQ_ZZ_FRACTION"] = str(args.zz_fraction)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    else:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        os.environ.pop("LVQQ_ZZ_FRACTION", None)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if args.qq_fraction is not None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        os.environ["LVQQ_QQ_FRACTION"] = str(args.qq_fraction)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    else:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        os.environ.pop("LVQQ_QQ_FRACTION", None)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if args.tautau_fraction is not None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        os.environ["LVQQ_TAUTAU_FRACTION"] = str(args.tautau_fraction)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    else:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        os.environ.pop("LVQQ_TAUTAU_FRACTION", None)

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    active_fractions = default_background_fractions()
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if args.background_fraction is not None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        active_fractions = {key: args.background_fraction for key in active_fractions}
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    for key, value in {
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "ww": args.ww_fraction,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "zz": args.zz_fraction,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "qq": args.qq_fraction,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "tautau": args.tautau_fraction,
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    }.items():
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        if value is not None:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
            active_fractions[key] = value

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print(
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "Background fractions:"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        f" WW={active_fractions['ww']:.6g},"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        f" ZZ={active_fractions['zz']:.6g},"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        f" qq={active_fractions['qq']:.6g},"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        f" tautau={active_fractions['tautau']:.6g}"
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    )

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    if args.slurm:
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        submit_to_slurm(args)
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        return

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    mapping: dict[str, list[tuple[str, Callable[[], None]]]] = {
# [Workflow] Encapsulated execution unit so each pipeline stage can be rerun independently or chained from the same driver.
        "histmaker": [("histmaker", step_histmaker)],
# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
        "treemaker": [("treemaker", step_treemaker)],
# [Workflow] Encapsulated execution unit so each pipeline stage can be rerun independently or chained from the same driver.
        "train": [("train", step_train)],
# [Workflow] Encapsulated execution unit so each pipeline stage can be rerun independently or chained from the same driver.
        "apply": [("apply", step_apply)],
# [Workflow] Encapsulated execution unit so each pipeline stage can be rerun independently or chained from the same driver.
        "fit": [("fit", step_fit)],
# [Workflow] Encapsulated execution unit so each pipeline stage can be rerun independently or chained from the same driver.
        "plots": [("plots", step_plots)],
# [Workflow] Encapsulated execution unit so each pipeline stage can be rerun independently or chained from the same driver.
        "paper": [("paper", step_paper)],
# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
        "stage1": [("histmaker", step_histmaker), ("treemaker", step_treemaker)],
# [Workflow] Encapsulated execution unit so each pipeline stage can be rerun independently or chained from the same driver.
        "ml": [("train", step_train), ("apply", step_apply), ("fit", step_fit)],
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        "all": [
# [Workflow] Encapsulated execution unit so each pipeline stage can be rerun independently or chained from the same driver.
            ("histmaker", step_histmaker),
# [I/O] Open ROOT/NumPy dataset object and read only required objects; defensive checks below avoid silent empty-tree failures.
            ("treemaker", step_treemaker),
# [Workflow] Encapsulated execution unit so each pipeline stage can be rerun independently or chained from the same driver.
            ("train", step_train),
# [Workflow] Encapsulated execution unit so each pipeline stage can be rerun independently or chained from the same driver.
            ("apply", step_apply),
# [Workflow] Encapsulated execution unit so each pipeline stage can be rerun independently or chained from the same driver.
            ("fit", step_fit),
# [Workflow] Encapsulated execution unit so each pipeline stage can be rerun independently or chained from the same driver.
            ("plots", step_plots),
# [Workflow] Encapsulated execution unit so each pipeline stage can be rerun independently or chained from the same driver.
            ("paper", step_paper),
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
        ],
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    }

# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    run_sequence(args.target, mapping[args.target])
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    print("\nWorkflow completed.")


# [Entry] Module entry point for direct execution from CLI.
if __name__ == "__main__":
# [Execution] Preserve this operation as-is; it contributes either to data preparation, feature transport, or inference bookkeeping with direct effect on downstream statistics.
    main()
