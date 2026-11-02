#!/bin/bash
# Extend a v25 control settle until CH4 emission changes <2 %/yr over two consecutive years (at most 5 extra years,
# i.e. to year 12), with the same settings as settle_v25.sbatch; then submit that site's control and basalt chains
# (chain_v25.sbatch, SY = final settle year) from the final state. Records the settle length in status/settle_length.txt.
# Usage: sbatch --array=0-1 --export=ALL,KRXN=paddy/krxn_calibrated_v25_cal.in,W=0.15 settle_ext.sbatch
#SBATCH --job-name=v25ext
#SBATCH --partition=sheffield
#SBATCH --account=default
#SBATCH --time=12:00:00
#SBATCH --mem=6G
#SBATCH --cpus-per-task=1
#SBATCH --output=logs/%x_%A_%a.out
set -u
cd $HOME/SCEPTER_v25
source stanage_handoff/slurm/modules.sh
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export SCEPTER_OUT=$HOME/fastdata/v25_out/ KEEPALK=1 TILL=0.2 XRS=,fhage
EXE=scepter_paddy_v25
OM="--omalloc=0.2:0.6:0.1"
PROD="--k=paddy/krxn_calibrated_v25.in --phd=14 --pox=0.3:0.9:6:1 --nucl=cc:0.001 --exe=$EXE --kscale=maf:0.45,fsp:0.25,amsi:30 --n2c=0.03 --n2oy=6.2:1:0.1 --o2inh=2.5e-7 --nstep=13 --q=0.5 --fe3in=0.3 --fe3=0.012 --om=450 $OM --rtsi=2e-3:2.7e-4:0.2"
P21="--nz=25 --ztot=0.5 --pan=0.2:0.24:0.1:0.8:1:0.1:0.21:-1:0.3"
SITES=(irr043 irr092); IDX=(10 14)   # chain_v25.sbatch array indices of each site's 0 t task (basalt = +1)
SITE=${SITES[$SLURM_ARRAY_TASK_ID]}
ARGS=$(python3 -c "
import csv
for r in csv.DictReader(open('stanage_handoff/arch/archetypes_v22.csv')):
    if r['arch']=='$SITE': print(r['args'])")
WM="--kaq=0.74"
st=status/v25_$SITE.txt
emis(){ python3 - "$1" <<'PY'
import sys, numpy as np
f = sys.argv[1] + '/flx/flx_gas-pch4.txt'
h = open(f).readline().split(); d = np.loadtxt(f, skiprows=1, ndmin=2)
dt = np.diff(np.concatenate([[0.0], d[:, 0]]))
c = lambda k: float((d[:, h.index(k)]*dt).sum()) if k in h else 0.0
print(c('dif') + c('ch4eb') + c('ch4pl'))
PY
}
Y=7; ok=0
for n in 8 9 10 11 12; do
  paddy/multiyear/run_chain.sh v25c_$SITE $n 0 v25s_$SITE $st $PROD $P21 $ARGS $WM || exit 1
  Y=$n
  e0=$(emis $SCEPTER_OUT/paddy/flood_v25c_${SITE}_y$((n-2))s); e1=$(emis $SCEPTER_OUT/paddy/flood_v25c_${SITE}_y$((n-1))s); e2=$(emis $SCEPTER_OUT/paddy/flood_v25c_${SITE}_y${n}s)
  echo "$SITE y$n emission $e0 $e1 $e2"
  python3 -c "import sys; a,b,c=$e0,$e1,$e2; sys.exit(0 if abs(b/a-1)<0.02 and abs(c/b-1)<0.02 else 1)" && { ok=1; break; }
done
echo "$SITE settle_years $Y converged $ok" >> status/settle_length.txt
sbatch --array=${IDX[$SLURM_ARRAY_TASK_ID]}-$((${IDX[$SLURM_ARRAY_TASK_ID]}+1)) --export=ALL,KRXN=$KRXN,W=$W,SY=$Y chain_v25.sbatch
