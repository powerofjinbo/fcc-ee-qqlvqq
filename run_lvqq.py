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
SETUP_SH = Path("/home/submit/jinboz1/tutorials/FCCAnalyses/setup.sh")

def parse_fraction(value: str) -> float:
    try:
        fraction = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("background fraction must be a float in (0, 1]") from exc
    if not (0.0 < fraction <= 1.0):
        raise argparse.ArgumentTypeError("background fraction must be in (0, 1]")
    return fraction


def default_background_fractions() -> dict[str, float]:
    return {"ww": 1.0, "zz": 1.0, "qq": 1.0, "tautau": 1.0, "zh_other": 1.0}


def run_bash(command: str, *, needs_setup: bool = False, extra_env: dict[str, str] | None = None) -> None:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)

    shell_cmd = f'cd "{ANALYSIS_DIR}" && {command}'
    if needs_setup:
        shell_cmd = f'source "{SETUP_SH}" >/dev/null 2>&1 && {shell_cmd}'

    subprocess.run(["bash", "-lc", shell_cmd], check=True, env=env)


def fccanalysis_run_command() -> str:
    raw_cpus = os.environ.get("LVQQ_CPUS", os.environ.get("SLURM_CPUS_PER_TASK", "32"))
    try:
        cpus = int(raw_cpus)
    except ValueError as exc:
        raise ValueError(f"Invalid CPU setting {raw_cpus!r}; expected a positive integer") from exc
    if cpus < 1:
        raise ValueError(f"Invalid CPU setting {raw_cpus!r}; expected a positive integer")
    return f"fccanalysis run --ncpus {cpus} h_hww_lvqq.py"


def step_histmaker() -> None:
    run_bash(fccanalysis_run_command(), needs_setup=True, extra_env={"LVQQ_MODE": "histmaker"})


def step_treemaker() -> None:
    run_bash(fccanalysis_run_command(), needs_setup=True, extra_env={"LVQQ_MODE": "treemaker"})


def step_scanmaker() -> None:
    run_bash(fccanalysis_run_command(), needs_setup=True, extra_env={"LVQQ_MODE": "scanmaker"})


def step_train() -> None:
    run_bash("python3 ml/train_xgboost_bdt.py")


def step_apply() -> None:
    run_bash("python3 ml/apply_xgboost_bdt.py")


def step_fit() -> None:
    run_bash("python3 ml/fit_profile_likelihood.py")


def step_cutscan() -> None:
    run_bash("python3 ml/scan_preselection_cuts.py")


def step_roc_plot() -> None:
    run_bash("python3 ml/regenerate_roc.py")


def step_supporting_figures() -> None:
    run_bash("python3 paper/generate_supporting_figures.py")


def step_sync_paper_figures() -> None:
    run_bash("python3 paper/sync_paper_figures.py")


def step_plots() -> None:
    run_bash("python3 plots_lvqq.py", needs_setup=True)
    step_roc_plot()
    step_supporting_figures()
    step_sync_paper_figures()


def step_cut_plots() -> None:
    run_bash("python3 plots_lvqq.py", needs_setup=True)


def step_paper() -> None:
    step_roc_plot()
    step_supporting_figures()
    step_sync_paper_figures()
    run_bash('cd paper && tectonic main.tex')


def submit_to_slurm(args: argparse.Namespace) -> None:
    log_dir = ANALYSIS_DIR / "logs" / "slurm"
    log_dir.mkdir(parents=True, exist_ok=True)

    rerun_cmd = [
        "env",
        f"LVQQ_CPUS={args.slurm_cpus}",
        "python3",
        str(ANALYSIS_DIR / "run_lvqq.py"),
        args.target,
    ]
    if args.signal_fraction is not None:
        rerun_cmd.extend(["--signal-fraction", str(args.signal_fraction)])
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
    if args.zh_other_fraction is not None:
        rerun_cmd.extend(["--zh-other-fraction", str(args.zh_other_fraction)])
    if args.sample_groups is not None:
        rerun_cmd.extend(["--sample-groups", args.sample_groups])
    if args.samples is not None:
        rerun_cmd.extend(["--samples", args.samples])
    if args.output_tag is not None:
        rerun_cmd.extend(["--output-tag", args.output_tag])

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
        choices=[
            "histmaker",
            "treemaker",
            "scanmaker",
            "cutscan",
            "scans",
            "train",
            "apply",
            "fit",
            "plots",
            "cutplots",
            "analysis",
            "paper",
            "stage1",
            "ml",
            "all",
        ],
        help="Workflow target to run",
    )
    parser.add_argument(
        "--background-fraction",
        type=parse_fraction,
        default=None,
        help="Global override for all backgrounds (WW/ZZ/qq/tautau/ZH(other)).",
    )
    parser.add_argument(
        "--signal-fraction",
        type=parse_fraction,
        default=None,
        help="Override signal processing fraction for quick smoke tests.",
    )
    parser.add_argument("--ww-fraction", type=parse_fraction, default=None)
    parser.add_argument("--zz-fraction", type=parse_fraction, default=None)
    parser.add_argument("--qq-fraction", type=parse_fraction, default=None)
    parser.add_argument("--tautau-fraction", type=parse_fraction, default=None)
    parser.add_argument("--zh-other-fraction", type=parse_fraction, default=None)
    parser.add_argument(
        "--sample-groups",
        default=None,
        help=(
            "Comma-separated sample groups to run: signal,ww,zz,qq,tautau,zh_other. "
            "Default is all groups."
        ),
    )
    parser.add_argument(
        "--samples",
        default=None,
        help=(
            "Comma-separated exact sample names to run. This is useful for splitting "
            "large groups such as qq into uu/dd/cc/ss/bb jobs."
        ),
    )
    parser.add_argument(
        "--output-tag",
        default=None,
        help="Write outputs to tagged directories, e.g. output/h_hww_lvqq_<tag> and plots_lvqq_<tag>.",
    )
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
    if args.output_tag is not None:
        os.environ["LVQQ_OUTPUT_TAG"] = args.output_tag
    else:
        os.environ.pop("LVQQ_OUTPUT_TAG", None)
    if args.signal_fraction is not None:
        os.environ["LVQQ_SIGNAL_FRACTION"] = str(args.signal_fraction)
    else:
        os.environ.pop("LVQQ_SIGNAL_FRACTION", None)
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
    if args.zh_other_fraction is not None:
        os.environ["LVQQ_ZH_OTHER_FRACTION"] = str(args.zh_other_fraction)
    else:
        os.environ.pop("LVQQ_ZH_OTHER_FRACTION", None)
    if args.sample_groups is not None:
        os.environ["LVQQ_SAMPLE_GROUPS"] = args.sample_groups
    else:
        os.environ.pop("LVQQ_SAMPLE_GROUPS", None)
    if args.samples is not None:
        os.environ["LVQQ_ONLY_SAMPLES"] = args.samples
    else:
        os.environ.pop("LVQQ_ONLY_SAMPLES", None)

    active_fractions = default_background_fractions()
    if args.background_fraction is not None:
        active_fractions = {key: args.background_fraction for key in active_fractions}
    for key, value in {
        "ww": args.ww_fraction,
        "zz": args.zz_fraction,
        "qq": args.qq_fraction,
        "tautau": args.tautau_fraction,
        "zh_other": args.zh_other_fraction,
    }.items():
        if value is not None:
            active_fractions[key] = value

    print(
        f"Signal fraction: {args.signal_fraction if args.signal_fraction is not None else 1.0:.6g}"
    )
    if args.output_tag is not None:
        print(f"Output tag: {args.output_tag}")
    if args.sample_groups is not None:
        print(f"Sample groups: {args.sample_groups}")
    if args.samples is not None:
        print(f"Samples: {args.samples}")
    print(
        "Background fractions:"
        f" WW={active_fractions['ww']:.6g},"
        f" ZZ={active_fractions['zz']:.6g},"
        f" qq={active_fractions['qq']:.6g},"
        f" tautau={active_fractions['tautau']:.6g},"
        f" ZH(other)={active_fractions['zh_other']:.6g}"
    )

    if args.slurm:
        submit_to_slurm(args)
        return

    mapping: dict[str, list[tuple[str, Callable[[], None]]]] = {
        "histmaker": [("histmaker", step_histmaker)],
        "treemaker": [("treemaker", step_treemaker)],
        "scanmaker": [("scanmaker", step_scanmaker)],
        "cutscan": [("cutscan", step_cutscan)],
        "scans": [("scanmaker", step_scanmaker), ("cutscan", step_cutscan)],
        "train": [("train", step_train)],
        "apply": [("apply", step_apply)],
        "fit": [("fit", step_fit)],
        "plots": [("plots", step_plots)],
        "cutplots": [("histmaker", step_histmaker), ("cut plots", step_cut_plots)],
        "analysis": [
            ("histmaker", step_histmaker),
            ("treemaker", step_treemaker),
            ("train", step_train),
            ("apply", step_apply),
            ("fit", step_fit),
            ("plots", step_plots),
        ],
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
