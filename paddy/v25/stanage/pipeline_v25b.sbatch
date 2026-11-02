#!/bin/bash
# v25b production pipeline, one site per array task: fresh 3-yr drained spin-up (--basalt=0) -> control settle to
# convergence (season CH4 emission changing <2 %/yr over two consecutive years; at least 7, at most 12 years) ->
# submit the site's 10-yr chains (chain_v25.sbatch: control 0 t and basalt from the final settled state).
# The reference task also submits the Fig. 6b w-structure chains (w 0 and 0.4, 0/10/20 t) after its main chains.
# krxn_calibrated_v25b.in (fhage 0.1, g2ch4 2280) and w 0.15 throughout. Settle lengths: status/v25b_settle_length.txt.
# Usage: sbatch --array=0-7 pipeline_v25b.sbatch
#SBATCH --job-name=v25bpl
#SBATCH --partition=sheffield
#SBATCH --account=default
#SBATCH --time=24:00:00
#SBATCH --mem=6G
#SBATCH --cpus-per-task=1
#SBATCH --output=logs/%x_%A_%a.out
set -u
cd $HOME/SCEPTER_v25
source stanage_handoff/slurm/modules.sh
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export SCEPTER_OUT=$HOME/fastdata/v25_out/ KEEPALK=1 TILL=0.2 XRS=,fhage
mkdir -p status logs
KRXN=paddy/krxn_calibrated_v25b.in; W=0.15
EXE=scepter_paddy_v25
OM="--omalloc=0.2:0.6:0.1"
SOIL="--ch4 --n --kaol=0.05 --refsoil --gt=0.02 --exe=$EXE --kscale=maf:0.45,fsp:0.25,amsi:30 --n2c=0.03 --n2oy=6.2:1:0.1 --o2inh=2.5e-7 --nstep=13 --q=0.5 --fe3in=0.3 --fe3=0.012 --om=450 $OM"
PROD="--k=$KRXN --phd=14 --pox=0.3:0.9:6:1 --nucl=cc:0.001 --exe=$EXE --kscale=maf:0.45,fsp:0.25,amsi:30 --n2c=0.03 --n2oy=6.2:1:0.1 --o2inh=2.5e-7 --nstep=13 --q=0.5 --fe3in=0.3 --fe3=0.012 --om=450 $OM --rtsi=2e-3:2.7e-4:$W"
P21="--nz=25 --ztot=0.5 --pan=0.2:0.24:0.1:0.8:1:0.1:0.21:-1:0.3"
SITES=(ref refq1 rf189 irr061 irr043 rf184 irr092 rf151)
CIDX=("0-2" "3-5" "6-7" "8-9" "10-11" "12-13" "14-15" "16-17")   # chain_v25.sbatch array indices per site
SITE=${SITES[$SLURM_ARRAY_TASK_ID]}
case $SITE in
  ref)   ARGS=""; WM="--kaq=0.74" ;;
  refq1) ARGS="--q=1.0"; WM="--kaq=0.74" ;;
  *) ARGS=$(python3 -c "
import csv
for r in csv.DictReader(open('stanage_handoff/arch/archetypes_v22.csv')):
    if r['arch']=='$SITE': print(r['args'])")
     [ -n "$ARGS" ] || { echo "no args for $SITE"; exit 2; }
     case $SITE in rf*) WM="--awd --kaq=0.96";; *) WM="--kaq=0.74";; esac ;;
esac
st=status/v25b_$SITE.txt
echo "site $SITE: $ARGS $WM"
grep -q "^v25bs_$SITE rc 0" $st 2>/dev/null || {
  python3 paddy/run_flooded_column.py v25bs_$SITE fe2o2,amo2o 3 --fallow --basalt=0 $SOIL $P21 $ARGS > /dev/null 2>&1
  echo "v25bs_$SITE rc $?" >> $st; }
emis(){ python3 - "$1" <<'PY'
import sys, numpy as np
f = sys.argv[1] + '/flx/flx_gas-pch4.txt'
h = open(f).readline().split(); d = np.loadtxt(f, skiprows=1, ndmin=2)
dt = np.diff(np.concatenate([[0.0], d[:, 0]]))
c = lambda k: float((d[:, h.index(k)]*dt).sum()) if k in h else 0.0
print(c('dif') + c('ch4eb') + c('ch4pl'))
PY
}
Y=0; ok=0
for n in 7 8 9 10 11 12; do
  # run_chain skips years already done and continues from the last fallow
  paddy/multiyear/run_chain.sh v25bc_$SITE $n 0 v25bs_$SITE $st $PROD $P21 $ARGS $WM || exit 1
  Y=$n
  e0=$(emis $SCEPTER_OUT/paddy/flood_v25bc_${SITE}_y$((n-2))s); e1=$(emis $SCEPTER_OUT/paddy/flood_v25bc_${SITE}_y$((n-1))s); e2=$(emis $SCEPTER_OUT/paddy/flood_v25bc_${SITE}_y${n}s)
  echo "$SITE y$n emission $e0 $e1 $e2"
  python3 -c "import sys; a,b,c=$e0,$e1,$e2; sys.exit(0 if abs(b/a-1)<0.02 and abs(c/b-1)<0.02 else 1)" && { ok=1; break; }
done
echo "$SITE settle_years $Y converged $ok" >> status/v25b_settle_length.txt
E=ALL,KRXN=$KRXN,W=$W,SY=$Y,SPRE=v25bc,CPRE=v25bb
j=$(sbatch --parsable --array=${CIDX[$SLURM_ARRAY_TASK_ID]} --export=$E chain_v25.sbatch)
echo "$SITE chains $j"
if [ $SITE = ref ]; then
  for w in 0 0.4; do
    sbatch --array=0-2 --dependency=afterany:$j --export=ALL,KRXN=$KRXN,W=$w,SY=$Y,SPRE=v25bc,CPRE=v25bb,TAG=w${w/./} chain_v25.sbatch
  done
fi
