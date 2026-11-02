#!/bin/bash
# Wang 2014 slag as run in the field (continuous flooding, final drain 2 wk before harvest; slag granular 1-7 mm), for the
# production/oxidation diagnostic: Si feedback w 0.2 vs 0 (geochemistry only), granular vs fine (80-100 um) slag PSD.
source <(sed -n '1,/^export -f spinset season/p' /home/user/runs/pan/runV.sh | sed 's#statusV#statusWg#')
PROD=$(echo $PROD | sed 's/--phd=14//'); export PROD
R=vc_p21i10_y7f; > $D/jobsWg.txt
for w in 0.2 0; do t=${w/./}
  echo "wf${t}_0 113 $R $RS --nfert=120 --basalt=0 --phd=14 $P21 --irralk=10 --rtsi=2e-3:2.7e-4:$w" >> $D/jobsWg.txt
  for d in 2 4 8; do
    echo "wf${t}g_$d 113 $R $RS --nfert=120 --rock=WangSlag --basalt=$d --psd=data/psdrain_wangslag.in --phd=14 $P21 --irralk=10 --rtsi=2e-3:2.7e-4:$w" >> $D/jobsWg.txt
    echo "wf${t}f_$d 113 $R $RS --nfert=120 --rock=WangSlag --basalt=$d --psd=data/psdrain_renforth_p80-100um.in --phd=14 $P21 --irralk=10 --rtsi=2e-3:2.7e-4:$w" >> $D/jobsWg.txt
  done; done
xargs -P 2 -L 1 bash -c 'season "$@"' _ < $D/jobsWg.txt
echo done >> $ST
