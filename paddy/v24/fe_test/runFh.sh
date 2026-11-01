#!/bin/bash
# v25 ferrihydrite ageing (fhage) first look: k_age 1/3/10 yr-1, K_si 0.3 mM; reference 0 vs 20 t, w 0, one season.
source <(sed -n '1,/^export -f spinset season/p' /home/user/runs/pan/runV.sh | sed 's#statusV#statusFh#')
export PROD="$(echo $PROD | sed -e 's/scepter_paddy_v21/scepter_paddy_v25/' -e 's/--phd=14//') --rtsi=2e-3:2.7e-4:0"
F=vc_rref_y7f; PS=--psd=data/psdrain_renforth_p80-100um.in; RSA=$RS,fhage
rm -f $D/jobsFh.txt
for k in 1 3 10; do
 echo "fh${k}_ref_0 113 $F $RSA --nfert=120 --basalt=0 --phd=14 $P21 --k=$D/k_fh$k.in" >> $D/jobsFh.txt
 echo "fh${k}_ref_20 113 $F $RSA --nfert=120 --basalt=20 $PS --phd=14 $P21 --k=$D/k_fh$k.in" >> $D/jobsFh.txt
done
xargs -P 4 -L 1 bash -c 'season "$@"' _ < $D/jobsFh.txt
for n in $(cut -d' ' -f1 $D/jobsFh.txt); do $D/../../pd/paddy/prune_run.sh season $SCEPTER_OUT/paddy/flood_$n; done
echo done >> $ST
