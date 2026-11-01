#!/bin/bash
# Frozen executable scepter_paddy_v22 (rock placed in 0-zmix only; commit 162913a), K_Si 2 mM, w 0.2, g2ch4 1860.
# Basalt runs redone after the rock-placement fix; controls are unaffected (no rock) and reused (r10_ref_0).
# Order: reference 10/20 t chains, Wang 2014 (flooded, granular slag) and Wang 2024 field seasons, then the six
# archetype chains (control + 20 t). Pool of 4.
source <(sed -n '1,/^export -f spinset season/p' /home/user/runs/pan/runV.sh | sed 's#statusV#statusZ#')
export PROD="$(echo $PROD | sed 's/scepter_paddy_v21/scepter_paddy_v22/') --rtsi=2e-3:2.7e-4:0.2"
job(){ set -- $1; if [ $1 = chain ]; then t=$2; d=$3; a=$(grep "^$t|" $D/archR.txt | cut -d'|' -f2)
    o=$SCEPTER_OUT/paddy/flood_rz_${t}_$d; [ -d $o ] || cp -a $SCEPTER_OUT/paddy/flood_vc_r${t}_y7f $o
    paddy/multiyear/run_chain.sh r22_${t}_$d 10 $d rz_${t}_$d $ST $PROD $P21 $a
  else shift; P2=$(echo $PROD | sed 's/--phd=14//'); PROD=$P2 season "$@"; fi; }
export -f job
W14="vc_p21i10_y7f $RS --nfert=120 --phd=14 $P21 --irralk=10"
W24="vc_wlsc05_y7f $RS --nfert=120 --awd --phd=14 $P21 $WLS --soilcc=0.005"
SL="--rock=WangSlag --psd=data/psdrain_wangslag.in"; WL="--rock=WangWls --psd=data/psdrain_renforth_p80-100um.in"
{ echo "chain ref 10"; echo "chain ref 20"
  echo "s z14_0 113 $W14 --basalt=0"; for d in 2 4 8; do echo "s z14_$d 113 $W14 $SL --basalt=$d"; done
  echo "s z24_0 153 $W24 --basalt=0"; echo "s z24_5 153 $W24 $WL --basalt=5"
  for t in rf189 irr061 irr043 rf184 irr092 rf151; do echo "chain $t 0"; echo "chain $t 20"; done; } > $D/jobsZ.txt
xargs -P 4 -I{} bash -c 'job "{}"' < $D/jobsZ.txt
echo done >> $ST
