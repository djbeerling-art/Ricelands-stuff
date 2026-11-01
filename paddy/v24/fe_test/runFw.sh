#!/bin/bash
# v25fw floodwater solute discharge test: reference site, 1 yr from v23 y10 states, kaq 0 vs 0.37 (w 0.2), kaq 0.37 m/yr (~100 mm/season); compare r23_ref_* y8-y9.
source <(sed -n '1,/^export -f spinset season/p' /home/user/runs/pan/runV.sh | sed 's#statusV#statusFw#')
export PROD="$(echo $PROD | sed 's/scepter_paddy_v21/scepter_paddy_v25fw/') --rtsi=2e-3:2.7e-4:0.2"
job(){ d=$1; k=$2; a=$(grep "^ref|" $D/archR.txt | cut -d'|' -f2); n=fw${k/./p}_ref_$d
  o=$SCEPTER_OUT/paddy/flood_fwst_${k/./p}_$d; [ -d $o ] || cp -a $SCEPTER_OUT/paddy/flood_r23_ref_${d}_y10f $o
  paddy/multiyear/run_chain.sh $n 1 $d fwst_${k/./p}_$d $ST $PROD $P21 $a $([ "$k" != 0 ] && echo --kaq=$k); }
export -f job
printf '%s\n' '20 0.37' '20 0' | xargs -P 4 -I{} bash -c 'job {}'
echo done >> $ST
