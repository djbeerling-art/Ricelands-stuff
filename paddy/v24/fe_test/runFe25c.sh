#!/bin/bash
# Diagnosis: does basalt raise CH4 production through O2 sinks (green-rust/Fe2+ oxidation) relieving O2 inhibition?
source <(sed -n '1,/^export -f spinset season/p' /home/user/runs/pan/runV.sh | sed 's#statusV#statusFe25#')
export PROD="$(echo $PROD | sed -e 's/scepter_paddy_v21/scepter_paddy_v23/' -e 's/--phd=14//') --rtsi=2e-3:2.7e-4:0"
F=vc_rref_y7f; PS=--psd=data/psdrain_renforth_p80-100um.in; RSG=$(echo $RS | sed 's/,groxy//')
cat > $D/jobsFe25c.txt <<J
fe_ref_0k1 113 $F $RS --nfert=120 --basalt=0 --phd=14 $P21 --o2inh=1e-6
fe_ref_20k1 113 $F $RS --nfert=120 --basalt=20 $PS --phd=14 $P21 --o2inh=1e-6
fe_ref_0k5 113 $F $RS --nfert=120 --basalt=0 --phd=14 $P21 --o2inh=5e-6
fe_ref_20k5 113 $F $RS --nfert=120 --basalt=20 $PS --phd=14 $P21 --o2inh=5e-6
J
xargs -P 4 -L 1 bash -c 'season "$@"' _ < $D/jobsFe25c.txt
echo donec >> $ST
