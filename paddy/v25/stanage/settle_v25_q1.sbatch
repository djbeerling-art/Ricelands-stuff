#!/bin/bash
# v25 control states, one site per array task: 3-yr drained spin-up (--basalt=0) -> 7-yr settle (no rock).
# Reference site: 0.5 m column with the plough pan, continuous flooding. Archetypes: v22 archetype soil/climate args;
# irrigated --kaq=0.74 (200 mm floodwater discharge per season), rainfed --awd --kaq=0.96.
# Options as paddy/v25/run_scripts/runV25.sh (runD.sh SOIL/PROD with the v25 executable and krxn_calibrated_v25.in,
# --rtsi=2e-3:2.7e-4:0.2, XRS=,fhage). Basalt chains are not started here (w to be refit from Gong).
# Percolation sensitivity: reference site with --q=1.0 m/yr (season and fallow; production uses 0.5).
# Usage: sbatch settle_v25_q1.sbatch
#SBATCH --job-name=v25q1
#SBATCH --partition=sheffield
#SBATCH --account=default
#SBATCH --time=16:00:00
#SBATCH --mem=6G
#SBATCH --cpus-per-task=1
#SBATCH --output=logs/%x_%j.out
set -u
cd $HOME/SCEPTER_v25
source stanage_handoff/slurm/modules.sh
# single-threaded OpenBLAS: with several threads the basalt seasons stalled at the first time step (siAltFe, 1 Nov)
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export SCEPTER_OUT=$HOME/fastdata/v25_out/ KEEPALK=1 TILL=0.2 XRS=,fhage
mkdir -p $SCEPTER_OUT status
EXE=scepter_paddy_v25
OM="--omalloc=0.2:0.6:0.1"
SOIL="--ch4 --n --kaol=0.05 --refsoil --gt=0.02 --exe=$EXE --kscale=maf:0.45,fsp:0.25,amsi:30 --n2c=0.03 --n2oy=6.2:1:0.1 --o2inh=2.5e-7 --nstep=13 --q=0.5 --fe3in=0.3 --fe3=0.012 --om=450 $OM"
PROD="--k=paddy/krxn_calibrated_v25.in --phd=14 --pox=0.3:0.9:6:1 --nucl=cc:0.001 --exe=$EXE --kscale=maf:0.45,fsp:0.25,amsi:30 --n2c=0.03 --n2oy=6.2:1:0.1 --o2inh=2.5e-7 --nstep=13 --q=0.5 --fe3in=0.3 --fe3=0.012 --om=450 $OM --rtsi=2e-3:2.7e-4:0.2"
P21="--nz=25 --ztot=0.5 --pan=0.2:0.24:0.1:0.8:1:0.1:0.21:-1:0.3"
SITES=(ref rf189 irr061 irr043 rf184 irr092 rf151)
SITE=ref; Q="--q=1.0"
if [ $SITE = ref ]; then ARGS=""; WM="--kaq=0.74"
else
  ARGS=$(python3 -c "
import csv
for r in csv.DictReader(open('stanage_handoff/arch/archetypes_v22.csv')):
    if r['arch']=='$SITE': print(r['args'])")
  [ -n "$ARGS" ] || { echo "no args for $SITE"; exit 2; }
  case $SITE in rf*) WM="--awd --kaq=0.96";; *) WM="--kaq=0.74";; esac
fi
st=status/v25_refq1.txt
echo "site $SITE args: $ARGS $WM"
grep -q "^v25s_refq1 rc 0" $st 2>/dev/null || {
  python3 paddy/run_flooded_column.py v25s_refq1 fe2o2,amo2o 3 --fallow --basalt=0 $SOIL $P21 $ARGS $Q > /dev/null 2>&1
  echo "v25s_refq1 rc $?" >> $st; }
# the 7-yr settle keeps its y7f restart state (run_chain prunes earlier years only)
paddy/multiyear/run_chain.sh v25c_refq1 7 0 v25s_refq1 $st $PROD $P21 $ARGS $WM $Q || exit 1
echo "settle done for $SITE"
