#!/bin/bash
# Diagnosis: does basalt raise CH4 production through O2 sinks (green-rust/Fe2+ oxidation) relieving O2 inhibition?
source <(sed -n '1,/^export -f spinset season/p' /home/user/runs/pan/runV.sh | sed 's#statusV#statusFe25#')
export PROD="$(echo $PROD | sed -e 's/scepter_paddy_v21/scepter_paddy_v23/' -e 's/--phd=14//') --rtsi=2e-3:2.7e-4:0"
F=vc_rref_y7f; PS=--psd=data/psdrain_renforth_p80-100um.in; RSG=$(echo $RS | sed 's/,groxy//')
cat > $D/jobsFe25b.txt <<J
fe_ref_0i 113 $F $RS --nfert=120 --basalt=0 --phd=14 $P21 --o2inh=1
fe_ref_20i 113 $F $RS --nfert=120 --basalt=20 $PS --phd=14 $P21 --o2inh=1
fe_ref_0g 113 $F $RSG --nfert=120 --basalt=0 --phd=14 $P21
fe_ref_20g 113 $F $RSG --nfert=120 --basalt=20 $PS --phd=14 $P21
J
xargs -P 4 -L 1 bash -c 'season "$@"' _ < $D/jobsFe25b.txt
echo doneb >> $ST
