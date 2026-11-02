#!/bin/bash
# Build/protocol check: irr061, full v25b protocol (3-yr spin-up, settle to convergence) then 1 yr at 0 and 20 t/ha,
# compared with the GMD v25b reference (set v25bb in paddy/v25/results/ghg_phase_rows.csv). Submit from the repo root after build.sh:  sbatch stanage_handoff/slurm/check_irr061.sbatch
# Expected ~2-3 h on one core. Result: tail logs/check_irr061_<jobid>.out (ends PASS or lists failures).
#SBATCH --job-name=chk25
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=04:00:00
#SBATCH --partition=sheffield
#SBATCH --account=default
#SBATCH --output=logs/check_irr061_%j.out
source stanage_handoff/slurm/modules.sh
source stanage_handoff/v25_options.env
export SCEPTER_OUT=${SCEPTER_OUT:-/mnt/parscratch/users/$USER/scepter_check/}
mkdir -p $SCEPTER_OUT/paddy status_check
t0=$(date +%s)
ARGS=$(python3 -c "
import csv
for r in csv.DictReader(open('stanage_handoff/arch/archetypes_v22.csv')):
    if r['arch']=='irr061': print(r['args'])")
bash stanage_handoff/run_arch_v22.sh irr061 "$ARGS" "0 20" 1 status_check/irr061.txt
echo "rc $? after $(( ($(date +%s)-t0)/60 )) min"; cat status_check/irr061.txt
python3 stanage_handoff/compare_ref.py $SCEPTER_OUT/paddy
