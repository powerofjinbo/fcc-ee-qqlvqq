#!/usr/bin/env python3
"""Unified driver for the lvqq analysis workflow."""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
from collections.abc import Callable
from pathlib import Path


ANALYSIS_DIR = Path(__file__).resolve().parent
SETUP_SH = Path(os.environ.get("FCCANALYSES_SETUP_SH", "/home/submit/jinboz1/tutorials/FCCAnalyses/setup.sh"))
MODEL_DIR = "ml/models/xgboost_bdt_v6"


def parse_fraction(value: str) -> float:
    try:
        fraction = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("background fraction must be a float in (0, 1]") from exc
    if not (0.0 < fraction <= 1.0):
        raise argparse.ArgumentTypeError("background fraction must be in (0, 1]")
    return fraction


def default_background_fractions() -> dict[str, float]:
    return {"ww": 0.10, "zz": 0.10, "qq": 0.05, "tautau": 0.10}


def run_bash(command: str, *, needs_setup: bool = False, extra_env: dict[str, str] | None = None) -> None:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)

    shell_cmd = f'cd "{ANALYSIS_DIR}" && {command}'
    if needs_setup:
        shell_cmd = f'source "{SETUP_SH}" >/dev/null 2>&1 && {shell_cmd}'

    subprocess.run(["bash", "-lc", shell_cmd], check=True, env=env)


def step_histmaker() -> None:
    run_bash("fccanalysis run h_hww_lvqq.py", needs_setup=True, extra_env={"LVQQ_MODE": "histmaker"})


def step_treemaker() -> None:
    run_bash("fccanalysis run h_hww_lvqq.py", needs_setup=True, extra_env={"LVQQ_MODE": "treemaker"})


def step_train() -> None:
    run_bash("python3 ml/train_xgboost_bdt.py")


def step_apply() -> None:
    run_bash("python3 ml/apply_xgboost_bdt.py")


def step_fit() -> None:
    run_bash(f"python3 ml/fit_profile_likelihood.py --model-dir {MODEL_DIR}")


def step_supporting_figures() -> None:
    run_bash("python3 paper/generate_supporting_figures.py")


def step_plots() -> None:
    run_bash("python3 plots_lvqq.py", needs_setup=True)
    step_supporting_figures()


def step_paper() -> None:
    run_bash('cd paper && tectonic main.tex')


def submit_to_slurm(args: argparse.Namespace) -> None:
    log_dir = ANALYSIS_DIR / "logs" / "slurm"
    log_dir.mkdir(parents=True, exist_ok=True)

    rerun_cmd = [
        "python3",
        str(ANALYSIS_DIR / "run_lvqq.py"),
        args.target,
    ]
    if args.background_fraction is not None:
        rerun_cmd.extend(["--background-fraction", str(args.background_fraction)])
    if args.ww_fraction is not None:
        rerun_cmd.extend(["--ww-fraction", str(args.ww_fraction)])
    if args.zz_fraction is not None:
        rerun_cmd.extend(["--zz-fraction", str(args.zz_fraction)])
    if args.qq_fraction is not None:
        rerun_cmd.extend(["--qq-fraction", str(args.qq_fraction)])
    if args.tautau_fraction is not None:
        rerun_cmd.extend(["--tautau-fraction", str(args.tautau_fraction)])

    submit_cmd = [
        "sbatch",
        "--parsable",
        f"--job-name=lvqq_{args.target}",
        f"--partition={args.slurm_partition}",
        f"--cpus-per-task={args.slurm_cpus}",
        f"--mem={args.slurm_mem}",
        f"--time={args.slurm_time}",
        f"--chdir={ANALYSIS_DIR}",
        f"--output={log_dir / '%x-%j.out'}",
        f"--error={log_dir / '%x-%j.err'}",
        "--wrap",
        shlex.join(rerun_cmd),
    ]

    result = subprocess.run(submit_cmd, check=True, text=True, capture_output=True)
    print(f"Submitted Slurm job {result.stdout.strip()}")
    print(f"Logs: {log_dir}")


def run_sequence(name: str, steps: list[tuple[str, Callable[[], None]]]) -> None:
    for label, fn in steps:
        print(f"\n==> {name}: {label}")
        fn()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "target",
        nargs="?",
        default="all",
        choices=["histmaker", "treemaker", "train", "apply", "fit", "plots", "paper", "stage1", "ml", "all"],
        help="Workflow target to run",
    )
    parser.add_argument(
        "--background-fraction",
        type=parse_fraction,
        default=None,
        help="Global override for all reducible backgrounds (WW/ZZ/qq/tautau).",
    )
    parser.add_argument("--ww-fraction", type=parse_fraction, default=None)
    parser.add_argument("--zz-fraction", type=parse_fraction, default=None)
    parser.add_argument("--qq-fraction", type=parse_fraction, default=None)
    parser.add_argument("--tautau-fraction", type=parse_fraction, default=None)
    parser.add_argument(
        "--slurm",
        action="store_true",
        help="Submit the requested workflow target to Slurm instead of running locally.",
    )
    parser.add_argument("--slurm-partition", default="submit")
    parser.add_argument("--slurm-cpus", type=int, default=16)
    parser.add_argument("--slurm-mem", default="48G")
    parser.add_argument("--slurm-time", default="2-00:00:00")
    return parser.parse_args()


def main() -> None:
    if not SETUP_SH.exists():
        raise SystemExit(f"Missing FCCAnalyses setup script: {SETUP_SH}")

    args = parse_args()
    if args.background_fraction is not None:
        os.environ["LVQQ_BACKGROUND_FRACTION"] = str(args.background_fraction)
    else:
        os.environ.pop("LVQQ_BACKGROUND_FRACTION", None)
    if args.ww_fraction is not None:
        os.environ["LVQQ_WW_FRACTION"] = str(args.ww_fraction)
    else:
        os.environ.pop("LVQQ_WW_FRACTION", None)
    if args.zz_fraction is not None:
        os.environ["LVQQ_ZZ_FRACTION"] = str(args.zz_fraction)
    else:
        os.environ.pop("LVQQ_ZZ_FRACTION", None)
    if args.qq_fraction is not None:
        os.environ["LVQQ_QQ_FRACTION"] = str(args.qq_fraction)
    else:
        os.environ.pop("LVQQ_QQ_FRACTION", None)
    if args.tautau_fraction is not None:
        os.environ["LVQQ_TAUTAU_FRACTION"] = str(args.tautau_fraction)
    else:
        os.environ.pop("LVQQ_TAUTAU_FRACTION", None)

    active_fractions = default_background_fractions()
    if args.background_fraction is not None:
        active_fractions = {key: args.background_fraction for key in active_fractions}
    for key, value in {
        "ww": args.ww_fraction,
        "zz": args.zz_fraction,
        "qq": args.qq_fraction,
        "tautau": args.tautau_fraction,
    }.items():
        if value is not None:
            active_fractions[key] = value

    print(
        "Background fractions:"
        f" WW={active_fractions['ww']:.6g},"
        f" ZZ={active_fractions['zz']:.6g},"
        f" qq={active_fractions['qq']:.6g},"
        f" tautau={active_fractions['tautau']:.6g}"
    )

    if args.slurm:
        submit_to_slurm(args)
        return

    mapping: dict[str, list[tuple[str, Callable[[], None]]]] = {
        "histmaker": [("histmaker", step_histmaker)],
        "treemaker": [("treemaker", step_treemaker)],
        "train": [("train", step_train)],
        "apply": [("apply", step_apply)],
        "fit": [("fit", step_fit)],
        "plots": [("plots", step_plots)],
        "paper": [("paper", step_paper)],
        "stage1": [("histmaker", step_histmaker), ("treemaker", step_treemaker)],
        "ml": [("train", step_train), ("apply", step_apply), ("fit", step_fit)],
        "all": [
            ("histmaker", step_histmaker),
            ("treemaker", step_treemaker),
            ("train", step_train),
            ("apply", step_apply),
            ("fit", step_fit),
            ("plots", step_plots),
            ("paper", step_paper),
        ],
    }

    run_sequence(args.target, mapping[args.target])
    print("\nWorkflow completed.")


if __name__ == "__main__":
    main()
