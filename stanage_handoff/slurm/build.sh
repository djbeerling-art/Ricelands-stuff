#!/bin/bash
# Build the production executable on Stanage (run once on a login node or in a short interactive job).
# v25 (final GMD model, 2 Nov 2026) = scepter.f90 at commit a8159b4; calibration paddy/krxn_calibrated_v25b.in and options
# in stanage_handoff/v25_options.env. (An identical exe already exists in ~/SCEPTER_v25 from the GMD runs; copying it
# into ~/SCEPTER is fine if both were compiled on the same node type.)
# Modules come from modules.sh (shared with arch_array.sbatch).
set -e
[ -d $HOME/SCEPTER ] || git clone https://github.com/djbeerling-art/Ricelands-stuff $HOME/SCEPTER
cd $HOME/SCEPTER && git fetch origin && git checkout claude/project-thread-lst1mi && git pull --ff-only   # = pip6bj-pan + global-run prep
source stanage_handoff/slurm/modules.sh
git show a8159b4:scepter.f90 > scepter.f90.v25
cmp -s scepter.f90 scepter.f90.v25 || echo "NOTE: branch scepter.f90 differs from v25 (a8159b4); building v25"
cp scepter.f90 scepter.f90.head && cp scepter.f90.v25 scepter.f90
# restore the branch's scepter.f90 even if make fails, so the next git checkout/pull is not blocked
# makefile_paddy_fast (banded solver, speciation cache, no -fcheck) is the production build: the plain makefile_paddy is
# ~15x slower. It uses -march=native, so compile ON A COMPUTE NODE of the partition the jobs run on (srun below), not
# on the login node. Run build.sh itself on the login node (git and pip need its network access).
srun --partition=sheffield --account=default --cpus-per-task=1 --mem=4G --time=00:30:00 \
  bash -c "source stanage_handoff/slurm/modules.sh && make --file=makefile_paddy_fast PROGRAM=scepter_paddy_v25 OBJS=scepter_paddy_v25.o" \
  || { mv scepter.f90.head scepter.f90; exit 1; }
mv scepter.f90.head scepter.f90
python3 -m pip install --user numpy scipy pandas scikit-learn SALib matplotlib
# Slurm does not create the --output directory: a job whose logs/ is missing fails at once with no log at all.
mkdir -p logs status
ls -l scepter_paddy_v25 && module list
