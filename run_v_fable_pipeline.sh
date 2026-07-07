#!/bin/bash
# Sequential v_fable pipeline driver (histmaker -> treemaker -> train -> apply
# -> fit -> plots). Each stage writes its own log and the chain stops on the
# first failure. Designed to survive SSH disconnects via nohup:
#
#   cd "/home/submit/jinboz1/work/Z(qq)WW(lvqq)"
#   mkdir -p logs/v_fable
#   nohup ./run_v_fable_pipeline.sh > logs/v_fable/pipeline.log 2>&1 &
#   tail -f logs/v_fable/pipeline.log
#
# Override the tag with:  LVQQ_TAG=my_tag ./run_v_fable_pipeline.sh
set -euo pipefail

cd "$(dirname "$(readlink -f "$0")")"
TAG="${LVQQ_TAG:-v_fable}"
LOGDIR="logs/${TAG}"
mkdir -p "${LOGDIR}"

STAGES=(histmaker treemaker train apply fit plots)

echo "[$(date '+%F %T')] v_fable pipeline starting (tag=${TAG})"
echo "[$(date '+%F %T')] stages: ${STAGES[*]}"

for stage in "${STAGES[@]}"; do
    log="${LOGDIR}/${stage}.log"
    echo "[$(date '+%F %T')] ==> ${stage} (log: ${log})"
    if python3 run_lvqq.py "${stage}" --output-tag "${TAG}" > "${log}" 2>&1; then
        echo "[$(date '+%F %T')] <== ${stage} OK"
    else
        echo "[$(date '+%F %T')] !! ${stage} FAILED — see ${log}" >&2
        exit 1
    fi
done

echo "[$(date '+%F %T')] all stages done."
FIT_JSON="ml/models/xgboost_bdt_${TAG}/fit_results.json"
if [[ -f "${FIT_JSON}" ]]; then
    echo "=== Fit summary (${FIT_JSON}) ==="
    python3 - "$FIT_JSON" <<'EOF'
import json, sys
r = json.load(open(sys.argv[1]))
for key in ("n_signal", "n_background", "mu_hat", "mu_err",
            "relative_uncertainty_pct", "physics_only_rel_uncertainty_pct",
            "score_source", "staterror_mode", "error_method"):
    if key in r:
        print(f"  {key}: {r[key]}")
EOF
fi
echo "Cutflow table: plots_lvqq_${TAG}/cutFlow_cutflow.txt"
