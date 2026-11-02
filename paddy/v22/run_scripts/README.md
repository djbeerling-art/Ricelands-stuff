Cloud run scripts behind the GMD reference-site chains (paths are those of the cloud container: D=/home/user/runs/pan,
SCEPTER_OUT=/home/user/runs/out/). runD.sh defines SOIL/PROD; runV.sh sources it (k file -> k_cal.in = krxn_calibrated_v22.in,
exe v21; v22/v23 runs swap the exe name) and defines P21 and the settled states; runR23.sh is the v23 reference rerun;
runC24.sh the v24 Si root-barrier tests. archR.txt holds per-site extra args ("ref|" = none).

Reference-site rock: no --rock, i.e. the driver default (data/dust_basalt.in without hornblende: fo 0.12, ab 0.172,
an 0.258, fa 0.05, dp 0.189, kfs 0.06, renormalised), with --psd=data/psdrain_renforth_p80-100um.in added by
run_chain.sh for every dose > 0. Start state for the 10-yr chains: flood_vc_rref_y7f (7-yr settle). Exe built with
makefile_paddy_fast.

Added 1 Nov 2026 (cloud originals, paths unchanged): runR.sh (10-yr reference + six archetypes, v21 baseline; chainsR.txt),
runZa.sh (v22 frozen exe: reference 10/20 t, Wang 2014/2024 field seasons, archetype chains), runZg.sh / runZh.sh /
runZv.sh (w 0 / w 0.4 reference chains; irr061 unpruned), runM.sh (Morris v22 driver -> paddy/screen/run_screen22.sh),
runZ.sh / runZ23.sh, runE.sh (7-yr settles dc7_* and g2ch4 calibration -> k_cal.in), runW.sh / runWg.sh (Wang sites),
jobsV.txt / jobsZa.txt (job lists as run), k_cal.in (= krxn_calibrated_v22.in). Evaluation-site seasons (Park, Gong,
Uchibayashi, Wang 2014 slag, Wang 2024 wollastonite) are defined in runV.sh / jobsV.txt; rock recipes data/dust_<rock>.in.
