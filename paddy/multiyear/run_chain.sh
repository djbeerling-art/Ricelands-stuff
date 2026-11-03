#!/bin/bash
# Multi-year paddy run as a chain of restarts: each year = one 113-d rice season (basalt applied at its start if dose > 0,
# urea, plants) followed by a drained, crop-free fallow (water table 0.5 m, no plant reactions, no fertiliser).
# Usage (repository root, SCEPTER_OUT set): paddy/multiyear/run_chain.sh <name> <years> <dose t/ha> <spin-up tag> <status file> [driver options]
# (no methanogen pH response unless --ch4ph=... is passed)
# Tags: <name>_y<n>s (season), <name>_y<n>f (fallow). Rerunning skips years already finished (status line rc 0).
# The annual OM input (--om=, g C m-2 yr-1, default 450) is split between the phases: a fraction OMF (environment,
# default 0.7: roots, exudates and residue incorporated at land preparation) during the season, the rest (stubble,
# weeds) during the fallow; FOPT (environment) adds driver options to the fallow only (e.g. "--temp=18 --fsat=0.3"); each phase gets the matching rate (g C m-2 yr-1) for its length.
# XRS (environment, e.g. ",fhage") appends extra reactions to the season and fallow reaction lists.
set -u
name=$1; ny=$2; dose=$3; prev=$4; st=$5; shift 5
om=$(printf '%s\n' "$@" | grep '^--om=' | tail -1 | cut -d= -f2); om=${om:-450}; OMF=${OMF:-0.7}
oms=$(python3 -c "print(round($om*$OMF/0.31,2))"); omf=$(python3 -c "print(round($om*(1-$OMF)/0.69,2))")
set -- $(printf '%s\n' "$@" | grep -v '^--om=')
RS=fe2o2,g2fe3,g2gr,g2so4,g2ch4,ch4o2,fe2gr,ch4pl,ch4eb,fe2fs,fesox,amo2o,g2n21,g2n2p,n2opl,g2gt,rtco2,g2o2,nh4up,rtoxy,groxy,siup,sidox${XRS:-}
RF=fe2o2,g2fe3,g2gr,g2so4,g2ch4,ch4o2,fe2gr,ch4eb,fe2fs,fesox,amo2o,g2n21,g2n2p,g2gt,g2o2,groxy,sidox${XRS:-}
C="--ch4 --n --kaol=0.05 --refsoil --gt=0.02 --nz=15 --exe=scepter_paddy_fast --nucl=cc:0.001 --kscale=maf:0.45,fsp:0.25"
ok(){ grep -q "^$1 rc 0" "$st" 2>/dev/null; }
# Transient climate (paddy/global/transient_clim.py): if the --clim file has per-year siblings <stem>_y<N>.csv, chain
# year y uses <stem>_y<y+CLIM_YOFF>.csv (clamped to the available years); otherwise --clim is used unchanged.
CLIM0=$(printf '%s\n' "$@" | grep '^--clim=' | tail -1 | cut -d= -f2)
CLIMN=0; [ -n "$CLIM0" ] && [ -f "${CLIM0%.csv}_y1.csv" ] && CLIMN=$(ls ${CLIM0%.csv}_y*.csv | wc -l)
# Dynamic Fe return (FERET=1, David 3 Nov 2026): v25b has no Fe return from below the pan (Fe-illuvial subsoil, capillary
# rise, deeper tillage) and a fixed irrigation/sediment Fe(III) input (--fe3in), so plough-layer Fe drains away over
# decades and the control's CH4 climbs. With FERET set, each year's --fe3in (ferrihydrite to the plough layer, with the
# OM input) is the net Fe that left the plough layer (z <= FERET_Z m, default 0.2) the year before, by transport across
# the pan, leaching and floodwater discharge (paddy/multiyear/fe_loss.py on the season + fallow zint files), floored at 0
# and capped at FERET_MAX (default 5) mol m-2 yr-1. The value is kept in the fallow's run dir (feret.txt), so it follows
# the restart state into the settle, the dose-chain copies and future-climate runs; a start without one (fresh spin-up)
# uses the --fe3in in the options. Status lines "<name>_y<n>f feret <value>". Same rule for control and treatment.
fe_in(){ [ -n "${FERET:-}" ] && [ -s $SCEPTER_OUT/paddy/flood_$1/feret.txt ] && echo "--fe3in=$(cat $SCEPTER_OUT/paddy/flood_$1/feret.txt)"; }
ARGS0=("$@")
for y in $(seq 1 $ny); do
  ts=${name}_y${y}s; tf=${name}_y${y}f
  if [ $CLIMN -gt 0 ]; then
    k=$(( y + ${CLIM_YOFF:-0} )); [ $k -lt 1 ] && k=1; [ $k -gt $CLIMN ] && k=$CLIMN
    set -- $(printf '%s\n' "${ARGS0[@]}" | sed "s#^--clim=.*#--clim=${CLIM0%.csv}_y$k.csv#")
  fi
  if [ -n "${FERET:-}" ]; then   # later options win, so the returned Fe overrides --fe3in for this year's season and fallow
    FI=$(fe_in $prev); [ -n "$FI" ] && set -- $(printf '%s\n' "$@" | grep -v '^--fe3in=') $FI
  fi
  if ! ok $ts; then
    # puddling before transplanting mixes the plough layer (TILL = depth in m, default 0.16; 0 = no tillage)
    [ "${TILL:-0.16}" != 0 ] && python3 paddy/multiyear/till.py $SCEPTER_OUT/paddy/flood_$prev ${TILL:-0.16}
    p=""; [ "$dose" != 0 ] && p=--psd=data/psdrain_renforth_p80-100um.in
    python3 paddy/run_flooded_column.py $ts $RS 0.31 --season --nfert=120 --rstrt=$prev --basalt=$dose --om=$oms $p $C "$@" > /dev/null 2>&1
    rc=$?; awk 'END{exit !($1+0>=0.3095)}' $SCEPTER_OUT/paddy/flood_$ts/flx/flx_gas-pch4.txt 2>/dev/null || rc=98
    find $SCEPTER_OUT/paddy/flood_$ts/flx -name 'flx_psd*' -delete 2>/dev/null
    echo "$ts rc $rc" >> "$st"; [ $rc = 0 ] || exit 1
  fi
  if ! ok $tf; then
    # the fallow takes the same soil options but no water-management flags (drained by --fallow)
    python3 paddy/run_flooded_column.py $tf $RF 0.69 --fallow --rstrt=$ts --basalt=0 --om=$omf $C $(printf '%s\n' "$@" | grep -v -e '^--awd$' -e '^--phd' -e '^--k=') --k=$(printf '%s\n' "$@" | grep '^--k=' | cut -d= -f2) ${FOPT:-} > /dev/null 2>&1
    rc=$?; awk 'END{exit !($1+0>=0.6895)}' $SCEPTER_OUT/paddy/flood_$tf/flx/flx_gas-pch4.txt 2>/dev/null || rc=98
    find $SCEPTER_OUT/paddy/flood_$tf/flx -name 'flx_psd*' -delete 2>/dev/null
    # KEEPALK=1 (environment) keeps the porewater, dissolved-gas and solid profiles for paddy/alk_flux.py
    if [ $y -gt 1 ]; then if [ -n "${KEEPALK:-}" ]; then paddy/prune_run.sh season $SCEPTER_OUT/paddy/flood_${name}_y$((y-1))[sf]
      else find $SCEPTER_OUT/paddy/flood_${name}_y$((y-1))[sf]/prof -type f -delete 2>/dev/null; fi; fi
    echo "$tf rc $rc" >> "$st"; [ $rc = 0 ] || exit 1
    if [ -n "${FERET:-}" ]; then
      L=$(python3 paddy/multiyear/fe_loss.py $SCEPTER_OUT/paddy/flood_$ts $SCEPTER_OUT/paddy/flood_$tf --z=${FERET_Z:-0.2}) || exit 1
      python3 -c "print('%.4f' % min(max($L, 0.), ${FERET_MAX:-5}))" > $SCEPTER_OUT/paddy/flood_$tf/feret.txt
      echo "$tf feret $(cat $SCEPTER_OUT/paddy/flood_$tf/feret.txt) loss $L" >> "$st"
    fi
  fi
  # keep only what ghg_budget.py reads (a season run is ~50 MB unpruned); the latest fallow keeps its restart state
  # NOPRUNE=1 (environment) keeps every output of the latest year (verification, process figures)
  [ -n "${NOPRUNE:-}" ] && [ $y = $ny ] || paddy/prune_run.sh season $SCEPTER_OUT/paddy/flood_$ts
  [ $y -gt 1 ] && paddy/prune_run.sh season $SCEPTER_OUT/paddy/flood_${name}_y$((y-1))f
  prev=$tf
done
