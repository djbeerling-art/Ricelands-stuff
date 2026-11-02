#!/bin/bash
# v25 Fe steady-state test: 7-yr reference controls from vc_rref_y7f, k_age 0.3/1 x goethite reduction vmax 30/60 (w 0)
source <(sed -n '1,/^export -f spinset season/p' /home/user/runs/pan/runV.sh | sed 's#statusV#statusFg#')
export PROD="$(echo $PROD | sed 's/scepter_paddy_v21/scepter_paddy_v25/') --rtsi=2e-3:2.7e-4:0" XRS=,fhage
job(){ k=$1; g=$2; t=fg${k/./p}g${g}; o=$SCEPTER_OUT/paddy/flood_${t}st; [ -d $o ] || cp -a $SCEPTER_OUT/paddy/flood_vc_rref_y7f $o
  paddy/multiyear/run_chain.sh ${t}_ref_0 7 0 ${t}st $ST $PROD $P21 --k=$D/k_fg_${k}_${g}.in; }
export -f job
printf '%s\n' '0.3 30' '0.3 60' '1 30' '1 60' | xargs -P 4 -I{} bash -c 'job {}'
echo done >> $ST
