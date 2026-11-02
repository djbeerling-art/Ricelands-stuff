#!/bin/bash
# v23 rerun of the reference-site 10-yr chains (w 0.2) at 0/10/20 t/ha/yr, same settled state and options as v22 (r10_ref_0, r22_ref_10/20).
source <(sed -n '1,/^export -f spinset season/p' /home/user/runs/pan/runV.sh | sed 's#statusV#statusR23#')
export PROD="$(echo $PROD | sed 's/scepter_paddy_v21/scepter_paddy_v23/') --rtsi=2e-3:2.7e-4:0.2"
job(){ d=$1; a=$(grep "^ref|" $D/archR.txt | cut -d'|' -f2); n=r23_ref_$d
  o=$SCEPTER_OUT/paddy/flood_rz23r_$d; [ -d $o ] || cp -a $SCEPTER_OUT/paddy/flood_vc_rref_y7f $o
  paddy/multiyear/run_chain.sh $n 10 $d rz23r_$d $ST $PROD $P21 $a; }
export -f job
printf '%s\n' 20 10 0 | xargs -P 3 -I{} bash -c 'job {}'
echo "r23 done" >> $ST
