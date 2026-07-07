#!/usr/bin/env python3
"""Organize per-cut plots into v7-style cut-by-stage folders.

This script is intentionally lightweight: it copies already-generated plots and
cut-strength tables into a stage-by-stage directory. It does not rerun the
event selection or remake histograms.
"""

from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass
from pathlib import Path


EXTENSIONS = (".pdf", ".png", ".txt", ".tex", ".csv")


def version_from_tag(tag: str) -> str:
    if "v_fable" in tag:
        return "v_fable"
    return next(
        (
            candidate
            for candidate in ("v12", "v11", "v10", "v9")
            if f"_{candidate}_" in tag or tag.endswith(f"_{candidate}")
        ),
        "latest",
    )


@dataclass(frozen=True)
class Stage:
    folder: str
    title: str
    diagnostics: tuple[str, ...] = ()
    plots: tuple[str, ...] = ()
    strength_cut: str | None = None


STAGES: tuple[Stage, ...] = (
    Stage(
        folder="cut0_overview",
        title="Global cutflow overview",
        plots=("cutFlow", "cutFlow_cutflow", "cutFlow_efficiency"),
    ),
    Stage(
        folder="cut1_lepton_candidate_10p60",
        title="Cut1: at least one lepton with 10 < p < 60 GeV",
        diagnostics=("cut1_lepton_candidate",),
        plots=(
            "n_leptons_p10_p60",
            "lepton_p",
            "lepton_p_after_cut1",
            "n_iso_leptons_p10_p60_after_cut1",
        ),
        strength_cut="cut1",
    ),
    Stage(
        folder="cut2_lepton_isolation",
        title="Cut2: selected lepton isolation",
        diagnostics=("cut2_lepton_isolation", "cut2_lepton_isolation_right_tail"),
        plots=(
            "lepton_iso",
            "lepton_iso_after_cut1",
            "n_iso_leptons_p10",
            "n_iso_leptons_p10_after_cut1",
            "n_iso_leptons_p10_p60_after_cut1",
            "n_iso_leptons_p10_after_cut2",
        ),
        strength_cut="cut2",
    ),
    Stage(
        folder="cut3_extra_lepton_veto",
        title="Cut3: veto extra lepton with p > 20 GeV",
        diagnostics=("cut3_extra_lepton_veto", "cut3_extra_lepton_momentum"),
        plots=(
            "n_extra_iso_leptons_p20",
            "n_extra_iso_leptons_p20_after_cut1",
            "extra_iso_lepton_p_after_cut2",
            "n_iso_leptons_p10_after_cut2",
        ),
        strength_cut="cut3",
    ),
    Stage(
        folder="cut4_missing_energy_window",
        title="Cut4: 10 < missing energy < 55 GeV",
        diagnostics=("cut4_missing_energy_window",),
        plots=(
            "missingEnergy_e",
            "missingEnergy_e_after_cut2",
            "missingEnergy_e_after_cut3",
            "missingEnergy_p",
            "missingEnergy_p_after_cut2",
            "missingEnergy_p_after_cut3",
            "missingMass",
            "missingMass_after_cut2",
            "missingMass_after_cut3",
            "cosTheta_miss",
            "cosTheta_miss_after_cut2",
            "cosTheta_miss_after_cut3",
        ),
        strength_cut="cut4",
    ),
    Stage(
        folder="cut5_four_jet_topology",
        title="Cut5: exclusive 4-jet topology and sqrt(d34) > 14 GeV",
        diagnostics=(
            "cut5_four_jet_reconstruction",
            "cut5_sqrt_d34_topology",
            "cut5_sqrt_d23_topology",
            "cut5_min_jet_p_topology",
            "cut5_min_jet_nconst_topology",
            "cut5_wstar_mass_topology",
            "cut5_deltaR_wstar_topology",
        ),
        plots=(
            "visibleEnergy",
            "njets",
            "sqrt_d34",
            "sqrt_d23",
            "min_jet_p",
            "Wstar_m",
            "deltaR_Wstar",
            "angle_Wstar_jj",
            "jet0_p",
            "jet1_p",
            "jet2_p",
            "jet3_p",
        ),
        strength_cut="cut5",
    ),
    Stage(
        folder="cut6_min_jet_nconst",
        title="Cut6: minimum jet constituent multiplicity > 8",
        diagnostics=("cut6_min_jet_nconst_topology", "cut6_mean_jet_nconst_topology"),
        plots=(
            "min_jet_nconst",
            "min_jet_nconst_after_cut5",
            "mean_jet_nconst",
            "mean_jet_nconst_after_cut6",
            "jet0_nconst",
            "jet1_nconst",
            "jet2_nconst",
            "jet3_nconst",
        ),
        strength_cut="cut6",
    ),
    Stage(
        folder="post_cut6_bdt_shape_inputs",
        title="Post-Cut6 diagnostic and BDT-shape inputs",
        diagnostics=(
            "bdt_input_zcand_mass",
            "bdt_input_zcand_momentum",
            "offshell_w_assignment_delta",
            "offshell_w_assignment_zwhypothesis",
            "zwchi2_pairing_diagnostic",
        ),
        plots=(
            "Zcand_m",
            "Zcand_p",
            "Hcand_m",
            "recoil_m",
            "deltaZ",
            "Zcand_m_ZWchi2",
            "Zcand_p_ZWchi2",
            "Hcand_m_ZWchi2",
            "recoil_m_ZWchi2",
            "Wstar_m",
            "Whad_m",
            "Whad_p",
            "Whad_m_ZWchi2",
            "Whad_p_ZWchi2",
            "Wlep_m",
            "Wlep_p",
            "abs_Wlep_mW",
            "abs_Whad_mW",
            "deltaW_onShell",
            "deltaW_onShell_ZWchi2",
            "lepW_offshell_like",
            "lepW_onshell_like",
            "hadW_onshell_like",
            "w_topology_category",
            "mW_min",
            "mW_max",
            "chi2_ZWpair",
            "delta_pairing_Zcand_m",
            "delta_pairing_Whad_m",
            "deltaR_Wstar",
            "angle_Wstar_jj",
            "sqrt_d23",
            "sqrt_d34",
            "min_jet_nconst_after_cut5",
            "mean_jet_nconst_after_cut6",
        ),
    ),
)


def copy_if_exists(src: Path, dst: Path, manifest: list[tuple[str, str, str, int, str]]) -> bool:
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    stat = dst.stat()
    manifest.append((dst.parent.name, dst.name, str(src.relative_to(src.parents[1])), stat.st_size, "copied"))
    return True


def copy_plot_stem(base_dir: Path, stage_dir: Path, stem: str, manifest: list[tuple[str, str, str, int, str]]) -> int:
    copied = 0
    for ext in EXTENSIONS:
        src = base_dir / f"{stem}{ext}"
        if copy_if_exists(src, stage_dir / src.name, manifest):
            copied += 1
    for suffix in ("_norm", "_shape"):
        for ext in (".pdf", ".png"):
            src = base_dir / f"{stem}{suffix}{ext}"
            if copy_if_exists(src, stage_dir / src.name, manifest):
                copied += 1
    return copied


def copy_diagnostic(
    base_dir: Path,
    stage_dir: Path,
    name: str,
    manifest: list[tuple[str, str, str, int, str]],
) -> int:
    copied = 0
    for subdir, prefix, suffix in (
        ("cut_diagnostics", "cut_diagnostics__", ""),
        ("cut_diagnostics_normalized", "cut_diagnostics_normalized__", "_norm"),
    ):
        for ext in (".pdf", ".png"):
            src = base_dir / subdir / f"{name}{suffix}{ext}"
            dst = stage_dir / f"{prefix}{name}{suffix}{ext}"
            if copy_if_exists(src, dst, manifest):
                copied += 1
    src = base_dir / "cut_diagnostics_normalized" / f"{name}_tail_fractions.csv"
    dst = stage_dir / f"{name}_tail_fractions.csv"
    if copy_if_exists(src, dst, manifest):
        copied += 1
    return copied


def copy_strength(
    base_dir: Path,
    stage_dir: Path,
    cut_id: str,
    manifest: list[tuple[str, str, str, int, str]],
) -> int:
    copied = 0
    strength_dir = base_dir / "cut_strength_by_cut"
    for ext in (".pdf", ".png", ".csv"):
        src = strength_dir / f"{cut_id}_strength_table{ext}"
        dst = stage_dir / f"cut_strength_before_after{ext}"
        if copy_if_exists(src, dst, manifest):
            copied += 1
    return copied


def copy_overview_strength(base_dir: Path, stage_dir: Path, manifest: list[tuple[str, str, str, int, str]]) -> int:
    copied = 0
    strength_dir = base_dir / "cut_strength_by_cut"
    for name in ("cut_strength_rejection_heatmap", "cut_precision_improvement"):
        for ext in (".pdf", ".png"):
            src = strength_dir / f"{name}{ext}"
            if copy_if_exists(src, stage_dir / src.name, manifest):
                copied += 1
    for name in ("cut_strength_summary.csv",):
        src = strength_dir / name
        if copy_if_exists(src, stage_dir / name, manifest):
            copied += 1
    return copied


def write_readme(out_dir: Path, tag: str) -> None:
    version = version_from_tag(tag)
    lines = [
        f"# Cut-by-stage plots for `{tag}`",
        "",
        f"This directory is an organized copy of already-generated {version} plot outputs.",
        "It does not rerun event selection or modify ROOT files.",
        "",
        "Each cut folder contains:",
        "- the main cut-diagnostic plot, when available;",
        "- normalized counterparts, when available;",
        "- supporting kinematic distributions used to motivate that cut;",
        "- `cut_strength_before_after.*`, showing immediate before/after yields and rejection for that cut.",
        "",
        f"Important {version} convention:",
        "- the nominal cut sequence ends at Cut6 (`min jet Nconst > 8`);",
        "- there are NO hard `Zcand_m` or `Zcand_p` windows: both are BDT inputs",
        "  (established by full-fit window scans, ml/scan_zcand_windows.py);",
        "- `Hcand_m` and `recoil_m` are diagnostic/BDT-shape variables, not hard filters.",
        "",
    ]
    (out_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def write_manifest(out_dir: Path, tag: str, manifest: list[tuple[str, str, str, int, str]]) -> None:
    version = version_from_tag(tag)
    manifest_path = out_dir / f"MANIFEST_{version}_latest.tsv"
    with manifest_path.open("w", encoding="utf-8") as handle:
        handle.write("stage\tfile\tsource\tsize_bytes\tstatus\n")
        for row in sorted(manifest):
            handle.write("\t".join(str(item) for item in row) + "\n")
    # Compatibility alias for scripts/notebooks that expect a generic name.
    shutil.copy2(manifest_path, out_dir / "MANIFEST_latest.tsv")
    shutil.copy2(manifest_path, out_dir / "CUT_STRENGTH_MANIFEST.tsv")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", default=None,
                        help="Output tag; default follows LVQQ_OUTPUT_TAG via ml_config")
    parser.add_argument("--plots-dir", default=None)
    args = parser.parse_args()

    if args.tag is None:
        from ml_config import DEFAULT_PLOTS_DIR, OUTPUT_TAG
        args.tag = OUTPUT_TAG or "current"
        base_dir = Path(args.plots_dir or DEFAULT_PLOTS_DIR)
    else:
        base_dir = Path(args.plots_dir or f"plots_lvqq_{args.tag}")
    if not base_dir.exists():
        raise SystemExit(f"Plots directory does not exist: {base_dir}")

    out_dir = base_dir / "cuts_by_stage"
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest: list[tuple[str, str, str, int, str]] = []
    stage_counts: list[tuple[str, int]] = []
    for stage in STAGES:
        stage_dir = out_dir / stage.folder
        stage_dir.mkdir(parents=True, exist_ok=True)
        copied = 0
        for diagnostic in stage.diagnostics:
            copied += copy_diagnostic(base_dir, stage_dir, diagnostic, manifest)
        for stem in stage.plots:
            copied += copy_plot_stem(base_dir, stage_dir, stem, manifest)
        if stage.strength_cut:
            copied += copy_strength(base_dir, stage_dir, stage.strength_cut, manifest)
        if stage.folder == "cut0_overview":
            copied += copy_overview_strength(base_dir, stage_dir, manifest)
        (stage_dir / "README.md").write_text(f"# {stage.title}\n", encoding="utf-8")
        stage_counts.append((stage.folder, copied))

    write_readme(out_dir, args.tag)
    write_manifest(out_dir, args.tag, manifest)

    print(f"Wrote cut-by-stage folders to: {out_dir}")
    for folder, copied in stage_counts:
        print(f"  {folder}: {copied} files")
    version = version_from_tag(args.tag)
    print(f"Manifest: {out_dir / f'MANIFEST_{version}_latest.tsv'}")


if __name__ == "__main__":
    main()
