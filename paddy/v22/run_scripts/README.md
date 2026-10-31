Cloud run scripts behind the GMD reference-site chains (paths are those of the cloud container: D=/home/user/runs/pan,
SCEPTER_OUT=/home/user/runs/out/). runD.sh defines SOIL/PROD; runV.sh sources it (k file -> k_cal.in = krxn_calibrated_v22.in,
exe v21; v22/v23 runs swap the exe name) and defines P21 and the settled states; runR23.sh is the v23 reference rerun;
runC24.sh the v24 Si root-barrier tests. archR.txt holds per-site extra args ("ref|" = none).

Reference-site rock: no --rock, i.e. the driver default (data/dust_basalt.in without hornblende: fo 0.12, ab 0.172,
an 0.258, fa 0.05, dp 0.189, kfs 0.06, renormalised), with --psd=data/psdrain_renforth_p80-100um.in added by
run_chain.sh for every dose > 0. Start state for the 10-yr chains: flood_vc_rref_y7f (7-yr settle). Exe built with
makefile_paddy_fast.
