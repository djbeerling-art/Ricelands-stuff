#!/bin/bash
# v25 settle with ferrihydrite ageing: 7-yr reference controls from vc_rref_y7f at k_age 2/3/5 yr-1 (+ 20 t/ha/yr at k 3) (g2ch4 1860 unchanged), w 0 (Fe pathway only; controls do not depend on w).
source <(sed -n '1,/^export -f spinset season/p' /home/user/runs/pan/runV.sh | sed 's#statusV#statusFhs#')
export PROD="$(echo $PROD | sed 's/scepter_paddy_v21/scepter_paddy_v25/') --rtsi=2e-3:2.7e-4:0" XRS=,fhage
job(){ k=$1; d=${2:-0}; o=$SCEPTER_OUT/paddy/flood_fhs${k}_${d}st; [ -d $o ] || cp -a $SCEPTER_OUT/paddy/flood_vc_rref_y7f $o
  paddy/multiyear/run_chain.sh fhs${k}_ref_$d 7 $d fhs${k}_${d}st $ST $PROD $P21 --k=$D/k_fh$k.in; }
export -f job
printf '%s\n' '3 0' '3 20' '2 0' '5 0' | xargs -P 4 -I{} bash -c 'job {}'
echo done >> $ST
