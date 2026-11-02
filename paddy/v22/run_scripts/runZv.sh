#!/bin/bash
# Fig 3 verification (v22): unpruned one-year runs at irr061 (flooded and AWD, 0 and 20 t) for PHREEQC re-speciation and element budgets.
source <(sed -n '1,/^export -f spinset season/p' /home/user/runs/pan/runV.sh | sed 's#statusV#statusZv#')
export PROD="$(echo $PROD | sed 's/scepter_paddy_v21/scepter_paddy_v22/') --rtsi=2e-3:2.7e-4:0.2" NOPRUNE=1
job(){ set -- $1; w=$1; d=$2; a=$(grep "^irr061|" $D/archR.txt | cut -d'|' -f2); [ $w = a ] && a="--awd $a"; n=r22v_irr061_$w$d
  o=$SCEPTER_OUT/paddy/flood_rzv_$w$d; [ -d $o ] || cp -a $SCEPTER_OUT/paddy/flood_vc_rirr061_y7f $o
  paddy/multiyear/run_chain.sh $n 1 $d rzv_$w$d $ST $PROD $P21 $a; }
export -f job
printf '%s\n' "f 0" "f 20" "a 0" "a 20" | xargs -P 2 -I{} bash -c 'job "{}"'
echo "zv done" >> $ST
