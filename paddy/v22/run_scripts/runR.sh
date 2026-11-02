#!/bin/bash
# 10-yr runs on the new baseline (David 29 Oct: 10 yr, not 20): reference site (0/10/20 t/ha/yr) and the six area-weighted
# archetypes (0/20 t/ha/yr). All: pan + basal O2 0.21 (0.5 m), OM split, paddy-age Fe, g2ch4 1860 (k_cal.in), adopted Si
# feedback 2e-3:2.7e-4:0.2. Soil conditioning by the 29 Oct site rule: dry-soil pH >= 6.8 -> 0.5 wt% calcite + 2 meq/L;
# else irrigation alkalinity irralk = interp(pH; 5.0/6.0/6.2/6.5 -> 0/1/4/10). Rainfed = AWD; irrigated = flooded + pre-harvest drain.
# Each: fresh spin-up + 7-yr settle (vc_<tag>), copied per dose (till edits restarts in place), then a 10-yr chain r10_<tag>_<dose>.
source <(sed -n '1,/^export -f spinset season/p' /home/user/runs/pan/runV.sh | sed 's#statusV#statusR#')
export PROD="$PROD --rtsi=2e-3:2.7e-4:0.2"
ia(){ python3 -c "import numpy as np; print(round(float(np.interp($1,[5.0,6.0,6.2,6.5],[0,1,4,10])),2))"; }
cat > $D/archR.txt <<A
ref|
rf189|--awd --rock=glb09 --irralk=$(ia 6.34) --cec=17.5 --temp=29.8 --om=533 --fe3=0.0125
irr061|--rock=glb04 --irralk=$(ia 6.04) --cec=16.9 --temp=28.7 --om=506 --fe3=0.0112
irr043|--rock=glb03 --irralk=$(ia 5.69) --cec=21.6 --temp=28.5 --om=871 --fe3=0.0147
rf184|--awd --rock=glb09 --irralk=10 --soilcc=0.005 --cec=33.5 --temp=31.6 --om=338 --fe3=0.0156
irr092|--rock=glb09 --irralk=$(ia 5.85) --cec=20.0 --temp=21.8 --om=880 --fe3=0.0124
rf151|--awd --rock=glb03 --irralk=$(ia 5.27) --cec=17.3 --temp=25.8 --om=900 --fe3=0.0133
A
settle(){ IFS='|' read t a <<< "$1"; spinset r$t $P21 $a; }
pair(){ IFS='|' read t a <<< "$1"; for d in $2; do echo "$t|$a|$d"; done; }
chain(){ IFS='|' read t a d <<< "$1"; o=$SCEPTER_OUT/paddy/flood_rx_${t}_$d
  [ -d $o ] || cp -a $SCEPTER_OUT/paddy/flood_vc_r${t}_y7f $o
  paddy/multiyear/run_chain.sh r10_${t}_$d 10 $d rx_${t}_$d $ST $PROD $P21 $a; }
export -f settle chain
cat $D/archR.txt | xargs -P 4 -I{} bash -c 'settle "{}"'
{ pair "$(sed -n 1p $D/archR.txt)" "0 10 20"; sed -n '2,$p' $D/archR.txt | while read l; do pair "$l" "0 20"; done; } > $D/chainsR.txt
cat $D/chainsR.txt | xargs -P 4 -I{} bash -c 'chain "{}"'
echo done >> $ST
