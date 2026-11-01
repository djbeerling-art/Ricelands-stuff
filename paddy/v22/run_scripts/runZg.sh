#!/bin/bash
# GMD figure set (30 Oct), frozen v22. Waits for runZf. One-year full-output runs: reference control (Fig 5 dynamics),
# irr061 flooded 0 and 20 t (Fig 3 re-speciation / mass balance); 10-yr Si-feedback-off (w = 0) reference chains at 0/10/20 t (Fig 8).
until grep -q "fig done" /home/user/runs/pan/statusZf 2>/dev/null; do sleep 60; done
source <(sed -n '1,/^export -f spinset season/p' /home/user/runs/pan/runV.sh | sed 's#statusV#statusZg#')
export PROD="$(echo $PROD | sed 's/scepter_paddy_v21/scepter_paddy_v22/') --rtsi=2e-3:2.7e-4:0.2"
job(){ set -- $1; k=$1; t=$2; d=$3; a=$(grep "^$t|" $D/archR.txt | cut -d'|' -f2)
  if [ $k = w0 ]; then n=r22w0_${t}_$d; ny=10; x=--rtsi=2e-3:2.7e-4:0; else n=r22y1_${t}_$d; ny=1; x=; fi
  o=$SCEPTER_OUT/paddy/flood_rz${k}_${t}_$d; [ -d $o ] || cp -a $SCEPTER_OUT/paddy/flood_vc_r${t}_y7f $o
  paddy/multiyear/run_chain.sh $n $ny $d rz${k}_${t}_$d $ST $PROD $P21 $a $x; }
export -f job
printf '%s\n' "w0 ref 20" "w0 ref 10" "w0 ref 0" "y1 ref 0" "y1 irr061 0" "y1 irr061 20" > $D/jobsZg.txt
xargs -P 4 -I{} bash -c 'job "{}"' < $D/jobsZg.txt
echo "zg done" >> $ST
