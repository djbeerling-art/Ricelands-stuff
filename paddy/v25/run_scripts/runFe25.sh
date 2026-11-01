#!/bin/bash
# v25 rerun (ferrihydrite ageing 0.3/yr, g2gt 60, floodwater discharge --kaq: continuous flooding 0.28, AWD/intermittent 0.96 m/yr; pots/batch closed). Was: test sites on the baseline (v21, OM split, Fe as paddy-age state, g2ch4 1860 = k_cal.in).
# Field sites (Wang 2014 slag, Wang 2024 wollastonite) with the pan + basal O2 0.21; pots and batch (Gong, Uchibayashi,
# Park) in the 0.3 m column without a pan. Each from a fresh spin-up + 7-yr settle, then one site season.
source <(sed -n '/^cd /,/^export -f cfg/p' /home/user/runs/pan/runD.sh | sed 's#statusD#statusFe25#')
D=/home/user/runs/pan; export D
export PROD=$(echo $PROD | sed -e 's/scepter_paddy_v20/scepter_paddy_v25/' -e "s#--k=[^ ]*#--k=/home/user/pd/paddy/krxn_calibrated_v25.in#")
export SOIL=$(echo $SOIL | sed 's/scepter_paddy_v20/scepter_paddy_v25/')
export RS=fhage,fe2o2,g2fe3,g2gr,g2so4,g2ch4,ch4o2,fe2gr,ch4pl,ch4eb,fe2fs,fesox,amo2o,g2n21,g2n2p,n2opl,g2gt,rtco2,g2o2,nh4up,rtoxy,groxy,siup,sidox
export RB=fhage,fe2o2,g2fe3,g2gr,g2so4,g2ch4,ch4o2,fe2gr,ch4eb,fe2fs,fesox,amo2o,g2n21,g2n2p,g2gt,g2o2,groxy,sidox   # batch: no plant terms
export C="--ch4 --n --kaol=0.05 --refsoil --gt=0.02 --nucl=cc:0.001"
export WLS="--cec=10 --temp=20.5 --q=1.1"            # Wang 2024: silt loam (10% clay), Liaoning, ~1.1 m/yr percolation
export P21="--nz=25 --ztot=0.5 --pan=0.2:0.24:0.1:0.8:1:0.1:0.21:-1:0.3"
export R03="--nz=15 --ztot=0.3"
spinset(){ s=$1; shift; grep -q "^v5s_$s rc 0" $ST || { python3 paddy/run_flooded_column.py v5s_$s fe2o2,amo2o 3 --fallow --basalt=0 $SOIL "$@" > $D/v5s_$s.log 2>&1
    echo "v5s_$s rc $?" >> $ST; paddy/prune_run.sh spin $SCEPTER_OUT/paddy/flood_vs_$s; }
  paddy/multiyear/run_chain.sh v5c_$s 7 0 v5s_$s $ST $PROD "$@"; }
season(){ t=$1; days=$2; prev=$3; rx=$4; shift 4; grep -q "^$t rc 0" $ST && return
  python3 paddy/run_flooded_column.py $t $rx $(python3 -c "print(round($days/365,4))") --season --rstrt=$prev $C $PROD "$@" > $D/$t.log 2>&1
  echo "$t rc $?" >> $ST; }
export XRS=,fhage
export PROD="$PROD --rtsi=2e-3:2.7e-4:0.2"
export -f spinset season
# phase 1: settled states (reference soil without pan, Wang 2024 site soil with pan); pan reference state exists (dc7_p21_0_y7f)
K=/home/user/pd/paddy/krxn_calibrated_v25_cal.in
sed 's/^fhage 0.3 3e-4/fhage 0.1 3e-4/' $K > $D/k25_age01.in
cp $K $D/k25_age03.in
export PROD=$(echo $PROD | sed "s#--rtsi=2e-3:2.7e-4:0.2#--rtsi=2e-3:2.7e-4:0.15#")
job(){ t=$1; k=$2; fe=$3; paddy/multiyear/run_chain.sh fe25_$t 8 0 v5c_p21_y7f $ST $(echo $PROD | sed "s#--k=[^ ]*#--k=$D/$k#") $P21 --kaq=0.74 --fe3in=$fe; }
export -f job
printf '%s\n' "a01f03 k25_age01.in 0.3" "a03f06 k25_age03.in 0.6" "a01f06 k25_age01.in 0.6" "a03f09 k25_age03.in 0.9" | xargs -P 4 -L 1 bash -c 'job $0 $1 $2'
echo done
