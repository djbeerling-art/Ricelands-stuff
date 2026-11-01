#!/bin/bash
# v22 Morris screen (Fig 6a), after the figure runs (runZg, runZh) have finished. Resumable.
until grep -q "zg done" /home/user/runs/pan/statusZg 2>/dev/null && grep -q "zh done" /home/user/runs/pan/statusZh 2>/dev/null && grep -q "zv done" /home/user/runs/pan/statusZv 2>/dev/null; do sleep 120; done
cd /home/user/pd && export SCEPTER_OUT=/home/user/runs/out/ TILL=0.2 && paddy/screen/run_screen22.sh /home/user/runs/m22 4
