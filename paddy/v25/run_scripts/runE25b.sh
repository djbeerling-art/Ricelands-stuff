#!/bin/bash
# v25b final evaluation set (w 0.15): Park, Uchibayashi, Wang 2024 wollastonite (reported <75 um -> P80 50 um), Gong w0/w0.4 brackets.
# v25b w refit (1 Nov 2026): fresh v25b spin-up + 7-yr settle (r03 pot column; p21 pan column under slag-site AWD),
# then Gong 36 t/ha and Wang 2014 slag 2/4/8 t/ha seasons. Slag uses the reported granular 1-7 mm PSD (psdrain_wangslag.in);
# a 100 um slag set at w 0.15 is kept to show the PSD effect. Resumable via statusW25b.
source <(sed -n '/^cd /,/^export -f cfg/p' /home/user/runs/pan/runD.sh | sed 's#statusD#statusW25b#')
D=/home/user/runs/pan; export D
K=/home/user/pd/paddy/krxn_calibrated_v25b.in
export PROD=$(echo $PROD | sed -e 's/scepter_paddy_v20/scepter_paddy_v25/' -e "s#--k=[^ ]*#--k=$K#")
export SOIL=$(echo $SOIL | sed 's/scepter_paddy_v20/scepter_paddy_v25/')
export RS=fhage,fe2o2,g2fe3,g2gr,g2so4,g2ch4,ch4o2,fe2gr,ch4pl,ch4eb,fe2fs,fesox,amo2o,g2n21,g2n2p,n2opl,g2gt,rtco2,g2o2,nh4up,rtoxy,groxy,siup,sidox
export C="--ch4 --n --kaol=0.05 --refsoil --gt=0.02 --nucl=cc:0.001"
export P21="--nz=25 --ztot=0.5 --pan=0.2:0.24:0.1:0.8:1:0.1:0.21:-1:0.3"
export R03="--nz=15 --ztot=0.3"
export XRS=,fhage
export PROD="$PROD --rtsi=2e-3:2.7e-4:0.15"
spinset(){ s=$1; shift; grep -q "^b5s_$s rc 0" $ST || { python3 paddy/run_flooded_column.py b5s_$s fe2o2,amo2o 3 --fallow --basalt=0 $SOIL "$@" > $D/b5s_$s.log 2>&1
    echo "b5s_$s rc $?" >> $ST; paddy/prune_run.sh spin $SCEPTER_OUT/paddy/flood_b5s_$s; }
  paddy/multiyear/run_chain.sh b5c_$s 7 0 b5s_$s $ST $PROD "$@"; }
season(){ t=$1; days=$2; prev=$3; rx=$4; shift 4; grep -q "^$t rc 0" $ST && return
  python3 paddy/run_flooded_column.py $t $rx $(python3 -c "print(round($days/365,4))") --season --rstrt=$prev $C $PROD "$@" > $D/$t.log 2>&1
  rc=$?; awk 'END{exit !($1+0>=0.99*'$days'/365)}' $SCEPTER_OUT/paddy/flood_$t/flx/flx_gas-pch4.txt 2>/dev/null || rc=98
  echo "$t rc $rc" >> $ST; }
export -f spinset season
export WLS="--cec=10 --temp=20.5 --q=1.1"
printf '%s\n' "wls $P21 $WLS --awd --kaq=0.96" | xargs -P 1 -I{} bash -c 'spinset {}'
grep -q "^b5c_wls_y7f rc 0" $ST || { echo settle-incomplete; exit 1; }
PROD=$(echo $PROD | sed 's/--phd=14//'); export PROD
R=b5c_p21_y7f; G=b5c_r03_y7f; W=b5c_wls_y7f
P50="--psd=data/psdrain_renforth_p80-50um.in"
RB=fhage,fe2o2,g2fe3,g2gr,g2so4,g2ch4,ch4o2,fe2gr,ch4eb,fe2fs,fesox,amo2o,g2n21,g2n2p,g2gt,g2o2,groxy,sidox
cat > $D/jobsE25b.txt <<J
e5wang_0 153 $W $RS --nfert=120 --basalt=0 --awd --phd=14 $P21 $WLS --kaq=0.96
e5wang_5 153 $W $RS --nfert=120 --rock=WangWls --basalt=5 $P50 --awd --phd=14 $P21 $WLS --kaq=0.96
e5uchi_0 99 $G $RS --nfert=120 --basalt=0 $R03
e5uchi_100 99 $G $RS --nfert=120 --rock=Akita --basalt=100 --psd=data/psdrain_akita.in $R03
e5park_0 100 $G $RB --basalt=0 --q=0.0001 $R03
e5park_390 100 $G $RB --rock=JB1b --basalt=390 --basfe3=0.03 --zmix=0.3 --q=0.0001 $R03
e5park_780 100 $G $RB --rock=JB1b --basalt=780 --basfe3=0.03 --zmix=0.3 --q=0.0001 $R03
e5gong_36w0 131 $G $RS --nfert=240 --rock=GongXuyi --basalt=36 $P50 --awd $R03 --rtsi=2e-3:2.7e-4:0
e5gong_36w0.4 131 $G $RS --nfert=240 --rock=GongXuyi --basalt=36 $P50 --awd $R03 --rtsi=2e-3:2.7e-4:0.4
J
xargs -P 4 -L 1 bash -c 'season "$@"' _ < $D/jobsE25b.txt
for r in $(cut -d' ' -f1 $D/jobsE25b.txt); do paddy/prune_run.sh season $SCEPTER_OUT/paddy/flood_$r 2>/dev/null; done
echo done
