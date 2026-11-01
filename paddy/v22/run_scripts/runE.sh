#!/bin/bash
# pan test E (v20, OM split): (1) one-off g2ch4 calibration on the pan + basal O2 0.21 set-up at the y8 state
# (1 yr from the 7-yr settle dc7_p21_0_y7f; OM converged, Fe as a slow paddy-age state), after 7-yr settles of all set-ups (restart states kept at y7);
# (2) basalt pairs 0 vs 20 t/ha/yr, 4 yr, from each set-up's y7 state with the calibrated constant.
source <(sed -n '/^cd /,/^export -f cfg/p' /home/user/runs/pan/runD.sh | sed 's#statusD#statusE#')
cfg(){ case $1 in n05) echo "--nz=25 --ztot=0.5 --pan=0:0:1:1:0:1:0.21:-1:0.3";; p00|p02|p05|p21) o=$(python3 -c "print(int('${1#p}')/100)");
  echo "--nz=25 --ztot=0.5 --pan=0.2:0.24:0.1:0.8:1:0.1:$o:-1:0.3";; esac; }
export -f cfg
D=/home/user/runs/pan; export D
job(){ case $1 in
  cal*) v=${1#cal}; paddy/multiyear/run_chain.sh ek_$v 1 0 dc7_p21_0_y7f $ST $(echo $PROD | sed "s#--k=[^ ]*#--k=$D/k_g2ch4_$v.in#") $(cfg p21);;
  set*) c=${1#set}; grep -q "^ds_$c rc 0" $ST || { python3 paddy/run_flooded_column.py ds_$c fe2o2,amo2o 3 --fallow --basalt=0 $SOIL $(cfg $c) > $D/ds_$c.log 2>&1
          echo "ds_$c rc $?" >> $ST; paddy/prune_run.sh spin $SCEPTER_OUT/paddy/flood_ds_$c; }
        paddy/multiyear/run_chain.sh dc7_${c}_0 7 0 ds_$c $ST $PROD $(cfg $c);;
  pair*) x=${1#pair}; c=${x%_*}; d=${x#*_}; paddy/multiyear/run_chain.sh ep_${c}_$d 4 $d dc7_${c}_0_y7f $ST $(echo $PROD | sed "s#--k=[^ ]*#--k=$D/k_cal.in#") $(cfg $c);;
  esac; }
export -f job
printf '%s\n' setp21 setp00 setn05 setp05 setp02 | xargs -P 4 -I{} bash -c 'job {}'
printf '%s\n' cal1850 cal2000 cal2150 | xargs -P 3 -I{} bash -c 'job {}'
# calibrated vmax: log-linear interpolation of year-8 season CH4 (first year after the 7-yr settle) to 135 kg/ha
python3 - <<'PY'
import subprocess, numpy as np
v = [1850, 2000, 2150]; c = []
for x in v:
    d = f'/home/user/runs/out/paddy/flood_ek_{x}_y1s'
    c.append(float(subprocess.run(['python3','paddy/ghg_budget.py',d,d],capture_output=True,text=True).stdout.splitlines()[2].split()[2]))
k = np.polyfit(np.log(c), np.log(v), 1); vm = float(np.exp(np.polyval(k, np.log(135.))))
print('cal', list(zip(v, c)), '-> g2ch4', round(vm))
s = open('/home/user/runs/pan/k_g2ch4_1850.in').read().replace('g2ch4 1850 30', f'g2ch4 {round(vm)} 30')
open('/home/user/runs/pan/k_cal.in','w').write(s)
PY
printf '%s\n' pairp21_0 pairp21_20 pairp00_0 pairp00_20 pairn05_0 pairn05_20 pairp05_0 pairp05_20 pairp02_0 pairp02_20 | xargs -P 4 -I{} bash -c 'job {}'
echo done >> $ST
