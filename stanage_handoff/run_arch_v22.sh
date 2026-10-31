#!/bin/bash
# One archetype, frozen v22 protocol (identical to the GMD archetype runs, runR.sh):
#   3-yr drained spin-up (gs22_<a>) -> 7-yr settle without rock (st22_<a>, kept as y7f) -> per dose, a copy of the settled
#   state and an N-yr chain (g22_<a>_<dose>) of 113-d season + 252-d fallow, basalt applied at the start of every season.
# Usage (repository root, SCEPTER_OUT set, v22_options.env sourced):
#   run_arch_v22.sh <arch> "<driver args>" "<doses e.g. 0 10 20>" <years> <status file>
# <driver args> come from archetypes.csv 'args' (rock, irralk, soilcc, cec, temp, om, fe3) plus --awd for rainfed archetypes.
# Rerunning resumes: finished phases are skipped via the status file. Disk: ~30 MB per pruned year.
# Future-climate cases (BASE_OUT set, environment): skip the spin-up and 7-yr settle, copy the baseline's settled state
# ($BASE_OUT/paddy/flood_st22_<arch>_y7f) and re-settle RESETTLE years (default 3, no rock) under the case's climate
# (st22_<a>, ending y${RESETTLE}f), then run the dose chains from that. BASE_OUT is the baseline run's SCEPTER_OUT.
set -u
a=$1; args=$2; doses=$3; ny=$4; ST=$5
ok(){ grep -q "^$1 rc 0" "$ST" 2>/dev/null; }
if [ -n "${BASE_OUT:-}" ]; then
  RS=${RESETTLE:-3}; b=$SCEPTER_OUT/paddy/flood_bs22_$a
  if ! ok st22_${a}_y${RS}f; then
    [ -d $b ] || cp -a $BASE_OUT/paddy/flood_st22_${a}_y7f $b || { echo "bs22_$a rc 97 (no baseline state)" >> "$ST"; exit 1; }
    paddy/multiyear/run_chain.sh st22_$a $RS 0 bs22_$a "$ST" $PROD $P21 $args || exit 1
    rm -rf $b
  fi
  for y in $(seq 1 $((RS-1))); do rm -rf $SCEPTER_OUT/paddy/flood_st22_${a}_y${y}[sf]; done
  for d in $doses; do
    o=$SCEPTER_OUT/paddy/flood_gx22_${a}_$d
    ok g22_${a}_${d}_y${ny}f && continue
    [ -d $o ] || cp -a $SCEPTER_OUT/paddy/flood_st22_${a}_y${RS}f $o
    paddy/multiyear/run_chain.sh g22_${a}_$d $ny $d gx22_${a}_$d "$ST" $PROD $P21 $args || exit 1
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
    python3 paddy/run_flooded_column.py gs22_$a fe2o2,amo2o 3 --fallow --basalt=0 $SOIL $P21 $args > "${ST%.txt}_spin.log" 2>&1
    rc=$?; [ -f $SCEPTER_OUT/paddy/flood_gs22_$a/run_complete.txt ] || rc=97   # SCEPTER can stop early yet exit 0
    echo "gs22_$a rc $rc (irralk x$f)" >> "$ST"; [ $rc = 0 ] && break
  done
  ok gs22_$a || exit 1
  echo "$args" > "$AF"
  paddy/prune_run.sh spin $SCEPTER_OUT/paddy/flood_gs22_$a
fi
paddy/multiyear/run_chain.sh st22_$a 7 0 gs22_$a "$ST" $PROD $P21 $args || exit 1
for y in 1 2 3 4 5 6; do rm -rf $SCEPTER_OUT/paddy/flood_st22_${a}_y${y}[sf]; done
for d in $doses; do
  o=$SCEPTER_OUT/paddy/flood_gx22_${a}_$d
  ok g22_${a}_${d}_y${ny}f && continue
  [ -d $o ] || cp -a $SCEPTER_OUT/paddy/flood_st22_${a}_y7f $o
  paddy/multiyear/run_chain.sh g22_${a}_$d $ny $d gx22_${a}_$d "$ST" $PROD $P21 $args || exit 1
  rm -rf $o
done
