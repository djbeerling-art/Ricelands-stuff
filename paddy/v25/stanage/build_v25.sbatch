#!/bin/bash
# Build scepter_paddy_v25 (makefile_paddy_fast, -march=native) on a compute node of the partition the runs use.
#SBATCH --job-name=v25build
#SBATCH --partition=sheffield
#SBATCH --account=default
#SBATCH --time=00:30:00
#SBATCH --mem=4G
#SBATCH --cpus-per-task=1
#SBATCH --output=logs/%x_%j.out
set -eu
cd $HOME/SCEPTER_v25
source stanage_handoff/slurm/modules.sh
rm -f *.o scepter_paddy_fast
make --file=makefile_paddy_fast
mv scepter_paddy_fast scepter_paddy_v25
git log --oneline -1
ls -l scepter_paddy_v25
