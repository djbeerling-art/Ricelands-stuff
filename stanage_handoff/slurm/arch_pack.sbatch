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
# SCEPTER's initial adsorption/CEC solve fails for a narrow, non-monotonic set of irrigation alkalinities, at spin-up or
# at a later restart (status rc 97/98). An archetype that fails that way is moved aside to $SCEPTER_OUT/failed/ and rerun
# from scratch with --irralk scaled by the next factor in ARCH_NUDGE; the factor used is in <status>.args and the log.
# Node-local runs (LOCALRUN=1, the default): each archetype runs in its own directory on the node's local disk
# ($TMPDIR), since ~600 concurrent runs writing many small files to Lustre made each run ~3x slower. Its existing run
# directories are copied in from $SCEPTER_OUT (resume), and the (pruned) directories are copied back with rsync every
# SYNCMIN minutes (default 20) and at the end; the status file is copied after the directories, so the status on scratch
# never lists a step whose directory is not there yet. A job killed at its time limit loses at most SYNCMIN minutes.
# LOCALRUN=0 runs directly on $SCEPTER_OUT as before.
sync_out() {   # <local SCEPTER_OUT> <arch> <status>: directories of this archetype only (others untouched)
    rsync -a --delete --include="flood_*_$2/***" --include="flood_*_$2_*/***" --exclude='*' $1/paddy/ $SCEPTER_OUT/paddy/ || return 1
    for x in .txt .args _spin.log; do [ ! -f $1/st$x ] || cp $1/st$x "${3%.txt}$x" || return 1; done
}
attempt() {    # <arch> <args> <nudge> <status>
    local a=$1 L
    if [ "${LOCALRUN:-1}" = 0 ] || ! command -v rsync > /dev/null; then
        NUDGE=$3 bash stanage_handoff/run_arch_v22.sh $a "$2" "$DOSES" $YEARS $4 >> $STATUS_DIR/$a.log 2>&1; return
    fi
    L=${TMPDIR:-/tmp}/scl_${SLURM_JOB_ID:-$$}_$a; rm -rf $L; mkdir -p $L/paddy
    find $SCEPTER_OUT/paddy -maxdepth 1 \( -name "flood_*_$a" -o -name "flood_*_${a}_*" \) -exec cp -a -t $L/paddy/ {} + ||
        { echo "$a: copy to local disk failed, running on scratch" >> $STATUS_DIR/$a.log; rm -rf $L
          NUDGE=$3 bash stanage_handoff/run_arch_v22.sh $a "$2" "$DOSES" $YEARS $4 >> $STATUS_DIR/$a.log 2>&1; return; }
    for x in .txt .args _spin.log; do [ -f "${4%.txt}$x" ] && cp "${4%.txt}$x" $L/st$x; done
    ( while sleep $(( ${SYNCMIN:-20}*60 )); do sync_out $L $a $4; done ) & local sp=$!
    SCEPTER_OUT=$L/ NUDGE=$3 bash stanage_handoff/run_arch_v22.sh $a "$2" "$DOSES" $YEARS $L/st.txt >> $STATUS_DIR/$a.log 2>&1
    local rc=$?
    pkill -P $sp 2>/dev/null; kill $sp 2>/dev/null; wait $sp 2>/dev/null
    sync_out $L $a $4 && rm -rf $L
    return $rc
}
export -f sync_out attempt
run_one() {
    IFS='|' read a args <<< "$1"
    local ST=$STATUS_DIR/$a.txt rc
    for f in ${ARCH_NUDGE:-1 0.95 1.05 0.9 1.1}; do
        if [ -s "${ST%.txt}.args" ] && ! grep -q "irralk x$f)" "$ST" 2>/dev/null; then continue; fi   # resume: skip used factors
        attempt $a "$args" $f $ST
        rc=$?
        [ $rc = 0 ] && break
        grep -q " rc 9[78]" "$ST" 2>/dev/null || break       # not the numerical failure (e.g. time limit): resume later
        d=$SCEPTER_OUT/failed/${a}_x$f; mkdir -p $d
        mv $SCEPTER_OUT/paddy/flood_*_${a}_* $SCEPTER_OUT/paddy/flood_gs22_$a $SCEPTER_OUT/paddy/flood_bs22_$a $d/ 2>/dev/null
        mv "$ST" "${ST%.txt}.args" "${ST%.txt}_spin.log" $d/ 2>/dev/null
        echo "$a failed at irralk x$f, retrying" >> $STATUS_DIR/$a.log
    done
    echo "$a rc=$rc $(date +%T)"
}
export -f run_one
echo "task $SLURM_ARRAY_TASK_ID on $(hostname): $(wc -l < $LIST) archetypes, $P cores, start $(date +%T)"
tr '\n' '\0' < $LIST | xargs -0 -P $P -I{} bash -c 'run_one "$1"' _ {}
