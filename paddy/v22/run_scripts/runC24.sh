#!/bin/bash
# v24 Si root-barrier alternative (ch4si): reference site, 10 yr from vc_rref_y7f, 0 and 20 t/ha/yr
source <(sed -n '1,/^export -f spinset season/p' /home/user/runs/pan/runV.sh | sed 's#statusV#statusC24#')
BASE="$(echo $PROD | sed 's/scepter_paddy_v21/scepter_paddy_v24/')"
export BASE
job(){ tag=$1; d=$2; extra=${3//|/ }; a=$(grep "^ref|" $D/archR.txt | cut -d'|' -f2); n=c24${tag}_$d
  o=$SCEPTER_OUT/paddy/flood_cz${tag}_$d; [ -d $o ] || cp -a $SCEPTER_OUT/paddy/flood_vc_rref_y7f $o
  paddy/multiyear/run_chain.sh $n 10 $d cz${tag}_$d $ST $BASE $extra $P21 $a; }
export -f job
cat <<J | xargs -P ${NP:-4} -L1 bash -c 'job $0 $1 "$2"'
cond 20 --rtsi=2e-3:2.7e-4:0|--ch4si=2e-3:2.7e-4:0.5:0
barr 20 --rtsi=2e-3:2.7e-4:0|--ch4si=2e-3:2.7e-4:0.5:0.5
tong 20 --rtsi=2e-3:2.7e-4:0.2|--ch4si=2e-3:2.7e-4:-0.2:0
cond 0 --rtsi=2e-3:2.7e-4:0|--ch4si=2e-3:2.7e-4:0.5:0
barr 0 --rtsi=2e-3:2.7e-4:0|--ch4si=2e-3:2.7e-4:0.5:0.5
tong 0 --rtsi=2e-3:2.7e-4:0.2|--ch4si=2e-3:2.7e-4:-0.2:0
J
echo "c24 done" >> $ST
