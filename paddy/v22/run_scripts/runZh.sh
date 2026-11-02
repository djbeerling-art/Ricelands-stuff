#!/bin/bash
# GMD figure set (30 Oct), frozen v22: stronger Si feedback (w = 0.4) reference 10-yr chains at 0/10/20 t (Fig 6b). Waits for runZf.
until grep -q "fig done" /home/user/runs/pan/statusZf 2>/dev/null; do sleep 60; done
source <(sed -n '1,/^export -f spinset season/p' /home/user/runs/pan/runV.sh | sed 's#statusV#statusZh#')
export PROD="$(echo $PROD | sed 's/scepter_paddy_v21/scepter_paddy_v22/') --rtsi=2e-3:2.7e-4:0.2"
job(){ set -- $1; k=$1; t=$2; d=$3; a=$(grep "^$t|" $D/archR.txt | cut -d'|' -f2)
  if [ $k = w4 ]; then n=r22w4_${t}_$d; ny=10; x=--rtsi=2e-3:2.7e-4:0.4; else n=r22y1_${t}_$d; ny=1; x=; fi
  o=$SCEPTER_OUT/paddy/flood_rz${k}_${t}_$d; [ -d $o ] || cp -a $SCEPTER_OUT/paddy/flood_vc_r${t}_y7f $o
  paddy/multiyear/run_chain.sh $n $ny $d rz${k}_${t}_$d $ST $PROD $P21 $a $x; }
export -f job
printf "%s\n" "w4 ref 20" "w4 ref 10" "w4 ref 0" > $D/jobsZh.txt
xargs -P 2 -I{} bash -c 'job "{}"' < $D/jobsZh.txt
echo "zh done" >> $ST
