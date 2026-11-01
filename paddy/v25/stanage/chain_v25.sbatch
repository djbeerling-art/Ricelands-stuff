#!/bin/bash
# v25 10-yr chains, control-matched: control (0 t) and basalt chains all start from the same vmax-1860 y7f settled
# state and all use the recalibrated krxn file, so the year-1 transient from the calibration change is shared.
# One (site, dose) per array task; each chain tills its own copy of the settled state.
# Usage: sbatch --array=0-17 --export=ALL,KRXN=paddy/<file>.in,W=<w>[,TAG=<tag>] chain_v25.sbatch
#SBATCH --job-name=v25ch
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
: ${KRXN:?set KRXN} ${W:?set W}
EXE=scepter_paddy_v25
OM="--omalloc=0.2:0.6:0.1"
PROD="--k=$KRXN --phd=14 --pox=0.3:0.9:6:1 --nucl=cc:0.001 --exe=$EXE --kscale=maf:0.45,fsp:0.25,amsi:30 --n2c=0.03 --n2oy=6.2:1:0.1 --o2inh=2.5e-7 --nstep=13 --q=0.5 --fe3in=0.3 --fe3=0.012 --om=450 $OM --rtsi=2e-3:2.7e-4:$W"
P21="--nz=25 --ztot=0.5 --pan=0.2:0.24:0.1:0.8:1:0.1:0.21:-1:0.3"
JOBS=(ref:0 ref:10 ref:20 refq1:0 refq1:10 refq1:20 rf189:0 rf189:20 irr061:0 irr061:20 irr043:0 irr043:20
      rf184:0 rf184:20 irr092:0 irr092:20 rf151:0 rf151:20)
SITE=${JOBS[$SLURM_ARRAY_TASK_ID]%:*}; DOSE=${JOBS[$SLURM_ARRAY_TASK_ID]#*:}
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
# SPRE/CPRE (environment) set the settle and chain name prefixes (default v25c/v25b); TAG (e.g. w0) keeps test chains apart from the main set; EXTRA adds driver options (e.g. --fe3in=0.6)
S=${SPRE:-v25c}_${SITE}_y${SY:-7}f; T=${CPRE:-v25b}${TAG:-}_${SITE}_$DOSE
[ -d $SCEPTER_OUT/paddy/flood_$S ] || { echo "missing settled state $S"; exit 3; }
[ -d $SCEPTER_OUT/paddy/flood_${T}_st ] || cp -r $SCEPTER_OUT/paddy/flood_$S $SCEPTER_OUT/paddy/flood_${T}_st
echo "$T: krxn $KRXN, w $W, args $ARGS $WM"
paddy/multiyear/run_chain.sh $T 10 $DOSE ${T}_st status/${CPRE:-v25b}${TAG:-}_$SITE.txt $PROD $P21 $ARGS $WM ${EXTRA:-}
echo "chain $T done rc $?"
