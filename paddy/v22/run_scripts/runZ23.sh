#!/bin/bash
# Carbon-closure fix (v23 = v22 + g2 oxalate/acetate C returned to CO2): rerun the Fig 3 verification runs; plus v22chk (fresh build of v22 source) at f0 for binary reproducibility.
source <(sed -n '1,/^export -f spinset season/p' /home/user/runs/pan/runV.sh | sed 's#statusV#statusZ23#')
export NOPRUNE=1
B="$(echo $PROD | sed 's/scepter_paddy_v21/scepter_paddy_v22/') --rtsi=2e-3:2.7e-4:0.2"
export P23="$(echo $B | sed 's/scepter_paddy_v22/scepter_paddy_v23/')" P22C="$(echo $B | sed 's/scepter_paddy_v22/scepter_paddy_v22chk/')"
job(){ set -- $1; v=$1; w=$2; d=$3; a=$(grep "^irr061|" $D/archR.txt | cut -d'|' -f2); [ $w = a ] && a="--awd $a"; n=r${v}v_irr061_$w$d
  o=$SCEPTER_OUT/paddy/flood_rz${v}_$w$d; [ -d $o ] || cp -a $SCEPTER_OUT/paddy/flood_vc_rirr061_y7f $o
  P=$P23; [ $v = 22c ] && P=$P22C
  paddy/multiyear/run_chain.sh $n 1 $d rz${v}_$w$d $ST $P $P21 $a; }
export -f job
printf '%s\n' "23 f 0" "23 f 20" "23 a 0" "23 a 20" "22c f 0" | xargs -P 4 -I{} bash -c 'job "{}"'
echo "z23 done" >> $ST
