#!/bin/bash
# One archetype, v25b protocol (as the GMD v25b runs, paddy/v25/stanage/pipeline_v25b.sbatch + chain_v25.sbatch; name kept):
#   3-yr drained spin-up (gs22_<a>) -> control settle to convergence, 7-12 yr (st22_<a>, kept as st22_<a>_set) -> per dose, a copy of the settled
#   state and an N-yr chain (g22_<a>_<dose>) of 113-d season + 252-d fallow, basalt applied at the start of every season.
# Usage (repository root, SCEPTER_OUT set, v22_options.env sourced):
#   run_arch_v22.sh <arch> "<driver args>" "<doses e.g. 0 10 20>" <years> <status file>
# <driver args> come from archetypes.csv 'args' (rock, irralk, soilcc, cec, temp, om, fe3) plus --awd for rainfed archetypes.
# Rerunning resumes: finished phases are skipped via the status file. Disk: ~30 MB per pruned year.
# Future-climate cases (BASE_OUT set, environment): skip the spin-up and 7-yr settle, copy the baseline's settled state
# ($BASE_OUT/paddy/flood_st22_<arch>_set) and re-settle RESETTLE years (default 3, no rock) under the case's climate
# (st22_<a>, ending y${RESETTLE}f), then run the dose chains from that. BASE_OUT is the baseline run's SCEPTER_OUT.
set -u
a=$1; args=$2; doses=$3; ny=$4; ST=$5
ok(){ grep -q "^$1 rc 0" "$ST" 2>/dev/null; }
# v25b: floodwater discharge by regime (KAQ_IRR/KAQ_RF from v25_options.env) on the season/fallow chains only; the
# drained spin-up gets neither --kaq nor --awd (as the GMD v25 settles). Unset KAQ_* (v22 env) leaves args unchanged.
kaq(){ [ -n "${KAQ_IRR:-}" ] || return 0; case " $args " in *" --awd "*) echo "--kaq=$KAQ_RF";; *) echo "--kaq=$KAQ_IRR";; esac; }
if [ -n "${BASE_OUT:-}" ]; then
  RS=${RESETTLE:-3}; b=$SCEPTER_OUT/paddy/flood_bs22_$a
  if ! ok st22_${a}_y${RS}f; then
    [ -d $b ] || cp -a $BASE_OUT/paddy/flood_st22_${a}_set $b || { echo "bs22_$a rc 97 (no baseline state)" >> "$ST"; exit 1; }
    paddy/multiyear/run_chain.sh st22_$a $RS 0 bs22_$a "$ST" $PROD $P21 $args $(kaq) || exit 1
    rm -rf $b
  fi
  for y in $(seq 1 $((RS-1))); do rm -rf $SCEPTER_OUT/paddy/flood_st22_${a}_y${y}[sf]; done
  for d in $doses; do
    o=$SCEPTER_OUT/paddy/flood_gx22_${a}_$d
    ok g22_${a}_${d}_y${ny}f && continue
    [ -d $o ] || cp -a $SCEPTER_OUT/paddy/flood_st22_${a}_y${RS}f $o
    paddy/multiyear/run_chain.sh g22_${a}_$d $ny $d gx22_${a}_$d "$ST" $PROD $P21 $args $(kaq) || exit 1
    rm -rf $o
  done
  exit 0
fi
# 3-yr drained spin-up (--fallow; args passed exactly as in the GMD runs)
# The initial adsorption/CEC equilibration can fail for a narrow, non-monotonic set of irrigation alkalinities (SCEPTER
# then stops with dt=0 but exits 0): such a spin-up is retried with --irralk scaled by NUDGE factors, and the args that
# worked are kept in <status>.args so the settle and dose chains (and resumes) use the same soil.
AF="${ST%.txt}.args"; [ -s "$AF" ] && args=$(cat "$AF")
if ! ok gs22_$a; then
  base=$args
  for f in ${NUDGE:-1 0.95 1.05 0.9 1.1}; do
    args=$(python3 -c "import re,sys; s=sys.argv[1]; print(re.sub(r'--irralk=([0-9.]+)', lambda m: '--irralk=%.3f' % (float(m.group(1))*$f), s))" "$base")
    rm -rf $SCEPTER_OUT/paddy/flood_gs22_$a
    python3 paddy/run_flooded_column.py gs22_$a fe2o2,amo2o 3 --fallow --basalt=0 $SOIL $P21 ${args/ --awd/} > "${ST%.txt}_spin.log" 2>&1
    rc=$?; [ -f $SCEPTER_OUT/paddy/flood_gs22_$a/run_complete.txt ] || rc=97   # SCEPTER can stop early yet exit 0
    echo "gs22_$a rc $rc (irralk x$f)" >> "$ST"; [ $rc = 0 ] && break
  done
  ok gs22_$a || exit 1
  echo "$args" > "$AF"
  paddy/prune_run.sh spin $SCEPTER_OUT/paddy/flood_gs22_$a
fi
# Control settle to convergence (v25b protocol, paddy/v25/stanage/pipeline_v25b.sbatch): at least SMIN (7), at most SMAX
# (12) years, stopping once season CH4 emission changes <2 %/yr over two consecutive years. The final fallow is renamed
# flood_st22_<a>_set (restart state for the dose chains and for future-climate BASE_OUT runs); status line
# "st22_<a>_set rc 0 years N converged 0|1".
emis(){ python3 - "$1" <<'PY'
import sys, numpy as np
f = sys.argv[1] + '/flx/flx_gas-pch4.txt'
h = open(f).readline().split(); d = np.loadtxt(f, skiprows=1, ndmin=2)
dt = np.diff(np.concatenate([[0.0], d[:, 0]]))
c = lambda k: float((d[:, h.index(k)]*dt).sum()) if k in h else 0.0
print(c('dif') + c('ch4eb') + c('ch4pl'))
PY
}
if ! ok st22_${a}_set; then
  Y=0; cv=0
  for n in $(seq ${SMIN:-7} ${SMAX:-12}); do
    paddy/multiyear/run_chain.sh st22_$a $n 0 gs22_$a "$ST" $PROD $P21 $args $(kaq) || exit 1
    Y=$n; e=$(for k in 2 1 0; do emis $SCEPTER_OUT/paddy/flood_st22_${a}_y$((n-k))s; done | tr '\n' ' ')
    python3 -c "import sys; a,b,c=map(float,'$e'.split()); sys.exit(0 if abs(b/a-1)<0.02 and abs(c/b-1)<0.02 else 1)" && { cv=1; break; }
  done
  rm -rf $SCEPTER_OUT/paddy/flood_st22_${a}_set
  mv $SCEPTER_OUT/paddy/flood_st22_${a}_y${Y}f $SCEPTER_OUT/paddy/flood_st22_${a}_set || exit 1
  for y in $(seq 1 $Y); do rm -rf $SCEPTER_OUT/paddy/flood_st22_${a}_y${y}[sf]; done
  echo "st22_${a}_set rc 0 years $Y converged $cv" >> "$ST"
fi
for d in $doses; do
  o=$SCEPTER_OUT/paddy/flood_gx22_${a}_$d
  ok g22_${a}_${d}_y${ny}f && continue
  [ -d $o ] || cp -a $SCEPTER_OUT/paddy/flood_st22_${a}_set $o
  paddy/multiyear/run_chain.sh g22_${a}_$d $ny $d gx22_${a}_$d "$ST" $PROD $P21 $args $(kaq) || exit 1
  rm -rf $o
done
