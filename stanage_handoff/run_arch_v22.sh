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
  # arch_pack retries a numerical failure (rc 97/98) with NUDGE = one irralk factor per attempt. The baseline path applies
  # it in the spin-up loop below; future cases skip that loop, so apply the factor here, or every retry repeats the
  # same irralk (seen for rf0401 in the SSP2-4.5 futures). A factor of 1 (first attempt) leaves args unchanged.
  case "${NUDGE:-1}" in *" "*|1) ;; *)
    args=$(python3 -c "import re,sys; s=sys.argv[1]; print(re.sub(r'--irralk=([0-9.]+)', lambda m: '--irralk=%.3f' % (float(m.group(1))*float(sys.argv[2])), s))" "$args" "$NUDGE")
    echo "bs22_$a irralk x$NUDGE: $args" >> "${ST%.txt}_spin.log";;
  esac
  if ! ok st22_${a}_y${RS}f; then
    # baseline state: a directory (older runs) or a member of the baseline's per-archetype archive $BASE_OUT/paddy_tar/<a>.tar.gz
    if [ ! -d $b ] && [ ! -d $BASE_OUT/paddy/flood_st22_${a}_set ] && [ -f $BASE_OUT/paddy_tar/$a.tar.gz ]; then
      tar -xzf $BASE_OUT/paddy_tar/$a.tar.gz -C $SCEPTER_OUT/paddy flood_st22_${a}_set && mv $SCEPTER_OUT/paddy/flood_st22_${a}_set $b
    fi
    [ -d $b ] || cp -a $BASE_OUT/paddy/flood_st22_${a}_set $b || { echo "bs22_$a rc 97 (no baseline state)" >> "$ST"; exit 1; }
    CLIM_YOFF=-$RS paddy/multiyear/run_chain.sh st22_$a $RS 0 bs22_$a "$ST" $PROD $P21 $args $(kaq) || exit 1   # transient climate: re-settle under year 1
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
# Control settle to steady state. v25b GMD protocol: at least SMIN (7), at most 12 years, stopping once season CH4 changes
# <2 %/yr over two consecutive years. Global runs (3 Nov 2026): reducible Fe(III) (amfe3) in cool, high-OM archetypes
# depletes with a ~20-yr e-folding time, so a 12-yr settle left the controls drifting (CH4 x2-3 over 25 yr). The settle
# therefore also requires the column Fe(III) stock (amfe3, from the latest fallow's restart profile) to change < FETOL
# (default 1 %/yr) over two consecutive years, up to SMAX (default 80) years. FETOL=off restores the CH4-only criterion.
# The final fallow is renamed flood_st22_<a>_set (restart state for the dose chains and future-climate BASE_OUT runs);
# status line "st22_<a>_set rc 0 years N converged 0|1"; the yearly CH4 and Fe(III) series are in <status>_settle.txt.
emis(){ python3 - "$1" <<'PY'
import sys, numpy as np
f = sys.argv[1] + '/flx/flx_gas-pch4.txt'
h = open(f).readline().split(); d = np.loadtxt(f, skiprows=1, ndmin=2)
dt = np.diff(np.concatenate([[0.0], d[:, 0]]))
c = lambda k: float((d[:, h.index(k)]*dt).sum()) if k in h else 0.0
print(c('dif') + c('ch4eb') + c('ch4pl'))
PY
}
# reducible Fe(III) stock of the plough layer (z <= FEZ m, default 0.2): dz-weighted amfe3, cell bounds at node midpoints
fe3(){ python3 - "$1" "${FEZ:-0.2}" <<'PY'
import sys
f, zmax = sys.argv[1] + '/prof/prof_sld-save.txt', float(sys.argv[2])
L = open(f).read().splitlines(); h = L[0]
names = ['z'] + [h[4+5*i:9+5*i].strip() for i in range((len(h.rstrip())-4)//5)]
j = names.index('amfe3')
r = [l.split() for l in L[1:] if l.strip()]
z = [float(x[0]) for x in r]; v = [float(x[j]) for x in r]
b = [0.] + [(z[i] + z[i+1])/2 for i in range(len(z) - 1)] + [z[-1] + (z[-1] - z[-2])/2]
print(sum(v[i]*max(0., min(b[i+1], zmax) - b[i]) for i in range(len(z))))
PY
}
# Per-archetype Fe(III) balance (David, 3 Nov 2026), for archetypes whose settle ran past ~20 yr: v25b has no Fe return
# from below the pan (Fe-illuvial subsoil, capillary rise) and fixes irrigation/sediment Fe at fe3in 0.3, so cool, high-OM
# soils settle only once their reducible Fe(III) is exhausted (control CH4 x5), which long-cultivated paddies never reach.
# FEBAL=1: an 8-yr probe settle (fp22_<a>, default fe3in) gives the whole-column amfe3 loss over years 3-8, and the settle
# and dose chains then use fe3in = 0.3 + that net loss, capped at FEMAX (default 1) mol/m2/yr, appended to the args (kept
# in <status>.args). Status line "fb22_<a> rc 0 loss L fe3in X". Use with the GMD settle cap (SMAX=12 FETOL=off).
if [ -n "${FEBAL:-}" ] && ! ok fb22_$a; then
  # run_chain prunes the previous fallow's profiles each year, so read year 3 before running on to year 8 (resumes)
  F3="${ST%.txt}_fe3y3.txt"
  if [ ! -s "$F3" ]; then
    paddy/multiyear/run_chain.sh fp22_$a 3 0 gs22_$a "$ST" $PROD $P21 $args $(kaq) || exit 1
    FEZ=99 fe3 $SCEPTER_OUT/paddy/flood_fp22_${a}_y3f > "$F3" || exit 1
  fi
  paddy/multiyear/run_chain.sh fp22_$a 8 0 gs22_$a "$ST" $PROD $P21 $args $(kaq) || exit 1
  r=$(python3 - $(cat "$F3") $(FEZ=99 fe3 $SCEPTER_OUT/paddy/flood_fp22_${a}_y8f) ${FEMAX:-1} <<'PY'
import sys
f3, f8, cap = map(float, sys.argv[1:])
loss = max((f3 - f8)/5, 0.)
print('%.4f %.3f' % (loss, min(0.3 + loss, cap)))
PY
) || exit 1
  set -- $r
  for y in $(seq 1 8); do rm -rf $SCEPTER_OUT/paddy/flood_fp22_${a}_y${y}[sf]; done
  args="$(echo "$args" | sed 's/ *--fe3in=[0-9.]*//') --fe3in=$2"; echo "$args" > "$AF"
  echo "fb22_$a rc 0 loss $1 fe3in $2" >> "$ST"
fi
if ! ok st22_${a}_set; then
  Y=0; cv=0; SL="${ST%.txt}_settle.txt"; touch "$SL"
  for n in $(seq ${SMIN:-7} ${SMAX:-80}); do
    grep -q "^$n " "$SL" && { Y=$n; continue; }   # resume: year already checked
    paddy/multiyear/run_chain.sh st22_$a $n 0 gs22_$a "$ST" $PROD $P21 $args $(kaq) || exit 1
    Y=$n; c=$(emis $SCEPTER_OUT/paddy/flood_st22_${a}_y${n}s 2>/dev/null || echo nan); f=$(fe3 $SCEPTER_OUT/paddy/flood_st22_${a}_y${n}f 2>/dev/null || echo nan)
    echo "$n $c $f" >> "$SL"
    [ $n -ge 3 ] && rm -rf $SCEPTER_OUT/paddy/flood_st22_${a}_y$((n-3))[sf]   # keep the last three years only
    python3 - "$SL" "${FETOL:-0.01}" <<'PY' && { cv=1; break; }
import sys, math
r = [l.split() for l in open(sys.argv[1]) if l.strip()]
if len(r) < 3: sys.exit(1)
(_, c0, f0), (_, c1, f1), (_, c2, f2) = r[-3:]
c0, c1, c2 = float(c0), float(c1), float(c2)
ok = abs(c1/c0-1) < 0.02 and abs(c2/c1-1) < 0.02
if sys.argv[2] != 'off':
    f0, f1, f2 = float(f0), float(f1), float(f2); t = float(sys.argv[2])
    ok = ok and not math.isnan(f2) and abs(f1/f0-1) < t and abs(f2/f1-1) < t
sys.exit(0 if ok else 1)
PY
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
