#!/bin/bash
# Calcareous-site variants: Gong and Wang 2024 with 0.5 wt% soil calcite (settled porewater pH ~6.55, the flooded-CO2 ceiling).
source <(sed -n '1,/^export -f spinset season/p' /home/user/runs/pan/runV.sh | sed 's#statusV#statusW#')
CC="--soilcc=0.005"
spinset wlsc05 $P21 $WLS --awd $CC
PROD=$(echo $PROD | sed 's/--phd=14//'); export PROD
G=vc_r03c05_y7f; W=vc_wlsc05_y7f
cat > $D/jobsW.txt <<J
vwangc_0 153 $W $RS --nfert=120 --basalt=0 --awd --phd=14 $P21 $WLS $CC
vwangc_5 153 $W $RS --nfert=120 --rock=WangWls --basalt=5 --psd=data/psdrain_renforth_p80-100um.in --awd --phd=14 $P21 $WLS $CC
vgongc_0 131 $G $RS --nfert=240 --basalt=0 --awd $R03 $CC
vgongc_36 131 $G $RS --nfert=240 --rock=GongXuyi --basalt=36 --psd=data/psdrain_renforth_p80-100um.in --awd $R03 $CC
vgongc_36w0 131 $G $RS --nfert=240 --rock=GongXuyi --basalt=36 --psd=data/psdrain_renforth_p80-100um.in --awd $R03 $CC --rtsi=5e-4:2.7e-4:0
J
xargs -P 4 -L 1 bash -c 'season "$@"' _ < $D/jobsW.txt
echo done >> $ST
