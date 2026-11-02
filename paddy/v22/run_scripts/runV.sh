#!/bin/bash
# Test sites on the new baseline (v21, OM split, Fe as paddy-age state, g2ch4 1860 = k_cal.in).
# Field sites (Wang 2014 slag, Wang 2024 wollastonite) with the pan + basal O2 0.21; pots and batch (Gong, Uchibayashi,
# Park) in the 0.3 m column without a pan. Each from a fresh spin-up + 7-yr settle, then one site season.
source <(sed -n '/^cd /,/^export -f cfg/p' /home/user/runs/pan/runD.sh | sed 's#statusD#statusV#')
D=/home/user/runs/pan; export D
export PROD=$(echo $PROD | sed -e 's/scepter_paddy_v20/scepter_paddy_v21/' -e "s#--k=[^ ]*#--k=$D/k_cal.in#")
export SOIL=$(echo $SOIL | sed 's/scepter_paddy_v20/scepter_paddy_v21/')
export RS=fe2o2,g2fe3,g2gr,g2so4,g2ch4,ch4o2,fe2gr,ch4pl,ch4eb,fe2fs,fesox,amo2o,g2n21,g2n2p,n2opl,g2gt,rtco2,g2o2,nh4up,rtoxy,groxy,siup,sidox
export RB=fe2o2,g2fe3,g2gr,g2so4,g2ch4,ch4o2,fe2gr,ch4eb,fe2fs,fesox,amo2o,g2n21,g2n2p,g2gt,g2o2,groxy,sidox   # batch: no plant terms
export C="--ch4 --n --kaol=0.05 --refsoil --gt=0.02 --nucl=cc:0.001"
export WLS="--cec=10 --temp=20.5 --q=1.1"            # Wang 2024: silt loam (10% clay), Liaoning, ~1.1 m/yr percolation
export P21="--nz=25 --ztot=0.5 --pan=0.2:0.24:0.1:0.8:1:0.1:0.21:-1:0.3"
export R03="--nz=15 --ztot=0.3"
spinset(){ s=$1; shift; grep -q "^vs_$s rc 0" $ST || { python3 paddy/run_flooded_column.py vs_$s fe2o2,amo2o 3 --fallow --basalt=0 $SOIL "$@" > $D/vs_$s.log 2>&1
    echo "vs_$s rc $?" >> $ST; paddy/prune_run.sh spin $SCEPTER_OUT/paddy/flood_vs_$s; }
  paddy/multiyear/run_chain.sh vc_$s 7 0 vs_$s $ST $PROD "$@"; }
season(){ t=$1; days=$2; prev=$3; rx=$4; shift 4; grep -q "^$t rc 0" $ST && return
  python3 paddy/run_flooded_column.py $t $rx $(python3 -c "print(round($days/365,4))") --season --rstrt=$prev $C $PROD "$@" > $D/$t.log 2>&1
  echo "$t rc $?" >> $ST; }
export -f spinset season
# phase 1: settled states (reference soil without pan, Wang 2024 site soil with pan); pan reference state exists (dc7_p21_0_y7f)
printf '%s\n' "r03 $R03" "wls $P21 $WLS --awd" | xargs -P 2 -I{} bash -c 'spinset {}'
NO="--phd=0"; PROD=$(echo $PROD | sed 's/--phd=14//'); export PROD   # pots and batch: no pre-harvest drain unless set
R=dc7_p21_0_y7f; G=vc_r03_y7f; W=vc_wls_y7f
cat > $D/jobsV.txt <<J
vslag_0 113 $R $RS --nfert=120 --basalt=0 --awd --phd=14 $P21
vslag_2 113 $R $RS --nfert=120 --rock=WangSlag --basalt=2 --psd=data/psdrain_renforth_p80-100um.in --awd --phd=14 $P21
vslag_4 113 $R $RS --nfert=120 --rock=WangSlag --basalt=4 --psd=data/psdrain_renforth_p80-100um.in --awd --phd=14 $P21
vslag_8 113 $R $RS --nfert=120 --rock=WangSlag --basalt=8 --psd=data/psdrain_renforth_p80-100um.in --awd --phd=14 $P21
vwang_0 153 $W $RS --nfert=120 --basalt=0 --awd --phd=14 $P21 $WLS
vwang_5 153 $W $RS --nfert=120 --rock=WangWls --basalt=5 --psd=data/psdrain_renforth_p80-100um.in --awd --phd=14 $P21 $WLS
vgong_0 131 $G $RS --nfert=240 --basalt=0 --awd $R03
vgong_36 131 $G $RS --nfert=240 --rock=GongXuyi --basalt=36 --psd=data/psdrain_renforth_p80-100um.in --awd $R03
vgong_36w0 131 $G $RS --nfert=240 --rock=GongXuyi --basalt=36 --psd=data/psdrain_renforth_p80-100um.in --awd $R03 --rtsi=5e-4:2.7e-4:0
vuchi_0 99 $G $RS --nfert=120 --basalt=0 $R03
vuchi_100 99 $G $RS --nfert=120 --rock=Akita --basalt=100 --psd=data/psdrain_akita.in $R03
vpark_0 100 $G $RB --basalt=0 --q=0.0001 $R03
vpark_390 100 $G $RB --rock=JB1b --basalt=390 --basfe3=0.03 --zmix=0.3 --q=0.0001 $R03
vpark_780 100 $G $RB --rock=JB1b --basalt=780 --basfe3=0.03 --zmix=0.3 --q=0.0001 $R03
J
xargs -P 4 -L 1 bash -c 'season "$@"' _ < $D/jobsV.txt
echo done >> $ST
