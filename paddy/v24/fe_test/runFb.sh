#!/bin/bash
# v25 basalt response with steady Fe settings (k_age 0.3, g2gt 60), w 0, 1 yr from fg0p3g60_ref_0_y7f: 0 vs 20 t/ha
source <(sed -n '1,/^export -f spinset season/p' /home/user/runs/pan/runV.sh | sed 's#statusV#statusFb#')
export PROD="$(echo $PROD | sed 's/scepter_paddy_v21/scepter_paddy_v25fw/') --rtsi=2e-3:2.7e-4:0" XRS=,fhage
job(){ d=$1; o=$SCEPTER_OUT/paddy/flood_fbst_$d; [ -d $o ] || cp -a $SCEPTER_OUT/paddy/flood_fg0p3g60_ref_0_y7f $o
  paddy/multiyear/run_chain.sh fb_ref_$d 2 $d fbst_$d $ST $PROD $P21 --k=$D/k_fg_0.3_60.in; }
export -f job
printf '%s\n' 20 0 | xargs -P 2 -I{} bash -c 'job {}'
echo done >> $ST
