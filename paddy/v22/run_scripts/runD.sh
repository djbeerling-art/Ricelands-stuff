#!/bin/bash
# pan test D (v20): OM split into plough-layer residue (60%, uniform 0-0.2 m) and root C (40%, exp(-z/0.1)),
# normalised to the column; urea and Fe(III) resupply to the plough layer. 12-yr settle chains from fresh spin-ups,
# same constants (krxn v16), to test whether the 0.3 vs 0.5 m difference and the pan effect survive equal C inputs.
cd /home/user/pd
export SCEPTER_OUT=/home/user/runs/out/ KEEPALK=1 TILL=0.2
OM="--omalloc=0.2:0.6:0.1"
export SOIL="--ch4 --n --kaol=0.05 --refsoil --gt=0.02 --exe=scepter_paddy_v20 --kscale=maf:0.45,fsp:0.25,amsi:30 --n2c=0.03 --n2oy=6.2:1:0.1 --o2inh=2.5e-7 --nstep=13 --q=0.5 --fe3in=0.3 --fe3=0.012 --om=450 $OM"
export PROD="--k=paddy/krxn_calibrated_v16.in --phd=14 --rtsi=5e-4:2.7e-4:0.5 --pox=0.3:0.9:6:1 --nucl=cc:0.001 --exe=scepter_paddy_v20 --kscale=maf:0.45,fsp:0.25,amsi:30 --n2c=0.03 --n2oy=6.2:1:0.1 --o2inh=2.5e-7 --nstep=13 --q=0.5 --fe3in=0.3 --fe3=0.012 --om=450 $OM"
export ST=/home/user/runs/pan/statusD
cfg(){ case $1 in r03) echo "--nz=15 --ztot=0.3";; n05) echo "--nz=25 --ztot=0.5 --pan=0:0:1:1:0:1:0.21:-1:0.3";;
  p00) echo "--nz=25 --ztot=0.5 --pan=0.2:0.24:0.1:0.8:1:0.1:0:-1:0.3";; p21) echo "--nz=25 --ztot=0.5 --pan=0.2:0.24:0.1:0.8:1:0.1:0.21:-1:0.3";; esac; }
export -f cfg
run(){ c=$1
  grep -q "^ds_$c rc 0" $ST 2>/dev/null || { python3 paddy/run_flooded_column.py ds_$c fe2o2,amo2o 3 --fallow --basalt=0 $SOIL $(cfg $c) > /home/user/runs/pan/ds_$c.log 2>&1
    echo "ds_$c rc $?" >> $ST; paddy/prune_run.sh spin $SCEPTER_OUT/paddy/flood_ds_$c; }
  paddy/multiyear/run_chain.sh dc_${c}_0 12 0 ds_$c $ST $PROD $(cfg $c); }
export -f run
printf "%s\n" r03 n05 p00 p21 | xargs -P 4 -I{} bash -c 'run {}'
echo done >> $ST
