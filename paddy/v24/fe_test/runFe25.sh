#!/bin/bash
# Reactive rock-Fe(III) test, Si root feedback OFF (w 0): can the geochemical Fe pathway alone reproduce observed
# silicate CH4 decreases? One season, v23 exe, from the settled validation states. Extra ferrihydrite via --basfe3.
source <(sed -n '1,/^export -f spinset season/p' /home/user/runs/pan/runV.sh | sed 's#statusV#statusFe25#')
export PROD="$(echo $PROD | sed -e 's/scepter_paddy_v21/scepter_paddy_v23/' -e 's/--phd=14//') --rtsi=2e-3:2.7e-4:0"
R=dc7_p21_0_y7f; G=vc_r03_y7f; F=vc_rref_y7f; PS=--psd=data/psdrain_renforth_p80-100um.in
cat > $D/jobsFe25.txt <<J
fe_ref_0 113 $F $RS --nfert=120 --basalt=0 --phd=14 $P21
fe_ref_20 113 $F $RS --nfert=120 --basalt=20 $PS --phd=14 $P21
fe_ref_20f6 113 $F $RS --nfert=120 --basalt=20 --basfe3=0.06 $PS --phd=14 $P21
fe_ref_20f12 113 $F $RS --nfert=120 --basalt=20 --basfe3=0.12 $PS --phd=14 $P21
fe_ref_20f25 113 $F $RS --nfert=120 --basalt=20 --basfe3=0.25 $PS --phd=14 $P21
fe_gong_0 131 $G $RS --nfert=240 --basalt=0 --awd $R03
fe_gong_36 131 $G $RS --nfert=240 --rock=GongXuyi --basalt=36 $PS --awd $R03
fe_gong_36f6 131 $G $RS --nfert=240 --rock=GongXuyi --basalt=36 --basfe3=0.06 $PS --awd $R03
fe_gong_36f12 131 $G $RS --nfert=240 --rock=GongXuyi --basalt=36 --basfe3=0.12 $PS --awd $R03
fe_slag_0 113 $R $RS --nfert=120 --basalt=0 --awd --phd=14 $P21
fe_slag_4 113 $R $RS --nfert=120 --rock=WangSlag --basalt=4 $PS --awd --phd=14 $P21
fe_slag_4f15 113 $R $RS --nfert=120 --rock=WangSlag --basalt=4 --basfe3=0.15 $PS --awd --phd=14 $P21
fe_bat_0 100 $G $RB --basalt=0 --q=0.0001 $R03
fe_bat_20 100 $G $RB --basalt=20 $PS --zmix=0.3 --q=0.0001 $R03
fe_bat_20f12 100 $G $RB --basalt=20 --basfe3=0.12 $PS --zmix=0.3 --q=0.0001 $R03
J
xargs -P 4 -L 1 bash -c 'season "$@"' _ < $D/jobsFe25.txt
echo done >> $ST
