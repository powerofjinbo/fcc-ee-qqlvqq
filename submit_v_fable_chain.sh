#!/bin/bash
# Submit the full v_fable pipeline to Slurm as a dependency chain:
# each stage starts automatically when the previous one succeeds
# (afterok), and downstream jobs are killed if a stage fails.
#
#   cd "/home/submit/jinboz1/work/Z(qq)WW(lvqq)"
#   ./submit_v_fable_chain.sh
#   squeue -u $USER          # watch progress
#   tail -f logs/slurm_v_fable/vfable_1_histmaker-<jobid>.out
set -euo pipefail

cd "$(dirname "$(readlink -f "$0")")"
TAG="${LVQQ_TAG:-v_fable}"
PARTITION="${LVQQ_PARTITION:-submit}"
BIG_CPUS=32
BIG_MEM="48G"
LOGDIR="logs/slurm_v_fable"
mkdir -p "${LOGDIR}"

submit() {
    local name="$1" walltime="$2" cpus="$3" mem="$4" dep="$5" target="$6"
    local depargs=()
    if [[ -n "${dep}" ]]; then
        depargs=(--dependency="afterok:${dep}" --kill-on-invalid-dep=yes)
    fi
    local jobid
    jobid=$(sbatch --parsable \
        --job-name="${name}" \
        --partition="${PARTITION}" \
        --cpus-per-task="${cpus}" \
        --mem="${mem}" \
        --time="${walltime}" \
        "${depargs[@]}" \
        --chdir="$PWD" \
        --output="${LOGDIR}/%x-%j.out" \
        --error="${LOGDIR}/%x-%j.err" \
        --wrap "env LVQQ_CPUS=${cpus} python3 run_lvqq.py ${target} --output-tag ${TAG}")
    # --parsable may return "jobid;cluster" on multi-cluster setups.
    echo "${jobid%%;*}"
}

j1=$(submit "vfable_1_histmaker" "1-00:00:00" "${BIG_CPUS}" "${BIG_MEM}" ""    "histmaker")
j2=$(submit "vfable_2_treemaker" "2-00:00:00" "${BIG_CPUS}" "${BIG_MEM}" "$j1" "treemaker")
j3=$(submit "vfable_3_train"     "1-00:00:00" "${BIG_CPUS}" "${BIG_MEM}" "$j2" "train")
j4=$(submit "vfable_4_apply"     "04:00:00"   8             "16G"        "$j3" "apply")
j5=$(submit "vfable_5_fit"       "08:00:00"   4             "16G"        "$j4" "fit")
j6=$(submit "vfable_6_plots"     "08:00:00"   4             "16G"        "$j5" "plots")

echo "Submitted v_fable chain (tag=${TAG}):"
echo "  1 histmaker : ${j1}"
echo "  2 treemaker : ${j2} (afterok:${j1})"
echo "  3 train     : ${j3} (afterok:${j2})"
echo "  4 apply     : ${j4} (afterok:${j3})"
echo "  5 fit       : ${j5} (afterok:${j4})"
echo "  6 plots     : ${j6} (afterok:${j5})"
echo "Logs: ${LOGDIR}/"
echo "Results when done: ml/models/xgboost_bdt_${TAG}/fit_results.json"
