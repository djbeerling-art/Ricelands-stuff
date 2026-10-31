#!/bin/bash
# Packed version of arch_array.sbatch: each array task runs PACK archetypes side by side, one per core.
# Why: Stanage's normal QOS allows only 50 running jobs per user (each array task is a job), so one archetype per
# task caps us at 50 archetypes at a time. With 12 cores per task, 50 tasks cover 600 archetypes in one wave.
# Task K runs CSV rows (K-1)*PACK+1 .. K*PACK, where PACK = --cpus-per-task. Submit from the repo root:
#   n=$(($(wc -l < CSV)-1)); P=12
#   sbatch --cpus-per-task=$P --array=1-$(( (n+P-1)/P )) stanage_handoff/slurm/arch_pack.sbatch CSV
# Overrides (DOSES, YEARS, STATUS_DIR, SCEPTER_OUT) only via --export=ALL,... as for arch_array.sbatch.
# Results are identical to arch_array.sbatch (same run_arch_v22.sh per archetype; resumes if resubmitted).
# Future cases: add BASE_OUT=<baseline SCEPTER_OUT> (and optionally RESETTLE=3) to --export to start from the baseline's
# settled soil instead of the full spin-up + settle (see run_arch_v22.sh).
# Per-archetype stdout/stderr go to $STATUS_DIR/<arch>.log; the task log lists each archetype's exit code.
#SBATCH --job-name=rice23p
#SBATCH --cpus-per-task=12
#SBATCH --mem-per-cpu=2G
#SBATCH --time=12:00:00
#SBATCH --partition=sheffield
#SBATCH --account=default
#SBATCH --output=logs/rice23p_%A_%a.out
source stanage_handoff/slurm/modules.sh
# SCEPTER is serial: keep OpenBLAS/OpenMP to one thread per archetype
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
source stanage_handoff/v22_options.env
export SCEPTER_OUT=${SCEPTER_OUT:-/mnt/parscratch/users/$USER/scepter/}
export STATUS_DIR=${STATUS_DIR:-status} DOSES=${DOSES:-0 10 20} YEARS=${YEARS:-10}
mkdir -p $SCEPTER_OUT/paddy $STATUS_DIR
P=${SLURM_CPUS_PER_TASK:-1}
LIST=$STATUS_DIR/pack_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}.list
python3 - "$1" $(( (SLURM_ARRAY_TASK_ID-1)*P )) $P > $LIST <<'PY'
import csv, sys
rows = list(csv.DictReader(open(sys.argv[1])))
s, p = int(sys.argv[2]), int(sys.argv[3])
for r in rows[s:s+p]:
    print(r['arch'] + '|' + r['args'] + (' --awd' if r['regime'] == 'rf' else ''))
PY
run_one() {
    IFS='|' read a args <<< "$1"
    bash stanage_handoff/run_arch_v22.sh $a "$args" "$DOSES" $YEARS $STATUS_DIR/$a.txt > $STATUS_DIR/$a.log 2>&1
    echo "$a rc=$? $(date +%T)"
}
export -f run_one
echo "task $SLURM_ARRAY_TASK_ID on $(hostname): $(wc -l < $LIST) archetypes, $P cores, start $(date +%T)"
tr '\n' '\0' < $LIST | xargs -0 -P $P -I{} bash -c 'run_one "$1"' _ {}
